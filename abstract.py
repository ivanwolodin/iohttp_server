import asyncio
import requests
import sys

from abc import ABCMeta, abstractmethod

from logger import Logger

LOCALHOST = 'http://127.0.0.1'


class AbstractCurrencyHandler(object,
                              metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        # default value
        self._value_by_currency = {
            'USD': 60,
            'EUR': 70,
            'RUB': 1,
        }
        self._total_amount = {
            'USD': 0,
            'EUR': 0,
            'RUB': 0,
        }
        # self.url = 'localhost'
        self.port = 8080

        # TODO: make it cleaner
        self._logger_obj = Logger()
        self.logger = self._logger_obj.get_logger()

    def change_port(self, port):
        self.port = port

    # def change_url(self, url):
    #     self.url = url

    def change_logger_level(self, logger_level):
        self._logger_obj.change_logger_level(logger_level)

    @staticmethod
    async def _spit_data_into_console(currency=None,
                                      total_amount=None):

        # update console if smth change once in a minute
        await asyncio.sleep(60)

        if currency is not None:
            print('Value of {} has changed'.format(currency))
        if total_amount is not None:
            print('Total amount has changed to {}'.format(total_amount))

    @staticmethod
    async def _fetch_from_information_server(session, url):
        async with session.get(url) as response:
            return await response.text()

    @staticmethod
    def run_server(**kwargs):
        raise NotImplementedError('function run_server() '
                                  'must be implemented')

    @staticmethod
    def fetch_currency(**kwargs):
        raise NotImplementedError('function fetch_currency() '
                                  'must be implemented')

    def check_server(self):
        """ TODO: Turn this ugly check for a good one """
        try:
            req = requests.get(url='{}:{}/'.format(LOCALHOST,
                                                   self.port))
        except Exception as e:
            self.logger.critical(
                'Cannot request {}:{}. Error: {}'.format(LOCALHOST,
                                                         self.port,
                                                         e))
            sys.exit(1)

        if req.status_code == 200:
            self.logger.debug('Server has been starter. '
                              'Url={}. '
                              'Port={}'.format(LOCALHOST,
                                               self.port))
            self.logger.debug('Initial amount: {}'.format(self._total_amount))
            self.logger.info('Server Started')
        else:
            self.logger.critical('Server is not Started')
            sys.exit(1)
