from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

# Models
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    full_name: str
    role: str = "user"
    
    attendance_logs: List["AttendanceLog"] = Relationship(back_populates="user")
    reports: List["WorkReport"] = Relationship(back_populates="user")

class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    
    projects: List["Project"] = Relationship(back_populates="client")

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    client_id: Optional[int] = Field(default=None, foreign_key="client.id")
    
    client: Optional[Client] = Relationship(back_populates="projects")
    reports: List["WorkReport"] = Relationship(back_populates="project")

class AttendanceLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: str  # ENTRATA, USCITA
    origin: str = "Manuale"
    status: str = "Autorizzata"
    
    user: Optional[User] = Relationship(back_populates="attendance_logs")

class WorkReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    project_id: int = Field(foreign_key="project.id")
    date: datetime
    hours: float
    description: str
    
    user: Optional[User] = Relationship(back_populates="reports")
    project: Optional[Project] = Relationship(back_populates="reports")
