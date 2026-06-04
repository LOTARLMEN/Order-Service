from app.config.base_setting import BaseConfig
from pydantic_settings import SettingsConfigDict


class DatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    DATABASE_NAME: str

    @property
    def URL(self):
        return (
            f"postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.DATABASE_NAME}"
        )
