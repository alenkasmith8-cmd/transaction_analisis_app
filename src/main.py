from src.config import file_path
from src.reports import spending_by_category
from src.services import get_transactions_ind
from src.utils import get_dict_transaction
from src.utils import reader_transaction_excel
from src.views import get_expenses_cards
from src.views import greeting_by_time_of_day
from src.views import top_transaction


def create_json_response(greeting, expenses_cards, top_transactions):
    return {"greeting": greeting, "cards": expenses_cards, "top_transactions": top_transactions}


def main() -> None:
    # 1. Получение текущего времени и приветствия
    greeting = greeting_by_time_of_day()
    print(greeting)  # Выводим приветствие

    # 2. Чтение транзакций из Excel
    try:
        transactions_df = reader_transaction_excel(str(file_path))
        print("Транзакции успешно загружены:")
        print(transactions_df.head())  # Вывод первых строк DataFrame
    except FileNotFoundError:
        print(f"Ошибка: файл {file_path} не найден.")
        return

    # 3. Преобразование DataFrame в словарь
    transactions_dict = get_dict_transaction(str(file_path))

    # 4. Генерация карт расходов
    expenses_cards = get_expenses_cards(transactions_df)

    # 5. Топ транзакции
    top_transactions = top_transaction(transactions_df)

    # 6. Формирование JSON-ответа
    json_response = create_json_response(greeting, expenses_cards, top_transactions)

    # 7. Вывод JSON-ответа
    print("JSON-ответ:")
    print(json_response)

    # 8. Остаток по счету (пример значения, вычисляемого на основе ваших данных)
    account_balance = 1000  # Здесь нужно получить реальную информацию о балансе
    print(f"У вас на счету: {account_balance} рублей.")

    # 9. Кешбэк (пример значения, вычисляемого по вашим критериям)
    cashback = 0  # Это значение должно быть вычислено на основе ваших данных
    print(f"Ваш кешбэк за месяц: {cashback} рублей.")

    # 10. Регистрация всех транзакций инд
    recent_transactions_json = get_transactions_ind(transactions_dict, "Физлицо")
    print("JSON со всеми транзакциями по физ. лицам:")
    print(recent_transactions_json)

    # 11. Пример: получение расходов по категории за последние 3 месяца
    category = "Продукты"  # Название категории, для которой вы хотите получить данные
    category_expenses = spending_by_category(transactions_df, category)
    print(f"Расходы по категории '{category}' за последние 3 месяца:")
    print(category_expenses)


if __name__ == "__main__":
    main()
