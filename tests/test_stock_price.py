import json
import os
from unittest.mock import MagicMock, patch

import pytest

from src.stock_price import get_stock_prices, save_to_json


@pytest.fixture
def mock_api_response():
    return {
        "data": [{"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust"}, {"symbol": "QQQ", "name": "Invesco QQQ Trust"}],
        "status": "ok",
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("API_KEY_twelvedata", "test_api_key_123")


@pytest.fixture
def mock_invalid_api_response():
    return {"error": "Invalid API key"}


@pytest.fixture
def temp_json_file(tmp_path):
    return tmp_path / "test_stock_prices.json"


@pytest.mark.parametrize(
    "virtual,expected_count",
    [
        (True, 1),  # Виртуальный режим должен возвращать 1 элемент
        (False, 2),  # Реальный режим должен возвращать 2 элемента (из mock)
    ],
)
def test_get_stock_prices(virtual, expected_count, mock_api_response, mock_env_vars):
    with patch("requests.get") as mock_get:
        # Настройка mock для реального режима
        if not virtual:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_get.return_value = mock_response

        result = get_stock_prices(virtual=virtual)

        if virtual:
            assert len(result) == expected_count
            assert result[0]["symbol"] == "SPY"
            assert result[0]["price"] == "400.00"
        else:
            assert len(result["data"]) == expected_count
            assert result["status"] == "ok"
            mock_get.assert_called_once()


def test_get_stock_prices_api_error(mock_env_vars):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        result = get_stock_prices(virtual=False)
        assert result == []


def test_get_stock_prices_missing_api_key():
    with patch.dict(os.environ, {"API_KEY_twelvedata": ""}):
        result = get_stock_prices(virtual=False)
        assert result == []


def test_get_stock_prices_json_decode_error(mock_env_vars):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_get.return_value = mock_response

        result = get_stock_prices(virtual=False)
        assert result == []


@pytest.mark.parametrize(
    "test_data,expected_filename",
    [([{"symbol": "AAPL", "price": "150.00"}], "test_output.json"), ([], "empty_output.json")],
)
def test_save_to_json(test_data, expected_filename, tmp_path):
    filepath = tmp_path / expected_filename

    save_to_json(test_data, str(filepath))

    # Проверяем, что файл создан и содержит правильные данные
    assert filepath.exists()
    with open(filepath, "r") as f:
        loaded_data = json.load(f)
    assert loaded_data == test_data


def test_integration_virtual_mode():
    result = get_stock_prices(virtual=True)
    assert len(result) == 1
    assert result[0]["symbol"] == "SPY"


def test_integration_real_mode(mock_api_response, mock_env_vars, tmp_path):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_get.return_value = mock_response

        result = get_stock_prices(virtual=False)
        assert len(result["data"]) == 2
        assert result["status"] == "ok"
