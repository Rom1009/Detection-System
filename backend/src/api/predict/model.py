from pydantic import BaseModel
from uuid import UUID
import numpy as np

class PredictionResponse(BaseModel):
    id: UUID
    image: str
    label: str
    mask: str
    confidence: float
    model_version: str