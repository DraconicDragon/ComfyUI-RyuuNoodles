import logging


def ryuu_log(*args, loglevel="info", sep=" ", end="\n"):
    """Custom log function that prefixes logs with [RyuuNoodles] and uses the specified log level."""
    prefix = "\033[38;5;81m[\033[38;5;213mRyuu\033[38;5;213mNoodles\033[38;5;81m]\033[0m"
    message = sep.join(str(arg) for arg in args)
    full_message = f"{prefix} {message}"

    loglevel = loglevel.lower()
    if loglevel == "debug":
        logging.debug(full_message)
    elif loglevel == "info":
        logging.info(full_message)
    elif loglevel == "warning":
        logging.warning(full_message)
    elif loglevel == "error":
        logging.error(full_message)
    elif loglevel == "critical":
        logging.critical(full_message)
    else:
        logging.info(full_message)
