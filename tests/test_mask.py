import pytest
from src.mask import get_mask_card_number
import logging
from unittest.mock import patch


@pytest.fixture
def valid_card_numbers():
    """Фикстура: корректные номера карт (только цифры)"""
    return [
        "1234567812345678",
        "1111222233334444",
        "9999",
        "5",
        "",
    ]


@pytest.fixture
def invalid_card_strings():
    """Фикстура: некорректные строки с буквами/символами — но с цифрами"""
    return [
        "1234a5678b9012",  # буквы + цифры
        "1234-5678-9012-3456",  # дефисы
        "1234 5678 9012 3456",  # пробелы
        "!@#$1234%^&*5678",  # спецсимволы
    ]


@pytest.fixture
def invalid_types():
    """Фикстура: неверные типы данных"""
    return [
        None,
        12345678,
        [],
        {},
        3.14,
    ]


@pytest.fixture
def mock_logger():
    """Фикстура: мок для логгера"""
    with patch("src.mask.logger") as mock:
        yield mock


@pytest.mark.parametrize(
    "card_number, expected",
    [
        ("1234567812345678", "5678"),
        ("1111222233334444", "4444"),
        ("9999", "9999"),
        ("5", "5"),
        ("", ""),
    ],
)
def test_get_mask_card_number_valid(card_number, expected):
    """Тест: корректные номера карт — возвращают последние 4 цифры"""
    result = get_mask_card_number(card_number)
    assert result == expected


@pytest.mark.parametrize(
    "card_number, expected",
    [
        ("1234a5678b9012", "9012"),
        ("1234-5678-9012-3456", "3456"),
        ("1234 5678 9012 3456", "3456"),
        ("!@#$1234%^&*5678", "5678"),
    ],
)
def test_get_mask_card_number_invalid_string_with_digits(card_number, expected, invalid_card_strings):
    """Тест: строки с символами — извлекаются цифры, возвращаются последние 4"""
    result = get_mask_card_number(card_number)
    assert result == expected


@pytest.mark.parametrize("invalid_input", [None, 12345678, [], {}, 3.14])
def test_get_mask_card_number_invalid_type(invalid_input, invalid_types):
    """Тест: неверные типы данных — возвращают пустую строку"""
    result = get_mask_card_number(invalid_input)
    assert result == ""


def test_get_mask_card_number_logs_success(mock_logger):
    """Тест: успешная обработка логируется как INFO с правильным форматом"""
    card_number = "1234567812345678"
    get_mask_card_number(card_number)
    mock_logger.info.assert_called_once_with(f"Извлечены последние цифры: '{card_number}' → '5678'")


def test_get_mask_card_number_logs_invalid_type(mock_logger):
    """Тест: неверный тип логируется как ERROR"""
    get_mask_card_number(None)
    mock_logger.error.assert_called_once_with(
        "Неверный тип номера карты: <class 'NoneType'> — ожидается str, получено: None"
    )


def test_get_mask_card_number_empty_string_no_log(mock_logger):
    """Тест: пустая строка не вызывает логирование (т.к. нет цифр)"""
    get_mask_card_number("")
    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()
