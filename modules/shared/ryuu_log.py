import logging
import os

# ANSI color codes
COLOR_BRACKET = "\033[38;5;81m"
COLOR_RYUU = "\033[38;5;213m"
COLOR_NOODLES = "\033[38;5;213m"
COLOR_RESET = "\033[0m"

ryuu_logger = logging.getLogger("RyuuNoodles")
ryuu_logger.setLevel(logging.DEBUG)


def ryuu_log(*args, loglevel="info", sep=" "):
    """
    Logger is called 'RyuuNoodles'.
    Valid loglevels: 'debug', 'info', 'warning', 'error', 'critical'.
    The environment variable 'RYUU_LOGLEVEL' can be set to control the logger's minimum log level (e.g., 'DEBUG', 'INFO', etc.).
    If 'RYUU_LOGLEVEL' is not set or is empty, the default log level is 'DEBUG'.
    """
    prefix = f"{COLOR_BRACKET}[{COLOR_RYUU}Ryuu{COLOR_NOODLES}Noodles{COLOR_BRACKET}]{COLOR_RESET}"

    level_colors = {
        "debug": "\033[38;5;46m",  # Green
        "info": "\033[38;5;39m",  # Blue
        "warning": "\033[38;5;214m",  # Orange
        "error": "\033[38;5;196m",  # Red
        "critical": "\033[38;5;199m",  # Magenta
    }
    loglevel = loglevel.lower()
    loglevel_upper = loglevel.upper()
    level_prefix = f"{level_colors.get(loglevel, '')}[{loglevel_upper}]\033[0m"

    message = sep.join(str(arg) for arg in args)
    # Color the message for debug, warning, error, and critical
    if loglevel in {"debug", "warning", "error", "critical"}:
        message = f"{level_colors.get(loglevel, '')}{message}\033[0m"

    full_message = f"{prefix}{level_prefix} {message}"

    # avoid unnecessary updates
    if not hasattr(ryuu_log, "_last_env_loglevel"):
        ryuu_log._last_env_loglevel = None

    env_loglevel = os.environ.get("RYUU_LOGLEVEL", "").upper()
    if env_loglevel != ryuu_log._last_env_loglevel:
        ryuu_logger.setLevel(getattr(logging, env_loglevel, logging.DEBUG))
        ryuu_logger.debug(
            f"{prefix}{level_prefix} {level_colors.get('debug', '')}Log level set to: {env_loglevel} (should say DEBUG) | If this is unexpected/uninteded, 'RYUU_LOGLEVEL' may have been 'None' or empty."
        )
        ryuu_log._last_env_loglevel = env_loglevel

    if loglevel == "debug":
        ryuu_logger.debug(full_message)
    elif loglevel == "info":
        ryuu_logger.info(full_message)
    elif loglevel == "warning":
        ryuu_logger.warning(full_message)
    elif loglevel == "error":
        ryuu_logger.error(full_message)
    elif loglevel == "critical":
        ryuu_logger.critical(full_message)
    else:
        ryuu_logger.warning(
            f"{prefix} Invalid loglevel. Falling back to 'warning' for this log message: {full_message}"
        )
