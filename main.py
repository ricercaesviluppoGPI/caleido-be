import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
from contextlib import asynccontextmanager
from database import create_db_and_tables, get_session
from models import *
from pydantic import BaseModel

# Pydantic Schemas for Requests
class LoginRequest(BaseModel):
    email: str
    password: str

class ReportCreate(BaseModel):
    project_id: int
    date: datetime
    hours: float
    description: str

class AttendanceResponse(BaseModel):
    success: bool
    record: Optional[AttendanceLog] = None
    message: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

client_name = os.getenv("CLIENT_NAME", "")

app = FastAPI(
    title="Caleido API", 
    version="1.0.0",
    lifespan=lifespan, 
    servers=[{"url": f"/{client_name}/caleido-backend"}],
    root_path=f"/{client_name}/caleido-backend" if client_name else "",
    openapi_version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Caleido API is running"}

# --- Auth ---
@app.post("/auth/login")
def login(creds: LoginRequest, session: Session = Depends(get_session)):
    # Real DB check with fallback to demo user if seeded
    user = session.exec(select(User).where(User.email == creds.email)).first()
    if user and user.password_hash == creds.password:
        return {"token": str(user.id), "user_name": user.full_name, "user_id": user.id}
    
    raise HTTPException(status_code=401, detail="Credenziali non valide")

from datetime import datetime, timezone

# ... (imports)

# --- Attendance ---
@app.get("/attendance/today", response_model=List[AttendanceLog])
def get_today_attendance(user_id: int = 1, session: Session = Depends(get_session)):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return session.exec(select(AttendanceLog).where(
        AttendanceLog.user_id == user_id, 
        AttendanceLog.timestamp >= today_start
    ).order_by(AttendanceLog.timestamp)).all()

@app.post("/attendance/clock-in", response_model=AttendanceResponse)
def clock_in(user_id: int = 1, session: Session = Depends(get_session)):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = session.exec(select(AttendanceLog).where(
        AttendanceLog.user_id == user_id, 
        AttendanceLog.timestamp >= today_start
    )).all()
    
    if len(today_logs) >= 4:
         raise HTTPException(status_code=400, detail="Limite giornaliero raggiunto")

    # Check if already clocked in (last record is ENTRATA)
    last_record = session.exec(select(AttendanceLog).where(AttendanceLog.user_id == user_id).order_by(AttendanceLog.timestamp.desc())).first()
    
    if last_record and last_record.type == "ENTRATA":
        raise HTTPException(status_code=400, detail="Utente già in servizio")
        
    new_record = AttendanceLog(user_id=user_id, type="ENTRATA", origin="Manuale", status="Autorizzata", timestamp=datetime.now(timezone.utc))
    session.add(new_record)
    session.commit()
    session.refresh(new_record)
    return {"success": True, "record": new_record, "message": "Entrata registrata"}

@app.post("/attendance/clock-out", response_model=AttendanceResponse)
def clock_out(user_id: int = 1, session: Session = Depends(get_session)):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = session.exec(select(AttendanceLog).where(
        AttendanceLog.user_id == user_id, 
        AttendanceLog.timestamp >= today_start
    )).all()
    
    if len(today_logs) >= 4:
         raise HTTPException(status_code=400, detail="Limite giornaliero raggiunto")

    # Check if clocked in checking last record
    last_record = session.exec(select(AttendanceLog).where(AttendanceLog.user_id == user_id).order_by(AttendanceLog.timestamp.desc())).first()
    
    if not last_record or last_record.type == "USCITA":
        raise HTTPException(status_code=400, detail="Utente non in servizio")
        
    new_record = AttendanceLog(user_id=user_id, type="USCITA", origin="Manuale", status="Autorizzata", timestamp=datetime.now(timezone.utc))
    session.add(new_record)
    session.commit()
    session.refresh(new_record)
    return {"success": True, "record": new_record, "message": "Uscita registrata"}

# --- Reports ---
@app.get("/reports", response_model=List[WorkReport])
def get_reports(user_id: int = 1, session: Session = Depends(get_session)):
    return session.exec(select(WorkReport).where(WorkReport.user_id == user_id).order_by(WorkReport.date.desc())).all()

@app.post("/reports", response_model=WorkReport)
def create_report(report: ReportCreate, user_id: int = 1, session: Session = Depends(get_session)):
    new_report = WorkReport(user_id=user_id, **report.dict())
    session.add(new_report)
    session.commit()
    session.refresh(new_report)
    return new_report

@app.delete("/reports/{report_id}")
def delete_report(report_id: int, user_id: int = 1, session: Session = Depends(get_session)):
    report = session.get(WorkReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report non trovato")
    if report.user_id != user_id:
         raise HTTPException(status_code=403, detail="Non autorizzato")
         
    session.delete(report)
    session.commit()
    return {"ok": True}

# --- Metadata ---
@app.get("/clients", response_model=List[Client])
def get_clients(session: Session = Depends(get_session)):
    return session.exec(select(Client)).all()

@app.get("/projects", response_model=List[Project])
def get_projects(session: Session = Depends(get_session)):
    return session.exec(select(Project)).all()
