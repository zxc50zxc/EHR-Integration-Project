from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DiagnosticReportCreate(BaseModel):
    patient_id: int
    report_code: str = Field(min_length=1, max_length=100)
    report_name: str = Field(min_length=1, max_length=255)
    status: str = "final"
    conclusion: str | None = None


class DiagnosticReportUpdate(BaseModel):
    report_code: str | None = Field(default=None, min_length=1, max_length=100)
    report_name: str | None = Field(default=None, min_length=1, max_length=255)
    status: str | None = None
    conclusion: str | None = None
    is_active: bool | None = None


class DiagnosticReportResponse(BaseModel):
    id: int
    patient_id: int
    report_code: str
    report_name: str
    status: str
    conclusion: str | None
    issued_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LabObservationCreate(BaseModel):
    patient_id: int
    diagnostic_report_id: int | None = None
    test_code: str = Field(min_length=1, max_length=100)
    test_name: str = Field(min_length=1, max_length=255)
    value: str = Field(min_length=1, max_length=100)
    unit: str | None = Field(default=None, max_length=50)
    reference_range: str | None = Field(default=None, max_length=100)
    status: str = "final"
    effective_date: str


class LabObservationUpdate(BaseModel):
    diagnostic_report_id: int | None = None
    test_code: str | None = Field(default=None, min_length=1, max_length=100)
    test_name: str | None = Field(default=None, min_length=1, max_length=255)
    value: str | None = Field(default=None, min_length=1, max_length=100)
    unit: str | None = Field(default=None, max_length=50)
    reference_range: str | None = Field(default=None, max_length=100)
    status: str | None = None
    effective_date: str | None = None
    is_active: bool | None = None


class LabObservationResponse(BaseModel):
    id: int
    patient_id: int
    diagnostic_report_id: int | None
    test_code: str
    test_name: str
    value: str
    unit: str | None
    reference_range: str | None
    status: str
    effective_date: str
    issued_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LabResultData(BaseModel):
    result_name: str = Field(min_length=1, max_length=255)
    result_value: str = Field(min_length=1, max_length=100)
    unit: str = Field(min_length=1, max_length=50)
    reference_range: str = Field(min_length=1, max_length=100)
    status: str = "normal"


class LabTestCreate(BaseModel):
    patient_id: int
    test_name: str = Field(min_length=1, max_length=255)
    test_code: str = Field(min_length=1, max_length=50)
    order_date: str
    assigned_to: int | None = None


class LabTestUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=20)
    result_date: str | None = None


class LabTestResponse(BaseModel):
    id: int
    patient_id: int
    practitioner_id: int
    assigned_to: int | None = None
    collected_by: int | None = None
    received_by: int | None = None
    resulted_by: int | None = None
    verified_by: int | None = None
    test_name: str
    status: str
    order_date: str
    result_date: str | None = None
    sample_collected_at: datetime | None = None
    received_at: datetime | None = None
    verified_at: datetime | None = None
    released_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LabResultResponse(BaseModel):
    id: int
    lab_test_id: int
    result_name: str
    result_value: str
    unit: str
    reference_range: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class LabTestWithResults(BaseModel):
    test: LabTestResponse
    results: list[LabResultResponse] = []


class LabTestAssign(BaseModel):
    assigned_to: int


class LabWorkflowActionResponse(BaseModel):
    message: str
    test: LabTestResponse
