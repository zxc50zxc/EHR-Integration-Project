from datetime import UTC, datetime

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.database.models import Medication, MedicationRequest, Patient, User, UserRole
from backend.schemas.fhir_models import FhirCodeableConcept, FhirCoding, FhirMedicationRequest, FhirReference
from backend.security.audit import log_audit


class MedicationService:
    @staticmethod
    def prescribe_medication(db: Session, med_data: dict, current_user: User) -> Medication:
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only physicians can prescribe")
        MedicationService._ensure_patient(db, med_data["patient_id"])

        medication = Medication(**med_data, practitioner_id=current_user.id)
        db.add(medication)
        db.commit()
        db.refresh(medication)

        log_audit(current_user.id, "prescribe_medication", "Medication", medication.id, db=db)
        db.commit()
        return medication

    @staticmethod
    def get_medication(db: Session, med_id: int, current_user: User) -> Medication:
        medication = db.query(Medication).filter(Medication.id == med_id).first()
        if not medication:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
        if current_user.role == UserRole.patient and current_user.patient_id != medication.patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        log_audit(current_user.id, "read_medication", "Medication", medication.id, db=db)
        db.commit()
        return medication

    @staticmethod
    def get_patient_medications(
        db: Session,
        patient_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Medication]:
        if current_user.role == UserRole.patient and current_user.patient_id != patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return db.query(Medication).filter(Medication.patient_id == patient_id).offset(skip).limit(limit).all()

    @staticmethod
    def update_medication(db: Session, med_id: int, med_data: dict, current_user: User) -> Medication:
        medication = db.query(Medication).filter(Medication.id == med_id).first()
        if not medication:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        for key, value in med_data.items():
            if value is not None:
                setattr(medication, key, value)

        db.commit()
        db.refresh(medication)
        log_audit(current_user.id, "update_medication", "Medication", medication.id, db=db)
        db.commit()
        return medication

    @staticmethod
    def stop_medication(db: Session, med_id: int, current_user: User) -> Medication:
        medication = db.query(Medication).filter(Medication.id == med_id).first()
        if not medication:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        medication.status = "stopped"
        medication.end_date = datetime.now(UTC).date().isoformat()
        db.commit()
        db.refresh(medication)
        log_audit(current_user.id, "stop_medication", "Medication", medication.id, db=db)
        db.commit()
        return medication

    @staticmethod
    def medication_to_fhir(medication: Medication) -> FhirMedicationRequest:
        dosage = {"text": f"{medication.dosage} {medication.frequency}", "route": {"text": medication.route}}
        return FhirMedicationRequest(
            id=str(medication.id),
            status=medication.status,
            medicationCodeableConcept={"text": medication.drug_name},
            subject={"reference": f"Patient/{medication.patient_id}"},
            dosageInstruction=[dosage],
            dosageInstructions=[dosage],
        )

    @staticmethod
    def create_medication_request(
        db: Session,
        medication_data: dict,
        current_user: User,
        request: Request | None = None,
    ) -> MedicationRequest:
        MedicationService._require_write_role(current_user)
        MedicationService._ensure_patient(db, medication_data["patient_id"])

        medication = MedicationRequest(**medication_data, practitioner_id=current_user.id)
        db.add(medication)
        db.commit()
        db.refresh(medication)

        log_audit(
            current_user.id,
            "create_medication_request",
            "MedicationRequest",
            medication.id,
            ip_address=MedicationService._client_ip(request),
            db=db,
        )
        db.commit()
        return medication

    @staticmethod
    def list_medication_requests(
        db: Session,
        current_user: User,
        patient_id: int | None = None,
        status_filter: str | None = None,
    ) -> list[MedicationRequest]:
        MedicationService._require_read_role(current_user)
        query = db.query(MedicationRequest).filter(MedicationRequest.is_active.is_(True))
        if patient_id is not None:
            query = query.filter(MedicationRequest.patient_id == patient_id)
        if status_filter is not None:
            query = query.filter(MedicationRequest.status == status_filter)
        return query.order_by(MedicationRequest.created_at.desc()).all()

    @staticmethod
    def get_medication_request(
        db: Session,
        medication_id: int,
        current_user: User,
        request: Request | None = None,
    ) -> MedicationRequest:
        MedicationService._require_read_role(current_user)
        medication = db.query(MedicationRequest).filter(MedicationRequest.id == medication_id, MedicationRequest.is_active.is_(True)).first()
        if not medication:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication request not found")

        log_audit(
            current_user.id,
            "read_medication_request",
            "MedicationRequest",
            medication.id,
            ip_address=MedicationService._client_ip(request),
            db=db,
        )
        db.commit()
        return medication

    @staticmethod
    def update_medication_request(
        db: Session,
        medication_id: int,
        medication_data: dict,
        current_user: User,
        request: Request | None = None,
    ) -> MedicationRequest:
        MedicationService._require_write_role(current_user)
        medication = db.query(MedicationRequest).filter(MedicationRequest.id == medication_id, MedicationRequest.is_active.is_(True)).first()
        if not medication:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication request not found")

        for key, value in medication_data.items():
            if value is not None:
                setattr(medication, key, value)

        db.commit()
        db.refresh(medication)
        log_audit(
            current_user.id,
            "update_medication_request",
            "MedicationRequest",
            medication.id,
            details=f"Fields: {sorted(medication_data.keys())}",
            ip_address=MedicationService._client_ip(request),
            db=db,
        )
        db.commit()
        return medication

    @staticmethod
    def delete_medication_request(
        db: Session,
        medication_id: int,
        current_user: User,
        request: Request | None = None,
    ) -> dict[str, str]:
        MedicationService._require_write_role(current_user)
        medication = db.query(MedicationRequest).filter(MedicationRequest.id == medication_id, MedicationRequest.is_active.is_(True)).first()
        if not medication:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication request not found")

        medication.is_active = False
        medication.status = "stopped"
        log_audit(
            current_user.id,
            "delete_medication_request",
            "MedicationRequest",
            medication.id,
            ip_address=MedicationService._client_ip(request),
            db=db,
        )
        db.commit()
        return {"message": "Medication request deleted successfully"}

    @staticmethod
    def to_fhir_medication_request(medication: MedicationRequest) -> FhirMedicationRequest:
        dosage_text = f"{medication.dosage} {medication.frequency}"
        if medication.route:
            dosage_text = f"{dosage_text} via {medication.route}"

        return FhirMedicationRequest(
            id=str(medication.id),
            status=medication.status,
            intent=medication.intent,
            medicationCodeableConcept=FhirCodeableConcept(
                coding=[FhirCoding(code=medication.medication_name, display=medication.medication_name)],
                text=medication.medication_name,
            ),
            subject=FhirReference(reference=f"Patient/{medication.patient_id}"),
            requester=FhirReference(reference=f"Practitioner/{medication.practitioner_id}"),
            authoredOn=medication.created_at.date().isoformat(),
            dosageInstruction=[{"text": dosage_text}],
        )

    @staticmethod
    def _ensure_patient(db: Session, patient_id: int) -> None:
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_active.is_(True)).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    @staticmethod
    def _require_read_role(current_user: User) -> None:
        if current_user.role not in [UserRole.admin, UserRole.physician, UserRole.nurse, UserRole.staff]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access medications")

    @staticmethod
    def _require_write_role(current_user: User) -> None:
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify medications")

    @staticmethod
    def _client_ip(request: Request | None) -> str | None:
        if request is None or request.client is None:
            return None
        return request.client.host
