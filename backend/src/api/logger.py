import logging
from enum import StrEnum
import sys

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"

class LogLevels(StrEnum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    CRITICAL = "CRITICAL"

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[95m"
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.msg = f"{color}{record.msg}{self.RESET}"
        return super().format(record)

def config_logging(log_level: str = LogLevels.ERROR):
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevels]

    if log_level not in log_levels:
        log_level = LogLevels.ERROR.value

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter(LOG_FORMAT_DEBUG))
    logger.addHandler(console_handler)

    logger.info(f"Logger initialized with level: {log_level}")
