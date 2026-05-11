from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.schemas.clinical import ClinicalDocumentCreate, ClinicalDocumentResponse, ClinicalDocumentSign, ClinicalDocumentUpdate
from backend.schemas.fhir_models import FhirDocumentReference
from backend.security.auth import get_current_user
from backend.services.clinical_service import ClinicalService

router = APIRouter(prefix="/clinical", tags=["Clinical Documentation"])


def document_to_fhir(document) -> FhirDocumentReference:
    return FhirDocumentReference(
        id=str(document.id),
        status="final" if document.is_signed else "current",
        type={"coding": [{"code": document.document_type}]},
        subject={"reference": f"Patient/{document.patient_id}"},
        date=document.created_at.isoformat(),
        author=[{"reference": f"Practitioner/{document.practitioner_id}"}] if document.practitioner_id else None,
        title=document.title,
        content=document.content,
        version=str(document.version),
    )


@router.post("/documents", response_model=ClinicalDocumentResponse)
def create_document(
    doc_data: ClinicalDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClinicalDocumentResponse:
    return ClinicalService.create_document(db, doc_data.model_dump(), current_user)


@router.get("/patient/{patient_id}/documents", response_model=list[ClinicalDocumentResponse])
def get_patient_documents(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClinicalDocumentResponse]:
    return ClinicalService.get_patient_documents(db, patient_id, current_user, skip, limit)


@router.get("/documents/{doc_id}", response_model=ClinicalDocumentResponse)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClinicalDocumentResponse:
    return ClinicalService.get_document(db, doc_id, current_user)


@router.put("/documents/{doc_id}", response_model=ClinicalDocumentResponse)
def update_document(
    doc_id: int,
    doc_data: ClinicalDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClinicalDocumentResponse:
    return ClinicalService.update_document(db, doc_id, doc_data.model_dump(exclude_unset=True), current_user)


@router.post("/documents/{doc_id}/sign", response_model=ClinicalDocumentResponse)
def sign_document(
    doc_id: int,
    payload: ClinicalDocumentSign | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClinicalDocumentResponse:
    return ClinicalService.sign_document(db, doc_id, current_user)


@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return ClinicalService.delete_document(db, doc_id, current_user)


@router.get("/documents/{doc_id}/fhir", response_model=FhirDocumentReference)
def get_document_fhir(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirDocumentReference:
    document = ClinicalService.get_document(db, doc_id, current_user)
    return document_to_fhir(document)
