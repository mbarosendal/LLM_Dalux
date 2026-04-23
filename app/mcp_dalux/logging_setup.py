from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
DEFAULT_CLIENT_LOG_NAME = "client_debug.log"


def configure_logging() -> None:
    """Configure shared logging for console and file output."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    attach_console_handler(root_logger, formatter)
    attach_file_handler(root_logger, DEFAULT_CLIENT_LOG_NAME, formatter)


def get_file_logger(name: str, log_filename: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger that writes to a dedicated file under logs."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    attach_file_handler(logger, log_filename, formatter)
    logger.propagate = False
    return logger


def attach_console_handler(logger: logging.Logger, formatter: logging.Formatter) -> None:
    """Attach a single console handler if one is not already present."""
    has_stream_handler = any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)

    if not has_stream_handler:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


def attach_file_handler(
    logger: logging.Logger,
    log_filename: str,
    formatter: logging.Formatter,
) -> None:
    """Attach a single file handler under logs if one is not already present."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / log_filename

    has_file_handler = any(
        isinstance(handler, logging.FileHandler) and Path(getattr(handler, "baseFilename", "")).resolve() == log_path.resolve()
        for handler in logger.handlers
    )

    if not has_file_handler:
        file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def append_structured_log_event(
    log_filename: str,
    source: str,
    event: str,
    payload: dict,
) -> None:
    """Append one event under logs with a consistent shape."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / log_filename

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "event": event,
        "payload": payload,
    }

    try:
        with log_path.open("a", encoding="utf-8") as debug_log_file:
            debug_log_file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception:
        # Structured debug logging must never break runtime flow.
        pass
