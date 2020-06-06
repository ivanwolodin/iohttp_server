import logging

from logging.handlers import TimedRotatingFileHandler


class Logger:
    FORMATTER = logging.Formatter(
        '%(asctime)s — %(name)s — %(levelname)s — %(message)s')
    LOG_FILE = 'currency_handler.log'

    def __init__(self):
        self.logger = None

    @staticmethod
    def _get_file_handler():
        file_handler = TimedRotatingFileHandler(Logger.LOG_FILE,
                                                when='midnight')

        file_handler.setFormatter(Logger.FORMATTER)
        return file_handler

    def change_logger_level(self, logger_level):
        """ Currently it supports only DEBUG mode and INFO mode.

            INFO is default mode

        """
        if logger_level == 'debug':
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    # @staticmethod
    # def get_logging_level():
    #     return logging.getLogger().getEffectiveLevel()

    def get_logger(self,
                   logger_name='currency_handler.log',
                   logger_level='info'):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        self.logger.addHandler(Logger._get_file_handler())

        # with this pattern, it's rarely necessary to propagate the error up to
        # parent
        self.logger.propagate = False
        return self.logger
