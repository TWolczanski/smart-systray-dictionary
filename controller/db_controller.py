from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, String, ForeignKey, create_engine

Base = declarative_base()

association_table_pl = Table(
    "association_pl",
    Base.metadata,
    Column("word_id", ForeignKey("word.id"), primary_key=True),
    Column("definition_id", ForeignKey("polish_definition.id"), primary_key=True)
)

association_table_en = Table(
    "association_en",
    Base.metadata,
    Column("word_id", ForeignKey("word.id"), primary_key=True),
    Column("definition_id", ForeignKey("english_definition.id"), primary_key=True)
)


class Word(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    word = Column(String)
    polish_definitions = relationship(
        "PolishDefinition",
        secondary=association_table_pl,
        back_populates="words"
    )
    english_definitions = relationship(
        "EnglishDefinition",
        secondary=association_table_en,
        back_populates="words"
    )


class PolishDefinition(Base):
    __tablename__ = "polish_definition"
    id = Column(Integer, primary_key=True)
    definition = Column(String)
    words = relationship(
        "Word",
        secondary=association_table_pl,
        back_populates="polish_definitions"
    )
    
    
class EnglishDefinition(Base):
    __tablename__ = "english_definition"
    id = Column(Integer, primary_key=True)
    definition = Column(String)
    words = relationship(
        "Word",
        secondary=association_table_en,
        back_populates="english_definitions"
    )
    

class DatabaseController():
    def __init__(self):
        engine = create_engine("sqlite:///./database/database.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def add_words(self, words, definition, def_lang):
        if def_lang == "pl":
            d = self.session.query(PolishDefinition).filter(PolishDefinition.definition == definition).first()
            if d is None:
                d = PolishDefinition(definition=definition)
            
            for word in words:
                w = self.session.query(Word).filter(Word.word == word).first()
                if w is None:
                    w = Word(word=word)
                if d not in w.polish_definitions:
                    w.polish_definitions.append(d)
                self.session.add(w)
                
            self.session.add(d)
        else:
            d = self.session.query(EnglishDefinition).filter(EnglishDefinition.definition == definition).first()
            if d is None:
                d = EnglishDefinition(definition=definition)
                
            for word in words:
                w = self.session.query(Word).filter(Word.word == word).first()
                if w is None:
                    w = Word(word=word)
                if d not in w.english_definitions:
                    w.english_definitions.append(d)
                self.session.add(w)
                
            self.session.add(d)
            
        self.session.commit()