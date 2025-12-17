from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str
    
    # Service
    service_name: str = "customer-service"
    service_host: str = "localhost"
    service_port: int = 8081
    
    # Consul
    consul_host: str = "localhost"
    consul_port: int = 8500
    
    # Application
    environment: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Create a global settings instance
settings = Settings()