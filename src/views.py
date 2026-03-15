import json
from datetime import datetime

import pandas as pd

from src.utils import *


def get_financial_report(datetime_str: str) -> str:
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    hour = dt.hour
    if 5 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 18:
        greeting = "Добрый день"
    elif 18 <= hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    print(f"Greeting: {greeting}")  # Отладочный вывод для проверки

    # Пример фиктивного номера карты
    card_number = "1234567812345678"
    card_data = get_mask_card_number(card_number)

    # Получаем общую сумму расходов
    column_name = "Сумма платежа"
    calculate_expenses = calculate_total_expenses(column_name)

    # Преобразуем DataFrame в список словарей
    if isinstance(calculate_expenses, pd.DataFrame):
        calculate_expenses = calculate_expenses.to_dict(orient="records")

    # Получаем кешбэк
    calculate_cashback = calculate_cashback_100()

    # Преобразуем DataFrame в список словарей
    if isinstance(calculate_cashback, pd.DataFrame):
        calculate_cashback = calculate_cashback.to_dict(orient="records")

    # Получаем топ-5 транзакций
    top_transactions = transactions_operations()

    # Преобразуем DataFrame в список словарей
    if isinstance(top_transactions, pd.DataFrame):
        top_transactions = top_transactions.to_dict(orient="records")

    # Получаем курс валют
    currency_rates = get_currency_rates()

    # Получаем стоимость акций
    stock_prices = get_stock_prices()

    # Преобразуем DataFrame в список словарей
    if isinstance(stock_prices, pd.DataFrame):
        stock_prices = stock_prices.to_dict(orient="records")

    # Формируем JSON-ответ
    result = {
        "greeting": greeting,
        "cards": card_data,
        "expenses": calculate_expenses,
        "cashback": calculate_cashback,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    datetime_str = "2023-10-20 10:00:00"  # Пример даты и времени
    report = get_financial_report(datetime_str)
    print(report)
