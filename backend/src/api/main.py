from fastapi import FastAPI
import logging
import uvicorn
from api import register_modules
from logger import config_logging, LogLevels
from database.db import create_db_and_tables
from dotenv import load_dotenv

load_dotenv()


config_logging(LogLevels.INFO)


create_db_and_tables()

def create_app():
    app = FastAPI(
        title="Universal Modular FastAPI")
    register_modules(app)
    logging.info("This is info")
    return app

# def create_celery():
#     celery = Celery(
#         __name__, 
#         broker = "redis://127.0.0.1:6379/0",
#         backend = "redis://127.0.0.1:6379/0"
#     )
#     create_celery(celery)    
#     return celery

app = create_app()
# celery = create_celery()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000,reload=True)