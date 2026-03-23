from io import BytesIO
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from config import FILE_PATH
from src.read_excel import read_operation_excel


# Фикстура для генерации тестовых данных
@pytest.fixture
def sample_excel_data():
    return [
        {"Дата операции": "01.01.2024", "Сумма платежа": -100.0, "Категория": "Продукты"},
        {"Дата операции": "02.01.2024", "Сумма платежа": -50.0, "Категория": "Транспорт"},
        {"Дата операции": "03.01.2024", "Сумма платежа": 200.0, "Категория": "Зарплата"},
    ]


# Фикстура для создания mock Excel файла
@pytest.fixture
def mock_excel_file(sample_excel_data):
    df = pd.DataFrame(sample_excel_data)
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    return excel_file


# Параметризированный тест для успешного чтения
@pytest.mark.parametrize("file_exists", [True, False])
def test_read_operation_excel_success(file_exists, sample_excel_data, mock_excel_file, capfd):
    with patch("pandas.read_excel") as mock_read_excel:
        if file_exists:
            # Настройка mock для успешного чтения
            mock_read_excel.return_value = pd.DataFrame(sample_excel_data)

            result = read_operation_excel()

            # Проверки
            assert isinstance(result, list)
            assert len(result) == 3
            assert result[0]["Категория"] == "Продукты"
            assert result[1]["Сумма платежа"] == -50.0
            mock_read_excel.assert_called_once_with(FILE_PATH)
        else:
            # Настройка mock для FileNotFoundError
            mock_read_excel.side_effect = FileNotFoundError(f"File {FILE_PATH} not found")

            result = read_operation_excel()

            # Проверяем вывод в stdout
            captured = capfd.readouterr()
            assert f"Файл не найден: {FILE_PATH}" in captured.out
            assert result == []


# Тест для обработки других исключений
def test_read_operation_excel_exception(capfd):
    with patch("pandas.read_excel") as mock_read_excel:
        test_exception = Exception("Test exception")
        mock_read_excel.side_effect = test_exception

        result = read_operation_excel()

        # Проверяем вывод в stdout
        captured = capfd.readouterr()
        assert "Ошибка при чтении Excel файла: Test exception" in captured.out
        assert result == []


# Тест для проверки структуры возвращаемых данных
def test_read_operation_excel_structure(sample_excel_data):
    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = pd.DataFrame(sample_excel_data)

        result = read_operation_excel()

        # Проверяем структуру данных
        assert all(isinstance(item, dict) for item in result)
        assert all("Дата операции" in item for item in result)
        assert all("Сумма платежа" in item for item in result)
        assert all("Категория" in item for item in result)


# Тест для пустого Excel файла
def test_read_operation_excel_empty():
    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = pd.DataFrame()

        result = read_operation_excel()

        assert isinstance(result, list)
        assert len(result) == 0
