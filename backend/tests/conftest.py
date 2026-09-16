import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app.models import User, Institution, Skill, StudentProfile, Company, AcademicianProfile
from app.auth import get_password_hash, create_access_token

# Use an in-memory SQLite database for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Seed baseline institution and skills for testing
    if session.query(Institution).count() == 0:
        inst = Institution(
            name="Test Engineering Institute",
            code="TEI-001",
            contact_email="contact@tei.edu"
        )
        session.add(inst)
        session.flush()

    if session.query(Skill).count() == 0:
        s1 = Skill(name="Python", category="technical", industry_benchmark=80.0)
        s2 = Skill(name="Cloud Computing (AWS/GCP)", category="technical", industry_benchmark=70.0)
        s3 = Skill(name="SQL & Relational Databases", category="technical", industry_benchmark=75.0)
        session.add_all([s1, s2, s3])
        session.flush()

    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def create_test_user_helper(db, email, role, full_name):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        token = create_access_token({"sub": str(existing.id), "role": existing.role})
        return existing, token

    u = User(
        email=email,
        password_hash=get_password_hash("TestPass123!"),
        full_name=full_name,
        role=role,
        is_active=True
    )
    db.add(u)
    db.flush()

    if role == "student":
        db.add(StudentProfile(user_id=u.id, degree="B.Tech", branch="Computer Science"))
    elif role == "industry":
        db.add(Company(user_id=u.id, name=f"{full_name} Corp", industry_sector="IT"))
    elif role == "academician":
        inst = db.query(Institution).first()
        db.add(AcademicianProfile(user_id=u.id, institution_id=inst.id if inst else None, department="CSE", designation="Professor"))

    db.commit()
    db.refresh(u)

    token = create_access_token({"sub": str(u.id), "role": u.role})
    return u, token

@pytest.fixture
def student_auth(db):
    user, token = create_test_user_helper(db, "student_test@skillsetu.edu", "student", "Student Test")
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

@pytest.fixture
def industry_auth(db):
    user, token = create_test_user_helper(db, "industry_test@skillsetu.edu", "industry", "Industry Test")
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

@pytest.fixture
def academician_auth(db):
    user, token = create_test_user_helper(db, "academician_test@skillsetu.edu", "academician", "Academician Test")
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

@pytest.fixture
def admin_auth(db):
    user, token = create_test_user_helper(db, "admin_test@skillsetu.edu", "institution_admin", "Admin Test")
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}
