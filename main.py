from fastapi import FastAPI, HTTPException, Header, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Literal, Optional
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
CALLS_API_KEY = os.getenv("CALLS_API_KEY")

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
    status = Column(String, nullable=True)
    doc_id = Column(String, nullable=True)
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
# NOTE: Manual migration required for status and doc_id if DB already exists
Base.metadata.create_all(bind=engine)

# Pydantic Schema
class TransferPayload(BaseModel):
    external_call_id: str
    call_date: datetime
    serial_number: str
    title: str
    subject: str
    description: Optional[str] = None
    address: Optional[str] = None
    school_code: str
    school_name: str
    province: str
    district: str
    reporter_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    product_type: str

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

def verify_calls_key(x_api_key: str = Header(...)):
    if x_api_key != CALLS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key for calls endpoint")

# API Endpoint

@app.patch("/calls/{call_id}")
def update_call(
    call_id: int,
    status: Optional[str] = None,
    doc_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _: None = Depends(verify_calls_key)
):
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    if status is not None:
        call.status = status
    if doc_id is not None:
        call.doc_id = doc_id
    db.commit()
    db.refresh(call)
    return {
        "id": call.id,
        "status": call.status,
        "doc_id": call.doc_id,
        "message": "Call record updated successfully."
    }

@app.get("/calls")
def list_calls(
    db: Session = Depends(get_db),
    _: None = Depends(verify_calls_key)
):
    calls = db.query(Call).order_by(Call.id.desc()).all()
    return [
        {
            "id": c.id,
            "external_call_id": c.external_call_id,
            "call_date": c.call_date,
            "serial_number": c.serial_number,
            "title": c.title,
            "subject": c.subject,
            "description": c.description,
            "address": c.address,
            "school_code": c.school_code,
            "school_name": c.school_name,
            "province": c.province,
            "district": c.district,
            "reporter_name": c.reporter_name,
            "phone": c.phone,
            "email": c.email,
            "product_type": c.product_type,
            "created_at": c.created_at,
            "status": c.status,
            "doc_id": c.doc_id,
        }
        for c in calls
    ]

@app.post("/transfer")
def transfer_call(
    data: TransferPayload,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key)
):
    # Benzersiz ID kontrolü
    if db.query(Call).filter(Call.external_call_id == data.external_call_id).first():
        raise HTTPException(
            status_code=409,
            detail="This call ID is already registered. Please use a different call ID."
        )

    try:
        call = Call(**data.dict(), status="AKTARILDI")
        db.add(call)
        db.commit()
        db.refresh(call)
        return {
            "id": call.id,
            "message": "New fault record created successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create record: {str(e)}")
