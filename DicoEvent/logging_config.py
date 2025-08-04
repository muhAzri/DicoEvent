import os
import sys
from pathlib import Path
from loguru import logger

# Base directory for log files
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

def configure_logging():
    """Configure Loguru logging with file separation and rotation."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler for development
    if os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes'):
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level="DEBUG"
        )
    
    # Application log file (INFO level and above)
    logger.add(
        LOGS_DIR / "application.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        filter=lambda record: record["level"].no >= logger.level("INFO").no
    )
    
    # Error log file (ERROR level and above)
    logger.add(
        LOGS_DIR / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    return logger

# Configure logging when module is imported
app_logger = configure_logging()

def get_logger(name: str = None):
    """Get a logger instance with optional name binding."""
    if name:
        return logger.bind(name=name)
    return logger