import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


all_media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all_media')


class Settings(BaseSettings):
    """Класс настроек бота"""
    bot_token: SecretStr
    database_file: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
