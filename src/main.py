import json
from datetime import datetime
from pprint import pprint

import pandas as pd

from src.mask import logger
from src.read_excel import read_operation_excel
from src.reports import spending_by_category
from src.services import simple_search
from src.views import get_financial_report


def main(datetime_str: str) -> str:
    """Основная функция программы"""
    logger.info("Финансовая аналитика запущена")
    print("Финансовая аналитика запущена")

    try:
        # 1. Получение финансового отчета
        print("\n1. Формирование финансового отчета...")
        # datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        financial_report = get_financial_report(datetime_str)
        report_data = json.loads(financial_report)
        print("Отчет сформирован")
        pprint(report_data)

        # 2. Простой поиск транзакций
        print("\n2. Выполнение простого поиска...")
        query = "Супермаркет"
        search_result = simple_search(query)
        search_data = json.loads(search_result)
        print(f"Найдено {len(search_data.get('transactions', []))} транзакций по запросу '{query}'")

        # 3. Генерация отчета по категории
        print("\n3. Генерация отчета по категории...")
        transactions_data = read_operation_excel()
        transactions_df = pd.DataFrame(transactions_data)

        if not transactions_df.empty:
            category = "Супермаркет"
            report = spending_by_category(transactions_df, category)
            print(f"Отчет по категории '{category}' сформирован ({len(report)} записей)")
        else:
            print("Нет данных для формирования отчета по категориям")

        logger.info("Программа завершила работу успешно")
        print("\nРабота программы завершена успешно")

    except Exception as e:
        logger.error(f"Ошибка в основном потоке: {str(e)}")
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    main("2021-12-31 23:59:59")
