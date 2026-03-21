# Проект "Мой банк"

## Описание:

Проект "Мой банкг" - это веб-приложение на Python для работы с различными банковскими операциями. Указанное приложение 
создает возможность пользователям сделать расчет своих расходов и кэшбека, узнать курс валют и акций на актуальную дату, 
а также сформировать отчет для удобства работы с данными.

## Установка:

1. Клонируйте репозиторий:

git clone git@github.com:ksucha1894-gif/kursach_1_1.git

2. Установите библиотеки с помощью import:

json, datetime, logging, os, csv, time

3. Установите зависимости:

poetry add pandas

poetry add requests

poetry add python-dotenv

pip install pytest

4. Сведения о API-ключе:

Использован API-ключ, предоставленный сервисом https://twelvedata.com/ в бесплатной подписке

5. Сведения о работе приложения:
5.1. Модуль main.py является точкой входа:

def main(datetime_str: str) -> str:
    """Основная функция программы"""
    logger.info("Финансовая аналитика запущена")
    print("Финансовая аналитика запущена")

    try:
        # 1. Получение финансового отчета
        print("\n1. Формирование финансового отчета...")
        # datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        financial_report = get_financial_report(datetime_str)
        report_data = json.loads(financial_report)
        print("Отчет сформирован")
        pprint(report_data)

        # 2. Простой поиск транзакций
        print("\n2. Выполнение простого поиска...")
        query = "Супермаркет"
        search_result = simple_search(query)
        search_data = json.loads(search_result)
        print(f"Найдено {len(search_data.get('transactions', []))} транзакций по запросу '{query}'")

        # 3. Генерация отчета по категории
        print("\n3. Генерация отчета по категории...")
        transactions_data = read_operation_excel()
        transactions_df = pd.DataFrame(transactions_data)

        if not transactions_df.empty:
            category = "Супермаркет"
            report = spending_by_category(transactions_df, category)
            print(f"Отчет по категории '{category}' сформирован ({len(report)} записей)")
        else:
            print("Нет данных для формирования отчета по категориям")

        logger.info("Программа завершила работу успешно")
        print("\nРабота программы завершена успешно")

    except Exception as e:
        logger.error(f"Ошибка в основном потоке: {str(e)}")
        print(f"Произошла ошибка: {str(e)}")

5.2. В модуле views прописана главная функция:
import json
from datetime import datetime

from src.utils import get_cards_summary, transactions_operations, get_currency_rates, get_stock_prices


