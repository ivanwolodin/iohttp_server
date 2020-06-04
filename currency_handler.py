"""
Приложение должно быть реализовано в виде модуля с абстрактным классом
и второго модуля, импортирующего этот класс.
При инициализации должна быть возможность передать наименования валют.

Библиотеки, рекомендуемые к использованию:
asyncio, aiohttp, argparse, logging, json, requests

"""
import asyncio
import json
import threading

from aiohttp import web, ClientSession
from random import randint

from abstract import AbstractCurrencyHandler


class CurrencyHandler(AbstractCurrencyHandler):
    def __init__(self):
        self.common_dict = {
            'USD': 60,
            'EUR': 70,
            'RUB': 1,
        }

    @staticmethod
    async def spit_data_into_console(currency=None,
                                     total_amount=None):
        """
        В этом асинхронном(?) потоке раз в минуту выводить в консоль те же данные,
        что в ф-ии handle_request(), в случае, если изменился курс к.-либо валюты
        или количество средств относительно предыдущего вывода в консоль.

        """
        await asyncio.sleep(60)
        if currency is not None:
            print('Value of {} has changed'.format(currency))
        if total_amount is not None:
            print('Total amount has changed to {}'.format(total_amount))

    async def _fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def fetch_currency(self):
        """ В первом асинхронном потоке получает раз
            в N минут из любого удобного открытого источника
         (например, отсюда: https://www.cbr-xml-daily.ru/daily_json.js)
          данные о курсе доллара, рубля и евро (по умолчанию).

        """
        while True:
            async with ClientSession() as session:
                await asyncio.sleep(4)
                data = await self._fetch(session,
                                   'https://www.cbr-xml-daily.ru/daily_json.js')

                response_from_server = json.loads(data, strict=False)
                try:
                    usd_value = response_from_server['Valute']['USD']['Value']
                    eur_value = response_from_server['Valute']['EUR']['Value']
                except Exception:
                    print(Exception)
                else:
                    if usd_value != self.common_dict.get('USD'):
                        await CurrencyHandler.spit_data_into_console(currency=usd_value)
                        print('Value of {} has changed!'.format(usd_value))
                        self.common_dict['USD'] = usd_value

                    if eur_value != self.common_dict.get('EUR'):
                        await CurrencyHandler.spit_data_into_console(currency=eur_value)
                        # await spit_data_into_console(currency=eur_value)
                        # print('Value of {} has changed!'.format(eur_value))
                        self.common_dict['EUR'] = eur_value

    def aiohttp_server(self):
        """ Во втором асинхронном потоке сервер отвечает на HTTP запросы на порту 8080.
            Необходимо реализовать REST api,
            отвечающее на запросы следующего вида
            (тип запроса, url, payload //комментарий):
                * GET /usd/get
                * GET /rub/get
                * GET /eur/get
                * GET /amount/get

                * POST /amount/set {"usd":10}
                * POST /amount/set {"rub":100.5, "eur":10, "usd":20}
                * POST /modify {"usd":5} // добавить к текущему количеству usd 5
                * POST /modify {"eur":10, "rub":-20} // добавить к текущему количеству eur 10,
                                                        уменьшить текущее количество rub на 20

        """

        def get_usd_currency(request):
            self.common_dict['USD'] = randint(1, 10)
            return web.Response(text=str(self.common_dict['USD']))

        def get_euro_currency(request):
            return web.Response(text=str(self.common_dict['EUR']))

        def get_rub_currency(request):
            return web.Response(text=str(self.common_dict['RUB']))

        app = web.Application()
        app.add_routes(
            [web.get('/usd/get', get_usd_currency),
             web.get('/eur/get', get_euro_currency),
             web.get('/rub/get', get_rub_currency),
             ]
        )
        runner = web.AppRunner(app)
        return runner

    def run_server(self, runner):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(runner.setup())

        site = web.TCPSite(runner, 'localhost', 8080)
        loop.run_until_complete(site.start())

        loop.run_forever()


def main():
    currency_handler_obj = CurrencyHandler()

    # отдельный поток для сервера
    t = threading.Thread(target=currency_handler_obj.run_server,
                         args=(currency_handler_obj.aiohttp_server(),))
    t.start()

    # поток для запросов курсов валют
    loop = asyncio.get_event_loop()
    loop.run_until_complete(currency_handler_obj.fetch_currency())


if __name__ == '__main__':
    main()
