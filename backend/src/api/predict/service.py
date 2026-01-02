from .interface import IPredictService
from fastapi import UploadFile

class PredictService(IPredictService):
    async def predict(self, file: UploadFile) -> dict:

        content = await file.read()

