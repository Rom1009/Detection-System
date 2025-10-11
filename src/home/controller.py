from fastapi import APIRouter
from starlette import status
from src.home.module import router

@router.get("/", status_code = status.HTTP_200_OK)
async def home():
    return {"message": "Welcome to the Home Page"}