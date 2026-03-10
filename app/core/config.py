from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Interview Scheduler API"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"


settings = Settings()