from src.read_excel import read_operation_excel


def calculate_total_expenses(column_name: str) -> float:
    """Вычисляет общую сумму расходов на основе указанной колонки."""

    total_expenses = 0.0

    for record in read_operation_excel():
        # Получаем сумму из указанной колонки и добавляем к общей сумме
        amount = float(record.get(column_name, 0))
        total_expenses += amount

    # Возвращаем абсолютное значение общей суммы расходов
    return abs(total_expenses)


# Пример вызова функции
column_name = "Сумма платежа"
total = calculate_total_expenses(column_name)
print(f"Общая сумма расходов: {total}")
