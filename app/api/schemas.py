from pydantic import BaseModel, Field


class ICPRequest(BaseModel):
    """Requête de création de job, reprenant les champs du formulaire ICP."""

    job_title: str
    country: str
    sector: str = ""
    max_prospects: int = Field(default=20, ge=1, le=100)
    required_keywords: list[str] = Field(default_factory=list)
    forbidden_keywords: list[str] = Field(default_factory=list)


class JobCreatedResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress_percent: int
    progress_text: str
    error: str | None = None


class ProspectResultSchema(BaseModel):
    name: str
    linkedin_url: str
    job_title: str
    status: str | None = None
    score: int | None = None
    confidence: float | None = None
    error: str | None = None


class JobResultsResponse(BaseModel):
    job_id: str
    prospects: list[ProspectResultSchema]
