from abc import ABC, abstractmethod
from fastapi import UploadFile

class IPredictService(ABC):
    @abstractmethod
    def predict(self, file: UploadFile) -> dict:
        pass

