from fastapi.testclient import TestClient

from backend.database.models import Medication, UserRole


def medication_payload(patient_id: int) -> dict:
    return {
        "patient_id": patient_id,
        "drug_name": "Amoxicillin",
        "dosage": "500mg",
        "frequency": "three times daily",
        "route": "oral",
        "start_date": "2026-02-01",
        "indication": "Demo infection treatment",
    }


def test_prescribe_stop_and_export_medication_fhir(client: TestClient, auth_headers, create_patient, db_session) -> None:
    patient = create_patient(mrn="MRN-MED-SVC-1")
    headers = auth_headers(role=UserRole.physician)

    created = client.post("/medications/prescribe", json=medication_payload(patient.id), headers=headers)
    med_id = created.json()["id"]
    stopped = client.post(f"/medications/{med_id}/stop", headers=headers)
    fhir = client.get(f"/medications/{med_id}/fhir", headers=headers)

    assert created.status_code == 200
    assert created.json()["drug_name"] == "Amoxicillin"
    assert stopped.status_code == 200
    assert stopped.json()["status"] == "stopped"
    assert fhir.status_code == 200
    assert fhir.json()["resourceType"] == "MedicationRequest"
    assert fhir.json()["dosageInstructions"][0]["route"]["text"] == "oral"
    assert db_session.query(Medication).count() == 1


def test_patient_medication_service_history(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-MED-SVC-2")
    headers = auth_headers(role=UserRole.physician)
    client.post("/medications/prescribe", json=medication_payload(patient.id), headers=headers)

    response = client.get(f"/medications/patient/{patient.id}/medications", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_nurse_cannot_prescribe_medication_service(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-MED-SVC-3")
    headers = auth_headers(role=UserRole.nurse)

    response = client.post("/medications/prescribe", json=medication_payload(patient.id), headers=headers)

    assert response.status_code == 403
