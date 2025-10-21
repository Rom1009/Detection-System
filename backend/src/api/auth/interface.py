from abc import ABC, abstractmethod

class IAuthService(ABC):
    @abstractmethod
    def login(self, username: str, password: str):
        pass

    @abstractmethod
    def register(self, username: str, password: str):
        pass

    @abstractmethod
    def logout(self, user_id: int):
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str):
        pass
