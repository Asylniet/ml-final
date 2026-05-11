from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    access_token_ttl: int
    refresh_token_ttl: int
    secret_key: str
    algorithm: str
