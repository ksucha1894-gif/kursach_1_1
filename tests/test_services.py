import json
from unittest.mock import MagicMock, patch

import pytest

from src.mask import logger
from src.read_excel import read_operation_excel
from src.services import simple_search


# Фикстура для создания тестовых транзакций
@pytest.fixture
def mock_transactions():
    return [
        {
            "Описание": "Покупка продуктов в Пятерочке",
            "Категория": "Супермаркет",
            "Сумма": 1500.00,
            "Дата": "2023-05-15",
        },
        {"Описание": "Поездка на каршеринге", "Категория": "Транспорт", "Сумма": 850.50, "Дата": "2023-05-16"},
        {"Описание": "Оплата интернета", "Категория": "Коммунальные услуги", "Сумма": 1200.00, "Дата": "2023-05-17"},
    ]


# Фикстура для mock-ирования read_operation_excel
@pytest.fixture
def mock_read_excel(mock_transactions):
    with patch("src.services.read_operation_excel", return_value=mock_transactions) as mock:
        yield mock


# Фикстура для mock-ирования logger
@pytest.fixture
def mock_logger():
    with patch("src.services.logger") as mock:
        yield mock


# Параметризованный тест для успешного поиска
@pytest.mark.parametrize(
    "query,expected_count",
    [
        ("Супермаркет", 1),  # Поиск по категории
        ("Пятерочке", 1),  # Поиск по описанию
        ("каршеринг", 1),  # Поиск по части слова
        ("Транспорт", 1),  # Поиск по категории
        ("Несуществующий", 0),  # Пустой результат
        ("", 3),  # Пустой запрос - все транзакции
    ],
)
def test_simple_search_success(mock_read_excel, mock_logger, query, expected_count):
    """Тест успешного выполнения поиска"""
    # Проверяем, что mock возвращает правильные данные
    assert len(mock_read_excel.return_value) == 3

    result = simple_search(query)
    data = json.loads(result)

    # Проверяем структуру ответа
    assert "transactions" in data
    assert len(data["transactions"]) == expected_count

    # Проверяем логирование
    if expected_count == 0:
        mock_logger.info.assert_called_with(f"Найдено {expected_count} транзакций по запросу '{query}'")
    else:
        mock_logger.info.assert_called_with(f"Найдено {expected_count} транзакций по запросу '{query}'")


# Тест обработки пустого файла
def test_simple_search_empty_file(mock_read_excel, mock_logger):
    """Тест обработки пустого файла с транзакциями"""
    # Переопределяем mock для возврата пустого списка
    with patch("src.services.read_operation_excel", return_value=[]):
        result = simple_search("Супермаркет")
        data = json.loads(result)

        assert data["transactions"] == []
        mock_logger.warning.assert_called_with("Файл с транзакциями пуст или не найден")


# Тест обработки ошибок
def test_simple_search_exception(mock_read_excel, mock_logger):
    """Тест обработки исключений"""
    # Переопределяем mock для генерации исключения
    with patch("src.services.read_operation_excel", side_effect=Exception("Test error")):
        result = simple_search("Супермаркет")
        data = json.loads(result)

        assert data["error"] == "Внутренняя ошибка сервера"
        mock_logger.error.assert_called_with("Ошибка при выполнении поиска: Test error")


# Тест формата вывода
def test_simple_search_output_format(mock_read_excel):
    """Тест формата вывода JSON"""
    result = simple_search("Супермаркет")
    data = json.loads(result)

    # Проверяем, что вывод содержит все необходимые поля
    assert isinstance(data, dict)
    assert "transactions" in data
    assert isinstance(data["transactions"], list)

    # Проверяем первый элемент
    if data["transactions"]:
        tx = data["transactions"][0]
        assert "Описание" in tx
        assert "Категория" in tx
        assert "Сумма" in tx
        assert "Дата" in tx


# Тест регистронезависимого поиска
def test_simple_search_case_insensitive(mock_read_excel):
    """Тест регистронезависимого поиска"""
    # Проверяем поиск в разном регистре
    for query in ["супермаркет", "СУПЕРМАРКЕТ", "СуПеРмАрКеТ"]:
        result = simple_search(query)
        data = json.loads(result)
        assert len(data["transactions"]) == 1


# Тест поиска по части слова
def test_simple_search_partial_match(mock_read_excel):
    """Тест поиска по части слова"""
    result = simple_search("прод")
    data = json.loads(result)
    assert len(data["transactions"]) == 1
    assert "продуктов" in data["transactions"][0]["Описание"].lower()
