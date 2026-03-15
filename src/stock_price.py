import json
import os

import requests
from dotenv import load_dotenv


# Работа со стоимостью акций из S&P500
def get_stock_prices(virtual=True):
    if virtual:
        return [{"symbol": "SPY", "price": "400.00"}]
    else:
        # Загружаем переменные окружения
        load_dotenv()
        apikey = os.getenv("API_KEY_twelvedata")

        # Проверяем, что API ключ загружен
        if not apikey:
            print("API_KEY not found. Please check your .env file.")
            return []

        # URL для получения ежедневных данных о ценах акций
        url = f"https://api.twelvedata.com/etfs/list?apikey=demo"

        # Выполнение GET-запроса к API
        response = requests.get(url)

        # Проверка статуса кода и обработка ответа
        if response.status_code == 200:
            try:
                data = response.json()
                print(json.dumps(data, indent=4))
                return data
            except json.JSONDecodeError as e:
                print("Ошибка декодирования JSON:", e)
        else:
            print("Ошибка при запросе к API, статус код:", response.status_code)
            print("Текст ответа:", response.text)
        return []


# Пример вызова функции для сохранения данных в JSON файл
def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# Пример вызова функции для сохранения цен акций
stock_data = get_stock_prices(virtual=False)

# Сохраняем в файл
current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_dir, "stock_prices.json")
save_to_json(stock_data, json_file_path)
