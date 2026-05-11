from fastapi.testclient import TestClient

from backend.database.models import AuditLog, Patient, UserRole


def test_register_user(client: TestClient, db_session) -> None:
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "full_name": "New User",
            "password": "password123",
            "role": "patient",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["patient_id"] is not None
    assert db_session.query(Patient).filter(Patient.email == "new@example.com").count() == 1
    assert db_session.query(AuditLog).count() == 1


def test_admin_can_list_registered_users(client: TestClient, auth_headers) -> None:
    admin_headers = auth_headers(username="admin-list", email="admin-list@example.com", role=UserRole.admin)
    client.post(
        "/auth/register",
        json={
            "username": "newpatient",
            "email": "newpatient@example.com",
            "full_name": "New Patient",
            "password": "password123",
            "role": "patient",
        },
    )

    response = client.get("/admin/users", headers=admin_headers)

    assert response.status_code == 200
    users = response.json()
    patient_user = next(user for user in users if user["username"] == "newpatient")
    assert patient_user["patient_id"] is not None


def test_admin_can_download_reports(client: TestClient, auth_headers) -> None:
    admin_headers = auth_headers(username="report-admin", email="report-admin@example.com", role=UserRole.admin)

    response = client.get("/admin/reports/compliance", headers=admin_headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "Metric,Value" in response.text


def test_login_returns_access_and_refresh_tokens(client: TestClient, create_user, db_session) -> None:
    create_user(username="physician", email="physician@example.com", role=UserRole.physician)

    response = client.post("/auth/login", json={"username": "physician", "password": "Password123!"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["role"] == "physician"
    assert db_session.query(AuditLog).count() == 1


def test_lab_technician_can_login_and_is_visible_to_admin(client: TestClient, auth_headers, create_user) -> None:
    create_user(username="labtech", email="labtech@example.com", role=UserRole.lab_technician)
    admin_headers = auth_headers(username="admin-labtech", email="admin-labtech@example.com", role=UserRole.admin)

    login_response = client.post("/auth/login", json={"username": "labtech", "password": "Password123!"})
    users_response = client.get("/admin/users", headers=admin_headers)

    assert login_response.status_code == 200
    assert login_response.json()["role"] == "lab_technician"
    assert any(user["username"] == "labtech" and user["role"] == "lab_technician" for user in users_response.json())


def test_login_rejects_invalid_credentials(client: TestClient, create_user) -> None:
    create_user(username="nurse", email="nurse@example.com", role=UserRole.nurse)

    response = client.post("/auth/login", json={"username": "nurse", "password": "wrong-password"})

    assert response.status_code == 401


def test_refresh_token_returns_new_access_token(client: TestClient, create_user) -> None:
    create_user(username="staff", email="staff@example.com", role=UserRole.staff)
    login_response = client.post("/auth/login", json={"username": "staff", "password": "Password123!"})
    refresh_token = login_response.json()["refresh_token"]

    response = client.post("/auth/refresh-token", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert response.json()["access_token"]
