from .service import PredictService
from .model import PredictionResponse
from fastapi import UploadFile

service = PredictService()  # Có thể inject sau này

async def predict_post(data: UploadFile):
    return await service.predict(data)

def predict_get():
    return {"message": "Predict page"}