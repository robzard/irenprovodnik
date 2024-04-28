import logging
import sys


def setup_logger(logger_name, log_file=None):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s')

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Удаление существующих обработчиков, если они есть
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger(__name__, 'logfile.log')
