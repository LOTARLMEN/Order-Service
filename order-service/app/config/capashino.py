from app.config.base_setting import BaseConfig
from pydantic_settings import SettingsConfigDict


class CapashinoConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="CAPASHINO_")

    X_API_KEY: str
    BASE_URL: str
