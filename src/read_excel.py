from typing import List, Dict, Any

import pandas as pd

from config import FILE_PATH


# Читаем excel-файл
def read_operation_excel() -> List[Dict[str, Any]]:
    """
    Функция принимает путь к файлу формата excel и возвращает список словарей.
    """
    try:
        excel_data = pd.read_excel(FILE_PATH)
        return excel_data.to_dict(orient="records")
    except FileNotFoundError:
        print(f"Файл не найден: {FILE_PATH}")
        return []
    except Exception as e:
        print(f"Ошибка при чтении Excel файла: {e}")
        return []


# Проверка функции
# if __name__ == "__main__":
#     print("Запуск теста чтения Excel-файла...")
#     operations = read_operation_excel()
#     if operations:
#         print(f"Успешно прочитано {len(operations)} операций:")
#         for i, op in enumerate(operations[:3], 1):  # Показываем первые 3 записи
#             print(f"  {i}. {op}")
#         if len(operations) > 3:
#             print("... и ещё", len(operations) - 3, "записей")
#     else:
#         print("Не удалось прочитать операции. Проверьте файл и путь.")
