from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import datetime
from ..database import get_db
from .. import models, schemas, auth

# Import ML and Agent (Delayed imports to avoid circular issues or env errors)
from agent.monitor_agent import HeartMonitoringAgent
from ml.prediction_pipeline import HybridPredictionPipeline

router = APIRouter(
    prefix="/health",
    tags=["Healthcare Data"]
)

# Initialize Agent and Pipeline singleton-style for the router
agent = HeartMonitoringAgent()
try:
    pipeline = HybridPredictionPipeline()
except Exception as e:
    print(f"Warning: ML Pipeline failed to initialize: {e}")
    pipeline = None

@router.post("/upload-clinical-data", response_model=schemas.ClinicalDataBase)
def upload_clinical_data(
    data: schemas.ClinicalDataCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_clinical = models.ClinicalData(**data.dict(), user_id=current_user.id)
    db.add(new_clinical)
    db.commit()
    db.refresh(new_clinical)
    return new_clinical

@router.post("/stream-vitals")
def stream_vitals(
    data: schemas.VitalStreamCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # 1. Save vital to DB
    new_vital = models.VitalStream(**data.dict(), user_id=current_user.id)
    db.add(new_vital)
    db.commit()

    # 2. Autonomous Agent Analysis
    agent_decision = agent.analyze_vitals(data.dict())
    
    result = {"status": "received", "agent_decision": agent_decision}

    # 3. Trigger Prediction if Agent decides
    if agent_decision["trigger_prediction"] and pipeline:
        # Get latest clinical data
        clinical = db.query(models.ClinicalData).filter(models.ClinicalData.user_id == current_user.id).order_by(models.ClinicalData.created_at.desc()).first()
        
        # Get last 12 vital records for LSTM window
        vitals = db.query(models.VitalStream).filter(models.VitalStream.user_id == current_user.id).order_by(models.VitalStream.timestamp.desc()).limit(12).all()
        
        if clinical and len(vitals) >= 12:
            # Convert DB models to dicts for pipeline
            clinical_dict = {c.name: getattr(clinical, c.name) for c in clinical.__table__.columns if c.name not in ['id', 'user_id', 'created_at']}
            vitals_window = [
                {'heart_rate': v.heart_rate, 'bp_sys': v.blood_pressure_sys, 'bp_dia': v.blood_pressure_dia, 'ecg_signal': v.ecg_signal}
                for v in reversed(vitals)
            ]
            
            prediction_res = pipeline.predict(clinical_dict, vitals_window)
            
            # Save Prediction
            new_pred = models.Prediction(
                user_id=current_user.id,
                risk_score=prediction_res['risk_score'],
                risk_category=prediction_res['risk_category'],
                agent_triggered=True,
                agent_decision_reason=", ".join(agent_decision['reasons'])
            )
            db.add(new_pred)
            
            # Create Alert if High Risk
            if prediction_res['risk_category'] == "High":
                new_alert = models.Alert(
                    user_id=current_user.id,
                    message=f"High Heart Disease Risk Detected ({prediction_res['risk_score']*100:.1f}%)",
                    severity="Critical",
                    status="unread"
                )
                db.add(new_alert)
            
            db.commit()
            result["prediction"] = prediction_res
        else:
            result["prediction_status"] = "Waiting for more data (Clinical Data or 12 Vital records required)"

    return result

@router.get("/prediction-history", response_model=List[schemas.PredictionResponse])
def get_prediction_history(
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Prediction).filter(models.Prediction.user_id == current_user.id).order_by(models.Prediction.timestamp.desc()).limit(limit).all()

@router.get("/alerts", response_model=List[schemas.AlertResponse])
def get_alerts(
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Alert).filter(models.Alert.user_id == current_user.id, models.Alert.status == "unread").order_by(models.Alert.timestamp.desc()).limit(limit).all()
