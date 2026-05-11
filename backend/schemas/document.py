from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClinicalDocumentCreate(BaseModel):
    patient_id: int
    document_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    status: str = "current"
    signed: bool = False


class ClinicalDocumentUpdate(BaseModel):
    document_type: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    status: str | None = None
    signed: bool | None = None


class ClinicalDocumentResponse(BaseModel):
    id: int
    patient_id: int
    version_group_id: int | None
    version: int
    document_type: str
    title: str
    content: str
    status: str
    author_id: int
    signed_by: int | None
    signed_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
