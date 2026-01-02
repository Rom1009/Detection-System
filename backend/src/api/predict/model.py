from pydantic import BaseModel
from uuid import UUID

class PredictionResponse(BaseModel):
    id: UUID
    label: str
    confidence: float
    model_version: str


