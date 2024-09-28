from pydantic_settings import BaseSettings
from pydantic import Field, BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class PerplexityConfig(BaseModel):
    model: str = "llama-3.1-sonar-small-128k-online"
    temperature: float = 0.0

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

class Config(BaseSettings):
    word_threshold: int = Field(
        default=1000,
        description="Number of words to truncate the content to when using the web search tool"
    )

class Settings(BaseSettings):
    credentials: Credentials = Credentials()
    perplexity: PerplexityConfig = PerplexityConfig()
    config: Config = Config()

settings = Settings()