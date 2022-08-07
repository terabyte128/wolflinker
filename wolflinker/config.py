from pydantic import BaseSettings


class Settings(BaseSettings):
    auth_username: str
    auth_password: str
