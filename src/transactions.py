import pandas as pd
from src.read_excel import read_operation_excel
from src.mask import logger
from typing import List, Dict, Any


def transactions_operations():
    """
    Вычисляет и возвращает топ-5 транзакций по сумме платежа в формате:
    {
        "top_transactions": [
            {
                "date": "21.12.2021",
                "amount": 1198.23,
                "category": "Переводы",
                "description": "..."
            },
            ...
        ]
    }
    """
    logger.info("Запуск функции transactions_operations()")

    transactions_data = list(read_operation_excel())

    if not transactions_data:
        logger.warning("Данные из Excel отсутствуют")
        return {"top_transactions": []}

    try:
        df = pd.DataFrame(transactions_data)
        required_cols = {"Дата операции", "Сумма платежа", "Категория", "Описание"}
        missing = required_cols - set(df.columns)
        if missing:
            logger.error(f"Отсутствуют обязательные столбцы: {missing}")
            return {"top_transactions": []}

        # Преобразование суммы платежа в числовой формат
        df["Сумма платежа"] = pd.to_numeric(df["Сумма платежа"], errors="coerce")
        # Преобразование даты
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        df["Дата операции"] = df["Дата операции"].dt.strftime("%d.%m.%Y")

        # Фильтрация: убираем NaN и отрицательные/нулевые суммы
        df = df.dropna(subset=["Сумма платежа", "Дата операции"])
        df = df[df["Сумма платежа"] > 0]

        # Сортировка по сумме (по убыванию) и выбор топ-5
        df_sorted = df.sort_values(by="Сумма платежа", ascending=False)
        top_5 = df_sorted.head(5)

        # Формируем результат
        top_transactions = [
            {
                "date": str(row["Дата операции"]),
                "amount": float(row["Сумма платежа"]),
                "category": str(row["Категория"]) if pd.notna(row["Категория"]) else "",
                "description": str(row["Описание"]) if pd.notna(row["Описание"]) else "",
            }
            for _, row in top_5.iterrows()
        ]

        logger.info(f"Успешно обработано {len(top_transactions)} транзакций")
        return {"top_transactions": top_transactions}

    except Exception as e:
        logger.exception(f"Неожиданная ошибка в transactions_operations(): {e}")
        return {"top_transactions": []}


# Проверка функции
# if __name__ == "__main__":
#     result = transactions_operations()
#     import json
#
#     print(json.dumps(result, ensure_ascii=False, indent=2))
