from datetime import UTC, datetime

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.database.models import ClinicalDocument, Patient, User, UserRole
from backend.schemas.fhir_models import (
    FhirCodeableConcept,
    FhirCoding,
    FhirDocumentReference,
    FhirDocumentReferenceContent,
    FhirReference,
)
from backend.security.audit import log_audit


class ClinicalDocumentService:
    @staticmethod
    def create_document(db: Session, document_data: dict, current_user: User, request: Request | None = None) -> ClinicalDocument:
        ClinicalDocumentService._require_write_role(current_user)
        ClinicalDocumentService._ensure_patient(db, document_data["patient_id"])

        signed = bool(document_data.pop("signed", False))
        document = ClinicalDocument(
            **document_data,
            author_id=current_user.id,
            practitioner_id=current_user.id,
            is_signed=signed,
            signed_by=current_user.id if signed else None,
            signed_at=datetime.now(UTC) if signed else None,
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        document.version_group_id = document.id
        db.commit()
        db.refresh(document)

        log_audit(
            current_user.id,
            "create_document",
            "DocumentReference",
            document.id,
            ip_address=ClinicalDocumentService._client_ip(request),
            db=db,
        )
        db.commit()
        return document

    @staticmethod
    def list_documents(db: Session, current_user: User, patient_id: int | None = None) -> list[ClinicalDocument]:
        ClinicalDocumentService._require_read_role(current_user)
        query = db.query(ClinicalDocument).filter(ClinicalDocument.is_active.is_(True))
        if patient_id is not None:
            query = query.filter(ClinicalDocument.patient_id == patient_id)
        return query.order_by(ClinicalDocument.updated_at.desc()).all()

    @staticmethod
    def get_document(db: Session, document_id: int, current_user: User, request: Request | None = None) -> ClinicalDocument:
        ClinicalDocumentService._require_read_role(current_user)
        document = db.query(ClinicalDocument).filter(ClinicalDocument.id == document_id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        log_audit(
            current_user.id,
            "read_document",
            "DocumentReference",
            document.id,
            ip_address=ClinicalDocumentService._client_ip(request),
            db=db,
        )
        db.commit()
        return document

    @staticmethod
    def get_document_versions(db: Session, document_id: int, current_user: User) -> list[ClinicalDocument]:
        document = ClinicalDocumentService.get_document(db, document_id, current_user)
        group_id = document.version_group_id or document.id
        return (
            db.query(ClinicalDocument)
            .filter(ClinicalDocument.version_group_id == group_id)
            .order_by(ClinicalDocument.version.asc())
            .all()
        )

    @staticmethod
    def update_document(
        db: Session,
        document_id: int,
        document_data: dict,
        current_user: User,
        request: Request | None = None,
    ) -> ClinicalDocument:
        ClinicalDocumentService._require_write_role(current_user)
        current = db.query(ClinicalDocument).filter(ClinicalDocument.id == document_id, ClinicalDocument.is_active.is_(True)).first()
        if not current:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active document not found")

        signed = document_data.pop("signed", None)
        current.is_active = False
        new_document = ClinicalDocument(
            patient_id=current.patient_id,
            version_group_id=current.version_group_id or current.id,
            version=current.version + 1,
            document_type=document_data.get("document_type", current.document_type),
            title=document_data.get("title", current.title),
            content=document_data.get("content", current.content),
            status=document_data.get("status", current.status),
            author_id=current.author_id,
            practitioner_id=current.practitioner_id or current.author_id,
            is_signed=True if signed is True else current.is_signed,
            signed_by=current_user.id if signed is True else current.signed_by,
            signed_at=datetime.now(UTC) if signed is True else current.signed_at,
        )
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        log_audit(
            current_user.id,
            "update_document",
            "DocumentReference",
            new_document.id,
            details=f"Previous version: {current.id}",
            ip_address=ClinicalDocumentService._client_ip(request),
            db=db,
        )
        db.commit()
        return new_document

    @staticmethod
    def delete_document(db: Session, document_id: int, current_user: User, request: Request | None = None) -> dict[str, str]:
        if current_user.role != UserRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete documents")
        document = db.query(ClinicalDocument).filter(ClinicalDocument.id == document_id, ClinicalDocument.is_active.is_(True)).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        document.is_active = False
        log_audit(
            current_user.id,
            "delete_document",
            "DocumentReference",
            document.id,
            ip_address=ClinicalDocumentService._client_ip(request),
            db=db,
        )
        db.commit()
        return {"message": "Document deleted successfully"}

    @staticmethod
    def to_fhir_document_reference(document: ClinicalDocument) -> FhirDocumentReference:
        return FhirDocumentReference(
            id=str(document.id),
            status="final" if document.is_signed else document.status,
            type=FhirCodeableConcept(
                coding=[FhirCoding(system="http://loinc.org", code=document.document_type, display=document.title)],
                text=document.title,
            ),
            subject=FhirReference(reference=f"Patient/{document.patient_id}"),
            author=[FhirReference(reference=f"Practitioner/{document.practitioner_id or document.author_id}")],
            date=document.updated_at.isoformat(),
            title=document.title,
            description=document.title,
            content=[FhirDocumentReferenceContent(attachment={"contentType": "text/plain", "data": document.content})],
            version=str(document.version),
        )

    @staticmethod
    def _ensure_patient(db: Session, patient_id: int) -> None:
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_active.is_(True)).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    @staticmethod
    def _require_read_role(current_user: User) -> None:
        if current_user.role not in [UserRole.admin, UserRole.physician, UserRole.nurse, UserRole.staff]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access documents")

    @staticmethod
    def _require_write_role(current_user: User) -> None:
        if current_user.role not in [UserRole.admin, UserRole.physician, UserRole.nurse]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify documents")

    @staticmethod
    def _client_ip(request: Request | None) -> str | None:
        if request is None or request.client is None:
            return None
        return request.client.host


class ClinicalService:
    @staticmethod
    def create_document(db: Session, doc_data: dict, current_user: User) -> ClinicalDocument:
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create documents")
        ClinicalDocumentService._ensure_patient(db, doc_data["patient_id"])

        document = ClinicalDocument(**doc_data, practitioner_id=current_user.id, author_id=current_user.id)
        db.add(document)
        db.commit()
        db.refresh(document)

        log_audit(current_user.id, "create_document", "ClinicalDocument", document.id, db=db)
        db.commit()
        return document

    @staticmethod
    def get_document(db: Session, doc_id: int, current_user: User) -> ClinicalDocument:
        document = db.query(ClinicalDocument).filter(ClinicalDocument.id == doc_id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if current_user.role == UserRole.patient and current_user.patient_id != document.patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        log_audit(current_user.id, "read_document", "ClinicalDocument", document.id, db=db)
        db.commit()
        return document

    @staticmethod
    def get_patient_documents(
        db: Session,
        patient_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ClinicalDocument]:
        if current_user.role == UserRole.patient and current_user.patient_id != patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return db.query(ClinicalDocument).filter(ClinicalDocument.patient_id == patient_id).offset(skip).limit(limit).all()

    @staticmethod
    def update_document(db: Session, doc_id: int, doc_data: dict, current_user: User) -> ClinicalDocument:
        document = db.query(ClinicalDocument).filter(ClinicalDocument.id == doc_id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if current_user.role not in [UserRole.admin, UserRole.physician]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        for key, value in doc_data.items():
            if value is not None:
                setattr(document, key, value)
        document.version += 1
        document.updated_at = datetime.now(UTC)

        db.commit()
        db.refresh(document)
        log_audit(current_user.id, "update_document", "ClinicalDocument", document.id, db=db)
        db.commit()
        return document

    @staticmethod
    def sign_document(db: Session, doc_id: int, current_user: User) -> ClinicalDocument:
        document = db.query(ClinicalDocument).filter(ClinicalDocument.id == doc_id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if current_user.role != UserRole.physician:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only physicians can sign")

        document.is_signed = True
        document.status = "final"
        document.signed_at = datetime.now(UTC)
        document.signed_by = current_user.id

        db.commit()
        db.refresh(document)
        log_audit(current_user.id, "sign_document", "ClinicalDocument", document.id, db=db)
        db.commit()
        return document

    @staticmethod
    def delete_document(db: Session, doc_id: int, current_user: User) -> dict[str, str]:
        document = db.query(ClinicalDocument).filter(ClinicalDocument.id == doc_id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if current_user.role != UserRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete")

        db.delete(document)
        db.commit()
        log_audit(current_user.id, "delete_document", "ClinicalDocument", doc_id, db=db)
        db.commit()
        return {"message": "Document deleted"}
