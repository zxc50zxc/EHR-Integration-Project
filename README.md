# EHR Integration System - Phase 1

## Overview

This is Phase 1 of the EHR Integration System, focused on:

- Authentication and authorization with JWT.
- Role-based access control.
- Patient self-registration that automatically creates and links a patient chart.
- Patient data management.
- Basic FHIR Patient R4-style resources.
- Clinical documentation with FHIR DocumentReference resources.
- Medication management with FHIR MedicationRequest resources.
- Lab results with FHIR Observation and DiagnosticReport resources.
- Practical service APIs for `/clinical`, `/medications`, and `/lab` workflows.
- Application-level SSN encryption.
- Audit logging.
- Seed data for a runnable demo.

## Setup

### Prerequisites

- Python 3.10+
- SQLite for immediate local demo, or PostgreSQL via `DATABASE_URL`

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional environment file:

```bash
cp .env.example .env
```

Generate a Fernet key for `ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Run the application:

```bash
python -m backend.main
```

Or:

```bash
uvicorn backend.main:app --reload
```

Swagger docs:

```text
http://localhost:8000/docs
```

## Frontend

The React frontend is in `frontend/` and connects to the backend at `http://localhost:8000`.

Install and run:

```bash
cd frontend
npm install
npm start
```

Production build:

```bash
cd frontend
npm run build
```

If your shell has custom npm environment variables that force npm outside the project directory, run:

```bash
env -u npm_config_devdir -u npm_config_prefix npm --prefix frontend start
```

Frontend features:

- React 18 + TypeScript.
- Tailwind CSS RTL Arabic UI.
- Axios API client with bearer token interceptor.
- React Router protected routes.
- Context API authentication state.
- Patient, Provider, and Admin portals.
- Clinical notes, medications, lab orders/results, and FHIR views.

## API Endpoints

Authentication:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh-token`
- `POST /auth/logout`

Admin:

- `GET /admin/users`
- `GET /admin/reports/{report_type}`

File Uploads:

- `POST /files/upload`

FHIR Patient:

- `GET /fhir/Patient`
- `GET /fhir/Patient/{id}`
- `POST /fhir/Patient`
- `PUT /fhir/Patient/{id}`
- `DELETE /fhir/Patient/{id}`

Clinical Documentation:

- `GET /fhir/DocumentReference`
- `GET /fhir/DocumentReference/{id}`
- `GET /fhir/DocumentReference/{id}/versions`
- `POST /fhir/DocumentReference`
- `PUT /fhir/DocumentReference/{id}`
- `DELETE /fhir/DocumentReference/{id}`

Medication Management:

- `GET /fhir/MedicationRequest`
- `GET /fhir/MedicationRequest/{id}`
- `GET /fhir/Patient/{id}/MedicationRequest`
- `POST /fhir/MedicationRequest`
- `PUT /fhir/MedicationRequest/{id}`
- `DELETE /fhir/MedicationRequest/{id}`

Lab Results:

- `GET /fhir/Observation`
- `GET /fhir/Observation/{id}`
- `GET /fhir/Patient/{id}/Observation`
- `POST /fhir/Observation`
- `PUT /fhir/Observation/{id}`
- `DELETE /fhir/Observation/{id}`
- `GET /fhir/DiagnosticReport`
- `GET /fhir/DiagnosticReport/{id}`
- `POST /fhir/DiagnosticReport`
- `PUT /fhir/DiagnosticReport/{id}`
- `DELETE /fhir/DiagnosticReport/{id}`

Clinical Documentation Service:

- `POST /clinical/documents`
- `GET /clinical/documents/{id}`
- `GET /clinical/patient/{patient_id}/documents`
- `PUT /clinical/documents/{id}`
- `POST /clinical/documents/{id}/sign`
- `DELETE /clinical/documents/{id}`
- `GET /clinical/documents/{id}/fhir`

Medication Management Service:

- `POST /medications/prescribe`
- `GET /medications/{id}`
- `GET /medications/patient/{patient_id}/medications`
- `PUT /medications/{id}`
- `POST /medications/{id}/stop`
- `GET /medications/{id}/fhir`

Lab Results Service:

- `POST /lab/tests/order`
- `GET /lab/tests/queue`
- `GET /lab/tests/{id}`
- `PUT /lab/tests/{id}`
- `GET /lab/patient/{patient_id}/tests`
- `POST /lab/tests/{id}/accept`
- `POST /lab/tests/{id}/assign`
- `POST /lab/tests/{id}/collect`
- `POST /lab/tests/{id}/receive`
- `POST /lab/tests/{id}/results`
- `POST /lab/tests/{id}/verify`
- `POST /lab/tests/{id}/release`
- `GET /lab/tests/{id}/results`
- `GET /lab/tests/{id}/full`

Lab order workflow:

1. Physician creates the order with `POST /lab/tests/order`.
2. The lab technician receives the queue through `GET /lab/tests/queue`.
3. The lab technician accepts the order, collects the sample, then receives it in the lab.
4. The lab technician enters structured result values and the test is marked `completed`.
5. A physician verifies the result and releases it.
6. Patients can see detailed result values only after the test reaches `released`.

## Seed Data

On startup, the app seeds:

- 6 users: `admin1`, `doctor1`, `nurse1`, `staff1`, `labtech1`, `patient1`
- 100 demo patients
- clinical documents for the first demo patients
- active medication requests for demo medication history
- diagnostic reports with linked lab observations
- 50 additional clinical documents for `/clinical`
- 200 medication prescriptions for `/medications`
- 100 lab tests with 500 lab results for `/lab`

Default password for all seeded users:

```text
password123
```

## Testing

```bash
pytest backend/tests/ -v
```

The test suite uses isolated in-memory SQLite and skips startup seed data.

## Phase 1 Limitations

This is a solid backend foundation, not a full legal compliance certification.

Implemented:

- Bcrypt password hashing.
- JWT access and refresh tokens.
- RBAC structure.
- Application-level SSN encryption.
- Audit logging basics.
- FHIR Patient-style JSON responses.
- FHIR DocumentReference, MedicationRequest, Observation, and DiagnosticReport JSON responses.
- Document versioning through immutable replacement versions.

Still required for production:

- TLS termination and hardened deployment.
- Managed secrets through Vault, AWS Secrets Manager, or cloud KMS.
- Database-level encryption/TDE.
- Full FHIR profile validation and conformance resources.
- Formal HIPAA/GDPR legal and operational review.

## Next Phases

- Clinical documentation service.
- Medication and lab result services.
- HL7 integration.
- Docker and Docker Compose.
- React frontend.
- Advanced HIPAA/GDPR controls.
