from .service import PredictService
from .model import PredictionResponse
from fastapi import UploadFile, HTTPException

api = PredictService()  # Có thể inject sau này

async def predict_post(data: UploadFile):
    try: 
        result = api.predict(data)
        return await result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def predict_get():
    return {"message": "Predict page"}