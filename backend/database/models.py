import enum
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


def utc_now() -> datetime:
    return datetime.now(UTC)


class UserRole(str, enum.Enum):
    admin = "admin"
    physician = "physician"
    nurse = "nurse"
    staff = "staff"
    lab_technician = "lab_technician"
    patient = "patient"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.patient, nullable=False)
    patient_id = Column(Integer, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    mrn = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(String(10), nullable=False)
    gender = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    encrypted_ssn = Column(String(500), nullable=True)
    insurance_id = Column(String(100), nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class ClinicalDocument(Base):
    __tablename__ = "clinical_documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    practitioner_id = Column(Integer, nullable=True)
    version_group_id = Column(Integer, nullable=True, index=True)
    version = Column(Integer, default=1, nullable=False)
    document_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(30), default="current", nullable=False)
    author_id = Column(Integer, nullable=False)
    is_signed = Column(Boolean, default=False, nullable=False)
    signed_by = Column(Integer, nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class MedicationRequest(Base):
    __tablename__ = "medication_requests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    practitioner_id = Column(Integer, nullable=False, index=True)
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    route = Column(String(100), nullable=True)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=True)
    status = Column(String(30), default="active", nullable=False)
    intent = Column(String(30), default="order", nullable=False)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    practitioner_id = Column(Integer, nullable=False)
    drug_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    route = Column(String(50), nullable=False)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=True)
    indication = Column(String(255), nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class DiagnosticReport(Base):
    __tablename__ = "diagnostic_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    report_code = Column(String(100), nullable=False)
    report_name = Column(String(255), nullable=False)
    status = Column(String(30), default="final", nullable=False)
    conclusion = Column(Text, nullable=True)
    issued_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class LabObservation(Base):
    __tablename__ = "lab_observations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    diagnostic_report_id = Column(Integer, nullable=True, index=True)
    test_code = Column(String(100), nullable=False)
    test_name = Column(String(255), nullable=False)
    value = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    status = Column(String(30), default="final", nullable=False)
    effective_date = Column(String(10), nullable=False)
    issued_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    practitioner_id = Column(Integer, nullable=False)
    assigned_to = Column(Integer, nullable=True, index=True)
    collected_by = Column(Integer, nullable=True)
    received_by = Column(Integer, nullable=True)
    resulted_by = Column(Integer, nullable=True)
    verified_by = Column(Integer, nullable=True)
    test_name = Column(String(255), nullable=False)
    test_code = Column(String(50), nullable=False)
    status = Column(String(20), default="ordered", nullable=False)
    order_date = Column(String(10), nullable=False)
    sample_collected_at = Column(DateTime(timezone=True), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    result_date = Column(String(10), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    lab_test_id = Column(Integer, nullable=False, index=True)
    result_name = Column(String(255), nullable=False)
    result_value = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=False)
    reference_range = Column(String(100), nullable=False)
    status = Column(String(20), default="normal", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
