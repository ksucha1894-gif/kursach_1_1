import json
from datetime import datetime

from src.utils import get_cards_summary, transactions_operations, get_currency_rates, get_stock_prices


def get_financial_report(datetime_str: str) -> str:
    """
    Главная функция, принимающая дату в формате YYYY-MM-DD HH:MM:SS
    и возвращающая JSON-ответ по ТЗ.
    """
    if datetime_str:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    else:
        dt = datetime.now()

    # Определяем приветствие
    hour = dt.hour
    if 5 <= hour < 11:
        greeting = "Доброе утро"
    elif 11 <= hour < 16:
        greeting = "Добрый день"
    elif 16 <= hour < 20:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    # 1. Получаем данные по картам
    cards_data = get_cards_summary(datetime_str)
    cards = []
    for card in cards_data.get("cards", []):
        try:
            last_digits = str(card.get("last_digits", ""))[-4:] if card.get("last_digits") else ""
            total_spent = float(card.get("total_spent", 0))
            cashback = float(total_spent // 100)  # 1 рубль на каждые 100 рублей
            if last_digits:  # Только валидные карты
                cards.append(
                    {"last_digits": last_digits, "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)}
                )
        except (ValueError, TypeError):
            continue

    # 2. Получаем топ-транзакции (все) и фильтруем по дате
    transactions_data = transactions_operations()
    top_transactions = []
    start_of_month = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    for tx in transactions_data.get("top_transactions", []):
        try:
            tx_date = datetime.strptime(tx["date"], "%d.%m.%Y")  # Формат: DD.MM.YYYY
            if start_of_month <= tx_date <= dt:  # Только в нужном диапазоне
                top_transactions.append(
                    {
                        "date": tx["date"],
                        "amount": float(tx["amount"]),
                        "category": tx.get("category", ""),
                        "description": tx.get("description", ""),
                    }
                )
        except (ValueError, TypeError, KeyError):
            continue  # Пропускаем битые записи

    # Сортируем по абсолютному значению суммы
    top_transactions.sort(key=lambda x: abs(x["amount"]), reverse=True)
    top_transactions = top_transactions[:5]  # Топ-5

    # 3. Курсы валют
    currency_rates_raw = get_currency_rates()
    currency_rates = []
    for cur in currency_rates_raw:
        try:
            currency = cur.get("currency", "").upper()
            rate = float(cur.get("rate", 0))
            if currency in ("USD", "EUR"):
                currency_rates.append({"currency": currency, "rate": round(rate, 2)})
        except (ValueError, TypeError):
            continue

    # 4. Акции S&P500 — фиксированный набор (если virtual=True)
    stock_prices_raw = get_stock_prices(virtual=True)
    stock_prices = []
    for stock in stock_prices_raw:
        try:
            stock_prices.append(
                {"stock": str(stock.get("stock", "")), "price": round(float(stock.get("price", 0)), 2)}
            )
        except (ValueError, TypeError):
            continue

    # Если акций меньше 5 — заполняем дефолтными
    if len(stock_prices) < 5:
        default_stocks = [
            {"stock": "AAPL", "price": 150.12},
            {"stock": "AMZN", "price": 3173.18},
            {"stock": "GOOGL", "price": 2742.39},
            {"stock": "MSFT", "price": 296.71},
            {"stock": "TSLA", "price": 1007.08},
        ]
        stock_prices = default_stocks[:5]

    # Формируем итоговый ответ
    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(result, ensure_ascii=False, indent=4)
