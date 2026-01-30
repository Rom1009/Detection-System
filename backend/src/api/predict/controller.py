from sqlmodel import Session
from .service import PredictService
from .model import PredictionResponse
from fastapi import UploadFile, HTTPException, Depends, BackgroundTasks
from src.api.database.db import get_session
from src.api.monitor.service import MonitorService

api = PredictService()  # Có thể inject sau này


async def predict_post(data: UploadFile, session: Session = Depends(get_session), background_tasks: BackgroundTasks = BackgroundTasks()) -> PredictionResponse:
    try: 
        result = api.predict(data, session, background_tasks)
        res = await result
        return res
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def predict_get():
    return {"message": "Predict page"}