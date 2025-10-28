# НАЧАЛО ВАШЕГО РЕШЕНИЯ

import schedule
import time
from scraper import scrape_books  # scraper.py в той же папке

def job_with_save():
    """
    Функция-обертка, которая вызывает парсер
    с флагом is_save=True.
    """
    print("--------------------")
    print(f"[{time.ctime()}] Запускаю плановый парсинг...")
    try:
        scrape_books(is_save=True)
        print(f"[{time.ctime()}] Парсинг успешно завершен.")
    except Exception as e:
        print(f"[{time.ctime()}] Ошибка во время парсинга: {e}")
    print("--------------------")

schedule.clear()

schedule.every().day.at("19:00").do(job_with_save)

print(f"[{time.ctime()}] Планировщик запущен.")
print("Ожидаю времени для запуска задачи...")

try:
    while True:
        schedule.run_pending()
        now = time.localtime()
        if now.tm_hour == 18 and now.tm_min >= 55:
            time.sleep(10)
        elif now.tm_hour == 18 and now.tm_min < 55:
            time.sleep(300)
        else:
            time.sleep(3600)
except KeyboardInterrupt:
    print(f"\n[{time.ctime()}] Планировщик остановлен вручную.")

# КОНЕЦ ВАШЕГО РЕШЕНИЯ