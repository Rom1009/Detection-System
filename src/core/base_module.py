from abc import ABC, abstractmethod
from fastapi import FastAPI, APIRouter
import importlib

class BaseModule(ABC):
    """
    Base class for all modules.
    Every custom module must inherit this class and implement setup_routes().
    """

    prefix: str = ""
    tags: list[str] = []

    def __init__(self):
        self.router = APIRouter(prefix=self.prefix, tags=self.tags)


        # Setup main components
        self.setup_routes()
        self.setup_middlewares()
        self.setup_events()

    @abstractmethod
    def setup_routes(self):
        """Define or attach the router"""
        pass

    def setup_middlewares(self):
        """Register custom middlewares if any"""
        pass

    def setup_events(self):
        """Define startup/shutdown events"""
        pass