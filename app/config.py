"""Application configuration with environment variable validation"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    # Snowflake Configuration
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_authenticator: Optional[str] = None  # e.g., "externalbrowser" or None for password
    snowflake_warehouse: Optional[str] = None
    snowflake_database: Optional[str] = None
    snowflake_schema: Optional[str] = None
    snowflake_role: Optional[str] = None
    snowflake_cortex_service_name: str = "product_search"
    snowflake_account_url: Optional[str] = None  # e.g., "https://ZGXJKBZ-LH19094.snowflakecomputing.com"
    snowflake_pat: Optional[str] = None  # Personal Access Token for REST API
    
    # Gemini AI Configuration
    gemini_api_key: Optional[str] = None
    
    # ElevenLabs Configuration
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_default_voice_id: Optional[str] = None
    
    # Vultr Configuration
    vultr_api_key: Optional[str] = None
    vultr_endpoint: Optional[str] = None
    
    # Solana Configuration (optional)
    solana_rpc_url: Optional[str] = None
    solana_private_key: Optional[str] = None
    
    # API Authentication
    api_key_secret: Optional[str] = None
    
    # Cloudinary Configuration
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None
    
    # Embedding Service Configuration
    embedding_service_url: str = "http://localhost:8001"
    
    def validate_required(self) -> None:
        """Validate that required environment variables are set"""
        required_for_demo = [
            "snowflake_account",
            "snowflake_user", 
            "snowflake_password",
            "gemini_api_key",
            "elevenlabs_api_key"
        ]
        missing = [var for var in required_for_demo if not getattr(self, var)]
        if missing:
            import warnings
            warnings.warn(
                f"Missing recommended environment variables: {', '.join(missing)}. "
                "Some features may not work properly.",
                UserWarning
            )


# Global settings instance
settings = Settings()

