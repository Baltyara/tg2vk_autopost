import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "app.log")

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(level)

    # stderr handler
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    root.addHandler(sh)

    # rotating file handler
    fh = RotatingFileHandler(file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setFormatter(formatter)
    root.addHandler(fh)


