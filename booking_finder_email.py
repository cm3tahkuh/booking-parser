
import pandas as pd
import re
from playwright.sync_api import sync_playwright

def find_emails(page):
    content = page.content()
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    return emails

def main():
    data = pd.read_csv('hotels_list.csv')
    search_queries = data.iloc[:, 0].tolist()

    # Считываем уже существующие email-адреса, если файл существует
    existing_emails = set()
    try:
        existing_emails_df = pd.read_csv('emails.csv')
        existing_emails = set(existing_emails_df['Email'].tolist())
    except FileNotFoundError:
        # Если файла нет, создаем новый
        with open('emails.csv', 'w') as f:
            f.write('Email\n')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for query in search_queries:
            try:
                # Добавляем "official website" к каждому поисковому запросу
                modified_query = f"{query} official website"

                page.goto('https://www.google.com')
                page.fill('textarea[aria-label="Найти"]', modified_query)
                with page.expect_navigation():
                    page.press('textarea[aria-label="Найти"]', 'Enter')
                page.wait_for_load_state('load', timeout=60000)  # Увеличенный таймаут

                first_result_selector = 'h3'
                first_result = page.query_selector(first_result_selector)

                if first_result:
                    with page.expect_navigation(wait_until='load'):
                        first_result.click()

                    emails = find_emails(page)
                    if emails:
                        new_emails = [email for email in emails if email not in existing_emails]
                        if new_emails:
                            # Сохраняем только новые, уникальные email-адреса в CSV-файл
                            with open('emails.csv', 'a') as f:
                                for email in new_emails:
                                    f.write(f'{email}\n')
                                    existing_emails.add(email)  # Обновляем множество существующих email-адресов
                        else:
                            print(f"No new emails found for {modified_query}. Skipping to next query.")
                    else:
                        print(f"No emails found for {modified_query}. Skipping to next query.")
                else:
                    print(f"No search results for {modified_query}. Skipping to next query.")
            except Exception as e:
                print(f"An error occurred while searching for {modified_query}: {e}")
                continue

        browser.close()

if __name__ == '__main__':
    main()
