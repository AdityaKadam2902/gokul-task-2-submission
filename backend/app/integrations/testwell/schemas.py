"""TestWell API request and raw response schemas.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from pydantic import BaseModel, ConfigDict, Field


class TestWellBiomarkerInput(BaseModel):
    """Anonymous numeric biomarker measurement for TestWell request.

    Contains STRICTLY anonymous measurement fields; never patient identifiers.
    """

    __test__ = False
    model_config = ConfigDict(extra="forbid")

    marker: str = Field(..., min_length=1, max_length=80, description="Provider query marker name")
    value: float = Field(..., description="Numeric biomarker measurement value")
    unit: str = Field(..., min_length=1, max_length=20, description="Measurement unit (e.g. mg/dL)")


class TestWellInterpretRequest(BaseModel):
    """Request payload for TestWell POST /api/agent/interpret_results."""

    __test__ = False
    model_config = ConfigDict(extra="forbid")

    values: list[TestWellBiomarkerInput] = Field(
        ...,
        min_length=1,
        max_length=40,
        description="List of analyte measurements to interpret",
    )


# --- Raw Provider Response Models ---


class TestWellRawInput(BaseModel):
    """Raw input echo from TestWell response."""

    model_config = ConfigDict(extra="ignore")

    marker: str
    value: float
    unit: str | None = None


class TestWellRawRange(BaseModel):
    """Raw reference range block from TestWell."""

    model_config = ConfigDict(extra="ignore")

    qualifier: str | None = None
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    text: str | None = None


class TestWellRawCitation(BaseModel):
    """Raw source citation from TestWell."""

    model_config = ConfigDict(extra="ignore")

    label: str
    url: str


class TestWellRawLinks(BaseModel):
    """Raw URLs from TestWell."""

    model_config = ConfigDict(extra="ignore")

    biomarker: str | None = None
    interpretation: str | None = None
    orderTest: str | None = None


class TestWellRawResultItem(BaseModel):
    """Individual marker interpretation item from TestWell results array."""

    model_config = ConfigDict(extra="ignore")

    input: TestWellRawInput
    found: bool = False
    marker: str | None = None
    slug: str | None = None
    flag: str = "unknown"
    range: TestWellRawRange | None = None
    deviationPct: float | None = None
    unitMismatch: bool = False
    suggests: str | None = None
    retest: str | None = None
    citations: list[TestWellRawCitation] = Field(default_factory=list)
    links: TestWellRawLinks | None = None
    suggestions: list[str] = Field(default_factory=list)


class TestWellRawSummary(BaseModel):
    """Aggregated interpretation counts from TestWell."""

    model_config = ConfigDict(extra="ignore")

    total: int = 0
    matched: int = 0
    high: int = 0
    low: int = 0
    normal: int = 0
    unknown: int = 0


class TestWellRawReviewed(BaseModel):
    """Review metadata from TestWell."""

    model_config = ConfigDict(extra="ignore")

    catalog: str | None = None
    reviewer: str | None = None


class TestWellRawResult(BaseModel):
    """Inner 'result' object of TestWell response."""

    model_config = ConfigDict(extra="ignore")

    results: list[TestWellRawResultItem] = Field(default_factory=list)
    summary: TestWellRawSummary | None = None
    disclaimer: str | None = None
    reviewed: TestWellRawReviewed | None = None


class TestWellRawResponse(BaseModel):
    """Top-level response envelope from TestWell."""

    model_config = ConfigDict(extra="ignore")

    tool: str = "interpret_results"
    result: TestWellRawResult
