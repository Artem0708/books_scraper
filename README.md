# Парсер книг (HW-3)

Проект для сбора данных с сайта `books.toscrape.com`.

## Цель

Сбор информации о книгах (название, цена, наличие, рейтинг и т.д.) со всех страниц каталога.

## Инструкция по запуску

1.  Клонируйте репозиторий:
    `git clone https://github.com/VASH_LOGIN/books_scraper.git`
2.  Перейдите в папку:
    `cd books_scraper`
3.  Создайте и активируйте виртуальное окружение:
    `python -m venv venv`
    `.\venv\Scripts\activate`
4.  Установите зависимости:
    `pip install -r requirements.txt`
5.  Запустите парсер:
    `python scraper.py`

## Используемые библиотеки

-   requests
-   beautifulsoup4
-   schedule
-   pytest (для тестов)

## Демонстрация Pull Request