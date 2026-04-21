from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend import models, auth

def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if test user exists
    user = db.query(models.User).filter(models.User.username == "test_patient").first()
    if not user:
        print("Seeding test user...")
        hashed_pw = auth.get_password_hash("password123")
        user = models.User(
            username="test_patient",
            hashed_password=hashed_pw,
            role="patient",
            full_name="John Doe (Test Patient)"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Add Clinical Data for the user (Crucial for Prediction Pipeline)
        clinical = models.ClinicalData(
            user_id=user.id,
            age=52, sex=1, cp=2, trestbps=135, chol=240, 
            fbs=0, restecg=1, thalach=145, exang=0, 
            oldpeak=1.2, slope=1, ca=0, thal=2
        )
        db.add(clinical)
        db.commit()
        print("Seed complete. User: test_patient, Password: password123")
    else:
        print("Database already seeded.")
    db.close()

if __name__ == "__main__":
    seed_data()
