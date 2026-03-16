from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str
    feishu_app_id: str
    feishu_app_secret: str
    feishu_verification_token: str
    tavily_api_key: str
    notion_token: str
    notion_database_id: str
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
