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

from abstract import AbstractCurrencyHandler


class CurrencyHandler(AbstractCurrencyHandler):
    def __init__(
            self,
            usd_value=None,
            euro_value=None,
            usd_amount=None,
            euro_amount=None,
            rubble_amount=None
    ):
        """ Without initialization values will be taken from Abstract class"""
        super().__init__()

        if usd_value is not None:
            self._value_by_currency['USD'] = usd_value

        if euro_value is not None:
            self._value_by_currency['EUR'] = euro_value

        if usd_amount is not None:
            self._total_amount['USD'] = usd_amount

        if euro_amount is not None:
            self._total_amount['EUR'] = euro_amount

        if rubble_amount is not None:
            self._total_amount['RUB'] = rubble_amount

    async def fetch_currency(self):
        """ В первом асинхронном потоке получает раз
            в N минут из любого удобного открытого источника
            (например, отсюда: https://www.cbr-xml-daily.ru/daily_json.js)
            данные о курсе доллара, рубля и евро (по умолчанию).

        """
        while True:
            async with ClientSession() as session:
                await asyncio.sleep(4)
                data = await self._fetch_from_information_server(session,
                                         'https://www.cbr-xml-daily.ru/daily_json.js')

                response_from_server = json.loads(data, strict=False)
                try:
                    usd_value = response_from_server['Valute']['USD']['Value']
                    eur_value = response_from_server['Valute']['EUR']['Value']
                except Exception:
                    print(Exception)
                else:
                    if usd_value != self._value_by_currency.get('USD'):
                        await self._spit_data_into_console(currency=usd_value)
                        self._value_by_currency['USD'] = usd_value

                    if eur_value != self._value_by_currency.get('EUR'):
                        await self._spit_data_into_console(currency=eur_value)
                        self._value_by_currency['EUR'] = eur_value

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

        async def get_usd_currency(request):
            return web.json_response(self._value_by_currency.get('USD'))

        async def get_euro_currency(request):
            return web.json_response(self._value_by_currency.get('EUR'))

        async def get_rub_currency(request):
            return web.json_response(self._value_by_currency.get('RUB'))

        async def get_total_money_amount(request):
            usd_value = self._value_by_currency.get('USD')
            euro_value = self._value_by_currency.get('EUR')
            euro_amount = self._total_amount['EUR']
            usd_amount = self._total_amount['USD']
            rubble_amount = self._total_amount['RUB']

            response = {
                'rub-usd': usd_value/1.0,
                'rub-eur': euro_value/1.0,
                'usd-eur': round(euro_value/usd_value, 2),

                'rub': rubble_amount,
                'usd': usd_amount,
                'eur': euro_amount,

                'sum': ' {} rub / {} usd / {} eur'.format(
                    # TODO: check it here
                    round(rubble_amount + usd_amount*usd_value + euro_amount*euro_value, 2),
                    round(rubble_amount/usd_value + usd_amount + euro_amount * (euro_value/usd_value), 2),
                    round(rubble_amount/euro_value + usd_amount * (euro_value/usd_value) + euro_amount, 2),
                )
            }
            return web.json_response(response,
                                     # headers={'content-type': 'plain/text'}
                                     )

        async def change_money_amount(request):
            """ Utterly change money amount
                    {"rub":100.5, "eur":10, "usd":20} ---> changes all currency amount
                    {"usd":10} ----> changes only USD amount, others currency remain as is

                WARNING: keys in coming json are lower case!

            """
            data = await request.json()
            self._total_amount['USD'] = data.get('usd', self._total_amount.get('USD'))
            self._total_amount['EUR'] = data.get('eur', self._total_amount.get('EUR'))
            self._total_amount['RUB'] = data.get('rub', self._total_amount.get('RUB'))

            return web.json_response({'result': True})

        async def modify_money_amount(request):
            """ Modifies money amount
                                {"rub":10, "eur":10, "usd":10} ---> add 10 to all items
                                {"usd": 15.6} ----> add 15.6 to USD amount
                                {"eur":10, "rub":-20}  ---> add 10 to eur amount, decrement RUB to a -20
                WARNING: keys in coming json are lower case!

            """
            data = await request.json()
            self._total_amount['USD'] += data.get('usd', 0)
            self._total_amount['EUR'] += data.get('eur', 0)
            self._total_amount['RUB'] += data.get('rub', 0)

            return web.json_response({'result': True})

        app = web.Application()
        # TODO: check if it is all really asyncronous
        app.add_routes(
            [
                web.get('/usd/get', get_usd_currency),
                web.get('/eur/get', get_euro_currency),
                web.get('/rub/get', get_rub_currency),
                web.get('/amount/get', get_total_money_amount),
                web.post('/amount/set', change_money_amount),
                web.post('/modify', modify_money_amount),
             ]
        )
        runner = web.AppRunner(app)
        return runner

    def run_server(self,
                   runner,
                   port):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(runner.setup())

        site = web.TCPSite(runner,
                           'localhost',
                           port)
        loop.run_until_complete(site.start())
        loop.run_forever()


def main():
    currency_handler_obj = CurrencyHandler(euro_value=150,
                                           usd_amount=10,
                                           rubble_amount=500)

    # отдельный поток для сервера
    t = threading.Thread(target=currency_handler_obj.run_server,
                         args=(currency_handler_obj.aiohttp_server(),
                               8080)
                         )
    # TODO: check if not fails here. If does - sys.exit(1)
    t.start()

    # поток для запросов курсов валют
    loop = asyncio.get_event_loop()
    loop.run_until_complete(currency_handler_obj.fetch_currency())


if __name__ == '__main__':
    main()
