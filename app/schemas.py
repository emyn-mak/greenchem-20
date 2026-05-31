from typing import Any, Literal

from pydantic import BaseModel, Field


ENVIRONMENT_FIELDS = [
    "temperature",
    "time",
    "light",
    "humidity",
    "pressure",
    "stirring",
    "ph",
    "atmosphere",
    "solvent",
    "catalyst",
    "catalyst_role",
    "concentration",
    "wavelength",
    "voltage",
    "current",
    "flow_rate",
]

ValidationStatus = Literal[
    "Published",
    "Predicted (compatible)",
    "Predicted (uncertain)",
    "Experimental required",
]


class AnalyzeRequest(BaseModel):
    formula_text: str = Field(..., min_length=1)


class Compound(BaseModel):
    quantity: str | None = None
    unit: str | None = None
    name: str | None = None
    formula: str | None = None
    role: str | None = None


class Environment(BaseModel):
    temperature: str | None = None
    time: str | None = None
    light: str | None = None
    humidity: str | None = None
    pressure: str | None = None
    stirring: str | None = None
    ph: str | None = None
    atmosphere: str | None = None
    solvent: str | None = None
    catalyst: str | None = None
    catalyst_role: str | None = None
    concentration: str | None = None
    wavelength: str | None = None
    voltage: str | None = None
    current: str | None = None
    flow_rate: str | None = None


class DetectedInput(BaseModel):
    compounds: list[Compound] = Field(default_factory=list)
    environment: Environment = Field(default_factory=Environment)


class SolventFacts(BaseModel):
    name: str
    formula: str | None = None
    ghs_codes: list[str] = Field(default_factory=list)
    boiling_point_c: float | None = None
    chem21_color: Literal["green", "yellow", "red", "unknown"] = "unknown"


class EvidenceItem(BaseModel):
    source: str
    statement: str


class Alternative(BaseModel):
    rank: int
    replacement_solvent: SolventFacts
    formula: list[str]
    environment: Environment
    compatibility_notes: list[str] = Field(default_factory=list)
    qualitative_benefits: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    status: Literal[
        "Literature reported",
        "Theoretically compatible",
        "Requires experiment",
        "Insufficient data",
    ]
    validation_status: ValidationStatus


class CurrentAssessment(BaseModel):
    solvent: SolventFacts | None = None
    catalyst_formula: str | None = None
    catalyst_role: str | None = None
    hazard_summary: list[str] = Field(default_factory=list)
    compatibility_warnings: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    detected_input: DetectedInput
    current_formula: CurrentAssessment
    alternatives_found: int
    alternatives: list[Alternative]
    validation_status: ValidationStatus
    status: str
    message: str
    human_validation_required: bool = True


def empty_environment_dict() -> dict[str, Any]:
    return {field: None for field in ENVIRONMENT_FIELDS}
