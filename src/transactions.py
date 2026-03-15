import pandas as pd

from src.read_excel import read_operation_excel


# Выбираем топ-5 транзакций по сумме платежа.
def transactions_operations():
    """Вычисляет и выводит топ-5 транзакций по сумме платежа."""

    # Вызываем функцию для получения данных из Excel
    transactions_df = read_operation_excel()

    # Преобразуем данные в DataFrame для дальнейшей обработки
    transactions_df = pd.DataFrame(transactions_df)

    # Отсортируем DataFrame по сумме платежа в порядке убывания
    transactions_df["Сумма платежа"] = transactions_df["Сумма платежа"].astype(float)  # Убедимся, что сумма как число
    sorted_transactions_df = transactions_df.sort_values(by="Сумма платежа", ascending=False)

    # Выберем топ-5 транзакций
    top_5_transactions = sorted_transactions_df.head(5)

    # Выведем топ-5 транзакций
    return top_5_transactions


top_5_transactions = transactions_operations()
print(top_5_transactions)
