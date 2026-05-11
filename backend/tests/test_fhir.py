from fastapi.testclient import TestClient

from backend.database.models import UserRole
from backend.tests.test_patient import patient_payload


def test_list_patients_returns_fhir_resources(client: TestClient, auth_headers) -> None:
    headers = auth_headers(role=UserRole.physician)
    client.post("/fhir/Patient", json=patient_payload("MRN-101"), headers=headers)
    client.post(
        "/fhir/Patient",
        json={**patient_payload("MRN-102"), "first_name": "Omar", "last_name": "Saleh"},
        headers=headers,
    )

    response = client.get("/fhir/Patient", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["resourceType"] == "Patient"
    assert body[0]["identifier"][0]["value"] == "MRN-101"


def test_delete_patient_soft_deletes_resource(client: TestClient, auth_headers) -> None:
    headers = auth_headers(role=UserRole.admin)
    created = client.post("/fhir/Patient", json=patient_payload("MRN-201"), headers=headers)
    patient_id = created.json()["id"]

    delete_response = client.delete(f"/fhir/Patient/{patient_id}", headers=headers)
    get_response = client.get(f"/fhir/Patient/{patient_id}", headers=headers)

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Patient deleted successfully"
    assert get_response.status_code == 404
