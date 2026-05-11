from fastapi.testclient import TestClient

from backend.database.models import ClinicalDocument, UserRole


def clinical_payload(patient_id: int) -> dict:
    return {
        "patient_id": patient_id,
        "document_type": "Note",
        "title": "Clinic Note",
        "content": "Patient reviewed in clinic and plan documented.",
    }


def test_clinical_document_crud_sign_and_fhir(client: TestClient, auth_headers, create_patient, db_session) -> None:
    patient = create_patient(mrn="MRN-CLINICAL-1")
    headers = auth_headers(role=UserRole.physician)

    created = client.post("/clinical/documents", json=clinical_payload(patient.id), headers=headers)
    doc_id = created.json()["id"]
    updated = client.put(f"/clinical/documents/{doc_id}", json={"title": "Updated Clinic Note"}, headers=headers)
    signed = client.post(f"/clinical/documents/{doc_id}/sign", headers=headers)
    fhir = client.get(f"/clinical/documents/{doc_id}/fhir", headers=headers)

    assert created.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["version"] == 2
    assert signed.status_code == 200
    assert signed.json()["is_signed"] is True
    assert fhir.status_code == 200
    assert fhir.json()["resourceType"] == "DocumentReference"
    assert db_session.query(ClinicalDocument).count() == 1


def test_only_physician_can_sign_clinical_document(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-CLINICAL-2")
    physician_headers = auth_headers(username="doc-sign", email="doc-sign@example.com", role=UserRole.physician)
    nurse_headers = auth_headers(username="nurse-sign", email="nurse-sign@example.com", role=UserRole.nurse)
    created = client.post("/clinical/documents", json=clinical_payload(patient.id), headers=physician_headers)

    response = client.post(f"/clinical/documents/{created.json()['id']}/sign", headers=nurse_headers)

    assert response.status_code == 403
