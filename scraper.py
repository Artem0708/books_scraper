# Библиотеки, которые могут вам понадобиться
# При необходимости расширяйте список
import time
import requests
import schedule
from bs4 import BeautifulSoup


def get_book_data(book_url: str) -> dict:
    """
    Парсит данные о книге с указанной страницы сайта Books to Scrape.

    Функция получает HTML-страницу книги, извлекает основную информацию о книге
    (название, цена, рейтинг, наличие, описание) и дополнительные характеристики
    из таблицы Product Information.

    Args:
        book_url (str): URL-адрес страницы книги для парсинга

    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    try:
        # Отправляем запрос к странице книги
        response = requests.get(book_url, timeout=5)
        response.raise_for_status()  # Проверяем успешность запроса

        # Создаем объект BeautifulSoup для парсинга
        soup = BeautifulSoup(response.content, 'html.parser')

        # Словарь для хранения данных о книге
        book_data = {}

        # 1. Название книги
        title_element = soup.find('h1')
        book_data['title'] = title_element.text.strip() if title_element else 'N/A'

        # 2. Цена
        price_element = soup.find('p', class_='price_color')
        book_data['price'] = price_element.text.strip() if price_element else 'N/A'

        # 3. Рейтинг
        rating_element = soup.find('p', class_='star-rating')
        if rating_element:
            rating_classes = rating_element.get('class', [])
            # Ищем класс, соответствующий рейтингу (One, Two, Three, Four, Five)
            rating = next((cls for cls in rating_classes if cls in ['One', 'Two', 'Three', 'Four', 'Five']), 'N/A')
            book_data['rating'] = rating
        else:
            book_data['rating'] = 'N/A'

        # 4. Наличие и количество
        stock_element = soup.find('p', class_='instock availability')
        book_data['stock'] = stock_element.text.strip() if stock_element else 'N/A'

        # 5. Описание
        description_element = soup.find('div', id='product_description')
        if description_element:
            # Описание находится в следующем sibling элементе
            description = description_element.find_next_sibling('p')
            book_data['description'] = description.text.strip() if description else 'N/A'
        else:
            book_data['description'] = 'N/A'

        # 6. Дополнительные характеристики из таблицы Product Information
        product_table = soup.find('table', class_='table table-striped')
        if product_table:
            rows = product_table.find_all('tr')
            for row in rows:
                header = row.find('th')
                value = row.find('td')
                if header and value:
                    key = header.text.strip().lower().replace(' ', '_')
                    book_data[key] = value.text.strip()

        return book_data

    except requests.RequestException as e:
        print(f"Ошибка при запросе к {book_url}: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при парсинге данных: {e}")
        return None
    # КОНЕЦ ВАШЕГО РЕШЕНИЯ


def scrape_books(is_save=False) -> list:
    """
    Проходит по всем страницам каталога Books to Scrape и парсит данные о книгах.

    Использует функцию get_book_data для получения информации о каждой книге.
    При необходимости сохраняет результат в файл books_data.txt.

    Args:
        save_to_file (bool): Если True, сохраняет результаты в файл books_data.txt.

    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    books_data = []
    page_number = 1

    while True:
        url = base_url.format(page_number)
        response = requests.get(url)

        # Если страница не найдена — значит, книги закончились
        if response.status_code == 404:
            break

        print(f"Обрабатываю страницу {page_number}...")

        soup = BeautifulSoup(response.content, "html.parser")
        book_links = soup.select("h3 > a")

        if not book_links:
            break

        # Проходим по всем книгам на странице
        for link in book_links:
            relative_url = link.get("href")
            book_url = "http://books.toscrape.com/catalogue/" + relative_url.replace("../", "")
            book_data = get_book_data(book_url)

            if book_data:
                books_data.append(book_data)

            time.sleep(1)

        page_number += 1

    # Сохранение в файл, если флаг установлен
    if is_save:
        try:
            with open("books_data.txt", "w", encoding="utf-8") as file:
                for book in books_data:
                    file.write(str(book) + "\n")
            print("Данные успешно сохранены в books_data.txt")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")

    print(f"Всего собрано книг: {len(books_data)}")
    return books_data
    # КОНЕЦ ВАШЕГО РЕШЕНИЯ