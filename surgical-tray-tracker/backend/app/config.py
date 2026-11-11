import os

class Settings:
    PROJECT_NAME: str = "SurgTrace AI Surgical Tray Tracking API"
    VERSION: str = "1.0.0"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", os.path.join(os.getcwd(), "storage"))

settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "uploads"), exist_ok=True)
