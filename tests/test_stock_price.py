import os
from unittest.mock import MagicMock, patch
import pytest
from src.stock_price import get_stock_prices


# Фикстура для виртуальных данных (соответствует реальному коду)
@pytest.fixture
def mock_virtual_data():
    return [{"stock": "AAPL", "price": "150.12"}, {"stock": "AMZN", "price": "3173.18"}]


# Фикстура для API-ответа (одинаковый для всех запросов в моке)
@pytest.fixture
def mock_api_response():
    return {"price": "400.00"}  # Как возвращает Twelve Data


# Фикстура для невалидного API-ответа
@pytest.fixture
def mock_invalid_api_response():
    return {"error": "Invalid API key"}


# Фикстура для переменных окружения
@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("API_KEY_twelvedata", "test_api_key_123")


@pytest.mark.parametrize(
    "virtual,expected_count",
    [
        (True, 2),  # Виртуальный режим: 2 акции из фикстуры
        (False, 2),  # Реальный режим: 2 акции, мокаем API
    ],
)
def test_get_stock_prices(virtual, expected_count, mock_api_response, mock_env_vars):
    with patch("requests.get") as mock_get:
        if not virtual:
            # Мокаем ответ для каждого запроса (AAPL и AMZN)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_get.return_value = mock_response

        result = get_stock_prices(virtual=virtual)

        # Проверяем структуру и количество
        assert len(result) == expected_count
        assert all(isinstance(item, dict) and "stock" in item and "price" in item for item in result)

        if virtual:
            # Проверяем виртуальные данные
            assert result[0]["stock"] == "AAPL"
            assert result[0]["price"] == "150.12"
            assert result[1]["stock"] == "AMZN"
            assert result[1]["price"] == "3173.18"
        else:
            # Проверяем, что обе акции получили одинаковый мок-ответ
            assert result[0]["stock"] == "AAPL"
            assert result[0]["price"] == "400.00"
            assert result[1]["stock"] == "AMZN"
            assert result[1]["price"] == "400.00"
            assert mock_get.call_count == 2  # Два вызова: AAPL и AMZN


def test_get_stock_prices_api_error(mock_env_vars):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        result = get_stock_prices(virtual=False)

        assert len(result) == 2
        assert result[0]["price"] == "0.00"
        assert result[1]["price"] == "0.00"


def test_get_stock_prices_missing_api_key():
    with patch.dict(os.environ, {"API_KEY_twelvedata": ""}):
        result = get_stock_prices(virtual=False)

        assert len(result) == 2
        assert result[0]["price"] == "0.00"
        assert result[1]["price"] == "0.00"


def test_get_stock_prices_json_decode_error(mock_env_vars):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")  # Или json.JSONDecodeError
        mock_get.return_value = mock_response

        result = get_stock_prices(virtual=False)

        assert len(result) == 2
        assert result[0]["price"] == "0.00"
        assert result[1]["price"] == "0.00"


def test_get_stock_prices_invalid_api_structure(mock_env_vars):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "no price"}  # Нет ключа "price"
        mock_get.return_value = mock_response

        result = get_stock_prices(virtual=False)

        assert len(result) == 2
        assert result[0]["price"] == "0.00"
        assert result[1]["price"] == "0.00"


def test_integration_virtual_mode():
    result = get_stock_prices(virtual=True)
    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == "150.12"
    assert result[1]["stock"] == "AMZN"
    assert result[1]["price"] == "3173.18"


def test_integration_real_mode(mock_api_response, mock_env_vars):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_get.return_value = mock_response

        result = get_stock_prices(virtual=False)

        assert len(result) == 2
        assert result[0]["stock"] == "AAPL"
        assert result[0]["price"] == "400.00"
        assert result[1]["stock"] == "AMZN"
        assert result[1]["price"] == "400.00"
        assert mock_get.call_count == 2  # Два запроса
