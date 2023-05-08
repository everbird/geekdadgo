#!/usr/bin/env python3

import logging
import sys


VERBOSE_LOG_LEVEL = {
    0: logging.ERROR,
    1: logging.WARN,
    2: logging.INFO,
    3: logging.DEBUG,
}


DEFAULT_FORMAT_STR = (
    '%(asctime)s %(levelname)s [%(process)d] %(name)s %(message)s'
)

def setup_logger(
    name,
    verbose=0,
    log_file=None,
    to_stdout=False,
    format_str=DEFAULT_FORMAT_STR
):
    logger = logging.getLogger(name)

    if verbose > 3:
        # More detial from top level logger (root logger)
        # No need to configure child loggers since message goes to parent logger
        # as well. Otherwise you'll get duplicate messages.
        root_log_level = logging.DEBUG
        logging.basicConfig(
            level=root_log_level,
            format=format_str,
            filename=log_file
        )
    else:
        log_level = VERBOSE_LOG_LEVEL.get(verbose, logging.DEBUG)
        handler = create_log_handler(log_level, format_str=format_str, log_file=log_file)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    return logger


def create_log_handler(log_level, format_str=DEFAULT_FORMAT_STR, log_file=None):
    if log_file:
        handler = logging.FileHandler(log_path)
    else:
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    return handler
