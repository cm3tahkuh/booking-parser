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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        all_emails = []

        for query in search_queries:
            try:
                page.goto('https://www.google.com')
                page.fill('textarea[aria-label="Найти"]', query)
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
                        all_emails.extend(emails)
                    else:
                        print(f"No emails found for {query}. Skipping to next query.")
                else:
                    print(f"No search results for {query}. Skipping to next query.")
            except Exception as e:
                print(f"An error occurred while searching for {query}: {e}")
                continue

        browser.close()

    unique_emails = set(all_emails)
    emails_df = pd.DataFrame({'emails': list(unique_emails)})
    emails_df.to_csv('emails.csv', index=False)

if __name__ == '__main__':
    main()
