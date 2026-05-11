from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.schemas.fhir_models import FhirMedicationRequest
from backend.schemas.medication import MedicationCreate, MedicationResponse, MedicationUpdate
from backend.security.auth import get_current_user
from backend.services.medication_service import MedicationService

router = APIRouter(prefix="/medications", tags=["Medications"])


@router.post("/prescribe", response_model=MedicationResponse)
def prescribe(
    med_data: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationResponse:
    return MedicationService.prescribe_medication(db, med_data.model_dump(), current_user)


@router.get("/patient/{patient_id}/medications", response_model=list[MedicationResponse])
def get_patient_medications(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MedicationResponse]:
    return MedicationService.get_patient_medications(db, patient_id, current_user, skip, limit)


@router.get("/{med_id}", response_model=MedicationResponse)
def get_medication(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationResponse:
    return MedicationService.get_medication(db, med_id, current_user)


@router.put("/{med_id}", response_model=MedicationResponse)
def update_medication(
    med_id: int,
    med_data: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationResponse:
    return MedicationService.update_medication(db, med_id, med_data.model_dump(exclude_unset=True), current_user)


@router.post("/{med_id}/stop", response_model=MedicationResponse)
def stop_medication(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MedicationResponse:
    return MedicationService.stop_medication(db, med_id, current_user)


@router.get("/{med_id}/fhir", response_model=FhirMedicationRequest)
def get_medication_fhir(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirMedicationRequest:
    medication = MedicationService.get_medication(db, med_id, current_user)
    return MedicationService.medication_to_fhir(medication)
