import pytest
from unittest.mock import patch
from src.transactions import transactions_operations
from typing import List, Dict, Any


def test_transactions_operations_valid_data(valid_transactions_data):
    """Тест: корректные данные → возвращает топ-5 положительных транзакций, отсортированных по убыванию."""
    with patch("src.transactions.read_operation_excel", return_value=valid_transactions_data):
        result = transactions_operations()

        assert "top_transactions" in result
        assert len(result["top_transactions"]) == 5

        # Проверяем суммы в порядке убывания
        amounts = [t["amount"] for t in result["top_transactions"]]
        assert amounts == [5000.0, 3000.5, 1500.0, 1198.23, 899.99]

        # Проверяем поля по позициям
        assert result["top_transactions"][0]["date"] == "21.12.2021"
        assert result["top_transactions"][1]["category"] == "Транспорт"
        assert result["top_transactions"][3]["description"] == "Доставка еды"
        assert result["top_transactions"][4]["description"] == "Такси"


def test_transactions_operations_missing_columns(missing_columns_data):
    """
    Тест: в данных отсутствует обязательный столбец 'Сумма платежа' у некоторых транзакций.
    Функция должна:
    - пропускать транзакции без 'Сумма платежа'
    - сортировать оставшиеся по убыванию суммы
    - возвращать не более 5 самых крупных
    """
    with patch("src.transactions.read_operation_excel", return_value=missing_columns_data):
        result = transactions_operations()

        # Проверяем, что структура ответа корректна
        assert "top_transactions" in result
        assert isinstance(result["top_transactions"], list)

        # В данных только 1 транзакция с 'Сумма платежа' ожидаем 1
        assert len(result["top_transactions"]) == 1

        # Проверяем содержимое единственной валидной транзакции
        tx = result["top_transactions"][0]
        assert tx["date"] == "21.12.2021"
        assert tx["amount"] == 5000.0
        assert tx["category"] == "Рестораны"
        assert tx["description"] == ""  # поле отсутствовало подставлено как пустая строка


@pytest.mark.parametrize(
    "transaction, expected_count",
    [
        (
            {
                "Дата операции": "21.12.2021 14:30:00",
                "Сумма платежа": "5000.0",
                "Категория": "Рестораны",
                "Описание": "Ужин",
            },
            1,
        ),
        (
            {
                "Дата операции": "21.12.2021 14:30:00",
                "Сумма платежа": "-2000.0",
                "Категория": "Перевод",
                "Описание": "Другу",
            },
            0,
        ),
        ({"Дата операции": "invalid-date", "Сумма платежа": "1000.0", "Категория": "Еда", "Описание": "Пицца"}, 0),
        ({"Дата операции": "21.12.2021 14:30:00", "Сумма платежа": "abc", "Категория": "Еда", "Описание": "Пицца"}, 0),
    ],
)
def test_transactions_operations_single_transaction(transaction, expected_count):
    """Параметризованный тест: фильтрация транзакций по валидности"""
    with patch("src.transactions.read_operation_excel", return_value=[transaction]):
        result = transactions_operations()
        assert len(result["top_transactions"]) == expected_count


def test_transactions_operations_empty_data(empty_transactions_data):
    """Тест: пустой список → возвращает пустой top_transactions"""
    with patch("src.transactions.read_operation_excel", return_value=empty_transactions_data):
        result = transactions_operations()
        assert result["top_transactions"] == []


def test_transactions_operations_invalid_data(invalid_data_data):
    """Тест: отрицательные суммы и неверная дата → фильтруются"""
    with patch("src.transactions.read_operation_excel", return_value=invalid_data_data):
        result = transactions_operations()
        assert len(result["top_transactions"]) == 0


def test_transactions_operations_mixed_data(mixed_data):
    """Тест: смешанные данные — возвращаются только валидные положительные"""
    with patch("src.transactions.read_operation_excel", return_value=mixed_data):
        result = transactions_operations()
        assert len(result["top_transactions"]) == 2
        assert result["top_transactions"][0]["amount"] == 5000.0
        assert result["top_transactions"][1]["amount"] == 3000.0
