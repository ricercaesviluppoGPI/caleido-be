from sqlmodel import SQLModel, create_engine, Session
from models import * # Import models to register them

# Using SQLite for ease of local demo, can be switched to Postgres
DATABASE_URL = "sqlite:///./caleido.db"
# DATABASE_URL = "postgresql://user:password@localhost/caleido"

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
