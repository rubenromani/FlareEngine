"""Provides a custom logger configuration utility.

This module contains functionality for creating and configuring logger instances
with predefined formatting and file handling capabilities.

Example:
    Basic usage example:

    ```
    from logger_provider import get_logger
    
    # Create a logger with INFO level
    logger = get_logger("my_module", "INFO")
    
    # Use the logger
    logger.info("This is an information message")
    ```
"""

import logging

def get_logger(name: str, level: str):
    """Creates and configures a logger with specified name and level.
    
    Configures a logger instance with a file handler that writes log entries
    to 'app.log' using a predefined format. Both the logger and handler
    are set to the same log level.
    
    Args:
        name: A string representing the logger name.
        level: A string specifying the logging level. 
            Must be one of "DEBUG", "INFO", "WARNING", "ERRORR", "CRITICAL".
            If an invalid level is provided, defaults to "ERROR".
    
    Returns:
        logging.Logger: A configured logger instance.
    
    Note:
        The log format used is: '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
    """

    
    logger = logging.getLogger(__name__)

    handler = logging.FileHandler('app.log')
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    match level:
        case "DEBUG":
            handler.setLevel(logging.DEBUG)
        case "INFO":
            handler.setLevel(logging.INFO)
        case "WARNING":
            handler.setLevel(logging.WARNING)
        case "ERRORR":
            handler.setLevel(logging.ERROR)
        case "CRITICAL":
            handler.setLevel(logging.CRITICAL)
        case _:
            handler.setLevel(logging.ERROR)

    logger.addHandler(handler)

    match level:
        case "DEBUG":
            logger.setLevel(logging.DEBUG)
        case "INFO":
            logger.setLevel(logging.INFO)
        case "WARNING":
            logger.setLevel(logging.WARNING)
        case "ERRORR":
            logger.setLevel(logging.ERROR)
        case "CRITICAL":
            logger.setLevel(logging.CRITICAL)
        case _:
            logger.setLevel(logging.ERROR)

    return logger