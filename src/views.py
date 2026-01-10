import json
import logging
import os
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Union

import pandas as pd
import requests

from src.config import file_path
from src.config import load_user_currencies
from src.config import load_user_stocks
from src.utils import get_currency_rates
from src.utils import get_expenses_cards
from src.utils import get_stock_price
from src.utils import greeting_by_time_of_day
from src.utils import top_transaction

# Настройка логирования
log_directory = "../logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logger = logging.getLogger("logs")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    file_handler = logging.FileHandler(os.path.join(log_directory, "views.log"), encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


def form_main_page_info(some_param: Union[str, dict], return_json: bool = False) -> Union[str, Dict[str, Any]]:
    """Возвращает общую информацию о банковских транзакциях за период с начала месяца до указанной даты."""
    logger.info(f"Запуск функции main с параметром: {some_param}")

    currencies = load_user_currencies()
    stocks = load_user_stocks()
    date_obj = None

    # Обрабатываем входные параметры для даты
    if isinstance(some_param, str):
        try:
            date_obj = datetime.strptime(some_param, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            logger.error(f"Ошибка преобразования даты: {e}")
            return json.dumps({"error": "Некорректный формат даты."}, ensure_ascii=False)
    elif isinstance(some_param, dict) and 'date' in some_param:
        try:
            date_obj = datetime.strptime(some_param['date'], "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            logger.error(f"Ошибка преобразования даты: {e}")
            return json.dumps({"error": "Некорректный формат даты."}, ensure_ascii=False)
    else:
        return json.dumps({"error": "Некорректный тип параметра. Ожидается строка или JSON."}, ensure_ascii=False)

    # Чтение данных из Excel
    try:
        data = pd.read_excel(file_path)
        data_df = pd.DataFrame(data)
        logger.info(f"Исходный DataFrame: {data_df}")
        data_df["datetime"] = pd.to_datetime(
            data_df["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True, errors="coerce"
        )
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return json.dumps({"error": "Не удалось прочитать данные."}, ensure_ascii=False)

    # Фильтрация данных по датам
    start_date = date_obj.replace(day=1, hour=0, minute=0, second=0)
    fin_date = date_obj
    logger.debug(f"Диапазон дат: с {start_date} по {fin_date}")

    json_data = data_df[data_df["datetime"].between(start_date, fin_date)]
    logger.info(f"Количество транзакций за период: {len(json_data)}")

    greeting = greeting_by_time_of_day()

    agg_dict = {
        "greeting": greeting,
        "cards": get_expenses_cards(json_data) if not json_data.empty else [],
        "top_transactions": top_transaction(json_data) if not json_data.empty else [],
        "currency_rates": get_currency_rates(currencies),
        "stock_prices": get_stock_price(stocks),
    }
    logger.info(f"Filtered transactions: {json_data}")
    logger.info(f"Agg dict before serialization: {agg_dict}")

    if json_data.empty:
        logger.warning("Нет транзакций за указанный период.")
        agg_dict["error"] = "Нет транзакций за указанный период."

    return json.dumps(agg_dict, ensure_ascii=False, indent=2) if return_json else agg_dict


def generate_response(date_str: str) -> str:
    """Генерирует ответ с информацией о транзакциях за указанный день."""
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_of_month = date.replace(day=1)

    cards_data = [{"last_digits": "5814", "total_spent": 1262.00}, {"last_digits": "7512", "total_spent": 7.94}]

    for card in cards_data:
        card["cashback"] = card["total_spent"] / 100

    top_transactions = [
        {
            "date": "21.12.2021",
            "amount": 1198.23,
            "category": "Переводы",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR",
        },
        {"date": "20.12.2021", "amount": 829.00, "category": "Супермаркеты", "description": "Лента"},
    ]

    try:
        with open('user_settings.json', 'r', encoding='utf-8') as f:
            user_settings = json.load(f)
    except FileNotFoundError:
        logger.error("Файл настроек пользователя не найден.")
        return json.dumps({"error": "Не удалось загрузить настройки пользователя."}, ensure_ascii=False)

    currency_rates = get_currency_rates(user_settings["user_currencies"])
    stock_prices = get_stock_price(user_settings["user_stocks"])

    current_time = datetime.now()

    return json.dumps(
        {
            "greeting": greeting_by_time_of_day(),
            "cards": cards_data,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        },
        ensure_ascii=False,
        indent=4,
    )


if __name__ == "__main__":
    date_string = "2021-12-17 14:52:09"
    result_json = form_main_page_info(date_string, return_json=True)
    print(result_json)

    stocks = load_user_stocks()
    prices = []

    for stock in stocks:
        response = requests.get(f"https://api.example.com/stocks/{stock}")  # Замените на актуальный API
        if response.ok:
            data = response.json()
            prices.append({"stock": stock, "price": data.get("price", "N/A")})  # Обработка отсутствующей цены
        else:
            logger.warning(f"Не удалось получить данные для акции {stock}: {response.status_code}")

    print(prices)
