from fastapi.testclient import TestClient

from backend.database.models import DiagnosticReport, LabObservation, UserRole


def report_payload(patient_id: int) -> dict:
    return {
        "patient_id": patient_id,
        "report_code": "BMP",
        "report_name": "Basic Metabolic Panel",
        "status": "final",
        "conclusion": "Renal function within reference range.",
    }


def observation_payload(patient_id: int, report_id: int | None = None) -> dict:
    return {
        "patient_id": patient_id,
        "diagnostic_report_id": report_id,
        "test_code": "2951-2",
        "test_name": "Sodium",
        "value": "140",
        "unit": "mmol/L",
        "reference_range": "135-145 mmol/L",
        "status": "final",
        "effective_date": "2026-01-02",
    }


def test_create_diagnostic_report_and_observation(client: TestClient, auth_headers, create_patient, db_session) -> None:
    patient = create_patient()
    headers = auth_headers(role=UserRole.staff)
    report = client.post("/fhir/DiagnosticReport", json=report_payload(patient.id), headers=headers)
    report_id = int(report.json()["id"])

    observation = client.post("/fhir/Observation", json=observation_payload(patient.id, report_id), headers=headers)
    fetched_report = client.get(f"/fhir/DiagnosticReport/{report_id}", headers=headers)

    assert report.status_code == 200
    assert observation.status_code == 200
    assert observation.json()["resourceType"] == "Observation"
    assert fetched_report.json()["result"] == [{"reference": f"Observation/{observation.json()['id']}", "display": None}]
    assert db_session.query(DiagnosticReport).count() == 1
    assert db_session.query(LabObservation).count() == 1


def test_patient_observation_history_filters_by_patient(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-LAB-2")
    other_patient = create_patient(mrn="MRN-LAB-3")
    headers = auth_headers(role=UserRole.staff)
    client.post("/fhir/Observation", json=observation_payload(patient.id), headers=headers)
    client.post("/fhir/Observation", json={**observation_payload(other_patient.id), "value": "138"}, headers=headers)

    response = client.get(f"/fhir/Patient/{patient.id}/Observation", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["subject"]["reference"] == f"Patient/{patient.id}"


def test_patient_role_cannot_create_lab_result(client: TestClient, auth_headers, create_patient) -> None:
    patient = create_patient(mrn="MRN-LAB-4")
    headers = auth_headers(username="patient-lab", email="patient-lab@example.com", role=UserRole.patient)

    response = client.post("/fhir/Observation", json=observation_payload(patient.id), headers=headers)

    assert response.status_code == 403
