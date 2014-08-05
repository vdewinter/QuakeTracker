from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Float, BigInteger
from sqlalchemy.orm import sessionmaker, scoped_session
import os

engine = create_engine(os.environ.get("DATABASE_URL", "sqlite:///quakes.db"), echo=True)
session = scoped_session(sessionmaker(bind = engine,
                                    autocommit = False,
                                    autoflush = False))
Base = declarative_base()
Base.query = session.query_property()

class Quake(Base):
    __tablename__ = "quakes"

    id = Column(String(30), primary_key = True)
    timestamp = Column(BigInteger, nullable = False, index = True)
    updated = Column(BigInteger)
    magnitude = Column(Float, nullable = False, index = True)
    tsunami = Column(BigInteger, nullable = True)
    latitude = Column(String(30), nullable = False)
    longitude = Column(String(30), nullable = False)

class QuakeUpdate(Base):
    __tablename__ = "quake_update"

    update_time = Column(String(30), primary_key = True)

def main():
    pass

if __name__ == "__main__":
    main()
