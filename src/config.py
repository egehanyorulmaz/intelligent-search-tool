from pydantic_settings import BaseSettings
from pydantic import Field, BaseModel
from dotenv import load_dotenv

load_dotenv()

from typing import Dict, Any

class AgentRegistration(BaseModel):
    name: str
    description: str
    function: Any
    config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

class Credentials(BaseSettings):
    perplexity_api_key: str = Field(alias="PERPLEXITY_API_KEY")
    google_api_key: str = Field(alias="GOOGLE_API_KEY")
    google_cse_id: str = Field(alias="GOOGLE_CSE_ID")
    wikipedia_user_agent: str = Field(alias="WIKIPEDIA_USER_AGENT")
    langsmith_api_key: str = Field(alias="LANGSMITH_API_KEY")
    openai_api_key: str = Field(default="OPENAI_API_KEY", alias="OPENAI_API_KEY")
    agent_temperature: float = Field(default=0.0, alias="AGENT_TEMPERATURE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class Settings(BaseSettings):
    credentials = Credentials()

settings = Settings()