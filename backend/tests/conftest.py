import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["SKIP_SEED_DATA"] = "true"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from backend.database.connection import get_db
from backend.database.models import Base, Patient, User, UserRole
from backend.main import app
from backend.security.auth import hash_password

engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(db_session: Session):
    def _create_user(
        *,
        username: str = "admin",
        email: str = "admin@example.com",
        password: str = "Password123!",
        role: UserRole = UserRole.admin,
    ) -> User:
        user = User(
            username=username,
            email=email,
            full_name=username.title(),
            password_hash=hash_password(password),
            role=role,
        )
        db_session.add(user)
        db_session.flush()
        if role == UserRole.patient:
            patient = Patient(
                mrn=f"USR{user.id:06d}",
                first_name=username.title(),
                last_name="Patient",
                date_of_birth="1990-01-01",
                gender="unknown",
                email=email,
            )
            db_session.add(patient)
            db_session.flush()
            user.patient_id = patient.id
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def auth_headers(client: TestClient, create_user):
    def _auth_headers(
        *,
        username: str = "admin",
        email: str = "admin@example.com",
        password: str = "Password123!",
        role: UserRole = UserRole.admin,
    ) -> dict[str, str]:
        create_user(username=username, email=email, password=password, role=role)
        response = client.post("/auth/login", json={"username": username, "password": password})
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture
def create_patient(db_session: Session):
    def _create_patient(*, mrn: str = "MRN-PHASE2") -> Patient:
        patient = Patient(
            mrn=mrn,
            first_name="Phase",
            last_name="Two",
            date_of_birth="1990-01-01",
            gender="F",
            phone="555-2000",
            email=f"{mrn.lower()}@example.com",
            city="Riyadh",
            country="SA",
        )
        db_session.add(patient)
        db_session.commit()
        db_session.refresh(patient)
        return patient

    return _create_patient
