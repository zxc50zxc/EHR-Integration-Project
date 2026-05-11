from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClinicalDocumentCreate(BaseModel):
    patient_id: int
    document_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class ClinicalDocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)


class ClinicalDocumentSign(BaseModel):
    is_signed: bool = True


class ClinicalDocumentResponse(BaseModel):
    id: int
    patient_id: int
    practitioner_id: int | None
    document_type: str
    title: str
    version: int
    is_signed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
