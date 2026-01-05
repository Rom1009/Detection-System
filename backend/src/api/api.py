from fastapi import FastAPI, APIRouter
from auth.module import AuthModule
from predict.module import PredictModule

def register_modules(app: FastAPI):
    
    api_router = APIRouter(prefix = "/api")
    
    modules = [
        AuthModule(),
        PredictModule(),
        # Thêm Module khác ở đây
    ]

    for module in modules:
        module.setup_routes()
        api_router.include_router(module.router, prefix = module.prefix, tags = module.tags)
        
    app.include_router(api_router)
