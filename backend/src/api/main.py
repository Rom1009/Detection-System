from fastapi import FastAPI
import logging
import uvicorn
from api import register_modules
from logger import config_logging, LogLevels
from database.db import create_db_and_tables


config_logging(LogLevels.INFO)


create_db_and_tables()

def create_app():
    app = FastAPI(
        title="Universal Modular FastAPI")
    register_modules(app)
    logging.info("This is info")
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000,reload=True)