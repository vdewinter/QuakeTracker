from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session

ENGINE = None
Session = None
engine = create_engine("sqlite:///quakes.db", echo = False)
session = scoped_session(sessionmaker(bind = engine,
                                    autocommit = False,
                                    autoflush = False))
Base = declarative_base()
Base.query = session.query_property()

class Quake(Base):
    __tablename__ = "quakes"

    id = Column(Integer, primary_key = True) # this should become epoch timestamp
    tsunami = Column(String(5), nullable = True)
    year = Column(Integer)
    month = Column(Integer, nullable = True) #needs default
    day = Column(Integer, nullable = True) #needs default
    hour = Column(Integer, nullable = True) #needs default
    magnitude_mw = Column(String(5), nullable = True)
    magnitude_ms = Column(String(5), nullable = True)
    magnitude_mb = Column(String(5), nullable = True)
    magnitude_ml = Column(String(5), nullable = True)
    magnitude_mfa = Column(String(5), nullable = True)
    magnitude_unk = Column(String(5), nullable = True)
    latitude = Column(String(10))
    longitude = Column(String(10))

# class Tsunami(Base):
#     __tablename__ = "tsunamis"

#     id = Column(Integer, primary_key = True)
#     tseventid = Column(Integer)
#     year = Column(Integer)
#     month = Column(Integer, nullable = True) #needs default
#     day = Column(Integer, nullable = True) #needs default
#     doubtful = Column(String(1), nullable = True)
#     latitude = Column(String(10))
#     longitude = Column(String(10))
#     distance_from_source = Column(Integer, nullable = True)
#     travel_time_hours = Column(Integer, nullable = True)
#     travel_time_minutes = Column(Integer, nullable = True)
#     water_height = Column(String(10), nullable = True)
#     horizontal_innundation = Column(String(10), nullable = True)
#     period = Column(Integer, nullable = True)

def main():
    pass

if __name__ == "__main__":
    main()
