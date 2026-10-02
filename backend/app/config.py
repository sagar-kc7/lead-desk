from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://leaddesk:leaddesk@db:5432/leaddesk"
    JWT_SECRET: str = "change-me-in-production"
    ACCESS_TOKEN_TTL_MINUTES: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 7
    SECURE_COOKIES: bool = False


settings = Settings()
