from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class PatientBase(BaseModel):
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    encrypted_ssn: str | None = None
    insurance_id: str | None = None
    emergency_contact: str | None = None
    emergency_contact_phone: str | None = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: str | None = None
    gender: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    encrypted_ssn: str | None = None
    insurance_id: str | None = None
    emergency_contact: str | None = None
    emergency_contact_phone: str | None = None
    is_active: bool | None = None


class PatientResponse(PatientBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
