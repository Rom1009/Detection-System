from sqlmodel import Session
from .service import PredictService
from .model import PredictionResponse
from fastapi import UploadFile, HTTPException, Depends
from database.db import get_session

api = PredictService()  # Có thể inject sau này

async def predict_post(data: UploadFile, session: Session = Depends(get_session)):
    try: 
        result = api.predict(data, session)
        return await result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def predict_get():
    return {"message": "Predict page"}