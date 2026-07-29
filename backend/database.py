import os
import json
from sqlalchemy import create_engine, Column, Integer, Float, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define database file path
DATABASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'predictions.db')}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Required for SQLite in multi-threaded environments like FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PredictionDBModel(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    probability = Column(Float, nullable=False)
    prediction = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    inputs = Column(Text, nullable=False)  # Store JSON representation of inputs

# Create all tables on import/startup
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
