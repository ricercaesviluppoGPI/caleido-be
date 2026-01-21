from sqlmodel import Session, select
from .database import engine, create_db_and_tables
from .models import User, Client, Project, AttendanceLog, WorkReport
from datetime import datetime, timedelta, timezone

def seed_data():
    create_db_and_tables()
    with Session(engine) as session:
        # Check if data exists
        if session.exec(select(User)).first():
            print("Data already seeded.")
            return

        print("Seeding data...")

        # User
        user = User(email="giuseppe.sacco@caleido.it", password_hash="Admin2026!", full_name="Sacco Giuseppe", role="admin")
        session.add(user)
        session.commit()
        session.refresh(user)

        # Clients
        c1 = Client(name="Ospedale San Raffaele")
        c2 = Client(name="Comune di Milano")
        c3 = Client(name="Ferrari S.p.A.")
        session.add_all([c1, c2, c3])
        session.commit()

        # Projects
        p1 = Project(name="Sviluppo Dashboard", client=c1)
        p2 = Project(name="Migrazione Cloud", client=c1)
        p3 = Project(name="Assistenza On-Site", client=c2)
        p4 = Project(name="Consulenza Sicurezza", client=c3)
        session.add_all([p1, p2, p3, p4])
        session.commit()
        
        # Attendance (Past 5 days logs)
        today = datetime.now(timezone.utc).date()
        for i in range(5):
            d = today - timedelta(days=i)
            # Entrada 8:00
            t_in = datetime.combine(d, datetime.min.time()).replace(tzinfo=timezone.utc) + timedelta(hours=8, minutes=30)
            log_in = AttendanceLog(user_id=user.id, timestamp=t_in, type="ENTRATA", origin="Automatica", status="Autorizzata")
            session.add(log_in)
            
            # Uscita 17:00
            t_out = datetime.combine(d, datetime.min.time()).replace(tzinfo=timezone.utc) + timedelta(hours=17, minutes=0)
            log_out = AttendanceLog(user_id=user.id, timestamp=t_out, type="USCITA", origin="Automatica", status="Autorizzata")
            session.add(log_out)
        
        session.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
