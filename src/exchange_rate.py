import json
import os
import time
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from config import COURSE_PATH, ROOT_DIR


def get_currency_rates() -> Optional[List[Dict[str, float]]]:
    # settings_file_path = os.path.join(ROOT_DIR, "data", "user_settings.json")
    # with open(settings_file_path) as f:
    #     user_settings = json.load(f)

    with open(COURSE_PATH) as file:
        data = json.load(file)
        currency = data.get("user_currencies", [])

    load_dotenv()
    api_key = os.getenv("API_KEY_twelvedata")
    if not api_key:
        print("API_KEY не найден или не определён")
        return None

    url = "https://api.twelvedata.com/quote"
    results = []

    for cur in currency:
        symbol = f"{cur}/RUB"
        params = {"symbol": symbol, "apikey": api_key}

        response = requests.get(url, params=params)
        # print(f"Ответ для {symbol}:", response.text)

        if response.status_code == 200:
            try:
                data = response.json()
                # Извлекаем текущий курс (close)
                exchange_rate = data.get("close")
                if exchange_rate:
                    # print(f"Курс {cur} к RUB: {exchange_rate}")
                    results.append({"currency": cur, "rate": exchange_rate})
                else:
                    print(f"Не удалось извлечь курс для {cur}")
            except json.JSONDecodeError:
                print("Ошибка декодирования JSON")
        else:
            print(f"Ошибка запроса для {cur}: {response.status_code}")

        time.sleep(1)  # Задержка между запросами

    return results


# if __name__ == "__main__":
#     rates = get_currency_rates()
#     print("Результаты:", rates)
