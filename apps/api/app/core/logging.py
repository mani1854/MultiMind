"""
logging.py — Structured Logging
================================
WHAT THIS DOES:
  Sets up structured logging using `structlog`.
  Instead of messy print() or basic logging, structlog outputs JSON:

  Normal print():       "Server started"
  structlog output:     {"event": "api.starting", "level": "info", "timestamp": "2024-08-15T10:30:00Z"}

WHY JSON LOGGING:
  - Machines can parse it (for dashboards, alerts)
  - Every log has a timestamp automatically
  - You can add context: logger.info("user.login", user_id="123", role="admin")
"""

import logging
import sys

import structlog


def configure_logging() -> None:
    """Configure structured JSON logging for the entire application."""

    # Set Python's built-in logging to INFO level
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)

    # Configure structlog with processors (each processor transforms the log)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,     # Merge context from async code
            structlog.processors.add_log_level,          # Add "level": "info"
            structlog.processors.TimeStamper(fmt="iso"),  # Add ISO timestamp
            structlog.processors.JSONRenderer(),          # Output as JSON
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Create a global logger instance — import this in any file
logger = structlog.get_logger()
