from pydantic import BaseModel, ConfigDict


class FhirIdentifier(BaseModel):
    use: str = "usual"
    type: str = "MRN"
    value: str


class FhirHumanName(BaseModel):
    use: str = "official"
    given: list[str]
    family: str


class FhirContactPoint(BaseModel):
    system: str
    value: str


class FhirAddress(BaseModel):
    use: str = "home"
    line: list[str] | None = None
    city: str | None = None
    state: str | None = None
    postalCode: str | None = None
    country: str | None = None


class FhirPatient(BaseModel):
    resourceType: str = "Patient"
    id: str
    identifier: list[FhirIdentifier]
    active: bool
    name: list[FhirHumanName]
    telecom: list[FhirContactPoint] | None = None
    birthDate: str
    gender: str
    address: list[FhirAddress] | None = None

    model_config = ConfigDict(from_attributes=True)


class FhirReference(BaseModel):
    reference: str
    display: str | None = None


class FhirCoding(BaseModel):
    system: str | None = None
    code: str
    display: str


class FhirCodeableConcept(BaseModel):
    coding: list[FhirCoding]
    text: str | None = None


class FhirDocumentReferenceContent(BaseModel):
    attachment: dict[str, str]


class FhirDocumentReference(BaseModel):
    resourceType: str = "DocumentReference"
    id: str
    status: str = "current"
    type: FhirCodeableConcept | dict
    subject: FhirReference | dict
    date: str
    author: list[FhirReference] | list[dict] | None = None
    title: str | None = None
    description: str | None = None
    content: list[FhirDocumentReferenceContent] | str | None = None
    version: str = "1"


class FhirMedicationRequest(BaseModel):
    resourceType: str = "MedicationRequest"
    id: str
    status: str
    intent: str = "order"
    medicationCodeableConcept: FhirCodeableConcept | dict
    subject: FhirReference | dict
    dosageInstruction: list[dict]
    dosageInstructions: list[dict] | None = None
    requester: FhirReference | None = None
    authoredOn: str | None = None


class FhirObservationValue(BaseModel):
    value: str
    unit: str | None = None


class FhirObservation(BaseModel):
    resourceType: str = "Observation"
    id: str
    status: str
    code: FhirCodeableConcept | dict
    subject: FhirReference | dict
    effectiveDateTime: str
    issued: str
    valueString: str
    valueQuantity: FhirObservationValue | dict | None = None
    referenceRange: list[dict[str, str]] | None = None


class FhirDiagnosticReport(BaseModel):
    resourceType: str = "DiagnosticReport"
    id: str
    status: str
    code: FhirCodeableConcept | dict
    subject: FhirReference | dict
    issued: str
    result: list[FhirReference] | list[dict]
    conclusion: str | None = None
