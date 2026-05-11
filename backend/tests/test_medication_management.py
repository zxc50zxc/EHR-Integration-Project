from fastapi.testclient import TestClient

from backend.database.models import MedicationRequest, UserRole


def medication_payload(patient_id: int) -> dict:
    return {
        "patient_id": patient_id,
        "medication_name": "Metformin",
        "dosage": "500 mg",
        "frequency": "Twice daily",
        "route": "oral",
        "start_date": "2026-01-01",
        "status": "active",
        "intent": "order",
        "notes": "Take with meals.",
    }


def test_create_medication_request_returns_fhir_resource(client: TestClient, auth_headers, create_patient, db_session) -> None:
    patient = create_patient()
    headers = auth_headers(role=UserRole.physician)

    response = client.post("/fhir/MedicationRequest", json=medication_payload(patient.id), headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["resourceType"] == "MedicationRequest"
    assert body["subject"]["reference"] == f"Patient/{patient.id}"
    assert body["medicationCodeableConcept"]["text"] == "Metformin"
    assert db_session.query(MedicationRequest).count() == 1


def test_patient_medication_history_filters_by_patient(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-MED-2")
    other_patient = create_patient(mrn="MRN-MED-3")
    headers = auth_headers(role=UserRole.physician)
    client.post("/fhir/MedicationRequest", json=medication_payload(patient.id), headers=headers)
    client.post("/fhir/MedicationRequest", json={**medication_payload(other_patient.id), "medication_name": "Aspirin"}, headers=headers)

    response = client.get(f"/fhir/Patient/{patient.id}/MedicationRequest", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["medicationCodeableConcept"]["text"] == "Metformin"


def test_nurse_cannot_create_medication_request(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-MED-4")
    headers = auth_headers(role=UserRole.nurse)

    response = client.post("/fhir/MedicationRequest", json=medication_payload(patient.id), headers=headers)

    assert response.status_code == 403
