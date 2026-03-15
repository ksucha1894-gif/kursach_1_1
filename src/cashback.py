import os

import pandas as pd

from config import FILE_PATH


# Функция для расчета кэшбэка
def calculate_cashback_100():
    # Чтение данных из Excel
    df = pd.read_excel(FILE_PATH)

    # Проверка наличия обязательной колонки
    if "Сумма платежа" not in df.columns:
        raise KeyError("В файле отсутствует колонка 'Сумма платежа'")

    # Инициализируем или обнуляем колонку "Кэшбэк"
    df["Кэшбэк"] = 0.0

    # Пересчитываем кэшбек только для расходов
    cash = df["Сумма платежа"] < 0
    df.loc[cash, "Кэшбэк"] = df.loc[cash, "Сумма платежа"].abs() // 100

    # Вывод результата
    print(df)

    # Запись изменений обратно в Excel
    current_dir = os.path.dirname(__file__)
    output_path = os.path.join(current_dir, "..", "data", "updated_operations.xlsx")
    df.to_excel(output_path, index=False)


# Вызов функции для проверки
calculate_cashback_100()
