import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from backend.config import settings
from backend.database.connection import SessionLocal, engine
from backend.database.models import (
    Base,
    ClinicalDocument,
    DiagnosticReport,
    LabObservation,
    LabResult,
    LabTest,
    Medication,
    MedicationRequest,
    Patient,
    User,
    UserRole,
    utc_now,
)
from backend.routes import admin, auth, clinical, fhir, files, lab, medication
from backend.security.auth import hash_password
from backend.security.encryption import encrypt_data


Base.metadata.create_all(bind=engine)


def ensure_runtime_schema() -> None:
    """Small schema upgrade for local demo databases until Alembic migrations are added."""
    datetime_type = "TIMESTAMP WITH TIME ZONE" if engine.dialect.name == "postgresql" else "DATETIME"
    inspector = inspect(engine)
    columns_by_table = {
        table: {column["name"] for column in inspector.get_columns(table)}
        for table in inspector.get_table_names()
    }
    additions = {
        "users": {
            "patient_id": "INTEGER",
        },
        "lab_tests": {
            "assigned_to": "INTEGER",
            "collected_by": "INTEGER",
            "received_by": "INTEGER",
            "resulted_by": "INTEGER",
            "verified_by": "INTEGER",
            "sample_collected_at": datetime_type,
            "received_at": datetime_type,
            "verified_at": datetime_type,
            "released_at": datetime_type,
        },
    }
    with engine.begin() as connection:
        for table, table_additions in additions.items():
            existing_columns = columns_by_table.get(table, set())
            for column_name, column_type in table_additions.items():
                if column_name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}"))


ensure_runtime_schema()


def backfill_user_patient_links(db) -> None:
    patient_user = db.query(User).filter(User.username == "patient1").first()
    first_patient = db.query(Patient).order_by(Patient.id.asc()).first()
    if patient_user and first_patient and not patient_user.patient_id:
        patient_user.patient_id = first_patient.id
        db.flush()

    for user in db.query(User).filter(User.role == UserRole.patient, User.patient_id.is_(None)).all():
        if user.username == "patient1" and first_patient:
            user.patient_id = first_patient.id
            continue
        names = user.full_name.split()
        patient = Patient(
            mrn=f"USR{user.id:06d}",
            first_name=names[0] if names else user.username,
            last_name=" ".join(names[1:]) if len(names) > 1 else "Patient",
            date_of_birth="1900-01-01",
            gender="unknown",
            email=user.email,
        )
        db.add(patient)
        db.flush()
        user.patient_id = patient.id
    db.commit()


