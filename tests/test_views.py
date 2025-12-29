import json
import pytest
from unittest.mock import patch
from views import generate_response, get_greeting, get_currency_rates, get_stock_prices


# Тестирование получения приветствия
def test_get_greeting():
    assert get_greeting(datetime(2023, 10, 1, 5, 30)) == "Доброй ночи"
    assert get_greeting(datetime(2023, 10, 1, 10, 30)) == "Доброе утро"
    assert get_greeting(datetime(2023, 10, 1, 14, 30)) == "Добрый день"
    assert get_greeting(datetime(2023, 10, 1, 19, 30)) == "Добрый вечер"


# Тестирование функции получения валютных курсов
@patch('views.requests.get')
def test_get_currency_rates(mock_get):
    mock_get.return_value.json.return_value = {
        "rates": {
            "USD": 1.0,
            "EUR": 0.85
        }
    }

    currencies = ["USD", "EUR"]
    expected_output = [
        {"currency": "USD", "rate": 1.0},
        {"currency": "EUR", "rate": 0.85}
    ]

    result = get_currency_rates(currencies)

    assert result == expected_output
    mock_get.assert_called_once()


# Тестирование функции получения цен акций
@patch('views.requests.get')
def test_get_stock_prices(mock_get):
    mock_get.return_value.json.return_value = {
        "price": 150.12
    }

    stocks = ["AAPL"]
    expected_output = [{"stock": "AAPL", "price": 150.12}]

    result = get_stock_prices(stocks)

    assert result == expected_output
    mock_get.assert_called_once()


# Тестирование главной функции generate_response
@patch('views.get_currency_rates')
@patch('views.get_stock_prices')
@patch('builtins.open', new_callable=pytest.mock.mock_open,
       read_data='{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}')
def test_generate_response(mock_open, mock_get_stock_prices, mock_get_currency_rates):
    mock_get_currency_rates.return_value = [
        {"currency": "USD", "rate": 73.21},
        {"currency": "EUR", "rate": 87.08}
    ]
    mock_get_stock_prices.return_value = [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18}
    ]

    date_string = "2020-05-20 15:30:00"
    response = json.loads(generate_response(date_string))

    assert response["greeting"] == "Добрый день"  # Время теста около 15:30
    assert len(response["cards"]) == 2  # У нас 2 карты в примере
    assert len(response["currency_rates"]) == 2  # У нас 2 валюты в настройках
    assert len(response["stock_prices"]) == 2  # У нас 2 акции в настройках


# Запуск тестов
if __name__ == "__main__":
    pytest.main()
