import pandas as pd
import time
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        page_url = input("Введите URL страницы: ")

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(page_url, timeout=60000)

        hotels_list = []

        while True:
            hotels = page.locator('//div[@data-testid="property-card"]').all()
            print(f'There are: {len(hotels)} hotels on this page.')

            for hotel in hotels:
                hotel_dict = {}
                hotel_dict = hotel.locator('//div[@data-testid="title"]').inner_text()
                hotels_list.append(hotel_dict)

            next_button = page.locator('button[aria-label="Next page"]')
            if next_button.is_enabled():
                next_button.click()
                time.sleep(3)
            else:
                break

        df = pd.DataFrame(hotels_list)


        try:
            existing_data = pd.read_csv('hotels_list.csv')
            df.to_csv('hotels_list.csv', mode='a', header=False, index=False)
            df.to_excel('hotels_list.xlsx', index=False)
        except FileNotFoundError:

            df.to_csv('hotels_list.csv', index=False)
            df.to_excel('hotels_list.xlsx', index=False)

        browser.close()


if __name__ == '__main__':
    main()
