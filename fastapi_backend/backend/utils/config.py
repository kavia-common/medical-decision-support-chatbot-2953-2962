import os
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    CORS_ALLOWED_ORIGINS: list[str] = []
    STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "local")
    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "./data/sessions")

    ONEDRIVE_CLIENT_ID: str | None = os.getenv("ONEDRIVE_CLIENT_ID")
    ONEDRIVE_CLIENT_SECRET: str | None = os.getenv("ONEDRIVE_CLIENT_SECRET")
    ONEDRIVE_TENANT_ID: str | None = os.getenv("ONEDRIVE_TENANT_ID")
    ONEDRIVE_DRIVE_ID: str | None = os.getenv("ONEDRIVE_DRIVE_ID")
    ONEDRIVE_FOLDER_ID: str | None = os.getenv("ONEDRIVE_FOLDER_ID")
    ONEDRIVE_AUTHORITY: str = os.getenv("ONEDRIVE_AUTHORITY", "https://login.microsoftonline.com")
    ONEDRIVE_SCOPE: str = os.getenv("ONEDRIVE_SCOPE", "https://graph.microsoft.com/.default")

    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "basic")

    APP_ENV: str = os.getenv("APP_ENV", "development")
    SITE_URL: str = os.getenv("SITE_URL", "http://localhost:3000")

    MEDICAL_DISCLAIMER: str = (
        "The information provided is for educational purposes only and is not a substitute for professional medical advice. "
        "Always consult a qualified healthcare provider for diagnosis and treatment."
    )
    SAFETY_WARNINGS: list[str] = [
        "If you experience severe symptoms (e.g., chest pain, difficulty breathing), seek emergency care immediately.",
        "Do not ignore professional medical advice due to information provided by this system."
    ]

@lru_cache
def get_settings() -> Settings:
    origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    origins_list = [o.strip() for o in origins.split(",") if o.strip()]
    s = Settings(CORS_ALLOWED_ORIGINS=origins_list)
    return s
