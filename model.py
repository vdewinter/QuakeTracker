from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.dialects import postgresql
import os

engine = create_engine("sqlite:///quakes.db", echo = False)
engine = create_engine(os.environ["DATABASE_URL"], echo=True)
session = scoped_session(sessionmaker(bind = engine,
                                    autocommit = False,
                                    autoflush = False))
Base = declarative_base()
Base.query = session.query_property()

class Quake(Base):
    __tablename__ = "quakes"

    id = Column(String(30), primary_key = True)
    timestamp = Column(postgresql.BIGINT)
    updated = Column(postgresql.BIGINT)
    magnitude = Column(Float)
    tsunami = Column(postgresql.BIGINT, nullable = True)
    latitude = Column(String(10))
    longitude = Column(String(10))

class QuakeUpdate(Base):
    __tablename__ = "quake_update"

    update_time = Column(String(30), primary_key = True)

def main():
    pass

if __name__ == "__main__":
    main()
