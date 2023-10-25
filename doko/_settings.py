"""Hidden to avoid confusions with the initialized settings"""

from datetime import timedelta

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    """
    Settings format we expect. A .env file with the following fields and defaults
    It gets initialized in the roots __init__.py
    """

    model_config = SettingsConfigDict(
        env_prefix="doko__",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    SESSION_TOKEN_VALIDITY_MINUTES: int = Field(default=12 * 60)
    RESET_DB_ON_STARTUP: bool = Field(default=True)
    DB_TEST_SETUP: bool = Field(
        default=True
    )
    # todo: validator for logging levels
    DEBUG_LEVEL: str = Field(default="INFO")
    DB_URL: str = Field()

    @computed_field  # type: ignore
    @property
    def SESSION_TOKEN_VALIDITY(self) -> timedelta:
        return timedelta(minutes=self.SESSION_TOKEN_VALIDITY_MINUTES)
