from PyQt5.QtCore import QObject
from threading import Thread
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, String, ForeignKey, create_engine, func
from queue import Queue
from functools import partial
import time
import random


Base = declarative_base()


class Association(Base):
    __tablename__ = "association"
    word_id = Column(ForeignKey("word.id"), primary_key=True)
    definition_id = Column(ForeignKey("definition.id"), primary_key=True)
    knowledge_level = Column(Integer)
    word = relationship("Word", back_populates="definitions")
    definition = relationship("Definition", back_populates="words")
    

class Word(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    word = Column(String)
    definitions = relationship("Association", back_populates="word")


class Definition(Base):
    __tablename__ = "definition"
    id = Column(Integer, primary_key=True)
    definition = Column(String)
    words = relationship("Association", back_populates="definition")
    
    
engine = create_engine("sqlite:///./database/database.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class RepetitionController(QObject):
    def __init__(self, repetition_model, search_model):
        self.repetition_model = repetition_model
        self.search_model = search_model
        self.repetitions_enabled = True
        self.quiz_timer = Thread(target=self.quiz_wait, daemon=True)
        self.quiz_timer.start()
        self.operations = Queue()
        self.consumer = Thread(target=self.consume)
        self.consumer.start()
    
    def quiz_wait(self):
        while True:
            time.sleep(self.repetition_model.quiz_interval + self.repetition_model.quiz_time)
            if self.repetitions_enabled:
                self.create_quiz()
    
    def consume(self):
        while True:
            op = self.operations.get(block=True)
            if op is None:
                break
            op()
            
    def add_meanings(self, words, definition):
        self.operations.put(partial(self.add_meanings_, words, definition))
        
    def add_meanings_(self, words, definition):
        session = Session()
        try:
            d = session.query(Definition).filter(Definition.definition == definition).first()
            if d is None:
                d = Definition(definition=definition)
            
            for word in words:
                w = session.query(Word).filter(Word.word == word).first()
                if w is None:
                    w = Word(word=word)
                    
                found = False
                for a in w.definitions:
                    if a.definition == d:
                        found = True
                        break
                        
                if not found:
                    a = Association(knowledge_level=1)
                    a.definition = d
                    w.definitions.append(a)
                    
                session.add(w)
                
            session.add(d)
            session.commit()
        except Exception as e:
            session.rollback()
            self.search_model.db_error = str(e)
        finally:
            session.close()
            self.search_model.database_operation_finished.emit()
    
    def create_quiz(self):
        self.operations.put(self.create_quiz_)
    
    def create_quiz_(self):
        session = Session()
        try:
            level = session.query(func.min(Association.knowledge_level)).first()[0]
            # find a random meaning with the lowest knowledge level
            meaning = (
                session.query(Association)
                .filter(Association.knowledge_level == level)
                .order_by(func.random())
                .first()
            )
            w = meaning.word
            d = meaning.definition
            
            # in a level 1 quiz you are supposed to choose the correct definition of a word 
            # from a list of 4 possible answers
            if level == 1:
                options = (
                    session.query(Definition)
                    .filter(Definition.definition != d.definition)
                    .order_by(func.random())
                    .limit(3)
                    .all()
                )
                # there is not enough data to generate the quiz
                if len(options) < 3:
                    raise
                options = list(map(lambda d: d.definition, options))
                options.append(d.definition)
                random.shuffle(options)
                self.repetition_model.quiz_level = 1
                self.repetition_model.quiz_question = w.word
                self.repetition_model.quiz_options = options
            
            # in a level 2 quiz you are supposed to choose a word
            # matching the given definition
            elif level == 2:
                options = (
                    session.query(Word)
                    .filter(Word.word != w.word)
                    .order_by(func.random())
                    .limit(3)
                    .all()
                )
                # there is not enough data to generate the quiz
                if len(options) < 3:
                    raise
                options = list(map(lambda w: w.word, options))
                options.append(w.word)
                random.shuffle(options)
                self.repetition_model.quiz_level = 2
                self.repetition_model.quiz_question = d.definition
                self.repetition_model.quiz_options = options
            
            # in a level 3 quiz you are supposed to enter a word
            # matching the given definition
            elif level == 3:
                self.repetition_model.quiz_level = 3
                self.repetition_model.quiz_question = d.definition
            
            self.repetition_model.quiz_created.emit()
            
        except Exception as e:
            session.rollback()
        finally:
            session.close()
    
    def check_quiz_answer(self, answer):
        self.operations.put(partial(self.check_quiz_answer_, answer))
        
    def check_quiz_answer_(self, answer):
        session = Session()
        try:
            question = self.repetition_model.quiz_question
            level = self.repetition_model.quiz_level
            
            if level == 1:
                # check which options are correct answers
                correct_answers = []
                correct_answers_assoc = []
                for option in self.repetition_model.quiz_options:
                    w = (
                        session.query(Word)
                        .filter(Word.word == question)
                        .first()
                    )
                    d = (
                        session.query(Definition)
                        .filter(Definition.definition == option)
                        .first()
                    )
                    assoc = None
                    for a in w.definitions:
                        if a.definition == d:
                            assoc = a
                            break
                    if assoc is not None:
                        correct_answers.append(option)
                        correct_answers_assoc.append(assoc)
                        
                # if the answer is correct, increase the knowledge level of the meaning
                if answer in correct_answers:
                    for i in range(len(correct_answers)):
                        if answer == correct_answers[i]:
                            correct_answers_assoc[i].knowledge_level = 2
                            session.add(correct_answers_assoc[i])
                    self.repetition_model.quiz_feedback = "Correct!"
                else:
                    self.repetition_model.quiz_feedback = "Wrong!"
                self.repetition_model.quiz_correct_answers = correct_answers
            
            elif level == 2:
                # check which options are correct answers
                correct_answers = []
                correct_answers_assoc = []
                for option in self.repetition_model.quiz_options:
                    d = (
                        session.query(Definition)
                        .filter(Definition.definition == question)
                        .first()
                    )
                    w = (
                        session.query(Word)
                        .filter(Word.word == option)
                        .first()
                    )
                    assoc = None
                    for a in d.words:
                        if a.word == w:
                            assoc = a
                            break
                    if assoc is not None:
                        correct_answers.append(option)
                        correct_answers_assoc.append(assoc)
                    
                # if the answer is correct, increase the knowledge level of the meaning
                if answer in correct_answers:
                    for i in range(4):
                        if answer == correct_answers[i]:
                            correct_answers_assoc[i].knowledge_level = 3
                            session.add(correct_answers_assoc[i])
                    self.repetition_model.quiz_feedback = "Correct!"
                # if the answer is incorrect, decrease the knowledge level of the meaning
                elif len(correct_answers) == 1:
                    correct_answers_assoc[0].knowledge_level = 1
                    session.add(correct_answers_assoc[0])
                    self.repetition_model.quiz_feedback = "Wrong! The correct answer is: " + correct_answers[0]
                else:
                    for a in correct_answers_assoc:
                        a.knowledge_level = 1
                        session.add(a)
                    self.repetition_model.quiz_feedback = "Wrong!"
                self.repetition_model.quiz_correct_answers = correct_answers
            
            elif level == 3:
                d = (
                    session.query(Definition)
                    .filter(Definition.definition == question)
                    .first()
                )
                w = (
                    session.query(Word)
                    .filter(Word.word == answer)
                    .first()
                )
                correct_answers = []
                correct_answers_assoc = []
                assoc = None
                for a in d.words:
                    correct_answers_assoc.append(a)
                    correct_answers.append(a.word)
                    if a.word == w:
                        assoc = a
                        
                # if the answer is wrong, decrease the knowledge level of every correct answer
                if assoc is None:
                    for a in correct_answers_assoc:
                        a.knowledge_level = 2
                        session.add(a)
                    self.repetition_model.quiz_feedback = "Wrong! An example of a correct answer is: " + random.choice(correct_answers)
                else:
                    assoc.knowledge_level = 3
                    session.add(assoc)
                    self.repetition_model.quiz_feedback = "Correct!"
                    
            # Session.commit()
            
        except Exception as e:
            session.rollback()
            self.repetition_model.quiz_feedback = "Error"
        finally:
            session.close()
            self.repetition_model.quiz_answer_checked.emit()