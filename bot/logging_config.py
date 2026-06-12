"""
Logging configuration for the trading bot.

Sets up structured logging with both file and console handlers.
File handler captures DEBUG+ messages for full traceability.
Console handler shows INFO+ messages for clean CLI output.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "trading_bot.log")


def setup_logging(
    log_file: str | None = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Configure and return the application logger.

    Args:
        log_file: Path to the log file. Defaults to logs/trading_bot.log.
        console_level: Minimum log level for console output.
        file_level: Minimum log level for file output.

    Returns:
        Configured logger instance.
    """
    log_file = log_file or DEFAULT_LOG_FILE
    log_dir = os.path.dirname(log_file)

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Get or create the root application logger
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # --- File handler (rotating, captures everything) ---
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # --- Console handler (clean, user-facing output) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.debug("Logging initialized — file: %s", log_file)
    return logger
