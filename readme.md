# Currency Exchange Service

A lightweight asynchronous microservice for tracking currency exchange rates and managing balances in multiple currencies.

The application is built with Python 3.7, `asyncio`, and `httpio`. It uses multiple threads to handle currency rate updates and incoming HTTP requests concurrently.

## Features

- Asynchronous exchange rate updates from a remote data provider.
- REST API for managing currency balances.
- Support for RUB, USD, and EUR.
- Automatic balance conversion using current exchange rates.
- Configurable update intervals.
- Logging and optional debug output.
- Integration tests using pytest.

## REST API

The HTTP server listens on port `8080`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/usd/get` | Get the current USD balance. |
| GET | `/rub/get` | Get the current RUB balance. |
| GET | `/eur/get` | Get the current EUR balance. |
| POST | `/amount/set` | Set currency balances. |
| POST | `/modify` | Increase or decrease existing balances. |
| GET | `/amount/get` | Get all balances, exchange rates, and total amounts. |
| GET | `/reverse_console_output_status` | Toggle console debug output. |

### Examples

Set currency balances:

```json
{
  "usd": 10,
  "rub": 100.5,
  "eur": 20
}
```

Modify existing balances:

```json
{
  "usd": 5,
  "eur": 10
}
```

Get all balances and exchange rates:

```http
GET /amount/get
```

Example response:

```json
{
  "rub-usd": 68.6319,
  "rub-eur": 77.9658,
  "usd-eur": 1.14,
  "rub": 0,
  "usd": 0,
  "eur": 0,
  "sum": "0.0 rub / 0.0 usd / 0.0 eur"
}
```

Successful operations return:

```json
{
  "result": true
}
```

## Project Structure

```text
.
├── abstract.py
├── currency_handler.py
├── logger.py
├── readme.md
├── requirements.txt
└── tests.py
```

- `abstract.py` — abstract base class defining common application functionality.
- `currency_handler.py` — main application logic and HTTP server.
- `logger.py` — logging configuration and utilities.
- `tests.py` — integration tests.

## Getting Started

### Requirements

- Python 3.7
- pip

### Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

Start the service with default settings:

```bash
python currency_handler.py
```

The HTTP server listens on port `8080`. By default, all currency balances are initialized to zero, and exchange rates are updated every 5 seconds.

### Command-Line Arguments

| Argument | Description | Default |
|---|---|---|
| `--eur` | Initial EUR balance | `0` |
| `--rub` | Initial RUB balance | `0` |
| `--usd` | Initial USD balance | `0` |
| `--period` | Exchange rate update interval (seconds) | `5` |
| `--debug` | Enable debug output | `False` |

Examples:

```bash
python currency_handler.py --eur 10 --usd 5 --rub 100 --period 5 --debug true
```

```bash
python currency_handler.py --eur 10 --debug true
```

## Testing

Run integration tests using pytest:

```bash
pytest -v tests.py
```

## Logging

The application uses Python's standard `logging` module.

Application events and exchange rate updates are recorded in `currency_handler.log`.

Debug mode additionally enables console output for incoming requests and exchange rate updates.

