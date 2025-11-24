"""
Logging Configuration
Configures structured logging with Loguru.
"""

import sys
import json
from pathlib import Path
from typing import Any, Dict
from loguru import logger

from app.core.config import settings


def json_formatter(record: Dict[str, Any]) -> str:
    """Custom JSON formatter for log records."""
    log_entry = {
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    
    # Add extra fields (avoid nested 'extra' in 'extra')
    if "extra" in record and isinstance(record["extra"], dict):
        for key, value in record["extra"].items():
            if key != "extra":  # Skip nested extra
                log_entry[key] = value
    
    # Add exception info if present
    if record.get("exception"):
        exc = record["exception"]
        log_entry["exception"] = {
            "type": exc.type.__name__ if exc.type else None,
            "value": str(exc.value) if exc.value else None,
        }
    
    return json.dumps(log_entry) + "\n"


def setup_logging() -> None:
    """Configure application logging."""
    # Remove default logger
    logger.remove()
    
    # Console logger - simple text format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Add console logger
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.log_level,
        colorize=True,
    )
    
    # Add file logger with simple text format (same as console)
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,  # Make it async for better performance
    )
    
    logger.info(
        "Logging configured",
        level=settings.log_level,
        format=settings.log_format,
        environment=settings.environment,
    )


def get_logger(name: str) -> logger:
    """
    Get a logger instance with a specific name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logger.bind(name=name)

