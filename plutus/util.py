"""
Utils
"""

from __future__ import annotations
from datetime import datetime
from typing import Any
import logging
import logging.config
import os
import pathlib


log = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------------------------------------------------
def configure_logging() -> None:
    """
    Configures logging
    """

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "stdout": {"class": "logging.StreamHandler", "formatter": "standard"},
        },
        "loggers": {
            "": {
                "handlers": ["stdout"],
                "level": get_env_var("LOG_LEVEL"),
            },
            "postgresql": {
                "handlers": ["stdout"],
                "level": "ERROR",
            },
            "botocore": {
                "handlers": ["stdout"],
                "level": "INFO",
            },
            "urllib3.connectionpool": {
                "handlers": ["stdout"],
                "level": "INFO",
            },
        },
    }
    if os.environ.get("ENVIRONMENT") == "local":
        log_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/plutus.log",
            "mode": "a",
            "maxBytes": 1048576,
            "backupCount": 1,
        }
        log_config["loggers"][""]["handlers"] = ["stdout", "file"]
    else:
        log_config["loggers"]["botocore.parsers"] = {
            "handlers": ["stdout"],
            "level": "INFO",
        }

    logging.config.dictConfig(log_config)


# ----------------------------------------------------------------------------------------------------------------------
# Datetime
# ----------------------------------------------------------------------------------------------------------------------
def instant():
    """
    Current time in UTC
    """

    return datetime.utcnow()


def instant_str():
    """
    Current time string in UTC
    """

    return instant().strftime("%Y-%m-%dT%H:%M:%S%z")


# ----------------------------------------------------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------------------------------------------------
def cwd():
    """
    Gets the current working directory
    """

    return pathlib.Path().cwd()


# ----------------------------------------------------------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------------------------------------------------------
class PlutusException(Exception):
    """
    Plutus base exception
    """


# ----------------------------------------------------------------------------------------------------------------------
# Environment vars
# ----------------------------------------------------------------------------------------------------------------------
def get_env_var(
    key: str,
    default: Any = None,
    is_list: bool = False,
    is_bool: bool = False,
    is_int: bool = False,
    exce: bool = True,
) -> Any:
    """
    Gets an environment variables
    """

    value = os.environ.get(key, default)
    if exce and not value:
        raise PlutusException(f"Missing required environment variable {key}")

    if is_list:
        value = value.split(",")
    elif is_int:
        value = int(value)
    elif is_bool:
        lower_val = value.lower()
        if lower_val in ["TRUE"]:
            value = True
        elif lower_val in ["FALSE"]:
            value = False

    elif value == "NONE":
        value = None

    return value


def set_env_var(key, value, is_list=False, is_bool=False, is_int=False, exce=False):
    """
    Sets an environment variable
    """

    if exce:
        if os.environ.get(key):
            raise PlutusException(f"Environment {key} variable already exists")

    if is_list:
        value = value.split(",")
    if is_int:
        value = str(value)
    elif is_bool:
        lower_val = value.lower()
        if lower_val in ["TRUE"]:
            value = True
        elif lower_val in ["FALSE"]:
            value = False

    os.environ[key] = value
