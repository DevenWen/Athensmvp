import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY")
    default_model: str = os.getenv("DEFAULT_MODEL", "openai/gpt-3.5-turbo")
    logician_model: str = os.getenv("LOGICIAN_MODEL", "openai/gpt-4-turbo")
    skeptic_model: str = os.getenv("SKEPTIC_MODEL", "anthropic/claude-3-opus")

settings = Settings()
