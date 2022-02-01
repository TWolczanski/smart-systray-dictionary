from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, String, ForeignKey, create_engine, func


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
    

class DatabaseController():
    def __init__(self):
        engine = create_engine("sqlite:///./database/database.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def add_words(self, words, definition):
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
    
    def get_random_meaning(self):
        min_level = self.session.query(func.min(Association.knowledge_level)).first()[0]
        meaning = self.session.query(Association).filter(Association.knowledge_level == min_level).order_by(func.random()).first()
        return meaning