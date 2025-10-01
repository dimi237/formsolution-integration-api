from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_URL: str = "http://localhost:4000"
    API_USERNAME: str = "user"
    API_PASSWORD: str = "pass"
    DOWNLOAD_DIR: str = "./downloads"
    CREDENTIAL_PATH: str = "./cred.json"
    
    mongo_url: str = "None"
    app_name: str = "None"

    class Config:
        env_file = ".env"
        extra = "ignore"
