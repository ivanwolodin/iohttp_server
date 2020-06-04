import asyncio
from abc import ABCMeta, abstractmethod


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

    @staticmethod
    async def _spit_data_into_console(currency=None,
                                      total_amount=None):
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
