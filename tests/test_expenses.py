from unittest.mock import patch

import pytest

from src.expenses import calculate_total_expenses
from src.read_excel import read_operation_excel


@pytest.fixture
def mock_excel_data():
    """Фикстура возвращает тестовые данные в формате, аналогичном read_operation_excel"""
    return [
        {"Сумма платежа": 100.50, "Дата": "2023-01-01"},
        {"Сумма платежа": 200.75, "Дата": "2023-01-02"},
        {"Сумма платежа": -150.25, "Дата": "2023-01-03"},
        {"Сумма платежа": 50.00, "Дата": "2023-01-04"},
    ]


@pytest.fixture
def mock_empty_data():
    """Фикстура возвращает пустой список"""
    return []


@pytest.fixture
def mock_invalid_data():
    """Фикстура возвращает данные с некорректными значениями"""
    return [
        {"Сумма платежа": 0, "Дата": "2023-01-02"},  # Заменили None на 0
        {"Сумма платежа": 100.50, "Дата": "2023-01-01"},
        {"Сумма платежа": 0, "Дата": "2023-01-03"},  # Добавили поле "Сумма платежа" со значением 0
    ]


@pytest.mark.parametrize(
    "column_name, expected_total",
    [
        ("Сумма платежа", 201.0),  # 100.5 + 200.75 - 150.25 + 50 = 201.0
        ("Другая колонка", 0.0),  # Если колонки нет, вернется 0
    ],
)
def test_calculate_total_expenses_normal(mock_excel_data, column_name, expected_total):
    """Тест проверки расчета общей суммы расходов с нормальными данными"""
    with patch("src.expenses.read_operation_excel", return_value=mock_excel_data):
        result = calculate_total_expenses(column_name)
        assert abs(result - expected_total) < 0.01


def test_calculate_total_expenses_empty(mock_empty_data):
    """Тест проверки работы с пустыми данными"""
    with patch("src.expenses.read_operation_excel", return_value=mock_empty_data):
        result = calculate_total_expenses("Сумма платежа")
        assert result == 0.0


def test_calculate_total_expenses_invalid(mock_invalid_data):
    """Тест проверки обработки некорректных данных"""
    with patch("src.expenses.read_operation_excel", return_value=mock_invalid_data):
        result = calculate_total_expenses("Сумма платежа")
        # Теперь ожидаем 0 + 100.50 + 0 = 100.50
        assert result == 100.50


def test_calculate_total_expenses_negative_values(mock_excel_data):
    """Тест проверки работы с отрицательными значениями"""
    with patch("src.expenses.read_operation_excel", return_value=mock_excel_data):
        result = calculate_total_expenses("Сумма платежа")
        # Функция возвращает 100.5 + 200.75 - 150.25 + 50 = 201.0
        assert result == 201.0


def test_calculate_total_expenses_different_column(mock_excel_data):
    """Тест проверки работы с разными названиями колонок"""
    modified_data = [{**item, "Новая колонка": item["Сумма платежа"]} for item in mock_excel_data]
    with patch("src.expenses.read_operation_excel", return_value=modified_data):
        result = calculate_total_expenses("Новая колонка")
        assert abs(result - 201.0) < 0.01  # 100.5 + 200.75 - 150.25 + 50 = 201.0
