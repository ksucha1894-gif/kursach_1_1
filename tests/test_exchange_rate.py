import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_user_settings():
    return {"some_setting": "value"}


@pytest.fixture
def mock_api_response():
    return {"close": 90.5, "symbol": "USD/RUB"}


def test_get_currency_rates_success(tmp_path, mock_user_settings, mock_api_response):
    # Создаем временные файлы
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    settings_file = data_dir / "user_settings.json"
    course_file = tmp_path / "courses.json"

    with open(settings_file, "w") as f:
        json.dump(mock_user_settings, f)
    with open(course_file, "w") as f:
        json.dump({"user_currencies": ["USD"]}, f)  # Только USD в конфиге

    # Мокаем ответы API для обеих валют
    usd_response = MagicMock()
    usd_response.status_code = 200
    usd_response.json.return_value = mock_api_response

    eur_response = MagicMock()
    eur_response.status_code = 200
    eur_response.json.return_value = {"close": 85.0, "symbol": "EUR/RUB"}

    # Настраиваем mock_get для разных запросов
    def get_side_effect(url, params=None):
        if params and params["symbol"] == "USD/RUB":
            return usd_response
        elif params and params["symbol"] == "EUR/RUB":
            return eur_response
        return MagicMock(status_code=404)

    with (
        patch("dotenv.load_dotenv"),
        patch("src.exchange_rate.ROOT_DIR", str(tmp_path)),
        patch("os.getenv", return_value="test_api_key"),
        patch("requests.get") as mock_get,
    ):

        mock_get.side_effect = get_side_effect

        from src.exchange_rate import get_currency_rates

        result = get_currency_rates()

        # Проверяем, что функция возвращает обе валюты (USD и EUR)
        assert len(result) == 2
        assert {"currency": "USD", "rate": 90.5} in result
        assert {"currency": "EUR", "rate": 85.0} in result

        # Проверяем, что API вызывался для обеих валют
        assert mock_get.call_count == 2
        calls = [call[1]["params"]["symbol"] for call in mock_get.call_args_list]
        assert "USD/RUB" in calls
        assert "EUR/RUB" in calls


def test_get_currency_rates_empty_currency_list(tmp_path, mock_user_settings):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    settings_file = data_dir / "user_settings.json"
    course_file = tmp_path / "courses.json"

    with open(settings_file, "w") as f:
        json.dump(mock_user_settings, f)
    with open(course_file, "w") as f:
        json.dump({"user_currencies": []}, f)  # Пустой список валют

    # Мокаем ответы API для обеих валют
    usd_response = MagicMock()
    usd_response.status_code = 200
    usd_response.json.return_value = {"close": 90.5, "symbol": "USD/RUB"}

    eur_response = MagicMock()
    eur_response.status_code = 200
    eur_response.json.return_value = {"close": 85.0, "symbol": "EUR/RUB"}

    def get_side_effect(url, params=None):
        if params and params["symbol"] == "USD/RUB":
            return usd_response
        elif params and params["symbol"] == "EUR/RUB":
            return eur_response
        return MagicMock(status_code=404)

    with (
        patch("dotenv.load_dotenv"),
        patch("src.exchange_rate.ROOT_DIR", str(tmp_path)),
        patch("os.getenv", return_value="test_api_key"),
        patch("requests.get") as mock_get,
    ):

        mock_get.side_effect = get_side_effect

        from src.exchange_rate import get_currency_rates

        result = get_currency_rates()

        # Проверяем, что функция всё равно возвращает обе валюты
        assert len(result) == 2
        assert {"currency": "USD", "rate": 90.5} in result
        assert {"currency": "EUR", "rate": 85.0} in result

        # Проверяем, что API вызывался для обеих валют
        assert mock_get.call_count == 2
