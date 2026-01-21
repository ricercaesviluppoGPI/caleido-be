from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import User, Client, Project

def seed_minimal():
    create_db_and_tables()
    with Session(engine) as session:
        # Check if data exists
        if session.exec(select(User)).first():
            print("Resetting data...")
            # For minimal seed, we just want to ensure clean state or just add user if missing
            # But simpler to just rely on fresh DB file.
            pass

        print("Seeding minimal data (User only)...")
        
        # User
        user = session.exec(select(User).where(User.email == "giuseppe.sacco@caleido.it")).first()
        if not user:
            user = User(email="giuseppe.sacco@caleido.it", password_hash="Admin2026!", full_name="Sacco Giuseppe", role="admin")
            session.add(user)
        
        # Clients & Projects (for Reports page validity)
        # Helper to get or create client
        def get_or_create_client(name):
            client = session.exec(select(Client).where(Client.name == name)).first()
            if not client:
                client = Client(name=name)
                session.add(client)
                session.flush() # flush to get ID
            return client

        c1 = get_or_create_client("Ospedale San Raffaele")
        c2 = get_or_create_client("Regione Puglia")
        c3 = get_or_create_client("Regione Toscana")
        
        # Helper to get or create project
        def get_or_create_project(name, client):
            project = session.exec(select(Project).where(Project.name == name)).first()
            if not project:
                project = Project(name=name, client=client)
                session.add(project)
            return project

        p1 = get_or_create_project("Sviluppo Dashboard", c1)
        p2 = get_or_create_project("Sviluppo Software", c2)
        p3 = get_or_create_project("AI Study", c3)
        p4 = get_or_create_project("Test Commessa", c1)
        
        session.commit()
        print("Minimal seeding complete.")

if __name__ == "__main__":
    seed_minimal()
