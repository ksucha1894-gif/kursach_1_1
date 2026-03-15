import logging
import os
import shutil
from unittest.mock import MagicMock, patch

import pytest

from src.mask import get_mask_card_number, log_dir, logger


# Фикстуры
@pytest.fixture
def setup_logs(tmp_path):
    """Фикстура для настройки тестовой среды с логированием"""
    # Сохраняем оригинальные пути
    original_log_dir = log_dir
    original_handlers = logger.handlers.copy()

    # Настраиваем тестовую директорию
    test_log_dir = tmp_path / "logs"
    os.makedirs(test_log_dir, exist_ok=True)

    # Перенастраиваем логгер
    test_log_file = test_log_dir / "mask.log"
    new_handler = logging.FileHandler(test_log_file)
    new_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.handlers.clear()
    logger.addHandler(new_handler)

    yield test_log_dir  # Передаем тестовую директорию в тест

    # Восстанавливаем оригинальные настройки
    logger.handlers.clear()
    logger.handlers.extend(original_handlers)


@pytest.fixture
def mock_logger():
    """Фикстура для мока логгера"""
    with patch("src.mask.logger") as mock:
        yield mock


# Параметризованные тесты
@pytest.mark.parametrize(
    "input_number,expected_output",
    [
        ("1234567812345678", " ****  **** **** 5678"),  # Корректный номер
        ("1234", " ****  **** **** 1234"),  # Короткий номер
        ("1", " ****  **** **** 1"),  # Очень короткий номер
        ("", " **** "),  # Пустая строка
    ],
)
def test_mask_card_number_valid(input_number, expected_output, mock_logger):
    """Тест проверки маскирования корректных номеров карт"""
    result = get_mask_card_number(input_number)

    if input_number:  # Если номер не пустой
        mock_logger.info.assert_called_once_with("Маскировка номера банковской карты")
    else:
        mock_logger.info.assert_not_called()

    assert result == expected_output


@pytest.mark.parametrize(
    "invalid_input",
    [
        "1234a567812345678",  # С буквой
        "1234-5678-1234-5678",  # С дефисами
        "1234 5678 1234 5678",  # С пробелами
        "!@#$%^&*()",  # Спецсимволы
    ],
)
def test_mask_card_number_invalid(invalid_input, mock_logger):
    """Тест проверки обработки некорректных номеров карт"""
    result = get_mask_card_number(invalid_input)

    mock_logger.error.assert_called_once_with("Введены недопустимые символы в номере карты")
    assert result == ""


def test_mask_card_number_none(mock_logger):
    """Тест проверки обработки None"""
    result = get_mask_card_number(None)

    mock_logger.error.assert_called_once_with("Введены недопустимые символы в номере карты")
    assert result == ""


def test_log_directory_creation(setup_logs):
    """Тест проверки создания директории логов"""
    assert os.path.exists(log_dir)
    assert os.path.isdir(log_dir)


def test_logging_output(setup_logs, tmp_path):
    """Тест проверки записи в лог-файл"""
    test_number = "1234567812345678"
    get_mask_card_number(test_number)

    log_file = tmp_path / "logs" / "mask.log"
    assert os.path.exists(log_file)

    with open(log_file, "r") as f:
        log_content = f.read()
        assert "Маскировка номера банковской карты" in log_content


def test_logger_configuration():
    """Тест проверки конфигурации логгера"""
    assert logger.name == "mask"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0
    assert isinstance(logger.handlers[0], logging.FileHandler)
