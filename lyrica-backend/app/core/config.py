"""
Application Configuration
Loads environment variables and provides configuration settings.
"""

from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application Settings
    app_name: str = Field(default="Lyrica", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(
        default="development", description="Environment (development, staging, production)"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/lyrica_dev",
        description="Database connection URL",
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=30, description="Max overflow connections")
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_max_connections: int = Field(default=50, description="Redis max connections")
    redis_decode_responses: bool = Field(default=True, description="Decode Redis responses")

    # LLM Configuration (Multi-Provider Support)
    llm_provider: str = Field(
        default="ollama", description="LLM provider (ollama, openai, gemini, grok)"
    )

    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    ollama_model: str = Field(default="llama3", description="Ollama model name")
    ollama_timeout: int = Field(default=300, description="Ollama request timeout (seconds)")
    ollama_temperature: float = Field(default=0.7, description="LLM temperature")
    ollama_max_tokens: int = Field(default=2048, description="Max tokens to generate")

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model name")
    openai_temperature: float = Field(default=0.7, description="OpenAI temperature")
    openai_max_tokens: int = Field(default=2048, description="OpenAI max tokens")
    openai_timeout: int = Field(default=300, description="OpenAI timeout (seconds)")
    openai_base_url: Optional[str] = Field(default=None, description="OpenAI base URL (optional)")

    # Google Gemini Configuration
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-pro", description="Gemini model name")
    gemini_temperature: float = Field(default=0.7, description="Gemini temperature")
    gemini_max_tokens: int = Field(default=2048, description="Gemini max tokens")
    gemini_timeout: int = Field(default=300, description="Gemini timeout (seconds)")

    # Grok (X.AI) Configuration
    grok_api_key: Optional[str] = Field(default=None, description="Grok API key")
    grok_model: str = Field(default="grok-beta", description="Grok model name")
    grok_temperature: float = Field(default=0.7, description="Grok temperature")
    grok_max_tokens: int = Field(default=2048, description="Grok max tokens")
    grok_timeout: int = Field(default=300, description="Grok timeout (seconds)")
    grok_base_url: str = Field(default="https://api.x.ai/v1", description="Grok base URL")

    # ChromaDB Configuration
    chromadb_host: str = Field(default="localhost", description="ChromaDB host")
    chromadb_port: int = Field(default=8001, description="ChromaDB port")
    chromadb_collection: str = Field(default="lyrics_embeddings", description="Collection name")
    chromadb_persist_directory: str = Field(
        default="./data/chromadb", description="Persist directory"
    )

    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model name"
    )
    embedding_dimension: int = Field(default=384, description="Embedding dimension")
    chunk_size: int = Field(default=512, description="Text chunk size")
    chunk_overlap: int = Field(default=50, description="Chunk overlap")

    # Security Configuration
    secret_key: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        description="Secret key for JWT",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=15, description="Access token expiration (minutes)"
    )
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration (days)")

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:19006"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials")
    cors_allow_methods: List[str] = Field(default=["*"], description="Allowed methods")
    cors_allow_headers: List[str] = Field(default=["*"], description="Allowed headers")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Requests per minute")
    rate_limit_per_day: int = Field(default=1000, description="Requests per day")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    log_file: str = Field(default="logs/app.log", description="Log file path")

    # Agent Configuration
    max_agent_iterations: int = Field(default=3, description="Max agent refinement iterations")
    agent_timeout: int = Field(default=300, description="Agent timeout (seconds)")
    enable_streaming: bool = Field(default=True, description="Enable streaming responses")

    # Feature Flags
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    enable_tracing: bool = Field(default=False, description="Enable OpenTelemetry tracing")
    enable_profiling: bool = Field(default=False, description="Enable profiling")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v_upper

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (for Alembic)."""
        return self.database_url.replace("+asyncpg", "")


# Global settings instance
settings = Settings()