def ensure_seed_user(db, username: str, email: str, full_name: str, role: UserRole) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        password_hash=hash_password("password123"),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_initial_data() -> None:
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            ensure_seed_user(db, "labtech1", "labtech@example.com", "Lab Technician", UserRole.lab_technician)
            backfill_user_patient_links(db)
            return

        users_data = [
            {"username": "admin1", "email": "admin@example.com", "full_name": "Admin User", "role": UserRole.admin},
            {"username": "doctor1", "email": "doctor@example.com", "full_name": "Dr. Ahmed", "role": UserRole.physician},
            {"username": "nurse1", "email": "nurse@example.com", "full_name": "Nurse Sarah", "role": UserRole.nurse},
            {"username": "staff1", "email": "staff@example.com", "full_name": "Staff Member", "role": UserRole.staff},
            {"username": "labtech1", "email": "labtech@example.com", "full_name": "Lab Technician", "role": UserRole.lab_technician},
            {"username": "patient1", "email": "patient@example.com", "full_name": "Patient John", "role": UserRole.patient},
        ]

        for user_data in users_data:
            db.add(
                User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    password_hash=hash_password("password123"),
                    role=user_data["role"],
                )
            )

        for index in range(100):
            db.add(
                Patient(
                    mrn=f"MRN{index + 1:05d}",
                    first_name=f"Patient{index + 1}",
                    last_name=f"Name{index + 1}",
                    date_of_birth=f"19{70 + index % 30}-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}",
                    gender="M" if index % 2 == 0 else "F",
                    phone=f"555-{1000 + index}",
                    email=f"patient{index + 1}@example.com",
                    city="Riyadh",
                    country="Saudi Arabia",
                    encrypted_ssn=encrypt_data(f"123-45-{6789 + index}") if index % 2 == 0 else None,
                )
            )

        db.commit()

        patient_user = db.query(User).filter(User.username == "patient1").first()
        first_patient = db.query(Patient).order_by(Patient.id.asc()).first()
        if patient_user and first_patient:
            patient_user.patient_id = first_patient.id
            db.commit()

        doctor = db.query(User).filter(User.username == "doctor1").first()
        nurse = db.query(User).filter(User.username == "nurse1").first()
        lab_technician = db.query(User).filter(User.username == "labtech1").first()
        patients = db.query(Patient).order_by(Patient.id.asc()).limit(10).all()

        for index, patient in enumerate(patients):
            db.add(
                ClinicalDocument(
                    patient_id=patient.id,
                    document_type="clinical-note",
                    title=f"Initial Clinical Note {index + 1}",
                    content=f"Patient {patient.mrn} presents for routine EHR integration demo visit.",
                    status="current",
                    author_id=doctor.id,
                    practitioner_id=doctor.id,
                    is_signed=True,
                    signed_by=doctor.id,
                )
            )
            db.add(
                MedicationRequest(
                    patient_id=patient.id,
                    practitioner_id=doctor.id,
                    medication_name="Atorvastatin",
                    dosage="20 mg",
                    frequency="Once daily",
                    route="oral",
                    start_date="2026-01-01",
                    status="active",
                    notes="Seeded medication for demo history.",
                )
            )
            report = DiagnosticReport(
                patient_id=patient.id,
                report_code="CBC",
                report_name="Complete Blood Count",
                status="final",
                conclusion="No critical abnormalities detected.",
            )
            db.add(report)
            db.flush()
            db.add(
                LabObservation(
                    patient_id=patient.id,
                    diagnostic_report_id=report.id,
                    test_code="718-7",
                    test_name="Hemoglobin",
                    value=f"{13 + (index % 3)}.{index % 10}",
                    unit="g/dL",
                    reference_range="13.0-17.0 g/dL",
                    status="final",
                    effective_date="2026-01-02",
                )
            )

        if nurse:
            db.add(
                ClinicalDocument(
                    patient_id=patients[0].id,
                    document_type="nursing-note",
                    title="Nursing Intake",
                    content="Vitals reviewed and patient education completed.",
                    status="current",
                    author_id=nurse.id,
                    practitioner_id=nurse.id,
                )
            )

        all_patients = db.query(Patient).order_by(Patient.id.asc()).all()
        for index, patient in enumerate(all_patients[:50]):
            db.add(
                ClinicalDocument(
                    patient_id=patient.id,
                    practitioner_id=doctor.id,
                    document_type="Summary" if index % 3 == 0 else "Note",
                    title=f"Clinical Documentation Service Note {index + 1}",
                    content=f"Structured clinical document for patient {patient.mrn}.",
                    author_id=doctor.id,
                    is_signed=index % 2 == 0,
                    signed_by=doctor.id if index % 2 == 0 else None,
                    signed_at=utc_now() if index % 2 == 0 else None,
                )
            )

        medication_names = ["Metformin", "Lisinopril", "Amlodipine", "Omeprazole"]
        for index in range(200):
            patient = all_patients[index % len(all_patients)]
            db.add(
                Medication(
                    patient_id=patient.id,
                    practitioner_id=doctor.id,
                    drug_name=medication_names[index % len(medication_names)],
                    dosage=f"{250 + (index % 4) * 250}mg",
                    frequency="twice daily" if index % 2 else "once daily",
                    route="oral",
                    start_date="2026-01-01",
                    indication="Demo prescription tracking",
                    status="active" if index % 5 else "completed",
                )
            )

        lab_result_templates = [
            ("Hemoglobin", "14.1", "g/dL", "13.0-17.0 g/dL"),
            ("WBC", "6.4", "10^9/L", "4.0-11.0 10^9/L"),
            ("Platelets", "240", "10^9/L", "150-450 10^9/L"),
            ("Sodium", "140", "mmol/L", "135-145 mmol/L"),
            ("Potassium", "4.2", "mmol/L", "3.5-5.1 mmol/L"),
        ]
        for index, patient in enumerate(all_patients[:100]):
            test = LabTest(
                patient_id=patient.id,
                practitioner_id=doctor.id,
                assigned_to=lab_technician.id if lab_technician else None,
                collected_by=lab_technician.id if lab_technician else None,
                received_by=lab_technician.id if lab_technician else None,
                resulted_by=lab_technician.id if lab_technician else None,
                verified_by=doctor.id,
                test_name="Comprehensive Demo Panel",
                test_code=f"LAB{index + 1:04d}",
                status="released",
                order_date="2026-01-02",
                sample_collected_at=utc_now(),
                received_at=utc_now(),
                result_date="2026-01-03",
                verified_at=utc_now(),
                released_at=utc_now(),
            )
            db.add(test)
            db.flush()
            for name, value, unit, reference_range in lab_result_templates:
                db.add(
                    LabResult(
                        lab_test_id=test.id,
                        result_name=name,
                        result_value=value,
                        unit=unit,
                        reference_range=reference_range,
                        status="normal",
                    )
                )

        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if os.getenv("SKIP_SEED_DATA", "").lower() != "true":
        seed_initial_data()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="EHR Integration System",
        description="Phase 1: Authentication & Patient Management",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(files.router)
    app.include_router(fhir.router)
    app.include_router(clinical.router)
    app.include_router(medication.router)
    app.include_router(lab.router)

    @app.get("/", tags=["health"])
    def root() -> dict[str, str]:
        return {
            "message": "EHR Integration System - Phase 1",
            "docs": "/docs",
            "version": "1.0.0",
        }

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
