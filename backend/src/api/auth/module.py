from core.base_module import BaseModule
from .controller import register, login, login_get
from fastapi import APIRouter

class AuthModule(BaseModule):
    
    prefix = "/auth" 
    tags = ["auth"]

    def __init__(self):
        super().__init__()
    
    def setup_routes(self):
        self.router = APIRouter()
        self.router.post("/register")(register)
        self.router.get("/login")(login_get)
        self.router.post("/login")(login)
        