from pydantic import computed_field
from pydantic_settings import SettingsConfigDict

from app.config.base_setting import BaseConfig


class DatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    DATABASE_NAME: str

    @computed_field
    @property
    def URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.DATABASE_NAME}"
        )
