from abc import ABC, abstractmethod
from fastapi import UploadFile, BackgroundTasks
from sqlmodel import Session

class IPredictService(ABC):
    @abstractmethod
    def load_model_direct(self):
        pass
    
    @abstractmethod
    def predict(self, file: UploadFile, session: Session, background_tasks: BackgroundTasks = BackgroundTasks()) -> dict:
        pass

