from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.cashback import calculate_cashback_100


@pytest.fixture
def mock_excel_data():
    """Фикстура для генерации тестовых данных"""
    return pd.DataFrame(
        {
            "Сумма платежа": [100.50, -250.75, -150.25, 50.00],
            "Дата": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
        }
    )


def test_calculate_cashback_correct_calculation(mock_excel_data):
    """Тест проверки корректного расчета кэшбэка"""
    processed_df = None

    def mock_to_excel(self, path, *args, **kwargs):
        nonlocal processed_df
        processed_df = self.copy()

    with (
        patch("pandas.read_excel", return_value=mock_excel_data.copy()),
        patch("pandas.DataFrame.to_excel", mock_to_excel),
    ):

        calculate_cashback_100()

        # Проверяем, что to_excel был вызван
        assert processed_df is not None

        # Проверяем расчет кэшбэка
        assert (processed_df["Сумма платежа"] < 0).sum() == 2  # 2 отрицательных значения
        assert (processed_df["Кэшбэк"] == [0, 2, 1, 0]).all()


def test_calculate_cashback_missing_column():
    """Тест проверки работы при отсутствии нужного столбца"""
    mock_data = pd.DataFrame({"Дата": ["2023-01-01"]})

    with patch("pandas.read_excel", return_value=mock_data):
        with pytest.raises(KeyError) as excinfo:
            calculate_cashback_100()
        assert "В файле отсутствует колонка 'Сумма платежа'" in str(excinfo.value)


def test_calculate_cashback_empty_data():
    """Тест проверки работы с пустыми данными"""
    mock_data = pd.DataFrame(columns=["Сумма платежа", "Дата"])
    processed_df = None

    def mock_to_excel(self, path, *args, **kwargs):
        nonlocal processed_df
        processed_df = self.copy()

    with patch("pandas.read_excel", return_value=mock_data), patch("pandas.DataFrame.to_excel", mock_to_excel):

        calculate_cashback_100()
        assert processed_df is not None
        assert len(processed_df) == 0
