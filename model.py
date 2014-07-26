from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, scoped_session

ENGINE = None
Session = None
engine = create_engine("sqlite:///quakes.db", echo = False)
session = scoped_session(sessionmaker(bind = engine,
                                    autocommit = False,
                                    autoflush = False))
Base = declarative_base()
Base.query = session.query_property()

def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("sqlite:///quakes.db", echo=True)
    Session = sessionmaker(bind = ENGINE)
    return Session()

class Quake(Base):
    __tablename__ = "quakes"

    id = Column(String(30), primary_key = True)
    timestamp = Column(Integer)
    updated = Column(Integer)
    magnitude = Column(Float)
    tsunami = Column(Integer, nullable = True)
    latitude = Column(String(10))
    longitude = Column(String(10))

class QuakeUpdate(Base):
    __tablename__ = "quake_update"

    update_time = Column(String(30), primary_key = True)

def main():
    pass

if __name__ == "__main__":
    main()
