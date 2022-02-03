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
        self.repetitions_enabled = False
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
        self.operations.put(lambda: self.create_quiz_())
    
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
        print(answer)
        self.repetition_model.quiz_answer_checked.emit()