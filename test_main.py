from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from .main import app, get_session
from .models import User, AttendanceLog, Client, Project, WorkReport
import pytest

# Test DB
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

@pytest.fixture(name="session")
def session_fixture():
    print("Tables:", SQLModel.metadata.tables.keys())
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_clock_in_clock_out_flow(client):
    # 1. Login (Mock)
    login_response = client.post("/auth/login", json={"email": "giuseppe.sacco@caleido.it", "password": "Admin2026!"})
    assert login_response.status_code == 200
    token = login_response.json()["token"]

    # 2. Clock In
    response = client.post("/attendance/clock-in?user_id=1")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["record"]["type"] == "ENTRATA"

    # 3. Clock In Again (Should Fail)
    response = client.post("/attendance/clock-in?user_id=1")
    assert response.status_code == 400
    assert response.json()["detail"] == "User already in service"

    # 4. Clock Out
    response = client.post("/attendance/clock-out?user_id=1")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["record"]["type"] == "USCITA"
    
    # 5. Clock Out Again (Should Fail)
    response = client.post("/attendance/clock-out?user_id=1")
    assert response.status_code == 400
    assert response.json()["detail"] == "User not in service"
