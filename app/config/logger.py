from loguru import logger

def configure_logger(prefix: str):
    if not logger._core.handlers:
        logger.add(
            lambda msg: print(msg, end=""),
            level="DEBUG",
            format=(
                f"<CYAN>{{time:YYYY-MM-DD HH:mm:ss.SSS}}</CYAN> | "
                "<b>{level:<8}</b> | "
                "<cyan>{name}:{function}:{line}</cyan> | "
                f"{prefix} <b>{{message}}</b>"
            ),
            colorize=True
        )
    return logger