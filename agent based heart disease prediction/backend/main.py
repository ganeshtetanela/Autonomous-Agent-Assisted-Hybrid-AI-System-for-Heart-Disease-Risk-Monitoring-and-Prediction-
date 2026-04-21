from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, health

# Initialize Database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agent-Based Heart Disease Prediction System",
    description="Backend API for the autonomous healthcare monitoring system.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "System Operational", "status": "online"}
