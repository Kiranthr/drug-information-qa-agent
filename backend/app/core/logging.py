"""
Structured logging configuration for the Drug Information Q&A Agent.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured logging for the application."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("drug_qa_agent")
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers if re-initialized
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


logger = setup_logging()
