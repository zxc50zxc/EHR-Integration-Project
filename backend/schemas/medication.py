from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MedicationRequestCreate(BaseModel):
    patient_id: int
    medication_name: str = Field(min_length=1, max_length=255)
    dosage: str = Field(min_length=1, max_length=100)
    frequency: str = Field(min_length=1, max_length=100)
    route: str | None = Field(default=None, max_length=100)
    start_date: str
    end_date: str | None = None
    status: str = "active"
    intent: str = "order"
    notes: str | None = None


class MedicationRequestUpdate(BaseModel):
    medication_name: str | None = Field(default=None, min_length=1, max_length=255)
    dosage: str | None = Field(default=None, min_length=1, max_length=100)
    frequency: str | None = Field(default=None, min_length=1, max_length=100)
    route: str | None = Field(default=None, max_length=100)
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    intent: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class MedicationRequestResponse(BaseModel):
    id: int
    patient_id: int
    practitioner_id: int
    medication_name: str
    dosage: str
    frequency: str
    route: str | None
    start_date: str
    end_date: str | None
    status: str
    intent: str
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicationCreate(BaseModel):
    patient_id: int
    drug_name: str = Field(min_length=1, max_length=255)
    dosage: str = Field(min_length=1, max_length=100)
    frequency: str = Field(min_length=1, max_length=100)
    route: str = Field(min_length=1, max_length=50)
    start_date: str
    end_date: str | None = None
    indication: str | None = Field(default=None, max_length=255)


class MedicationUpdate(BaseModel):
    frequency: str | None = Field(default=None, min_length=1, max_length=100)
    status: str | None = Field(default=None, max_length=20)
    end_date: str | None = None


class MedicationResponse(BaseModel):
    id: int
    patient_id: int
    practitioner_id: int
    drug_name: str
    dosage: str
    frequency: str
    route: str
    end_date: str | None
    indication: str | None
    status: str
    start_date: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
