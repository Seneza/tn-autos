# Logger setup

import logging
import logfire

def setup_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logfire.configure()  # Configure logfire for logging
    return logger
