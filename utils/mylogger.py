# coding:utf-8
import logging
import logging.handlers
import os
import datetime
import sys

from Conf.conf import Level, LogPath

APP_NAME = "pm"


def get_logger(logfile="test"):
    """
    获取日志句柄的方法
    """
    logger = logging.getLogger(logfile)
    log_level = Level
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        log_root = LogPath
        if not os.path.exists(log_root):
            os.mkdir(log_root)
        logfile = APP_NAME + '_' + logfile + '.log.' + datetime.datetime.now().strftime('%Y-%m-%d')
        file_handle = logging.handlers.RotatingFileHandler(log_root + os.sep + logfile, maxBytes=1024 * 1024 * 50,
                                                           backupCount=5, encoding="utf-8", delay=False)
        file_handle.suffix = "%Y-%m-%d"
        file_handle.setLevel(logging._levelNames.get(log_level, 'ERROR'))

        formatter = logging.Formatter(
            '[%(asctime)s] {%(pathname)s:%(lineno)d} %(funcName)s %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S'
        )
        file_handle.setFormatter(formatter)
        logger.addHandler(file_handle)
    return logger

# DEFAULT_LOGGER = get_logger()
