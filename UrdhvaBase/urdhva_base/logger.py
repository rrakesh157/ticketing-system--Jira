"""
Application logger generation
"""

import os
import logging
import urdhva_base
import logging.handlers


class Logger(object):
    """
    Logger class
    """
    _instances = {}

    @classmethod
    def get_instance(cls, log_file=None):
        """
        Logger get instance
        """
        if not log_file:
            raise RuntimeError("Require log file name.")
        if log_file not in Logger._instances:
            Logger._instances[log_file] = Logger(log_file)

        return Logger._instances[log_file].my_logger

    def __init__(self, log_file):
        """
        Logger initilization
        """
        if not os.path.exists(urdhva_base.settings.log_base_dir):
            os.makedirs(urdhva_base.settings.log_base_dir)

        log_file_path = os.path.join(urdhva_base.settings.log_base_dir, log_file + ".log")

        # Set up a specific logger with our desired output level
        self.my_logger = logging.getLogger(log_file)
        self.my_logger.setLevel(logging.DEBUG)

        # Add the log message handler to the logger
        handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=urdhva_base.settings.log_max_size,
                                                       backupCount=urdhva_base.settings.log_max_count)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(funcName)s '
                                      '%(lineno)s %(message)s')
        handler.setFormatter(formatter)
        self.my_logger.addHandler(handler)
