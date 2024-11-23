"""A module for Logger setup."""
# logger.py
# Logger setup

import logging

import logfire


def setup_logger() -> logging.Logger:
    """
    Set up and configure the application's logger.

    This function initializes the logging configuration with the INFO level,
    creates a logger for the current module, configures Logfire for enhanced logging,
    and returns the configured logger instance.

    Returns:
        logging.Logger: A configured logger instance for the application.

    Raises:
        Exception: If Logfire configuration fails.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    try:
        logfire.configure()  # Configure logfire for logging
    except Exception as e:
        logger.error("Failed to configure Logfire.", exc_info=True)
        raise e
    return logger
