from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.schemas.lab import (
    LabResultData,
    LabResultResponse,
    LabTestAssign,
    LabTestCreate,
    LabTestResponse,
    LabTestUpdate,
    LabTestWithResults,
)
from backend.security.auth import get_current_user
from backend.services.lab_service import LabService

router = APIRouter(prefix="/lab", tags=["Lab Results"])


@router.post("/tests/order", response_model=LabTestResponse)
def order_test(
    test_data: LabTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.order_test(db, test_data.model_dump(), current_user)


@router.get("/tests/queue", response_model=list[LabTestResponse])
def get_lab_queue(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LabTestResponse]:
    return LabService.get_lab_queue(db, current_user, status)


@router.get("/patient/{patient_id}/tests", response_model=list[LabTestResponse])
def get_patient_tests(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LabTestResponse]:
    return LabService.get_patient_tests(db, patient_id, current_user, skip, limit)


@router.get("/tests/{test_id}", response_model=LabTestResponse)
def get_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.get_test(db, test_id, current_user)


@router.put("/tests/{test_id}", response_model=LabTestResponse)
def update_test(
    test_id: int,
    test_data: LabTestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.update_test(db, test_id, test_data.model_dump(exclude_unset=True), current_user)


@router.post("/tests/{test_id}/assign", response_model=LabTestResponse)
def assign_test(
    test_id: int,
    payload: LabTestAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.assign_test(db, test_id, payload.assigned_to, current_user)


@router.post("/tests/{test_id}/accept", response_model=LabTestResponse)
def accept_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.accept_test(db, test_id, current_user)


@router.post("/tests/{test_id}/collect", response_model=LabTestResponse)
def collect_sample(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.collect_sample(db, test_id, current_user)


@router.post("/tests/{test_id}/receive", response_model=LabTestResponse)
def receive_sample(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.receive_sample(db, test_id, current_user)


@router.post("/tests/{test_id}/results", response_model=LabResultResponse)
def add_result(
    test_id: int,
    result_data: LabResultData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabResultResponse:
    return LabService.add_result(db, test_id, result_data.model_dump(), current_user)


@router.post("/tests/{test_id}/verify", response_model=LabTestResponse)
def verify_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.verify_test(db, test_id, current_user)


@router.post("/tests/{test_id}/release", response_model=LabTestResponse)
def release_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LabTestResponse:
    return LabService.release_test(db, test_id, current_user)


@router.get("/tests/{test_id}/results", response_model=list[LabResultResponse])
def get_results(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LabResultResponse]:
    return LabService.get_test_results(db, test_id, current_user)


@router.get("/tests/{test_id}/full", response_model=LabTestWithResults)
def get_test_with_results(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    test = LabService.get_test(db, test_id, current_user)
    results = LabService.get_test_results(db, test_id, current_user)
    return {"test": test, "results": results}
