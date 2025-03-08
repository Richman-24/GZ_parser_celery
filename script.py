# script.py
import time
from tasks import parse_page, parse_xml

def main():
    # Ссылки на страницы
    page_range = 2
    main_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="

    # Парсим первую страницу и получаем список ссылок
    for page in range(1, page_range + 1):
        url = f"{main_url}{page}"
        res = parse_page.delay(url).get()

        # Асинхронно парсим каждую ссылку из res
        for link in res:
            results = parse_xml.delay(link).get()
            print(f"Results from {link}: {results}")
        time.sleep(10)
if __name__ == "__main__":
    main()