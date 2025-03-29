"""Logging utilities for the Dot CLI tool."""

import logging
import os
import sys
from typing import Optional


def setup_logger(level: Optional[int] = None) -> logging.Logger:
    """Set up and configure the logger."""
    if level is None:
        # Determine log level from environment
        log_level_str = os.environ.get("DOT_LOG_LEVEL", "INFO").upper()
        try:
            level = getattr(logging, log_level_str)
        except AttributeError:
            level = logging.INFO

    # Create logger
    logger = logging.getLogger("dot")
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers = []

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


# Create a global logger instance
logger = setup_logger()
