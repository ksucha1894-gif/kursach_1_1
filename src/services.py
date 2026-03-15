import json
import logging
from typing import Dict, List

from src.mask import logger
from src.read_excel import read_operation_excel


def simple_search(query: str) -> str:
    """
    Функция сервиса «Простой поиск».
    Принимает строку-запрос и возвращает JSON-ответ со всеми транзакциями,
    содержащими запрос в описании или категории.
    """
    try:
        # Загружаем данные из Excel
        transactions = read_operation_excel()

        if not transactions:
            logger.warning("Файл с транзакциями пуст или не найден")
            return json.dumps({"transactions": []}, ensure_ascii=False)

        # Фильтруем транзакции по запросу
        filtered_transactions = [
            tx
            for tx in transactions
            if query.lower() in str(tx.get("Описание", "")).lower()
            or query.lower() in str(tx.get("Категория", "")).lower()
        ]

        # Логируем результат
        logger.info(f"Найдено {len(filtered_transactions)} транзакций по запросу '{query}'")

        # Возвращаем JSON-ответ
        return json.dumps({"transactions": filtered_transactions}, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка при выполнении поиска: {str(e)}")
        return json.dumps({"error": "Внутренняя ошибка сервера"}, ensure_ascii=False)


# Пример использования функции simple_search
if __name__ == "__main__":
    # Пример 1: Поиск по категории
    print("Пример 1: Поиск транзакций по категории 'Супермаркет'")
    result_products = simple_search("Супермаркет")
    print(result_products)
    print("\n" + "-" * 50 + "\n")

    # Пример 2: Поиск по описанию
    print("Пример 2: Поиск транзакций с описанием 'Каршеринг'")
    result_purchase = simple_search("Каршеринг")
    print(result_purchase)
    print("\n" + "-" * 50 + "\n")

    # Пример 3: Поиск по несуществующему запросу
    print("Пример 3: Поиск транзакций по несуществующему запросу 'Несуществующая категория'")
    result_empty = simple_search("Несуществующая категория")
    print(result_empty)
