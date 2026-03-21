import json
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from src.mask import get_mask_card_number
from src.read_excel import read_operation_excel


def get_cards_summary(date_str: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Возвращает сумму трат и кэшбэк по каждой карте за период с начала месяца до указанной даты.
    Формат даты: "YYYY-MM-DD HH:MM:SS"
    Возвращает:
    {
        "cards": [
            {
                "last_digits": "5814",
                "total_spent": 1262.00,
                "cashback": 12.62
            }
        ]
    }
    """
    try:
        end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return {"cards": []}

    start_of_month = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    records = read_operation_excel()
    if not records:
        return {"cards": []}

    df = pd.DataFrame(records)
    required_cols = {"Дата операции", "Сумма платежа", "Номер карты"}
    if not required_cols.issubset(df.columns):
        return {"cards": []}

    # Парсинг даты: ожидаем DD.MM.YYYY HH:MM:SS
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["Дата операции"])

    # Приведение суммы к числу
    df["Сумма платежа"] = pd.to_numeric(df["Сумма платежа"], errors="coerce")
    df = df.dropna(subset=["Сумма платежа"])

    # Фильтруем только положительные суммы как расходы
    df = df[df["Сумма платежа"] > 0]

    # Фильтруем по дате
    df_filtered = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= end_date)]

    if df_filtered.empty:
        return {"cards": []}

    cards_summary = []
    for card_number, group in df_filtered.groupby("Номер карты"):
        if not isinstance(card_number, str) or not card_number.strip():
            continue

        last_digits = get_mask_card_number(card_number.strip())
        if not last_digits:
            continue

        total_spent = group["Сумма платежа"].sum()
        total_spent = round(float(total_spent), 2)
        cashback = round(total_spent * 0.01, 2)

        cards_summary.append({"last_digits": last_digits, "total_spent": total_spent, "cashback": cashback})

    # Сортировка по last_digits для стабильности тестов
    cards_summary.sort(key=lambda x: x["last_digits"])

    return {"cards": cards_summary}


# Пример использования
# if __name__ == "__main__":
#     test_date = "2021-12-31 23:59:59"
#     result = get_cards_summary(test_date)

# print(json.dumps(result, ensure_ascii=False, indent=2))
