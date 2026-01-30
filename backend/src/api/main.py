from fastapi import FastAPI
import logging
import uvicorn
<<<<<<< HEAD
from api import register_modules
from logger import config_logging, LogLevels
=======
from src.api.api import register_modules
from src.api.logger import config_logging, LogLevels
from src.api.database.db import create_db_and_tables
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator

load_dotenv()
>>>>>>> dev


config_logging(LogLevels.INFO)


<<<<<<< HEAD

def create_app():
    app = FastAPI(title="Universal Modular FastAPI")
=======
create_db_and_tables()

def create_app():
    app = FastAPI(
        title="Universal Modular FastAPI")
>>>>>>> dev
    register_modules(app)
    logging.info("This is info")
    return app

<<<<<<< HEAD
app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3000,reload=True)
=======
# def create_celery():
#     celery = Celery(
#         __name__, 
#         broker = "redis://127.0.0.1:6379/0",
#         backend = "redis://127.0.0.1:6379/0"
#     )
#     create_celery(celery)    
#     return celery

app = create_app()

Instrumentator().instrument(app).expose(app)

# celery = create_celery()

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=5000,reload=True)
>>>>>>> dev
