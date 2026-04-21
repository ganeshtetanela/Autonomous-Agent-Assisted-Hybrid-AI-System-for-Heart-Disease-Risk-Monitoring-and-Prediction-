from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # 'doctor' or 'patient'
    full_name = Column(String)

class ClinicalData(Base):
    __tablename__ = "clinical_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    age = Column(Integer)
    sex = Column(Integer)
    cp = Column(Integer)  # chest pain type
    trestbps = Column(Integer)  # resting blood pressure
    chol = Column(Integer)  # serum cholestoral
    fbs = Column(Integer)  # fasting blood sugar
    restecg = Column(Integer)
    thalach = Column(Integer)  # max heart rate
    exang = Column(Integer)
    oldpeak = Column(Float)
    slope = Column(Integer)
    ca = Column(Integer)
    thal = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class VitalStream(Base):
    __tablename__ = "vital_streams"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heart_rate = Column(Float)
    blood_pressure_sys = Column(Float)
    blood_pressure_dia = Column(Float)
    ecg_signal = Column(Float)
    activity_level = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    risk_score = Column(Float)
    risk_category = Column(String)  # Low, Medium, High
    agent_triggered = Column(Boolean, default=False)
    agent_decision_reason = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    severity = Column(String) # Warning, Critical
    status = Column(String) # unread, acknowledged
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
