import asyncio
import json
import threading

from aiohttp import web, ClientSession
from random import randint


common_dict = {
    'USD': 60,
    'EUR': 70,
    'RUB': 1,
}

N = 3  # variable from args


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


##########################################################################
# ############                GETTING CURRENCY
##########################################################################
# Thread number one


async def fetch_currency():
    """ В первом асинхронном потоке получает раз
        в N минут из любого удобного открытого источника
     (например, отсюда: https://www.cbr-xml-daily.ru/daily_json.js)
      данные о курсе доллара, рубля и евро (по умолчанию).

    """
    while True:
        async with ClientSession() as session:
            await asyncio.sleep(N)
            data = await fetch(session,
                               'https://www.cbr-xml-daily.ru/daily_json.js')

            resonse_from_server = json.loads(data, strict=False)
            try:
                usd_value = resonse_from_server['Valute']['USD']['Value']
                eur_value = resonse_from_server['Valute']['EUR']['Value']
            except Exception:
                print(Exception)
            else:
                if usd_value != common_dict.get('USD'):
                    # print('Value of {} has changed!'.format(usd_value))
                    common_dict['USD'] = usd_value
                if eur_value != common_dict.get('EUR'):
                    # print('Value of {} has changed!'.format(eur_value))
                    common_dict['EUR'] = eur_value


##########################################################################
# ############                SERVER IN THREAD
##########################################################################
# THREAD NUMBER TWO
def aiohttp_server():
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
        common_dict['USD'] = randint(1, 10)
        return web.Response(text=str(common_dict['USD']))

    def get_euro_currency(request):
        return web.Response(text=str(common_dict['EUR']))

    def get_rub_currency(request):
        return web.Response(text=str(common_dict['RUB']))

    app = web.Application()
    app.add_routes(
        [web.get('/usd/get', get_usd_currency),
         web.get('/eur/get', get_euro_currency),
         web.get('/rub/get', get_rub_currency),
         ]
    )
    runner = web.AppRunner(app)
    return runner


def run_server(runner):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(runner.setup())

    site = web.TCPSite(runner, 'localhost', 8080)
    loop.run_until_complete(site.start())

    loop.run_forever()


# Thread number three
async def spit_data_into_console(currency=None,
                                 total_amount=None
                                 ):
    """
    В этом асинхронном потоке раз в минуту выводить в консоль те же данные,
    что в ф-ии handle_request(), в случае, если изменился курс к.-либо валюты
    или количество средств относительно предыдущего вывода в консоль.

    """
    if currency is not None:
        print('Value of {} has changed'.format(currency))
    if total_amount is not None:
        print('Total amount has changed to {}'.format(total_amount))


def main():
    # отдельный поток для сервера
    t = threading.Thread(target=run_server, args=(aiohttp_server(),))
    t.start()

    # поток для запросов курсов валют
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_currency())


if __name__ == '__main__':
    main()
