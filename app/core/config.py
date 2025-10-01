from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Formsoltion Integration API"
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name:str = "integrations"
    BASE_URL: str = "http://localhost:4000"
    API_USERNAME: str = "user"
    API_PASSWORD: str = "pass"
    DOWNLOAD_DIR: str = "./downloads"
    scheduler_timezone: str = "UTC"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
