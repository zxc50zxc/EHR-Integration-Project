from datetime import UTC, datetime

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.database.models import DiagnosticReport, LabObservation, LabResult, LabTest, Patient, User, UserRole
from backend.schemas.fhir_models import (
    FhirCodeableConcept,
    FhirCoding,
    FhirDiagnosticReport,
    FhirObservation,
    FhirObservationValue,
    FhirReference,
)
from backend.security.audit import log_audit


class LabService:
    @staticmethod
    def order_test(db: Session, test_data: dict, current_user: User) -> LabTest:
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only physicians can order tests")
        LabService._ensure_patient(db, test_data["patient_id"])

        test = LabTest(**test_data, practitioner_id=current_user.id, status="ordered")
        db.add(test)
        db.commit()
        db.refresh(test)

        log_audit(current_user.id, "order_lab_test", "LabTest", test.id, db=db)
        db.commit()
        return test

    @staticmethod
    def get_lab_queue(db: Session, current_user: User, status_filter: str | None = None) -> list[LabTest]:
        if current_user.role not in [UserRole.admin, UserRole.physician, UserRole.nurse, UserRole.staff, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        query = db.query(LabTest)
        if status_filter:
            query = query.filter(LabTest.status == status_filter)
        return query.order_by(LabTest.created_at.desc()).all()

    @staticmethod
    def get_test(db: Session, test_id: int, current_user: User) -> LabTest:
        test = db.query(LabTest).filter(LabTest.id == test_id).first()
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab test not found")
        if current_user.role == UserRole.patient and current_user.patient_id != test.patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return test

    @staticmethod
    def get_patient_tests(
        db: Session,
        patient_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LabTest]:
        if current_user.role == UserRole.patient and current_user.patient_id != patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return db.query(LabTest).filter(LabTest.patient_id == patient_id).offset(skip).limit(limit).all()

    @staticmethod
    def update_test(db: Session, test_id: int, test_data: dict, current_user: User) -> LabTest:
        test = LabService.get_test(db, test_id, current_user)
        if current_user.role not in [UserRole.admin, UserRole.physician, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        for key, value in test_data.items():
            if value is not None:
                setattr(test, key, value)
        db.commit()
        db.refresh(test)
        log_audit(current_user.id, "update_lab_test", "LabTest", test.id, db=db)
        db.commit()
        return test

    @staticmethod
    def assign_test(db: Session, test_id: int, assigned_to: int, current_user: User) -> LabTest:
        if current_user.role not in [UserRole.admin, UserRole.nurse, UserRole.staff, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        assignee = db.query(User).filter(User.id == assigned_to, User.is_active.is_(True)).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
        if assignee.role not in [UserRole.admin, UserRole.nurse, UserRole.staff, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lab tests can only be assigned to lab users")
        test = LabService.get_test(db, test_id, current_user)
        LabService._ensure_test_status(test, ["ordered", "accepted"], "Only ordered tests can be accepted")
        test.assigned_to = assigned_to
        test.status = "accepted"
        db.commit()
        db.refresh(test)
        log_audit(current_user.id, "accept_lab_test", "LabTest", test.id, details=f"assigned_to={assigned_to}", db=db)
        db.commit()
        return test

    @staticmethod
    def accept_test(db: Session, test_id: int, current_user: User) -> LabTest:
        return LabService.assign_test(db, test_id, current_user.id, current_user)

    @staticmethod
    def collect_sample(db: Session, test_id: int, current_user: User) -> LabTest:
        if current_user.role not in [UserRole.admin, UserRole.nurse, UserRole.staff, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        test = LabService.get_test(db, test_id, current_user)
        LabService._ensure_test_status(test, ["accepted"], "Sample can only be collected after the test is accepted")
        test.collected_by = current_user.id
        test.sample_collected_at = datetime.now(UTC)
        test.status = "collected"
        db.commit()
        db.refresh(test)
        log_audit(current_user.id, "collect_lab_sample", "LabTest", test.id, db=db)
        db.commit()
        return test

    @staticmethod
    def receive_sample(db: Session, test_id: int, current_user: User) -> LabTest:
        if current_user.role not in [UserRole.admin, UserRole.nurse, UserRole.staff, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        test = LabService.get_test(db, test_id, current_user)
        LabService._ensure_test_status(test, ["collected"], "Sample can only be received after collection")
        test.received_by = current_user.id
        test.received_at = datetime.now(UTC)
        test.status = "received"
        db.commit()
        db.refresh(test)
        log_audit(current_user.id, "receive_lab_sample", "LabTest", test.id, db=db)
        db.commit()
        return test

    @staticmethod
    def add_result(db: Session, test_id: int, result_data: dict, current_user: User) -> LabResult:
        test = db.query(LabTest).filter(LabTest.id == test_id).first()
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab test not found")
        if current_user.role not in [UserRole.admin, UserRole.nurse, UserRole.staff, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        LabService._ensure_test_status(test, ["received", "completed"], "Results can only be entered after lab receipt")

        result = LabResult(lab_test_id=test_id, **result_data)
        db.add(result)
        test.resulted_by = current_user.id
        test.status = "completed"
        test.result_date = datetime.now(UTC).date().isoformat()

        db.commit()
        db.refresh(result)
        log_audit(current_user.id, "add_lab_result", "LabResult", result.id, db=db)
        db.commit()
        return result

    @staticmethod
    def verify_test(db: Session, test_id: int, current_user: User) -> LabTest:
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only physicians can verify results")
        test = LabService.get_test(db, test_id, current_user)
        LabService._ensure_test_status(test, ["completed"], "Only completed tests can be verified")
        if not LabService.get_test_results(db, test_id, current_user):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot verify a test without results")
        test.verified_by = current_user.id
        test.verified_at = datetime.now(UTC)
        test.status = "verified"
        db.commit()
        db.refresh(test)
        log_audit(current_user.id, "verify_lab_test", "LabTest", test.id, db=db)
        db.commit()
        return test

    @staticmethod
    def release_test(db: Session, test_id: int, current_user: User) -> LabTest:
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only physicians can release results")
        test = LabService.get_test(db, test_id, current_user)
        if test.status != "verified":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only verified results can be released")
        test.released_at = datetime.now(UTC)
        test.status = "released"
        db.commit()
        db.refresh(test)
        log_audit(current_user.id, "release_lab_test", "LabTest", test.id, db=db)
        db.commit()
        return test

    @staticmethod
    def get_test_results(db: Session, test_id: int, current_user: User) -> list[LabResult]:
        test = LabService.get_test(db, test_id, current_user)
        if current_user.role == UserRole.patient and current_user.patient_id != test.patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        if current_user.role == UserRole.patient and test.status != "released":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Results are not released to patient yet")
        return db.query(LabResult).filter(LabResult.lab_test_id == test_id).all()

    @staticmethod
    def create_diagnostic_report(
        db: Session,
        report_data: dict,
        current_user: User,
        request: Request | None = None,
    ) -> DiagnosticReport:
        LabService._require_write_role(current_user)
        LabService._ensure_patient(db, report_data["patient_id"])

        report = DiagnosticReport(**report_data)
        db.add(report)
        db.commit()
        db.refresh(report)

        log_audit(
            current_user.id,
            "create_diagnostic_report",
            "DiagnosticReport",
            report.id,
            ip_address=LabService._client_ip(request),
            db=db,
        )
        db.commit()
        return report

    @staticmethod
    def list_diagnostic_reports(db: Session, current_user: User, patient_id: int | None = None) -> list[DiagnosticReport]:
        LabService._require_read_role(current_user)
        query = db.query(DiagnosticReport).filter(DiagnosticReport.is_active.is_(True))
        if patient_id is not None:
            query = query.filter(DiagnosticReport.patient_id == patient_id)
        return query.order_by(DiagnosticReport.issued_at.desc()).all()

    @staticmethod
    def get_diagnostic_report(
        db: Session,
        report_id: int,
        current_user: User,
        request: Request | None = None,
    ) -> DiagnosticReport:
        LabService._require_read_role(current_user)
        report = db.query(DiagnosticReport).filter(DiagnosticReport.id == report_id, DiagnosticReport.is_active.is_(True)).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic report not found")

        log_audit(
            current_user.id,
            "read_diagnostic_report",
            "DiagnosticReport",
            report.id,
            ip_address=LabService._client_ip(request),
            db=db,
        )
        db.commit()
        return report

    @staticmethod
    def update_diagnostic_report(
        db: Session,
        report_id: int,
        report_data: dict,
        current_user: User,
        request: Request | None = None,
    ) -> DiagnosticReport:
        LabService._require_write_role(current_user)
        report = db.query(DiagnosticReport).filter(DiagnosticReport.id == report_id, DiagnosticReport.is_active.is_(True)).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic report not found")

        for key, value in report_data.items():
            if value is not None:
                setattr(report, key, value)
        db.commit()
        db.refresh(report)

        log_audit(
            current_user.id,
            "update_diagnostic_report",
            "DiagnosticReport",
            report.id,
            details=f"Fields: {sorted(report_data.keys())}",
            ip_address=LabService._client_ip(request),
            db=db,
        )
        db.commit()
        return report

    @staticmethod
    def delete_diagnostic_report(db: Session, report_id: int, current_user: User, request: Request | None = None) -> dict[str, str]:
        LabService._require_write_role(current_user)
        report = db.query(DiagnosticReport).filter(DiagnosticReport.id == report_id, DiagnosticReport.is_active.is_(True)).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic report not found")

        report.is_active = False
        log_audit(
            current_user.id,
            "delete_diagnostic_report",
            "DiagnosticReport",
            report.id,
            ip_address=LabService._client_ip(request),
            db=db,
        )
        db.commit()
        return {"message": "Diagnostic report deleted successfully"}

    @staticmethod
    def create_observation(
        db: Session,
        observation_data: dict,
        current_user: User,
        request: Request | None = None,
    ) -> LabObservation:
        LabService._require_write_role(current_user)
        LabService._ensure_patient(db, observation_data["patient_id"])
        if observation_data.get("diagnostic_report_id"):
            LabService._ensure_report(db, observation_data["diagnostic_report_id"], observation_data["patient_id"])

        observation = LabObservation(**observation_data)
        db.add(observation)
        db.commit()
        db.refresh(observation)

        log_audit(
            current_user.id,
            "create_observation",
            "Observation",
            observation.id,
            ip_address=LabService._client_ip(request),
            db=db,
        )
        db.commit()
        return observation

    @staticmethod
    def list_observations(
        db: Session,
        current_user: User,
        patient_id: int | None = None,
        diagnostic_report_id: int | None = None,
    ) -> list[LabObservation]:
        LabService._require_read_role(current_user)
        query = db.query(LabObservation).filter(LabObservation.is_active.is_(True))
        if patient_id is not None:
            query = query.filter(LabObservation.patient_id == patient_id)
        if diagnostic_report_id is not None:
            query = query.filter(LabObservation.diagnostic_report_id == diagnostic_report_id)
        return query.order_by(LabObservation.issued_at.desc()).all()

    @staticmethod
    def get_observation(db: Session, observation_id: int, current_user: User, request: Request | None = None) -> LabObservation:
        LabService._require_read_role(current_user)
        observation = db.query(LabObservation).filter(LabObservation.id == observation_id, LabObservation.is_active.is_(True)).first()
        if not observation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")

        log_audit(
            current_user.id,
            "read_observation",
            "Observation",
            observation.id,
            ip_address=LabService._client_ip(request),
            db=db,
        )
        db.commit()
        return observation

    @staticmethod
    def update_observation(
        db: Session,
        observation_id: int,
        observation_data: dict,
        current_user: User,
        request: Request | None = None,
    ) -> LabObservation:
        LabService._require_write_role(current_user)
        observation = db.query(LabObservation).filter(LabObservation.id == observation_id, LabObservation.is_active.is_(True)).first()
        if not observation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")

        if observation_data.get("diagnostic_report_id"):
            LabService._ensure_report(db, observation_data["diagnostic_report_id"], observation.patient_id)

        for key, value in observation_data.items():
            if value is not None:
                setattr(observation, key, value)
        db.commit()
        db.refresh(observation)

        log_audit(
            current_user.id,
            "update_observation",
            "Observation",
            observation.id,
            details=f"Fields: {sorted(observation_data.keys())}",
            ip_address=LabService._client_ip(request),
            db=db,
        )
        db.commit()
        return observation

    @staticmethod
    def delete_observation(db: Session, observation_id: int, current_user: User, request: Request | None = None) -> dict[str, str]:
        LabService._require_write_role(current_user)
        observation = db.query(LabObservation).filter(LabObservation.id == observation_id, LabObservation.is_active.is_(True)).first()
        if not observation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")

        observation.is_active = False
        log_audit(
            current_user.id,
            "delete_observation",
            "Observation",
            observation.id,
            ip_address=LabService._client_ip(request),
            db=db,
        )
        db.commit()
        return {"message": "Observation deleted successfully"}

    @staticmethod
    def to_fhir_observation(observation: LabObservation) -> FhirObservation:
        reference_range = [{"text": observation.reference_range}] if observation.reference_range else None
        return FhirObservation(
            id=str(observation.id),
            status=observation.status,
            code=FhirCodeableConcept(
                coding=[FhirCoding(system="http://loinc.org", code=observation.test_code, display=observation.test_name)],
                text=observation.test_name,
            ),
            subject=FhirReference(reference=f"Patient/{observation.patient_id}"),
            effectiveDateTime=observation.effective_date,
            issued=observation.issued_at.isoformat(),
            valueString=observation.value,
            valueQuantity=FhirObservationValue(value=observation.value, unit=observation.unit),
            referenceRange=reference_range,
        )

    @staticmethod
    def to_fhir_diagnostic_report(report: DiagnosticReport, observations: list[LabObservation]) -> FhirDiagnosticReport:
        return FhirDiagnosticReport(
            id=str(report.id),
            status=report.status,
            code=FhirCodeableConcept(
                coding=[FhirCoding(system="http://loinc.org", code=report.report_code, display=report.report_name)],
                text=report.report_name,
            ),
            subject=FhirReference(reference=f"Patient/{report.patient_id}"),
            issued=report.issued_at.isoformat(),
            result=[FhirReference(reference=f"Observation/{observation.id}") for observation in observations],
            conclusion=report.conclusion,
        )

    @staticmethod
    def _ensure_patient(db: Session, patient_id: int) -> None:
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_active.is_(True)).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    @staticmethod
    def _ensure_report(db: Session, report_id: int, patient_id: int) -> None:
        report = (
            db.query(DiagnosticReport)
            .filter(DiagnosticReport.id == report_id, DiagnosticReport.patient_id == patient_id, DiagnosticReport.is_active.is_(True))
            .first()
        )
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic report not found")

    @staticmethod
    def _require_read_role(current_user: User) -> None:
        if current_user.role not in [UserRole.admin, UserRole.physician, UserRole.nurse, UserRole.staff, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access lab results")

    @staticmethod
    def _require_write_role(current_user: User) -> None:
        if current_user.role not in [UserRole.admin, UserRole.physician, UserRole.nurse, UserRole.staff, UserRole.lab_technician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify lab results")

    @staticmethod
    def _ensure_test_status(test: LabTest, allowed_statuses: list[str], detail: str) -> None:
        if test.status not in allowed_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    @staticmethod
    def _client_ip(request: Request | None) -> str | None:
        if request is None or request.client is None:
            return None
        return request.client.host
