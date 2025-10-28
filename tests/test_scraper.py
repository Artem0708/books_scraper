import pytest
import requests  # Нужен для типа исключения RequestException
from scraper import scrape_books, get_book_data
import scraper  # Нам нужен импорт всего модуля для корректного мокинга
import time  # Нужен для мокинга time.sleep


# Фиктивный класс ответа, который мы будем использовать в моках
class FakeResponse:
    """
    Поддельный объект Response, который имитирует
    поведение ответа от requests.get().
    """

    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
        # ИСПРАВЛЕНИЕ 1: Добавляем атрибут .content, который использует BeautifulSoup
        self.content = text.encode('utf-8')

    def raise_for_status(self):
        """Имитирует проверку статуса. Выбрасывает исключение для 4xx/5xx."""
        if self.status_code >= 400:
            raise requests.RequestException(f"HTTP Error {self.status_code}")


# --- Тест 1 (Исправленный) ---

def test_scrape_books_mocked(monkeypatch, tmp_path):
    """
    Тест функции scrape_books без реальных запросов.
    Проверяем, что функция вызывает get_book_data и возвращает список.
    """

    # 1️⃣ Подменим requests.get, который используется в scrape_books
    #    для получения страницы со *списком* книг.
    def fake_get_list_page(url, *args, **kwargs):
        # Возвращаем маленький HTML с одной книгой и без кнопки "next"
        html = """
        <html>
        <body>
            <h3><a href="book_1.html" title="Test Book">Test Book</a></h3>
            <!-- Нет кнопки 'next', цикл парсинга завершится -->
        </body>
        </html>
        """
        # Имитируем вторую страницу как 404, чтобы цикл завершился
        if "page-2" in url:
            return FakeResponse("Not Found", 404)

        return FakeResponse(html)

    # `scrape_books` импортирует `requests` напрямую, поэтому мокаем "requests.get"
    # ИСПРАВЛЕНИЕ: мокаем scraper.requests.get, так как import requests в scraper.py
    monkeypatch.setattr("scraper.requests.get", fake_get_list_page)

    # 2️⃣ Подменим get_book_data — она не должна ходить в сеть.
    #    Пусть просто возвращает фиктивные данные.
    monkeypatch.setattr(
        "scraper.get_book_data",
        lambda url: {"title": "Test Book", "price": "£10.00", "availability": "In stock"}
    )

    # 3️⃣ ИСПРАВЛЕНИЕ: Запускаем парсер с аргументами,
    #    соответствующими scraper.py (is_save=False)
    #    и проверяем ВОЗВРАЩАЕМОЕ значение, а не файл.
    books_list = scrape_books(is_save=False)

    # 4️⃣ Проверяем, что функция вернула ожидаемые данные
    assert isinstance(books_list, list)
    assert len(books_list) == 1
    assert books_list[0]["title"] == "Test Book"
    assert books_list[0]["price"] == "£10.00"
    assert books_list[0]["availability"] == "In stock"


# --- Тест 2 (Новый) ---

def test_get_book_data_success(monkeypatch):
    """
    Тест функции get_book_data на успешный парсинг страницы книги.
    """
    # 1️⃣ Готовим фиктивный HTML для страницы *одной* книги
    book_html = """
    <html>
        <body>
            <h1>Test Book Title</h1>
            <p class="price_color">£12.34</p>
            <p class="instock availability">
                In stock (10 available)
            </p>
            <!-- Добавим таблицу для полной проверки -->
            <table class="table table-striped">
                <tr><th>UPC</th><td>test_upc</td></tr>
            </table>
        </body>
    </html>
    """

    # 2️⃣ Подменяем requests.get ВНУТРИ модуля scraper
    #    Функция get_book_data вызывает requests.get, который был импортирован
    #    внутри scraper.py
    def fake_get_book_page(url, *args, **kwargs):
        return FakeResponse(book_html)

    monkeypatch.setattr("scraper.requests.get", fake_get_book_page)

    # 3️⃣ Подменяем time.sleep ВНУТРИ модуля scraper, чтобы тест не ждал
    # (Хотя get_book_data его не вызывает, это не помешает)
    monkeypatch.setattr("scraper.time.sleep", lambda seconds: None)

    # 4️⃣ Вызываем тестируемую функцию
    data = get_book_data("http://fake-book-url.com/book1.html")

    # 5️⃣ Проверяем результат
    assert data is not None
    assert isinstance(data, dict)
    assert data["title"] == "Test Book Title"
    assert data["price"] == "£12.34"
    # .strip() нужен, т.к. BeautifulSoup может захватить лишние пробелы и \n
    assert data["stock"] == "In stock (10 available)"
    assert data["upc"] == "test_upc"


# --- Тест 3 (Новый) ---

def test_get_book_data_network_failure(monkeypatch):
    """
    Тест функции get_book_data на случай ошибки сети (e.g., 404).
    """

    # 1️⃣ Настраиваем мок requests.get, чтобы он выбрасывал исключение
    def fake_get_error(url, *args, **kwargs):
        response = FakeResponse("Not Found", status_code=404)
        response.raise_for_status()  # Это выбросит исключение requests.RequestException

    # Мокаем именно `scraper.requests.get`
    monkeypatch.setattr("scraper.requests.get", fake_get_error)

    # 2️⃣ Подменяем time.sleep (хотя до него не дойдет, это хорошая практика)
    monkeypatch.setattr("scraper.time.sleep", lambda seconds: None)

    # 3️⃣ Вызываем функцию
    data = get_book_data("http://broken-url.com/book_not_found.html")

    # 4️⃣ Ожидаем, что функция корректно обработала ошибку и вернула None
    assert data is None

