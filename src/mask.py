import logging
import os
import re

from config import ROOT_DIR

# Определяем абсолютный путь к файлу
log_dir = os.path.join(ROOT_DIR, "logs")
log_file = os.path.join(log_dir, "mask.log")

# Создаем папку для логов, если она не существует
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логирования
logger = logging.getLogger("mask")
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


# Создаем функцию маски для карт
def get_mask_card_number(number: str) -> str:
    """
    Функция принимает число - номер карты.
    Маска преобразует число в формат XXXX XX** **** XXXX.
    Если в номере есть недопустимые символы, логирует ошибку.
    """
    if number is None:  # Проверяем на None
        logger.error("Введены недопустимые символы в номере карты")
        return ""

    if re.fullmatch(r"\d+", number):  # Проверяем, что введены только цифры
        masked_number = f" ****  **** **** {number[-4:]}"
        print("Логирование начинается")
        logger.info("Маскировка номера банковской карты")
        return masked_number
    if not number:
        return " **** "
    else:
        logger.error("Введены недопустимые символы в номере карты")
        return ""


if __name__ == "__main__":
    test_number = "1234567812345678"
    masked = get_mask_card_number(test_number)
    print(masked)
