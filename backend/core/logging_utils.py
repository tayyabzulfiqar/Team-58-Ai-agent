import logging
import os


def configure_logging() -> None:
    level_name = os.getenv("TEAM58_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    if logging.getLogger().handlers:
        logging.getLogger().setLevel(level)
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
