import os

class Settings:
    PROJECT_NAME: str = "SURG-3D Surgical Instrument Pipeline API"
    VERSION: str = "1.0.0"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", os.path.join(os.getcwd(), "storage"))
    SIMULATION_MODE: bool = os.getenv("SIMULATION_MODE", "true").lower() == "true"

settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
