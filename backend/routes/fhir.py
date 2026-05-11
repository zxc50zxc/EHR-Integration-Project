from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.schemas.document import ClinicalDocumentCreate, ClinicalDocumentUpdate
from backend.schemas.fhir_models import FhirDiagnosticReport, FhirDocumentReference, FhirMedicationRequest, FhirObservation, FhirPatient
from backend.schemas.lab import DiagnosticReportCreate, DiagnosticReportUpdate, LabObservationCreate, LabObservationUpdate
from backend.schemas.medication import MedicationRequestCreate, MedicationRequestUpdate
from backend.schemas.patient import PatientCreate, PatientUpdate
from backend.security.auth import get_current_user
from backend.services.clinical_service import ClinicalDocumentService
from backend.services.lab_service import LabService
from backend.services.medication_service import MedicationService
from backend.services.patient_service import PatientService

router = APIRouter(prefix="/fhir", tags=["FHIR"])


@router.get("/Patient", response_model=list[FhirPatient])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FhirPatient]:
    patients = PatientService.get_all_patients(db, current_user, skip, limit)
    return [PatientService.to_fhir_patient(patient) for patient in patients]


@router.get("/Patient/{patient_id}", response_model=FhirPatient)
def get_patient(
    patient_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirPatient:
    patient = PatientService.get_patient(db, patient_id, current_user, request)
    return PatientService.to_fhir_patient(patient)


@router.post("/Patient", response_model=FhirPatient)
def create_patient(
    patient_data: PatientCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirPatient:
    patient = PatientService.create_patient(
        db,
        patient_data.model_dump(),
        current_user,
        request,
    )
    return PatientService.to_fhir_patient(patient)


@router.put("/Patient/{patient_id}", response_model=FhirPatient)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirPatient:
    patient = PatientService.update_patient(
        db,
        patient_id,
        patient_data.model_dump(exclude_unset=True),
        current_user,
        request,
    )
    return PatientService.to_fhir_patient(patient)


@router.delete("/Patient/{patient_id}")
def delete_patient(
    patient_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return PatientService.delete_patient(db, patient_id, current_user, request)


@router.get("/DocumentReference", response_model=list[FhirDocumentReference])
def list_document_references(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    patient_id: int | None = None,
) -> list[FhirDocumentReference]:
    documents = ClinicalDocumentService.list_documents(db, current_user, patient_id)
    return [ClinicalDocumentService.to_fhir_document_reference(document) for document in documents]


@router.get("/DocumentReference/{document_id}", response_model=FhirDocumentReference)
def get_document_reference(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirDocumentReference:
    document = ClinicalDocumentService.get_document(db, document_id, current_user, request)
    return ClinicalDocumentService.to_fhir_document_reference(document)


@router.get("/DocumentReference/{document_id}/versions", response_model=list[FhirDocumentReference])
def get_document_versions(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FhirDocumentReference]:
    documents = ClinicalDocumentService.get_document_versions(db, document_id, current_user)
    return [ClinicalDocumentService.to_fhir_document_reference(document) for document in documents]


@router.post("/DocumentReference", response_model=FhirDocumentReference)
def create_document_reference(
    document_data: ClinicalDocumentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirDocumentReference:
    document = ClinicalDocumentService.create_document(db, document_data.model_dump(), current_user, request)
    return ClinicalDocumentService.to_fhir_document_reference(document)


@router.put("/DocumentReference/{document_id}", response_model=FhirDocumentReference)
def update_document_reference(
    document_id: int,
    document_data: ClinicalDocumentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirDocumentReference:
    document = ClinicalDocumentService.update_document(
        db,
        document_id,
        document_data.model_dump(exclude_unset=True),
        current_user,
        request,
    )
    return ClinicalDocumentService.to_fhir_document_reference(document)


@router.delete("/DocumentReference/{document_id}")
def delete_document_reference(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return ClinicalDocumentService.delete_document(db, document_id, current_user, request)


@router.get("/MedicationRequest", response_model=list[FhirMedicationRequest])
def list_medication_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    patient_id: int | None = None,
    status_filter: str | None = None,
) -> list[FhirMedicationRequest]:
    medications = MedicationService.list_medication_requests(db, current_user, patient_id, status_filter)
    return [MedicationService.to_fhir_medication_request(medication) for medication in medications]


@router.get("/Patient/{patient_id}/MedicationRequest", response_model=list[FhirMedicationRequest])
def get_patient_medication_history(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FhirMedicationRequest]:
    medications = MedicationService.list_medication_requests(db, current_user, patient_id)
    return [MedicationService.to_fhir_medication_request(medication) for medication in medications]


@router.get("/MedicationRequest/{medication_id}", response_model=FhirMedicationRequest)
def get_medication_request(
    medication_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirMedicationRequest:
    medication = MedicationService.get_medication_request(db, medication_id, current_user, request)
    return MedicationService.to_fhir_medication_request(medication)


@router.post("/MedicationRequest", response_model=FhirMedicationRequest)
def create_medication_request(
    medication_data: MedicationRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirMedicationRequest:
    medication = MedicationService.create_medication_request(db, medication_data.model_dump(), current_user, request)
    return MedicationService.to_fhir_medication_request(medication)


@router.put("/MedicationRequest/{medication_id}", response_model=FhirMedicationRequest)
def update_medication_request(
    medication_id: int,
    medication_data: MedicationRequestUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirMedicationRequest:
    medication = MedicationService.update_medication_request(
        db,
        medication_id,
        medication_data.model_dump(exclude_unset=True),
        current_user,
        request,
    )
    return MedicationService.to_fhir_medication_request(medication)


@router.delete("/MedicationRequest/{medication_id}")
def delete_medication_request(
    medication_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return MedicationService.delete_medication_request(db, medication_id, current_user, request)


@router.get("/Observation", response_model=list[FhirObservation])
def list_observations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    patient_id: int | None = None,
    diagnostic_report_id: int | None = None,
) -> list[FhirObservation]:
    observations = LabService.list_observations(db, current_user, patient_id, diagnostic_report_id)
    return [LabService.to_fhir_observation(observation) for observation in observations]


@router.get("/Patient/{patient_id}/Observation", response_model=list[FhirObservation])
def get_patient_observations(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FhirObservation]:
    observations = LabService.list_observations(db, current_user, patient_id)
    return [LabService.to_fhir_observation(observation) for observation in observations]


@router.get("/Observation/{observation_id}", response_model=FhirObservation)
def get_observation(
    observation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirObservation:
    observation = LabService.get_observation(db, observation_id, current_user, request)
    return LabService.to_fhir_observation(observation)


@router.post("/Observation", response_model=FhirObservation)
def create_observation(
    observation_data: LabObservationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirObservation:
    observation = LabService.create_observation(db, observation_data.model_dump(), current_user, request)
    return LabService.to_fhir_observation(observation)


@router.put("/Observation/{observation_id}", response_model=FhirObservation)
def update_observation(
    observation_id: int,
    observation_data: LabObservationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirObservation:
    observation = LabService.update_observation(
        db,
        observation_id,
        observation_data.model_dump(exclude_unset=True),
        current_user,
        request,
    )
    return LabService.to_fhir_observation(observation)


@router.delete("/Observation/{observation_id}")
def delete_observation(
    observation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return LabService.delete_observation(db, observation_id, current_user, request)


@router.get("/DiagnosticReport", response_model=list[FhirDiagnosticReport])
def list_diagnostic_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    patient_id: int | None = None,
) -> list[FhirDiagnosticReport]:
    reports = LabService.list_diagnostic_reports(db, current_user, patient_id)
    return [
        LabService.to_fhir_diagnostic_report(
            report,
            LabService.list_observations(db, current_user, diagnostic_report_id=report.id),
        )
        for report in reports
    ]


@router.get("/DiagnosticReport/{report_id}", response_model=FhirDiagnosticReport)
def get_diagnostic_report(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirDiagnosticReport:
    report = LabService.get_diagnostic_report(db, report_id, current_user, request)
    observations = LabService.list_observations(db, current_user, diagnostic_report_id=report.id)
    return LabService.to_fhir_diagnostic_report(report, observations)


@router.post("/DiagnosticReport", response_model=FhirDiagnosticReport)
def create_diagnostic_report(
    report_data: DiagnosticReportCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirDiagnosticReport:
    report = LabService.create_diagnostic_report(db, report_data.model_dump(), current_user, request)
    return LabService.to_fhir_diagnostic_report(report, [])


@router.put("/DiagnosticReport/{report_id}", response_model=FhirDiagnosticReport)
def update_diagnostic_report(
    report_id: int,
    report_data: DiagnosticReportUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FhirDiagnosticReport:
    report = LabService.update_diagnostic_report(
        db,
        report_id,
        report_data.model_dump(exclude_unset=True),
        current_user,
        request,
    )
    observations = LabService.list_observations(db, current_user, diagnostic_report_id=report.id)
    return LabService.to_fhir_diagnostic_report(report, observations)


@router.delete("/DiagnosticReport/{report_id}")
def delete_diagnostic_report(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return LabService.delete_diagnostic_report(db, report_id, current_user, request)
