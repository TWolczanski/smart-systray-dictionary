from PyQt5.QtCore import QObject
from threading import Thread
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, String, ForeignKey, create_engine, func
from queue import Queue
from functools import partial
import time


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
        self.quiz_timer = Thread(target=self.quiz_wait, daemon=True)
        self.quiz_timer.start()
        self.operations = Queue()
        self.consumer = Thread(target=self.consume)
        self.consumer.start()
    
    def quiz_wait(self):
        while True:
            time.sleep(self.repetition_model.quiz_interval + self.repetition_model.quiz_time)
            self.create_quiz()
            self.repetition_model.quiz_created.emit()
    
    def consume(self):
        self.session = Session()
        while True:
            op = self.operations.get(block=True)
            if op is None:
                self.session.close()
                break
            op()
            
    def add_meanings(self, words, definition):
        self.operations.put(partial(self.add_meanings_, words, definition))
        
    def add_meanings_(self, words, definition):
        try:
            d = self.session.query(Definition).filter(Definition.definition == definition).first()
            if d is None:
                d = Definition(definition=definition)
            
            for word in words:
                w = self.session.query(Word).filter(Word.word == word).first()
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
                    
                self.session.add(w)
                
            self.session.add(d)
            self.session.commit()
            
        except Exception as e:
            self.search_model.db_error = str(e)
            
        self.search_model.database_operation_finished.emit()
    
    def create_quiz(self):
        self.operations.put(lambda: self.create_quiz_())
    
    def create_quiz_(self):
        min_level = self.session.query(func.min(Association.knowledge_level)).first()[0]
        meaning = self.session.query(Association).filter(Association.knowledge_level == min_level).order_by(func.random()).first()