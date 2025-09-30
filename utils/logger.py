"""
Logging utility for the Multilingual RAG Planner application
"""

import os
import sys
from loguru import logger
from datetime import datetime

def setup_logger(name: str = "app"):
    """
    Set up logger with appropriate configuration
    
    Args:
        name (str): Logger name
        
    Returns:
        Logger instance
    """
    # Remove default logger
    logger.remove()
    
    # Determine log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Console logging format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # File logging format
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True
    )
    
    # Add file handler for general logs
    logger.add(
        f"{log_dir}/app_{datetime.now().strftime('%Y-%m-%d')}.log",
        format=file_format,
        level=log_level,
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Add error file handler
    logger.add(
        f"{log_dir}/errors_{datetime.now().strftime('%Y-%m-%d')}.log",
        format=file_format,
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    return logger.bind(name=name)