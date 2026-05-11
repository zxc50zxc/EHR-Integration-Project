from fastapi.testclient import TestClient

from backend.database.models import AuditLog, Patient, UserRole


def patient_payload(mrn: str = "MRN-001") -> dict:
    return {
        "mrn": mrn,
        "first_name": "Amina",
        "last_name": "Hassan",
        "date_of_birth": "1985-04-12",
        "gender": "F",
        "phone": "+15555550100",
        "email": "amina.hassan@example.com",
        "address": "100 Health Ave",
        "city": "Riyadh",
        "state": "Riyadh",
        "postal_code": "11564",
        "country": "SA",
        "insurance_id": "INS-100",
        "encrypted_ssn": "123-45-6789",
    }


def test_create_patient_returns_fhir_without_plaintext_ssn(
    client: TestClient,
    auth_headers,
    db_session,
) -> None:
    headers = auth_headers(role=UserRole.physician)

    response = client.post("/fhir/Patient", json=patient_payload(), headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["resourceType"] == "Patient"
    assert body["identifier"][0]["value"] == "MRN-001"
    assert "ssn" not in body

    patient = db_session.get(Patient, int(body["id"]))
    assert patient is not None
    assert patient.encrypted_ssn != "123-45-6789"
    assert db_session.query(AuditLog).count() >= 2


def test_update_patient_requires_clinical_role(client: TestClient, auth_headers) -> None:
    patient_headers = auth_headers(
        username="patient-user",
        email="patient@example.com",
        role=UserRole.patient,
    )

    response = client.post("/fhir/Patient", json=patient_payload(), headers=patient_headers)

    assert response.status_code == 403


def test_get_patient_records_read_audit(client: TestClient, auth_headers, db_session) -> None:
    headers = auth_headers(role=UserRole.admin)
    created = client.post("/fhir/Patient", json=patient_payload("MRN-002"), headers=headers)
    patient_id = created.json()["id"]

    response = client.get(f"/fhir/Patient/{patient_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == patient_id
    assert db_session.query(AuditLog).count() >= 3


def test_nurse_can_list_patients(client: TestClient, auth_headers, create_patient) -> None:
    create_patient(mrn="MRN-NURSE-LIST")
    headers = auth_headers(username="nurse-list", email="nurse-list@example.com", role=UserRole.nurse)

    response = client.get("/fhir/Patient?limit=1000", headers=headers)

    assert response.status_code == 200
    assert any(patient["identifier"][0]["value"] == "MRN-NURSE-LIST" for patient in response.json())
