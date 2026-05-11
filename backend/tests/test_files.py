from fastapi.testclient import TestClient

from backend.database.models import UserRole


def test_patient_can_upload_file_for_own_chart(client: TestClient, create_user) -> None:
    patient = create_user(username="upload-patient", email="upload-patient@example.com", role=UserRole.patient)
    token = client.post("/auth/login", json={"username": patient.username, "password": "Password123!"}).json()["access_token"]

    response = client.post(
        "/files/upload",
        data={"document_type": "patient-document", "description": "Home blood pressure record"},
        files={"file": ("bp.txt", b"120/80", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["patient_id"] == patient.patient_id
    assert response.json()["filename"] == "bp.txt"


def test_staff_upload_requires_patient_id(client: TestClient, auth_headers) -> None:
    headers = auth_headers(username="upload-nurse", email="upload-nurse@example.com", role=UserRole.nurse)

    response = client.post(
        "/files/upload",
        data={"document_type": "clinical-document"},
        files={"file": ("note.txt", b"note", "text/plain")},
        headers=headers,
    )

    assert response.status_code == 400
