import logging
import time
from functools import wraps


def logging_config(
        level=logging.INFO,
        log_format: str = '%(asctime)s %(name)-20s %(levelname)-10s %(message)s',
        log_date_fmt: str = '%Y-%m-%dT%H:%M:%S%z',
        **kwargs
):
    """Wrapper for logging basic config with a default format
    :param level: logging level
    :param log_format: logging format
    :param log_date_fmt: logging date format
    :param kwargs:
    :return:
    """
    logging.basicConfig(level=level, format=log_format, datefmt=log_date_fmt, **kwargs)
    logging.Formatter.converter = time.gmtime


def log_timer_wrapper(logger: logging.Logger, level: int = logging.DEBUG):
    def called(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            func_name = func.__name__
            logger.log(level=level, msg=f'{func_name} started')
            start = time.perf_counter()
            result = func(*args, **kwargs)
            logger.log(level=level, msg=f'{func_name} took {time.perf_counter() - start:.2f}s')
            return result
        return wrapped
    return called
