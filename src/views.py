import json
from datetime import datetime, timedelta
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Функция для получения текущего времени и задания приветствия
def get_greeting(current_time):
    if current_time.hour < 6:
        return "Доброй ночи"
    elif current_time.hour < 12:
        return "Доброе утро"
    elif current_time.hour < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"


# Функция для получения данных о курсах валют
def get_currency_rates(currencies):
    rates = []

    for currency in currencies:
        response = requests.get(f"https://api.apilayer.com/exchangerates_data/live?base=USD&symbols=EUR,GBP")
        data = response.json()
        rates.append({"currency": currency, "rate": data["rates"][currency]})

    return rates


# Функция для получения цен акций
def get_stock_prices(stocks):
    prices = []

    for stock in stocks:
        response = requests.get(f"https://api.example.com/stocks/{stock}")  # Замените на актуальный API
        data = response.json()
        prices.append({"stock": stock, "price": data["price"]})

    return prices


# Главная функция для обработки входящей даты и генерации ответа
def generate_response(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_of_month = date.replace(day=1)

    # Предположим, что данные о картах и транзакциях поступают из базы данных
    cards_data = [
        {"last_digits": "5814", "total_spent": 1262.00},
        {"last_digits": "7512", "total_spent": 7.94}
    ]

    # Считаем кэшбэк
    for card in cards_data:
        card["cashback"] = card["total_spent"] / 100

    top_transactions = [
        {"date": "21.12.2021", "amount": 1198.23, "category": "Переводы",
         "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
        {"date": "20.12.2021", "amount": 829.00, "category": "Супермаркеты", "description": "Лента"},
        {"date": "20.12.2021", "amount": 421.00, "category": "Различные товары", "description": "Ozon.ru"},
        {"date": "16.12.2021", "amount": -14216.42, "category": "ЖКХ", "description": "ЖКУ Квартира"},
        {"date": "16.12.2021", "amount": 453.00, "category": "Бонусы", "description": "Кешбэк за обычные покупки"},
    ]

    # Получаем пользовательские настройки
    with open('user_settings.json', 'r', encoding='utf-8') as f:
        user_settings = json.load(f)

    # Получаем курсы валют и цены акций
    currency_rates = get_currency_rates(user_settings["user_currencies"])
    stock_prices = get_stock_prices(user_settings["user_stocks"])

    current_time = datetime.now()

    return json.dumps({
        "greeting": get_greeting(current_time),
        "cards": cards_data,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }, ensure_ascii=False, indent=4)


# Пример использования функции
if __name__ == "__main__":
    date_string = "2020-05-20 15:30:00"
    response = generate_response(date_string)
    print(response)
