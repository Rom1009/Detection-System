from .interface import IAuthService

class AuthService(IAuthService):
    def login(self, username: str, password: str):
        # TODO: check DB, hash password,...
        return {"message": f"User {username} logged in"}

    def register(self, username: str, password: str):
        # TODO: add to DB
        return {"message": f"User {username} registered successfully"}

    def logout(self, user_id: int):
        return {"message": f"User {user_id} logged out"}

    def refresh_token(self, refresh_token: str):
        return {"access_token": "new_token"}
