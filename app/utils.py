import os
import logging
import sys


class LogHelper(object):
    @classmethod
    def get_debug_env_flag(cls):
        return bool(os.environ.get('DEBUG', 'false').lower() == 'true')

    @classmethod
    def get_fast_api_logger(cls, name, log_level=logging.DEBUG):
        """For more on logging, see the readme"""
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        return logger

    @classmethod
    def get_debug_logger(cls, name):
        return cls.get_fast_api_logger(name, log_level=logging.DEBUG)

    @classmethod
    def get_info_logger(cls, name):
        return cls.get_fast_api_logger(name, log_level=logging.INFO)

    @classmethod
    def get_env_logger(cls, name):
        is_debug = cls.get_debug_env_flag()
        if is_debug:
            return cls.get_debug_logger(name)
        return cls.get_info_logger(name)
