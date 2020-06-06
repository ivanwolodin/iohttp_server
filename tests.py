from multiprocessing import Process

import requests

from currency_handler import main

# start separate process
p = Process(target=main, args=(True,))
p.start()


def test_index_page():
    req = requests.get('http://127.0.0.1:8080/')
    assert req.status_code == 200


def test_usd_page():
    req = requests.get('http://127.0.0.1:8080/usd/get')
    assert req.status_code == 200


def test_eur_page():
    req = requests.get('http://127.0.0.1:8080/eur/get')
    assert req.status_code == 200


def test_set_money():
    req = requests.post('http://127.0.0.1:8080/amount/set',
                        json={"rub": 10, "eur": 30, "usd": 20})
    assert req.status_code == 200


def test_get_money_amount():
    req = requests.get('http://127.0.0.1:8080/amount/get')
    if req.status_code != 200:
        assert False

    data = req.json()
    rubbles = data.get('rub')
    dollars = data.get('usd')
    euros = data.get('eur')

    if rubbles != 10:
        assert False

    if euros != 30:
        assert False

    if dollars != 20:
        assert False

    assert True
