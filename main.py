from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr
from typing import Literal
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key kontrol
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

# FastAPI app
app = FastAPI(title="Aidata Transfer API", version="2.0")

# Database setup (SQLite)
DATABASE_URL = "sqlite:///./aidata.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    external_call_id = Column(String, unique=True, index=True)
    call_date = Column(DateTime)
    serial_number = Column(String)
    title = Column(String)
    subject = Column(String)
    description = Column(Text)
    address = Column(String)
    school_code = Column(String)
    school_name = Column(String)
    province = Column(String)
    district = Column(String)
    reporter_name = Column(String)
    phone = Column(String)
    email = Column(String)
    product_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schema
class TransferPayload(BaseModel):
    external_call_id: str
    call_date: datetime
    serial_number: str
    title: str
    subject: str
    description: str
    address: str
    school_code: str
    school_name: str
    province: str
    district: str
    reporter_name: str
    phone: str
    email: EmailStr
    product_type: Literal["MPC1", "3DP1"]

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Geçersiz API anahtarı.")

# API Endpoint
@app.post("/transfer")
def transfer_call(
    data: TransferPayload,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key)
):
    # Benzersiz ID kontrolü
    existing = db.query(Call).filter(Call.external_call_id == data.external_call_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="external_call_id daha önce kullanılmış.")

    call = Call(**data.dict())
    db.add(call)
    db.commit()
    db.refresh(call)
    return {
        "id": call.id,
        "message": "New fault record created successfully."
    }

