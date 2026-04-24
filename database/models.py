"""
Database models and connection management
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Listing(Base):
    __tablename__ = 'listings'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(50))
    brand = Column(String(50))
    model = Column(String(100))
    year = Column(Integer)
    trim = Column(String(100))
    price = Column(Integer)
    mileage = Column(Integer)
    exterior_color = Column(String(50))
    interior_color = Column(String(50))
    options = Column(Text)
    location_city = Column(String(100))
    location_state = Column(String(2))
    listing_url = Column(String(500))
    listing_date = Column(Date)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    price_per_mile = Column(Float)  # Add this column

def get_engine():
    """Get database engine"""
    db_path = os.getenv('DATABASE_URL', 'sqlite:///data/tesla_market.db')
    if db_path.startswith('sqlite:///'):
        db_dir = os.path.dirname(db_path.replace('sqlite:///', ''))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    return create_engine(db_path)

def init_db():
    """Initialize database tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()