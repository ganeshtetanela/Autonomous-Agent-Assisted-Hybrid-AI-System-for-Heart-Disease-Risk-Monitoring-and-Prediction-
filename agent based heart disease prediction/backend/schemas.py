from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class ClinicalDataBase(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

class ClinicalDataCreate(ClinicalDataBase):
    pass

class VitalStreamCreate(BaseModel):
    heart_rate: float
    blood_pressure_sys: float
    blood_pressure_dia: float
    ecg_signal: float
    activity_level: str

class PredictionResponse(BaseModel):
    risk_score: float
    risk_category: str
    agent_triggered: bool
    agent_decision_reason: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True

class AlertResponse(BaseModel):
    id: int
    message: str
    severity: str
    status: str
    timestamp: datetime

    class Config:
        orm_mode = True
