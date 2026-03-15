from typing import Dict, List

import pandas as pd

from config import FILE_PATH


# Читаем excel-файл
def read_operation_excel() -> List[Dict]:
    """Функция принимает путь к файлу формата excel и возвращает список словарей."""
    try:
        excel_data = pd.read_excel(FILE_PATH)
        return excel_data.to_dict(orient="records")
    except FileNotFoundError:
        print(f"Файл не найден: {FILE_PATH}")
        return []
    except Exception as e:
        print(f"Ошибка при чтении Excel файла: {e}")
        return []
