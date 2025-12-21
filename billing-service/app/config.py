from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str

    # Service
    service_name: str = "billing-service"
    service_host: str = "billing-service"  # Matches container name usually
    service_port: int = 8083

    # Consul
    consul_host: str = "consul"
    consul_port: int = 8500

    # Application
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
