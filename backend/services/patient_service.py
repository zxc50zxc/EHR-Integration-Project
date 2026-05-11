from fastapi import HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database.models import Patient, User, UserRole
from backend.schemas.fhir_models import FhirAddress, FhirContactPoint, FhirHumanName, FhirIdentifier, FhirPatient
from backend.security.audit import log_audit
from backend.security.encryption import encrypt_data


class PatientService:
    @staticmethod
    def create_patient(db: Session, patient_data: dict, current_user: User, request: Request | None = None) -> Patient:
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create patients")

        existing = db.query(Patient).filter(Patient.mrn == patient_data["mrn"]).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient with this MRN already exists")

        if patient_data.get("encrypted_ssn"):
            patient_data["encrypted_ssn"] = encrypt_data(patient_data["encrypted_ssn"])

        patient = Patient(**patient_data)
        db.add(patient)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient with this MRN already exists") from exc

        db.refresh(patient)
        log_audit(
            current_user.id,
            "create_patient",
            "Patient",
            patient.id,
            ip_address=PatientService._client_ip(request),
            db=db,
        )
        db.commit()
        return patient

    @staticmethod
    def get_patient(db: Session, patient_id: int, current_user: User, request: Request | None = None) -> Patient:
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_active.is_(True)).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        if current_user.role == UserRole.patient and current_user.patient_id != patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this patient")

        log_audit(
            current_user.id,
            "read_patient",
            "Patient",
            patient.id,
            ip_address=PatientService._client_ip(request),
            db=db,
        )
        db.commit()
        return patient

    @staticmethod
    def get_all_patients(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> list[Patient]:
        if current_user.role not in [UserRole.admin, UserRole.physician, UserRole.nurse, UserRole.staff]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to list patients")

        return db.query(Patient).filter(Patient.is_active.is_(True)).offset(skip).limit(limit).all()

    @staticmethod
    def update_patient(
        db: Session,
        patient_id: int,
        patient_data: dict,
        current_user: User,
        request: Request | None = None,
    ) -> Patient:
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_active.is_(True)).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update patients")

        if patient_data.get("encrypted_ssn"):
            patient_data["encrypted_ssn"] = encrypt_data(patient_data["encrypted_ssn"])

        for key, value in patient_data.items():
            if value is not None:
                setattr(patient, key, value)

        db.commit()
        db.refresh(patient)
        log_audit(
            current_user.id,
            "update_patient",
            "Patient",
            patient.id,
            details=f"Fields: {sorted(patient_data.keys())}",
            ip_address=PatientService._client_ip(request),
            db=db,
        )
        db.commit()
        return patient

    @staticmethod
    def delete_patient(db: Session, patient_id: int, current_user: User, request: Request | None = None) -> dict[str, str]:
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_active.is_(True)).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        if current_user.role != UserRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete patients")

        patient.is_active = False
        log_audit(
            current_user.id,
            "delete_patient",
            "Patient",
            patient_id,
            ip_address=PatientService._client_ip(request),
            db=db,
        )
        db.commit()
        return {"message": "Patient deleted successfully"}

    @staticmethod
    def to_fhir_patient(patient: Patient) -> FhirPatient:
        telecom: list[FhirContactPoint] = []
        if patient.phone:
            telecom.append(FhirContactPoint(system="phone", value=patient.phone))
        if patient.email:
            telecom.append(FhirContactPoint(system="email", value=patient.email))

        addresses: list[FhirAddress] | None = None
        if patient.city or patient.address:
            addresses = []
            addresses.append(
                FhirAddress(
                    line=[patient.address] if patient.address else [],
                    city=patient.city,
                    state=patient.state,
                    postalCode=patient.postal_code,
                    country=patient.country,
                )
            )

        return FhirPatient(
            id=str(patient.id),
            identifier=[FhirIdentifier(value=patient.mrn)],
            active=patient.is_active,
            name=[FhirHumanName(family=patient.last_name, given=[patient.first_name])],
            telecom=telecom or None,
            gender=patient.gender,
            birthDate=patient.date_of_birth,
            address=addresses,
        )

    @staticmethod
    def _client_ip(request: Request | None) -> str | None:
        if request is None or request.client is None:
            return None
        return request.client.host
