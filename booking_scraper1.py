
import pandas as pd
import time
import re
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        page_url = input("Введите URL страницы: ")

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(page_url, timeout=60000)

        # Создаем пустой DataFrame для хранения результатов
        df = pd.DataFrame(columns=['Hotel Name'])

        # Извлечение текста из h1 элемента
        total_hotels_text = page.locator('h1[aria-live="assertive"]').inner_text()
        print(f"Извлеченный текст из h1: {total_hotels_text}")

        # Удаление пробелов из числа перед конвертацией
        cleaned_text = total_hotels_text.replace(' ', '')
        
        # Регулярное выражение для поиска числа без пробелов
        match = re.search(r'\d+', cleaned_text)
        if match:
            total_hotels = int(match.group())
        else:
            print("Не удалось найти количество отелей.")
            browser.close()
            return

        print(f'Общее количество отелей: {total_hotels}')

        previous_height = 0
        reached_end = False

        # Допустимая погрешность (например, 5 отелей)
        tolerance = 5

        while len(df) < total_hotels - tolerance:
            # Парсим отели на текущей видимой части страницы
            hotels = page.locator('//div[@data-testid="property-card"]').all()

            for hotel in hotels:
                hotel_name = hotel.locator('//div[@data-testid="title"]').inner_text()

                # Проверка на дубликат в уже добавленных данных
                if hotel_name not in df['Hotel Name'].values:
                    # Добавляем данные в DataFrame
                    new_row = pd.DataFrame([[hotel_name]], columns=['Hotel Name'])
                    df = pd.concat([df, new_row], ignore_index=True)

                    # Записываем данные в CSV и Excel файлы
                    try:
                        df.to_csv('hotels_list.csv', index=False)
                        df.to_excel('hotels_list.xlsx', index=False)
                    except PermissionError as e:
                        print(f"Ошибка записи файла: {e}. Закройте файл и попробуйте снова.")

            # Проверяем наличие кнопки с указанными классами и скроллим вниз
            load_more_button = page.locator('button.dba1b3bddf.e99c25fd33.ea757ee64b.f1c8772a7d.ea220f5cdc.f870aa1234')
            if load_more_button.is_visible():
                load_more_button.click()
                time.sleep(5)  # Время ожидания для полной загрузки новых результатов
                continue  # Продолжаем после нажатия на кнопку
            else:
                # Скроллинг страницы до самого низа
                page.evaluate("window.scrollBy(0, window.innerHeight);")
                time.sleep(0.5)  # Задержка для более медленного скроллинга

            # Проверяем, достигли ли мы конца страницы
            new_height = page.evaluate("() => document.body.scrollHeight")
            if new_height == previous_height:
                reached_end = True
            else:
                previous_height = new_height

            # Если достигли конца страницы и количество отелей близко к числу из h1, завершаем работу
            if len(df) >= total_hotels - tolerance:
                reached_end = True

        print(f'Общее количество спарсенных отелей: {len(df)}')
        browser.close()

if __name__ == '__main__':
    main()
