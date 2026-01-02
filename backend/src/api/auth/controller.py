from .service import AuthService
from .model import LoginRequest, RegisterRequest

service = AuthService()  # Có thể inject sau này

def login(data: LoginRequest):
    return service.login(data.username, data.password)

def register(data: RegisterRequest):
    return service.register(data.username, data.password)
