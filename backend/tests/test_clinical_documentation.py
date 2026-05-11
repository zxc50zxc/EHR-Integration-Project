from fastapi.testclient import TestClient

from backend.database.models import AuditLog, ClinicalDocument, UserRole


def document_payload(patient_id: int) -> dict:
    return {
        "patient_id": patient_id,
        "document_type": "clinical-note",
        "title": "Progress Note",
        "content": "Patient is stable and denies acute symptoms.",
        "status": "current",
        "signed": True,
    }


def test_create_document_reference_returns_fhir_resource(client: TestClient, auth_headers, create_patient, db_session) -> None:
    patient = create_patient()
    headers = auth_headers(role=UserRole.physician)

    response = client.post("/fhir/DocumentReference", json=document_payload(patient.id), headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["resourceType"] == "DocumentReference"
    assert body["subject"]["reference"] == f"Patient/{patient.id}"
    assert body["version"] == "1"
    assert db_session.query(ClinicalDocument).count() == 1
    assert db_session.query(AuditLog).count() >= 2


def test_update_document_creates_new_version(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-DOC-2")
    headers = auth_headers(role=UserRole.physician)
    created = client.post("/fhir/DocumentReference", json=document_payload(patient.id), headers=headers)
    document_id = created.json()["id"]

    updated = client.put(
        f"/fhir/DocumentReference/{document_id}",
        json={"content": "Updated clinical note content.", "signed": True},
        headers=headers,
    )
    versions = client.get(f"/fhir/DocumentReference/{updated.json()['id']}/versions", headers=headers)

    assert updated.status_code == 200
    assert updated.json()["version"] == "2"
    assert versions.status_code == 200
    assert [version["version"] for version in versions.json()] == ["1", "2"]


def test_patient_role_cannot_create_document(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-DOC-3")
    headers = auth_headers(username="patient-doc", email="patient-doc@example.com", role=UserRole.patient)

    response = client.post("/fhir/DocumentReference", json=document_payload(patient.id), headers=headers)

    assert response.status_code == 403
