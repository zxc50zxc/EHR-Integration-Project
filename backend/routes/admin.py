import csv
from datetime import UTC, datetime
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import AuditLog, ClinicalDocument, LabResult, LabTest, Medication, Patient, User, UserRole
from backend.schemas.user import UserResponse
from backend.security.auth import require_roles

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
) -> list[User]:
    return db.query(User).order_by(User.id.asc()).all()


@router.get("/reports/{report_type}")
def download_report(
    report_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
) -> Response:
    reports = {
        "compliance": _compliance_report,
        "usage": _usage_report,
        "patients": _patients_report,
        "lab": _lab_report,
    }
    if report_type not in reports:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    csv_content = reports[report_type](db)
    filename = f"{report_type}-report-{datetime.now(UTC).date().isoformat()}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _write_csv(headers: list[str], rows: list[list[object]]) -> str:
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue()


def _compliance_report(db: Session) -> str:
    rows = [
        ["Generated At", datetime.now(UTC).isoformat()],
        ["Active Users", db.query(User).filter(User.is_active.is_(True)).count()],
        ["Active Patients", db.query(Patient).filter(Patient.is_active.is_(True)).count()],
        ["Audit Events", db.query(AuditLog).count()],
        ["Signed Clinical Documents", db.query(ClinicalDocument).filter(ClinicalDocument.is_signed.is_(True)).count()],
        ["Released Lab Tests", db.query(LabTest).filter(LabTest.status == "released").count()],
    ]
    return _write_csv(["Metric", "Value"], rows)


def _usage_report(db: Session) -> str:
    rows = [
        ["users", db.query(User).count()],
        ["patients", db.query(Patient).count()],
        ["clinical_documents", db.query(ClinicalDocument).count()],
        ["medications", db.query(Medication).count()],
        ["lab_tests", db.query(LabTest).count()],
        ["lab_results", db.query(LabResult).count()],
        ["audit_events", db.query(AuditLog).count()],
    ]
    return _write_csv(["Resource", "Count"], rows)


def _patients_report(db: Session) -> str:
    patients = db.query(Patient).order_by(Patient.id.asc()).limit(1000).all()
    rows = [
        [patient.id, patient.mrn, patient.first_name, patient.last_name, patient.gender, patient.date_of_birth, patient.email]
        for patient in patients
    ]
    return _write_csv(["ID", "MRN", "First Name", "Last Name", "Gender", "Date Of Birth", "Email"], rows)


def _lab_report(db: Session) -> str:
    tests = db.query(LabTest).order_by(LabTest.created_at.desc()).limit(1000).all()
    rows = [
        [
            test.id,
            test.patient_id,
            test.practitioner_id,
            test.assigned_to,
            test.test_name,
            test.test_code,
            test.status,
            test.order_date,
            test.result_date,
        ]
        for test in tests
    ]
    return _write_csv(
        ["ID", "Patient ID", "Practitioner ID", "Assigned To", "Test Name", "Test Code", "Status", "Order Date", "Result Date"],
        rows,
    )