def get_financial_report(datetime_str: str) -> str:
    """
    Главная функция, принимающая дату в формате YYYY-MM-DD HH:MM:SS
    и возвращающая JSON-ответ по ТЗ.
    """
    if datetime_str:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    else:
        dt = datetime.now()

    # Определяем приветствие
    hour = dt.hour
    if 5 <= hour < 11:
        greeting = "Доброе утро"
    elif 11 <= hour < 16:
        greeting = "Добрый день"
    elif 16 <= hour < 20:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    # 1. Получаем данные по картам
    cards_data = get_cards_summary(datetime_str)
    cards = []
    for card in cards_data.get("cards", []):
        try:
            last_digits = str(card.get("last_digits", ""))[-4:] if card.get("last_digits") else ""
            total_spent = float(card.get("total_spent", 0))
            cashback = float(total_spent // 100)  # 1 рубль на каждые 100 рублей
            if last_digits:  # Только валидные карты
                cards.append(
                    {"last_digits": last_digits, "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)}
                )
        except (ValueError, TypeError):
            continue

    # 2. Получаем топ-транзакции (все) и фильтруем по дате
    transactions_data = transactions_operations()
    top_transactions = []
    start_of_month = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    for tx in transactions_data.get("top_transactions", []):
        try:
            tx_date = datetime.strptime(tx["date"], "%d.%m.%Y")  # Формат: DD.MM.YYYY
            if start_of_month <= tx_date <= dt:  # Только в нужном диапазоне
                top_transactions.append(
                    {
                        "date": tx["date"],
                        "amount": float(tx["amount"]),
                        "category": tx.get("category", ""),
                        "description": tx.get("description", ""),
                    }
                )
        except (ValueError, TypeError, KeyError):
            continue  # Пропускаем битые записи

    # Сортируем по абсолютному значению суммы
    top_transactions.sort(key=lambda x: abs(x["amount"]), reverse=True)
    top_transactions = top_transactions[:5]  # Топ-5

    # 3. Курсы валют
    currency_rates_raw = get_currency_rates()
    currency_rates = []
    for cur in currency_rates_raw:
        try:
            currency = cur.get("currency", "").upper()
            rate = float(cur.get("rate", 0))
            if currency in ("USD", "EUR"):
                currency_rates.append({"currency": currency, "rate": round(rate, 2)})
        except (ValueError, TypeError):
            continue

    # 4. Акции S&P500 — фиксированный набор (если virtual=True)
    stock_prices_raw = get_stock_prices(virtual=True)
    stock_prices = []
    for stock in stock_prices_raw:
        try:
            stock_prices.append(
                {"stock": str(stock.get("stock", "")), "price": round(float(stock.get("price", 0)), 2)}
            )
        except (ValueError, TypeError):
            continue

    # Если акций меньше 5 — заполняем дефолтными
    if len(stock_prices) < 5:
        default_stocks = [
            {"stock": "AAPL", "price": 150.12},
            {"stock": "AMZN", "price": 3173.18},
            {"stock": "GOOGL", "price": 2742.39},
            {"stock": "MSFT", "price": 296.71},
            {"stock": "TSLA", "price": 1007.08},
        ]
        stock_prices = default_stocks[:5]

    # Формируем итоговый ответ
    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(result, ensure_ascii=False, indent=4)

5.3. Модуль utils является модулем со вспомогательными функциями для главной функции модуля views:
from src.cards import get_cards_summary
from src.stock_price import get_stock_prices
from src.exchange_rate import get_currency_rates
from src.transactions import transactions_operations
from src.read_excel import read_operation_excel

# Константы
CONFIG_PATH = "config.json"
ROOT_DIR = "."

5.4. Чтение файла excel, который используется для анализа, проводится в модуле read_excel:
def read_operation_excel() -> List[Dict[str, Any]]:
    """
    Функция принимает путь к файлу формата excel и возвращает список словарей.
    """
    try:
        excel_data = pd.read_excel(FILE_PATH)
        return excel_data.to_dict(orient="records")
    except FileNotFoundError:
        print(f"Файл не найден: {FILE_PATH}")
        return []
    except Exception as e:
        print(f"Ошибка при чтении Excel файла: {e}")
        return []

5.5. С помощью модуля mask создает маскировку банковской карты, а также логирование:
log_dir = os.path.join(ROOT_DIR, "logs")
log_file = os.path.join(log_dir, "mask.log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger("mask")
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def get_mask_card_number(number: Union[str, int, list, dict, float, None]) -> str:
    """
    Принимает номер карты как строку (может содержать цифры, звёздочки, пробелы, дефисы).
    Возвращает **только последние 4 цифры** в виде строки, например: "5814".

    Если цифр меньше 4 — возвращает все доступные цифры (например, "719").
    Если цифр нет — возвращает пустую строку.

    Если входной аргумент не строка (включая None, int, list, dict, float) —
    возвращает пустую строку и логирует ошибку.

    Примеры:
        "1234567812345678" → "5678"
        "**** 5814" → "5814"
        "123" → "123"
        None → ""
        12345678 → ""
        [] → ""
    """
    # Обработка всех неверных типов: включая None, int, list, dict, float
    if not isinstance(number, str):
        logger.error(f"Неверный тип номера карты: {type(number)} — ожидается str, получено: {number}")
        return ""  # ← ВСЕГДА возвращаем пустую строку для неверных типов

    # Теперь number — точно str
    if number == "":
        logger.warning(f"В номере карты не найдено ни одной цифры: '{number}'")
        return ""

    # Извлекаем только цифры из строки
    digits = re.sub(r"\D", "", number)

    if not digits:
        logger.warning(f"В номере карты не найдено ни одной цифры: '{number}'")
        return ""

    # Возвращаем последние 1–4 цифры
    last_digits = digits[-4:]
    logger.info(f"Извлечены последние цифры: '{number}' → '{last_digits}'")
    return last_digits

5.6. Возвращаем сумму трат и кэшбэк по каждой карте за период с начала месяца до указанной даты в модуле cards:
def get_cards_summary(date_str: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Возвращает сумму трат и кэшбэк по каждой карте за период с начала месяца до указанной даты.
    Формат даты: "YYYY-MM-DD HH:MM:SS"
    Возвращает:
    {
        "cards": [
            {
                "last_digits": "5814",
                "total_spent": 1262.00,
                "cashback": 12.62
            }
        ]
    }
    """
    try:
        end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return {"cards": []}

    start_of_month = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    records = read_operation_excel()
    if not records:
        return {"cards": []}

    df = pd.DataFrame(records)
    required_cols = {"Дата операции", "Сумма платежа", "Номер карты"}
    if not required_cols.issubset(df.columns):
        return {"cards": []}

    # Парсинг даты: ожидаем DD.MM.YYYY HH:MM:SS
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["Дата операции"])

    # Приведение суммы к числу
    df["Сумма платежа"] = pd.to_numeric(df["Сумма платежа"], errors="coerce")
    df = df.dropna(subset=["Сумма платежа"])

    # Фильтруем только положительные суммы как расходы
    df = df[df["Сумма платежа"] > 0]

    # Фильтруем по дате
    df_filtered = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= end_date)]

    if df_filtered.empty:
        return {"cards": []}

    cards_summary = []
    for card_number, group in df_filtered.groupby("Номер карты"):
        if not isinstance(card_number, str) or not card_number.strip():
            continue

        last_digits = get_mask_card_number(card_number.strip())
        if not last_digits:
            continue

        total_spent = group["Сумма платежа"].sum()
        total_spent = round(float(total_spent), 2)
        cashback = round(total_spent * 0.01, 2)

        cards_summary.append({"last_digits": last_digits, "total_spent": total_spent, "cashback": cashback})

    # Сортировка по last_digits для стабильности тестов
    cards_summary.sort(key=lambda x: x["last_digits"])

    return {"cards": cards_summary}

5.7. Чтобы узнать курс валют воспользуемся модулем exchange_rate и помощью API:
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

5.8. Чтобы узнать стоимость акций воспользуемся модулем stock_price и API:
# Работа со стоимостью акций из S&P500
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

5.9. Узнаем топ-5 транзакций с помощью модуля transactions:
# Выбираем топ-5 транзакций по сумме платежа.
def transactions_operations():
    """
    Вычисляет и возвращает топ-5 транзакций по сумме платежа в формате:
    {
        "top_transactions": [
            {
                "date": "21.12.2021",
                "amount": 1198.23,
                "category": "Переводы",
                "description": "..."
            },
            ...
        ]
    }
    """
    logger.info("Запуск функции transactions_operations()")

    transactions_data = list(read_operation_excel())

    if not transactions_data:
        logger.warning("Данные из Excel отсутствуют")
        return {"top_transactions": []}

    try:
        df = pd.DataFrame(transactions_data)
        required_cols = {"Дата операции", "Сумма платежа", "Категория", "Описание"}
        missing = required_cols - set(df.columns)
        if missing:
            logger.error(f"Отсутствуют обязательные столбцы: {missing}")
            return {"top_transactions": []}

        # Преобразование суммы платежа в числовой формат
        df["Сумма платежа"] = pd.to_numeric(df["Сумма платежа"], errors="coerce")
        # Преобразование даты
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        df["Дата операции"] = df["Дата операции"].dt.strftime("%d.%m.%Y")

        # Фильтрация: убираем NaN и отрицательные/нулевые суммы
        df = df.dropna(subset=["Сумма платежа", "Дата операции"])
        df = df[df["Сумма платежа"] > 0]

        # Сортировка по сумме (по убыванию) и выбор топ-5
        df_sorted = df.sort_values(by="Сумма платежа", ascending=False)
        top_5 = df_sorted.head(5)

        # Формируем результат
        top_transactions = [
            {
                "date": str(row["Дата операции"]),
                "amount": float(row["Сумма платежа"]),
                "category": str(row["Категория"]) if pd.notna(row["Категория"]) else "",
                "description": str(row["Описание"]) if pd.notna(row["Описание"]) else "",
            }
            for _, row in top_5.iterrows()
        ]

        logger.info(f"Успешно обработано {len(top_transactions)} транзакций")
        return {"top_transactions": top_transactions}

    except Exception as e:
        logger.exception(f"Неожиданная ошибка в transactions_operations(): {e}")
        return {"top_transactions": []}

5.10. Выведем простой поиск в модуле services:
def simple_search(query: str) -> str:
    """
    Функция сервиса «Простой поиск».
    Принимает строку-запрос и возвращает JSON-ответ со всеми транзакциями,
    содержащими запрос в описании или категории.
    """
    try:
        # Загружаем данные из Excel
        transactions = read_operation_excel()

        if not transactions:
            logger.warning("Файл с транзакциями пуст или не найден")
            return json.dumps({"transactions": []}, ensure_ascii=False)

        # Фильтруем транзакции по запросу
        filtered_transactions = [
            tx
            for tx in transactions
            if query.lower() in str(tx.get("Описание", "")).lower()
            or query.lower() in str(tx.get("Категория", "")).lower()
        ]

        # Логируем результат
        logger.info(f"Найдено {len(filtered_transactions)} транзакций по запросу '{query}'")

        # Возвращаем JSON-ответ
        return json.dumps({"transactions": filtered_transactions}, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка при выполнении поиска: {str(e)}")
        return json.dumps({"error": "Внутренняя ошибка сервера"}, ensure_ascii=False)

5.11. Создадим отчеты в модуле reports:
# Путь к директории для отчетов
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)


# Декоратор для записи результата в файл
def report_to_file(filename: Optional[str] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Декоратор {func.__name__} начал работу")

            result = func(*args, **kwargs)

            # Определяем имя файла
            if filename:
                report_name = filename if filename.endswith(".txt") else f"{filename}.txt"
            else:
                report_name = f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            report_path = os.path.join(REPORTS_DIR, report_name)

            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    if isinstance(result, pd.DataFrame):
                        f.write(result.to_string(index=False))
                    else:
                        f.write(str(result))
                logger.info(f"Отчет успешно записан в файл: {report_path}")
            except Exception as e:
                logger.error(f"Ошибка при записи файла {report_path}: {str(e)}")
                raise

            return result

        return wrapper

    return decorator


# Функция отчета: траты по категории за последние 3 месяца
@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    """
    logger.info(f"Начинаем обработку отчета по категории '{category}'")

    if transactions.empty:
        logger.warning("DataFrame с транзакциями пуст")
        return pd.DataFrame()

    # Приводим 'Дата операции' к datetime
    transactions_copy = transactions.copy()
    transactions_copy["Дата операции"] = pd.to_datetime(
        transactions_copy["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    # Пробуем альтернативный формат даты
    if transactions_copy["Дата операции"].isna().any():
        transactions_copy["Дата операции"] = pd.to_datetime(
            transactions_copy["Дата операции"], format="%d.%m.%Y", errors="coerce"
        )

    # Определяем целевую дату
    if date is None:
        target_date = datetime.now()
    else:
        formats = ["%d.%m.%Y %H:%M:%S", "%d.%m.%Y"]
        target_date = None
        for fmt in formats:
            try:
                target_date = datetime.strptime(date, fmt)
                break
            except ValueError:
                continue
        if target_date is None:
            error_msg = f"Некорректный формат даты: {date}. Ожидается ДД.ММ.ГГГГ или ДД.ММ.ГГГГ ЧЧ:ММ:СС"
            logger.error(error_msg)
            raise ValueError(error_msg)

    start_date = target_date - timedelta(days=90)
    logger.info(f"Период отчета: с {start_date} по {target_date}")

    # Фильтруем транзакции
    filtered = transactions_copy[
        (transactions_copy["Категория"] == category)
        & (transactions_copy["Сумма платежа"] < 0)
        & (transactions_copy["Дата операции"] >= start_date)
        & (transactions_copy["Дата операции"] <= target_date)
    ].copy()

    logger.info(f"Найдено {len(filtered)} транзакций для категории '{category}'")

    if filtered.empty:
        logger.info(f"Нет расходов для категории '{category}' в указанном диапазоне дат")
        return filtered

    # Сортировка и возвращение результата
    filtered = filtered.sort_values(by="Дата операции", ascending=False)
    return filtered.head(5)

5.12. Прописаны тесты для указанных функций в модулях test_cards, test_exchange_rate, test_mask, 
test_read_excel, test_reports, test_services, test_stock_price, test_transactions:
@pytest.mark.parametrize(
    "input_data, cutoff_date, expected",
    [
        # Тест 1: Одна транзакция, одна карта
        (
            [{"Дата операции": "31.12.2021 14:20:00", "Сумма платежа": 2500.0, "Номер карты": "1234567890123456"}],
            "2021-12-31 23:59:59",
            {"cards": [{"last_digits": "3456", "total_spent": 2500.0, "cashback": 25.0}]},
        ),
        # Тест 2: Две транзакции на одной карте
        (
            [
                {"Дата операции": "15.12.2021 10:00:00", "Сумма платежа": 1200.0, "Номер карты": "1234567890123456"},
                {"Дата операции": "25.12.2021 16:30:00", "Сумма платежа": 800.0, "Номер карты": "1234567890123456"},
            ],
            "2021-12-31 23:59:59",
            {"cards": [{"last_digits": "3456", "total_spent": 2000.0, "cashback": 20.0}]},
        ),
        # Тест 3: Две карты
        (
            [
                {"Дата операции": "05.12.2021 09:15:00", "Сумма платежа": 1500.0, "Номер карты": "1234567890123456"},
                {"Дата операции": "10.12.2021 11:20:00", "Сумма платежа": 700.0, "Номер карты": "9876543210987654"},
            ],
            "2021-12-31 23:59:59",
            {
                "cards": [
                    {"last_digits": "3456", "total_spent": 1500.0, "cashback": 15.0},
                    {"last_digits": "7654", "total_spent": 700.0, "cashback": 7.0},
                ]
            },
        ),
        # Тест 4: Транзакции до начала месяца — игнорируются
        (
            [
                {"Дата операции": "28.11.2021 18:45:00", "Сумма платежа": 1000.0, "Номер карты": "1234567890123456"},
                {"Дата операции": "02.12.2021 12:00:00", "Сумма платежа": 500.0, "Номер карты": "1234567890123456"},
            ],
            "2021-12-15 23:59:59",
            {"cards": [{"last_digits": "3456", "total_spent": 500.0, "cashback": 5.0}]},
        ),
        # Тест 5: Транзакции в периоде — учитываются
        (
            [
                {"Дата операции": "10.12.2021 10:30:00", "Сумма платежа": 1000.0, "Номер карты": "1234567890125814"},
                {"Дата операции": "25.11.2021 15:00:00", "Сумма платежа": 500.0, "Номер карты": "1234567890125814"},
            ],
            "2021-12-15 23:59:59",
            {"cards": [{"last_digits": "5814", "total_spent": 1000.0, "cashback": 10.0}]},
        ),
        # Тест 6: Нет транзакций в периоде
        (
            [
                {"Дата операции": "20.11.2021 10:00:00", "Сумма платежа": 300.0, "Номер карты": "1234567890123456"},
                {"Дата операции": "05.01.2022 08:00:00", "Сумма платежа": 400.0, "Номер карты": "1234567890123456"},
            ],
            "2021-12-15 23:59:59",
            {"cards": []},
        ),
        # Тест 7: Некорректная дата — пропускается
        (
            [
                {"Дата операции": "invalid-date", "Сумма платежа": 100.0, "Номер карты": "1234567890123456"},
                {"Дата операции": "15.12.2021 14:00:00", "Сумма платежа": 200.0, "Номер карты": "1234567890123456"},
            ],
            "2021-12-15 23:59:59",
            {"cards": [{"last_digits": "3456", "total_spent": 200.0, "cashback": 2.0}]},
        ),
    ],
)
@patch("src.cards.pd.read_excel")
def test_get_cards_summary(mock_read_excel, mock_transactions, input_data, cutoff_date, expected):
    # Создаём DataFrame через фикстуру из conftest.py
    mock_read_excel.return_value = mock_transactions(input_data)
    result = get_cards_summary(cutoff_date)

    # Сортируем для стабильного сравнения
    result["cards"].sort(key=lambda x: x["last_digits"])
    expected["cards"].sort(key=lambda x: x["last_digits"])

    assert result == expected, f"Expected {expected}, got {result}"

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

@pytest.fixture
def valid_card_numbers():
    """Фикстура: корректные номера карт (только цифры)"""
    return [
        "1234567812345678",
        "1111222233334444",
        "9999",
        "5",
        "",
    ]


@pytest.fixture
def invalid_card_strings():
    """Фикстура: некорректные строки с буквами/символами — но с цифрами"""
    return [
        "1234a5678b9012",  # буквы + цифры
        "1234-5678-9012-3456",  # дефисы
        "1234 5678 9012 3456",  # пробелы
        "!@#$1234%^&*5678",  # спецсимволы
    ]


@pytest.fixture
def invalid_types():
    """Фикстура: неверные типы данных"""
    return [
        None,
        12345678,
        [],
        {},
        3.14,
    ]


@pytest.fixture
def mock_logger():
    """Фикстура: мок для логгера"""
    with patch("src.mask.logger") as mock:
        yield mock


@pytest.mark.parametrize(
    "card_number, expected",
    [
        ("1234567812345678", "5678"),
        ("1111222233334444", "4444"),
        ("9999", "9999"),
        ("5", "5"),
        ("", ""),
    ],
)
def test_get_mask_card_number_valid(card_number, expected):
    """Тест: корректные номера карт — возвращают последние 4 цифры"""
    result = get_mask_card_number(card_number)
    assert result == expected


@pytest.mark.parametrize(
    "card_number, expected",
    [
        ("1234a5678b9012", "9012"),
        ("1234-5678-9012-3456", "3456"),
        ("1234 5678 9012 3456", "3456"),
        ("!@#$1234%^&*5678", "5678"),
    ],
)
def test_get_mask_card_number_invalid_string_with_digits(card_number, expected, invalid_card_strings):
    """Тест: строки с символами — извлекаются цифры, возвращаются последние 4"""
    result = get_mask_card_number(card_number)
    assert result == expected


@pytest.mark.parametrize("invalid_input", [None, 12345678, [], {}, 3.14])
def test_get_mask_card_number_invalid_type(invalid_input, invalid_types):
    """Тест: неверные типы данных — возвращают пустую строку"""
    result = get_mask_card_number(invalid_input)
    assert result == ""


def test_get_mask_card_number_logs_success(mock_logger):
    """Тест: успешная обработка логируется как INFO с правильным форматом"""
    card_number = "1234567812345678"
    get_mask_card_number(card_number)
    mock_logger.info.assert_called_once_with(f"Извлечены последние цифры: '{card_number}' → '5678'")


def test_get_mask_card_number_logs_invalid_type(mock_logger):
    """Тест: неверный тип логируется как ERROR"""
    get_mask_card_number(None)
    mock_logger.error.assert_called_once_with(
        "Неверный тип номера карты: <class 'NoneType'> — ожидается str, получено: None"
    )


def test_get_mask_card_number_empty_string_no_log(mock_logger):
    """Тест: пустая строка не вызывает логирование (т.к. нет цифр)"""
    get_mask_card_number("")
    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()

# Фикстура для генерации тестовых данных
@pytest.fixture
def sample_excel_data():
    return [
        {"Дата операции": "01.01.2024", "Сумма платежа": -100.0, "Категория": "Продукты"},
        {"Дата операции": "02.01.2024", "Сумма платежа": -50.0, "Категория": "Транспорт"},
        {"Дата операции": "03.01.2024", "Сумма платежа": 200.0, "Категория": "Зарплата"},
    ]


# Фикстура для создания mock Excel файла
@pytest.fixture
def mock_excel_file(sample_excel_data):
    df = pd.DataFrame(sample_excel_data)
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    return excel_file


# Параметризированный тест для успешного чтения
@pytest.mark.parametrize("file_exists", [True, False])
def test_read_operation_excel_success(file_exists, sample_excel_data, mock_excel_file, capfd):
    with patch("pandas.read_excel") as mock_read_excel:
        if file_exists:
            # Настройка mock для успешного чтения
            mock_read_excel.return_value = pd.DataFrame(sample_excel_data)

            result = read_operation_excel()

            # Проверки
            assert isinstance(result, list)
            assert len(result) == 3
            assert result[0]["Категория"] == "Продукты"
            assert result[1]["Сумма платежа"] == -50.0
            mock_read_excel.assert_called_once_with(FILE_PATH)
        else:
            # Настройка mock для FileNotFoundError
            mock_read_excel.side_effect = FileNotFoundError(f"File {FILE_PATH} not found")

            result = read_operation_excel()

            # Проверяем вывод в stdout
            captured = capfd.readouterr()
            assert f"Файл не найден: {FILE_PATH}" in captured.out
            assert result == []


# Тест для обработки других исключений
def test_read_operation_excel_exception(capfd):
    with patch("pandas.read_excel") as mock_read_excel:
        test_exception = Exception("Test exception")
        mock_read_excel.side_effect = test_exception

        result = read_operation_excel()

        # Проверяем вывод в stdout
        captured = capfd.readouterr()
        assert "Ошибка при чтении Excel файла: Test exception" in captured.out
        assert result == []


# Тест для проверки структуры возвращаемых данных
def test_read_operation_excel_structure(sample_excel_data):
    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = pd.DataFrame(sample_excel_data)

        result = read_operation_excel()

        # Проверяем структуру данных
        assert all(isinstance(item, dict) for item in result)
        assert all("Дата операции" in item for item in result)
        assert all("Сумма платежа" in item for item in result)
        assert all("Категория" in item for item in result)


# Тест для пустого Excel файла
def test_read_operation_excel_empty():
    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = pd.DataFrame()

        result = read_operation_excel()

        assert isinstance(result, list)
        assert len(result) == 0

def test_spending_by_category_returns_correct_count():
    """Тестирует, что функция возвращает правильное количество строк."""
    # Создаем тестовые данные за 90 дней (октябрь-декабрь 2021)
    end_date = datetime.strptime("31.12.2021", "%d.%m.%Y")
    start_date = end_date - timedelta(days=90)

    # Генерируем даты в диапазоне в правильном формате
    dates = pd.date_range(start_date, end_date, freq="10D").strftime("%d.%m.%Y %H:%M:%S")

    test_data = {
        "Дата операции": dates,
        "Категория": ["Супермаркеты"] * len(dates),
        "Сумма платежа": [-1000] * len(dates),
    }
    df = pd.DataFrame(test_data)

    result = spending_by_category(df, "Супермаркеты", "31.12.2021")
    assert len(result) > 0, f"Ожидалось не менее 1 строки, получено {len(result)}"
    assert all(result["Категория"] == "Супермаркеты")


def test_spending_by_category_filters_by_category():
    """Тестирует, что функция фильтрует по правильной категории."""
    # Создаем тестовые данные за 90 дней
    end_date = datetime.strptime("31.12.2021", "%d.%m.%Y")
    start_date = end_date - timedelta(days=90)

    # Генерируем даты в диапазоне в правильном формате
    dates = pd.date_range(start_date, end_date, freq="10D").strftime("%d.%m.%Y %H:%M:%S")

    test_data = {
        "Дата операции": dates,
        "Категория": ["Супермаркеты"] * len(dates),
        "Сумма платежа": [-1000] * len(dates),
    }
    df = pd.DataFrame(test_data)

    # Добавляем несколько записей другой категории
    df.loc[1, "Категория"] = "Кафе"
    df.loc[3, "Категория"] = "Кафе"

    result = spending_by_category(df, "Супермаркеты", "31.12.2021")

    # Проверяем только фильтрацию по категории
    assert all(result["Категория"] == "Супермаркеты"), "Все строки должны быть категории 'Супермаркеты'"

    # Проверяем, что возвращено хотя бы 5 строк (как в текущем результате)
    assert len(result) >= 5, f"Ожидалось хотя бы 5 строк, получено {len(result)}"

    # Альтернативный вариант: проверяем, что количество не превышает ожидаемого
    assert len(result) <= len(dates) - 2, f"Количество строк не должно превышать {len(dates)-2}"

# Фикстура для создания тестовых транзакций
@pytest.fixture
def mock_transactions():
    return [
        {
            "Описание": "Покупка продуктов в Пятерочке",
            "Категория": "Супермаркет",
            "Сумма": 1500.00,
            "Дата": "2023-05-15",
        },
        {"Описание": "Поездка на каршеринге", "Категория": "Транспорт", "Сумма": 850.50, "Дата": "2023-05-16"},
        {"Описание": "Оплата интернета", "Категория": "Коммунальные услуги", "Сумма": 1200.00, "Дата": "2023-05-17"},
    ]


# Фикстура для mock-ирования read_operation_excel
@pytest.fixture
def mock_read_excel(mock_transactions):
    with patch("src.services.read_operation_excel", return_value=mock_transactions) as mock:
        yield mock


# Фикстура для mock-ирования logger
@pytest.fixture
def mock_logger():
    with patch("src.services.logger") as mock:
        yield mock


# Параметризованный тест для успешного поиска
@pytest.mark.parametrize(
    "query,expected_count",
    [
        ("Супермаркет", 1),  # Поиск по категории
        ("Пятерочке", 1),  # Поиск по описанию
        ("каршеринг", 1),  # Поиск по части слова
        ("Транспорт", 1),  # Поиск по категории
        ("Несуществующий", 0),  # Пустой результат
        ("", 3),  # Пустой запрос - все транзакции
    ],
)
def test_simple_search_success(mock_read_excel, mock_logger, query, expected_count):
    """Тест успешного выполнения поиска"""
    # Проверяем, что mock возвращает правильные данные
    assert len(mock_read_excel.return_value) == 3

    result = simple_search(query)
    data = json.loads(result)

    # Проверяем структуру ответа
    assert "transactions" in data
    assert len(data["transactions"]) == expected_count

    # Проверяем логирование
    if expected_count == 0:
        mock_logger.info.assert_called_with(f"Найдено {expected_count} транзакций по запросу '{query}'")
    else:
        mock_logger.info.assert_called_with(f"Найдено {expected_count} транзакций по запросу '{query}'")


# Тест обработки пустого файла
def test_simple_search_empty_file(mock_read_excel, mock_logger):
    """Тест обработки пустого файла с транзакциями"""
    # Переопределяем mock для возврата пустого списка
    with patch("src.services.read_operation_excel", return_value=[]):
        result = simple_search("Супермаркет")
        data = json.loads(result)

        assert data["transactions"] == []
        mock_logger.warning.assert_called_with("Файл с транзакциями пуст или не найден")


# Тест обработки ошибок
def test_simple_search_exception(mock_read_excel, mock_logger):
    """Тест обработки исключений"""
    # Переопределяем mock для генерации исключения
    with patch("src.services.read_operation_excel", side_effect=Exception("Test error")):
        result = simple_search("Супермаркет")
        data = json.loads(result)

        assert data["error"] == "Внутренняя ошибка сервера"
        mock_logger.error.assert_called_with("Ошибка при выполнении поиска: Test error")


# Тест формата вывода
def test_simple_search_output_format(mock_read_excel):
    """Тест формата вывода JSON"""
    result = simple_search("Супермаркет")
    data = json.loads(result)

    # Проверяем, что вывод содержит все необходимые поля
    assert isinstance(data, dict)
    assert "transactions" in data
    assert isinstance(data["transactions"], list)

    # Проверяем первый элемент
    if data["transactions"]:
        tx = data["transactions"][0]
        assert "Описание" in tx
        assert "Категория" in tx
        assert "Сумма" in tx
        assert "Дата" in tx


# Тест регистронезависимого поиска
def test_simple_search_case_insensitive(mock_read_excel):
    """Тест регистронезависимого поиска"""
    # Проверяем поиск в разном регистре
    for query in ["супермаркет", "СУПЕРМАРКЕТ", "СуПеРмАрКеТ"]:
        result = simple_search(query)
        data = json.loads(result)
        assert len(data["transactions"]) == 1


# Тест поиска по части слова
def test_simple_search_partial_match(mock_read_excel):
    """Тест поиска по части слова"""
    result = simple_search("прод")
    data = json.loads(result)
    assert len(data["transactions"]) == 1
    assert "продуктов" in data["transactions"][0]["Описание"].lower()

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

def test_transactions_operations_valid_data(valid_transactions_data):
    """Тест: корректные данные → возвращает топ-5 положительных транзакций, отсортированных по убыванию."""
    with patch("src.transactions.read_operation_excel", return_value=valid_transactions_data):
        result = transactions_operations()

        assert "top_transactions" in result
        assert len(result["top_transactions"]) == 5

        # Проверяем суммы в порядке убывания
        amounts = [t["amount"] for t in result["top_transactions"]]
        assert amounts == [5000.0, 3000.5, 1500.0, 1198.23, 899.99]

        # Проверяем поля по позициям
        assert result["top_transactions"][0]["date"] == "21.12.2021"
        assert result["top_transactions"][1]["category"] == "Транспорт"
        assert result["top_transactions"][3]["description"] == "Доставка еды"
        assert result["top_transactions"][4]["description"] == "Такси"


def test_transactions_operations_missing_columns(missing_columns_data):
    """
    Тест: в данных отсутствует обязательный столбец 'Сумма платежа' у некоторых транзакций.
    Функция должна:
    - пропускать транзакции без 'Сумма платежа'
    - сортировать оставшиеся по убыванию суммы
    - возвращать не более 5 самых крупных
    """
    with patch("src.transactions.read_operation_excel", return_value=missing_columns_data):
        result = transactions_operations()

        # Проверяем, что структура ответа корректна
        assert "top_transactions" in result
        assert isinstance(result["top_transactions"], list)

        # В данных только 1 транзакция с 'Сумма платежа' ожидаем 1
        assert len(result["top_transactions"]) == 1

        # Проверяем содержимое единственной валидной транзакции
        tx = result["top_transactions"][0]
        assert tx["date"] == "21.12.2021"
        assert tx["amount"] == 5000.0
        assert tx["category"] == "Рестораны"
        assert tx["description"] == ""  # поле отсутствовало подставлено как пустая строка


@pytest.mark.parametrize(
    "transaction, expected_count",
    [
        (
            {
                "Дата операции": "21.12.2021 14:30:00",
                "Сумма платежа": "5000.0",
                "Категория": "Рестораны",
                "Описание": "Ужин",
            },
            1,
        ),
        (
            {
                "Дата операции": "21.12.2021 14:30:00",
                "Сумма платежа": "-2000.0",
                "Категория": "Перевод",
                "Описание": "Другу",
            },
            0,
        ),
        ({"Дата операции": "invalid-date", "Сумма платежа": "1000.0", "Категория": "Еда", "Описание": "Пицца"}, 0),
        ({"Дата операции": "21.12.2021 14:30:00", "Сумма платежа": "abc", "Категория": "Еда", "Описание": "Пицца"}, 0),
    ],
)
def test_transactions_operations_single_transaction(transaction, expected_count):
    """Параметризованный тест: фильтрация транзакций по валидности"""
    with patch("src.transactions.read_operation_excel", return_value=[transaction]):
        result = transactions_operations()
        assert len(result["top_transactions"]) == expected_count


def test_transactions_operations_empty_data(empty_transactions_data):
    """Тест: пустой список → возвращает пустой top_transactions"""
    with patch("src.transactions.read_operation_excel", return_value=empty_transactions_data):
        result = transactions_operations()
        assert result["top_transactions"] == []


def test_transactions_operations_invalid_data(invalid_data_data):
    """Тест: отрицательные суммы и неверная дата → фильтруются"""
    with patch("src.transactions.read_operation_excel", return_value=invalid_data_data):
        result = transactions_operations()
        assert len(result["top_transactions"]) == 0


def test_transactions_operations_mixed_data(mixed_data):
    """Тест: смешанные данные — возвращаются только валидные положительные"""
    with patch("src.transactions.read_operation_excel", return_value=mixed_data):
        result = transactions_operations()
        assert len(result["top_transactions"]) == 2
        assert result["top_transactions"][0]["amount"] == 5000.0
        assert result["top_transactions"][1]["amount"] == 3000.0
