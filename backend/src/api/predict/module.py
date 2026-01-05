from core.base_module import BaseModule
from .controller import predict_get, predict_post
from fastapi import APIRouter
from .model import PredictionResponse

class PredictModule(BaseModule):
    
    prefix = "/predict" 
    tags = ["predict"]

    def __init__(self):
        super().__init__()
    
    def setup_routes(self):
        self.router = APIRouter()
        self.router.post("/", response_model=PredictionResponse)(predict_post)
        self.router.get("/")(predict_get)
        