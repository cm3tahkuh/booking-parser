# Booking.com Parser

This is simple scraper that uses Playwright to extract data from Booking.com

This example is made for educational purposese.

This scrapit is easy to customize.

check both Excel & CSV files (hotels_list) to see how final data will look like. 

## To Install:
- (Optional: create & activate a virtual environment) `python -m venv myenv`, then `myenv\Scripts\activate`

- `pip install -r requirements.txt`
- `pip install playwright`
- `playwright install chromium`
- `pip install pandas`
- `pip install openpyxl`

## to Run:
- `При каждом запуске cmd из проводника в первую очередь нужно писать` `myenv\Scripts\activate``
- Язык на сайте ставим English(US) - обязательно
- Сначала парсим отели - `python booking_scraper1.py`
- Ищем emails - `python booking_finder_email.py` 


