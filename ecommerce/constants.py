import logging
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# a way to control the log level of a caught exception
EXCEPTION_LOG_LEVELS = {
    ValidationError: logging.WARNING,
    IntegrityError: logging.ERROR,
    Exception: logging.CRITICAL,
}
