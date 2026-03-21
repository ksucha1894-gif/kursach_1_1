import json
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv


def get_stock_prices(virtual: bool = True) -> List[Dict[str, str]]:
    """
    Возвращает текущие цены для нескольких акций: AAPL и AMZN.
    - Если virtual=True: возвращает фиктивные данные для тестирования.
    - Если virtual=False: обращается к API Twelve Data для получения реальных цен.
    Возвращает список: [
        {"stock": "AAPL", "price": "150.12"},
        {"stock": "AMZN", "price": "3173.18"}
    ]
    """
    if virtual:
        return [{"stock": "AAPL", "price": "150.12"}, {"stock": "AMZN", "price": "3173.18"}]

    # Загружаем переменные окружения
    load_dotenv()
    apikey = os.getenv("API_KEY_twelvedata")

    # Проверка API ключа
    if not apikey or apikey == "demo":
        print("API_KEY not found or still using 'demo'. Please set a valid API key in .env file.")
        return [{"stock": "AAPL", "price": "0.00"}, {"stock": "AMZN", "price": "0.00"}]

    # Список акций
    symbols = ["AAPL", "AMZN"]
    result = []

    for symbol in symbols:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={apikey}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "price" in data:
                result.append({"stock": symbol, "price": str(data["price"])})
            else:
                print(f"Непредвиденная структура ответа для {symbol}: {data}")
                result.append({"stock": symbol, "price": "0.00"})

        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети при запросе к Twelve Data для {symbol}: {e}")
            result.append({"stock": symbol, "price": "0.00"})
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON для {symbol}: {e}")
            result.append({"stock": symbol, "price": "0.00"})
        except Exception as e:
            print(f"Неизвестная ошибка для {symbol}: {e}")
            result.append({"stock": symbol, "price": "0.00"})

    return result


# Пример использования
# if __name__ == "__main__":
#     # Получаем данные (реальный API)
#     stock_data = get_stock_prices(virtual=False)
#
#     # Формируем финальный JSON-объект с ключом "stock_prices"
#     final_output = {"stock_prices": stock_data}
#
#     # Выводим в консоль в красивом формате JSON
#     print(json.dumps(final_output, indent=4, ensure_ascii=False))
