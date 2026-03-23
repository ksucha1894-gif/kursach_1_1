import os
from datetime import datetime, timedelta
from functools import wraps
from typing import List, Dict, Any, Optional

import pandas as pd

from src.mask import logger
from src.read_excel import read_operation_excel

# Путь к директории для отчетов
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)


# Декоратор для записи результата в файл
def report_to_file(filename: Optional[str] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Декоратор {func.__name__} начал работу")

            result = func(*args, **kwargs)

            # Определяем имя файла
            if filename:
                report_name = filename if filename.endswith(".txt") else f"{filename}.txt"
            else:
                report_name = f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            report_path = os.path.join(REPORTS_DIR, report_name)

            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    if isinstance(result, pd.DataFrame):
                        f.write(result.to_string(index=False))
                    else:
                        f.write(str(result))
                logger.info(f"Отчет успешно записан в файл: {report_path}")
            except Exception as e:
                logger.error(f"Ошибка при записи файла {report_path}: {str(e)}")
                raise

            return result

        return wrapper

    return decorator


# Функция отчета: траты по категории за последние 3 месяца
@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    """
    logger.info(f"Начинаем обработку отчета по категории '{category}'")

    if transactions.empty:
        logger.warning("DataFrame с транзакциями пуст")
        return pd.DataFrame()

    # Приводим 'Дата операции' к datetime
    transactions_copy = transactions.copy()
    transactions_copy["Дата операции"] = pd.to_datetime(
        transactions_copy["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    # Пробуем альтернативный формат даты
    if transactions_copy["Дата операции"].isna().any():
        transactions_copy["Дата операции"] = pd.to_datetime(
            transactions_copy["Дата операции"], format="%d.%m.%Y", errors="coerce"
        )

    # Определяем целевую дату
    if date is None:
        target_date = datetime.now()
    else:
        formats = ["%d.%m.%Y %H:%M:%S", "%d.%m.%Y"]
        target_date = None
        for fmt in formats:
            try:
                target_date = datetime.strptime(date, fmt)
                break
            except ValueError:
                continue
        if target_date is None:
            error_msg = f"Некорректный формат даты: {date}. Ожидается ДД.ММ.ГГГГ или ДД.ММ.ГГГГ ЧЧ:ММ:СС"
            logger.error(error_msg)
            raise ValueError(error_msg)

    start_date = target_date - timedelta(days=90)
    logger.info(f"Период отчета: с {start_date} по {target_date}")

    # Фильтруем транзакции
    filtered = transactions_copy[
        (transactions_copy["Категория"] == category)
        & (transactions_copy["Сумма платежа"] < 0)
        & (transactions_copy["Дата операции"] >= start_date)
        & (transactions_copy["Дата операции"] <= target_date)
    ].copy()

    logger.info(f"Найдено {len(filtered)} транзакций для категории '{category}'")

    if filtered.empty:
        logger.info(f"Нет расходов для категории '{category}' в указанном диапазоне дат")
        return filtered

    # Сортировка и возвращение результата
    filtered = filtered.sort_values(by="Дата операции", ascending=False)
    return filtered.head(5)


# Пример использования
# if __name__ == "__main__":
#     # Загружаем транзакции
#     transactions_data = read_operation_excel()
#     transactions_df = pd.DataFrame(transactions_data)
#
#     try:
#         # Пример 1: Отчет по категории "Супермаркет" за последние 3 месяца
#         products_report = spending_by_category(transactions_df, "Супермаркет")
#         print("Отчет по супермаркетам успешно создан")
#
#         # Пример 2: Отчет по категории "Каршеринг" на конкретную дату
#         transport_report = spending_by_category(transactions_df, "Каршеринг", "26.12.2021")
#         print("Отчет по каршерингу успешно создан")
#
#         # Пример 3: Отчет с несуществующей категорией
#         empty_report = spending_by_category(transactions_df, "Несуществующая категория")
#         print("Отчет по несуществующей категории создан")
#
#     except Exception as e:
#         logger.error(f"Ошибка при создании отчета: {str(e)}")
#         print(f"Произошла ошибка: {str(e)}")
