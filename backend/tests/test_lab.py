from fastapi.testclient import TestClient

from backend.database.models import LabResult, LabTest, UserRole


def lab_test_payload(patient_id: int) -> dict:
    return {
        "patient_id": patient_id,
        "test_name": "Lipid Panel",
        "test_code": "LPID",
        "order_date": "2026-02-02",
    }


def lab_result_payload() -> dict:
    return {
        "result_name": "LDL Cholesterol",
        "result_value": "92",
        "unit": "mg/dL",
        "reference_range": "<100 mg/dL",
    }


def test_order_lab_test_add_result_and_fetch_full(client: TestClient, auth_headers, create_patient, db_session) -> None:
    patient = create_patient(mrn="MRN-LAB-SVC-1")
    physician_headers = auth_headers(role=UserRole.physician)
    lab_headers = auth_headers(username="lab-tech", email="lab-tech@example.com", role=UserRole.lab_technician)

    ordered = client.post("/lab/tests/order", json=lab_test_payload(patient.id), headers=physician_headers)
    test_id = ordered.json()["id"]
    client.post(f"/lab/tests/{test_id}/accept", headers=lab_headers)
    client.post(f"/lab/tests/{test_id}/collect", headers=lab_headers)
    client.post(f"/lab/tests/{test_id}/receive", headers=lab_headers)
    result = client.post(f"/lab/tests/{test_id}/results", json=lab_result_payload(), headers=lab_headers)
    full = client.get(f"/lab/tests/{test_id}/full", headers=physician_headers)

    assert ordered.status_code == 200
    assert result.status_code == 200
    assert result.json()["result_name"] == "LDL Cholesterol"
    assert full.status_code == 200
    assert full.json()["test"]["status"] == "completed"
    assert len(full.json()["results"]) == 1
    assert db_session.query(LabTest).count() == 1
    assert db_session.query(LabResult).count() == 1


def test_lab_order_full_workflow_and_patient_release(client: TestClient, create_user) -> None:
    physician = create_user(username="workflow-doc", email="workflow-doc@example.com", role=UserRole.physician)
    lab_technician = create_user(username="workflow-labtech", email="workflow-labtech@example.com", role=UserRole.lab_technician)
    patient_user = create_user(username="workflow-patient", email="workflow-patient@example.com", role=UserRole.patient)
    other_patient_user = create_user(username="other-patient", email="other-patient@example.com", role=UserRole.patient)

    physician_token = client.post("/auth/login", json={"username": physician.username, "password": "Password123!"}).json()["access_token"]
    lab_token = client.post("/auth/login", json={"username": lab_technician.username, "password": "Password123!"}).json()["access_token"]
    patient_token = client.post("/auth/login", json={"username": patient_user.username, "password": "Password123!"}).json()["access_token"]
    other_patient_token = client.post("/auth/login", json={"username": other_patient_user.username, "password": "Password123!"}).json()["access_token"]
    physician_headers = {"Authorization": f"Bearer {physician_token}"}
    lab_headers = {"Authorization": f"Bearer {lab_token}"}
    patient_headers = {"Authorization": f"Bearer {patient_token}"}
    other_patient_headers = {"Authorization": f"Bearer {other_patient_token}"}

    ordered = client.post("/lab/tests/order", json=lab_test_payload(patient_user.patient_id), headers=physician_headers)
    assert ordered.status_code == 200
    test_id = ordered.json()["id"]
    assert ordered.json()["status"] == "ordered"

    queue = client.get("/lab/tests/queue", headers=lab_headers)
    assert queue.status_code == 200
    assert any(test["id"] == test_id for test in queue.json())

    accepted = client.post(f"/lab/tests/{test_id}/accept", headers=lab_headers)
    collected = client.post(f"/lab/tests/{test_id}/collect", headers=lab_headers)
    received = client.post(f"/lab/tests/{test_id}/receive", headers=lab_headers)
    result = client.post(f"/lab/tests/{test_id}/results", json=lab_result_payload(), headers=lab_headers)
    lab_verify = client.post(f"/lab/tests/{test_id}/verify", headers=lab_headers)
    physician_result = client.post(f"/lab/tests/{test_id}/results", json=lab_result_payload(), headers=physician_headers)
    unreleased_patient_results = client.get(f"/lab/tests/{test_id}/results", headers=patient_headers)
    wrong_patient_results = client.get(f"/lab/tests/{test_id}/results", headers=other_patient_headers)
    verified = client.post(f"/lab/tests/{test_id}/verify", headers=physician_headers)
    released = client.post(f"/lab/tests/{test_id}/release", headers=physician_headers)
    released_patient_results = client.get(f"/lab/tests/{test_id}/results", headers=patient_headers)

    assert accepted.json()["status"] == "accepted"
    assert collected.json()["status"] == "collected"
    assert received.json()["status"] == "received"
    assert result.status_code == 200
    assert lab_verify.status_code == 403
    assert physician_result.status_code == 403
    assert unreleased_patient_results.status_code == 403
    assert wrong_patient_results.status_code == 403
    assert verified.json()["status"] == "verified"
    assert released.json()["status"] == "released"
    assert released_patient_results.status_code == 200
    assert len(released_patient_results.json()) == 1


def test_nurse_can_enter_lab_results(client: TestClient, create_user) -> None:
    physician = create_user(username="nurse-lab-doc", email="nurse-lab-doc@example.com", role=UserRole.physician)
    nurse = create_user(username="nurse-lab", email="nurse-lab@example.com", role=UserRole.nurse)
    patient_user = create_user(username="nurse-lab-patient", email="nurse-lab-patient@example.com", role=UserRole.patient)

    physician_token = client.post("/auth/login", json={"username": physician.username, "password": "Password123!"}).json()["access_token"]
    nurse_token = client.post("/auth/login", json={"username": nurse.username, "password": "Password123!"}).json()["access_token"]
    physician_headers = {"Authorization": f"Bearer {physician_token}"}
    nurse_headers = {"Authorization": f"Bearer {nurse_token}"}

    ordered = client.post("/lab/tests/order", json=lab_test_payload(patient_user.patient_id), headers=physician_headers)
    test_id = ordered.json()["id"]

    accepted = client.post(f"/lab/tests/{test_id}/accept", headers=nurse_headers)
    collected = client.post(f"/lab/tests/{test_id}/collect", headers=nurse_headers)
    received = client.post(f"/lab/tests/{test_id}/receive", headers=nurse_headers)
    result = client.post(f"/lab/tests/{test_id}/results", json=lab_result_payload(), headers=nurse_headers)

    assert accepted.status_code == 200
    assert collected.json()["status"] == "collected"
    assert received.json()["status"] == "received"
    assert result.status_code == 200


def test_nurse_cannot_order_lab_test(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-LAB-SVC-2")
    headers = auth_headers(role=UserRole.nurse)

    response = client.post("/lab/tests/order", json=lab_test_payload(patient.id), headers=headers)

    assert response.status_code == 403
