import logging
import os
import re
from typing import Union

from config import ROOT_DIR

# Настройка логирования
log_dir = os.path.join(ROOT_DIR, "logs")
log_file = os.path.join(log_dir, "mask.log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger("mask")
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def get_mask_card_number(number: Union[str, int, list, dict, float, None]) -> str:
    """
    Принимает номер карты как строку (может содержать цифры, звёздочки, пробелы, дефисы).
    Возвращает **только последние 4 цифры** в виде строки, например: "5814".

    Если цифр меньше 4 — возвращает все доступные цифры (например, "719").
    Если цифр нет — возвращает пустую строку.

    Если входной аргумент не строка (включая None, int, list, dict, float) —
    возвращает пустую строку и логирует ошибку.

    Примеры:
        "1234567812345678" → "5678"
        "**** 5814" → "5814"
        "123" → "123"
        None → ""
        12345678 → ""
        [] → ""
    """
    # Обработка всех неверных типов: включая None, int, list, dict, float
    if not isinstance(number, str):
        logger.error(f"Неверный тип номера карты: {type(number)} — ожидается str, получено: {number}")
        return ""  # ← ВСЕГДА возвращаем пустую строку для неверных типов

    # Теперь number — точно str
    if number == "":
        logger.warning(f"В номере карты не найдено ни одной цифры: '{number}'")
        return ""

    # Извлекаем только цифры из строки
    digits = re.sub(r"\D", "", number)

    if not digits:
        logger.warning(f"В номере карты не найдено ни одной цифры: '{number}'")
        return ""

    # Возвращаем последние 1–4 цифры
    last_digits = digits[-4:]
    logger.info(f"Извлечены последние цифры: '{number}' → '{last_digits}'")
    return last_digits


# Пример работы функции (для тестирования)
# if __name__ == "__main__":
#     test_cases = [
#         "*7197",
#         "1234567812345678",
#         "**** 5814",
#         "1234-5678-9012-5814",
#         "7197",
#         "123",
#         "12",
#         "",
#         None,
#         "**** **** **** 1234",
#         "*123",
#         "abc",
#     ]
#
#     for test in test_cases:
#         result = get_mask_card_number(test)
#         print(f"'{test}' → '{result}'")
