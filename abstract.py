import asyncio
import requests

from abc import ABCMeta, abstractmethod

from logger import Logger

LOCALHOST = 'http://127.0.0.1'


class AbstractCurrencyHandler(object,
                              metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        # default values
        self._value_by_currency = {
            'USD': 68,
            'EUR': 78,
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

        self.console_output = False

    def change_port(self, port):
        self.port = port

    # def change_url(self, url):
    #     self.url = url

    # def get_logger_level(self):
    #     return self._logger_obj.get_logging_level()

    def change_logger_level(self, logger_level):
        self._logger_obj.change_logger_level(logger_level)

    def _log_events(self, msg):
        if self.console_output:
            return
        self.logger.info(msg=msg)

    def _console_output(self,
                        data=None,
                        API=''):
        if not self.console_output:
            return
        if API:
            print('API={}'.format(API), data)
        else:
            print(data)

    async def _hook_currency_values_changed(self, currency):
        await asyncio.sleep(60)

        response = ''
        if currency['what_changed']['USD']:
            response += 'USD has changed to {}'.format(currency['USD_value'])
            response += ' '
        if currency['what_changed']['EUR']:
            response += 'EUR has changed to {}'.format(currency['EUR_value'])
        print(response)
        self.logger.info(response)

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
            return False

        if req.status_code == 200:
            self.logger.debug('Server has been starter. '
                              'Url={}. '
                              'Port={}'.format(LOCALHOST,
                                               self.port))
            self.logger.debug('Initial amount: {}'.format(self._total_amount))
            self.logger.info('Server Started')
            return True
        else:
            self.logger.critical('Server is not Started')
            return False
