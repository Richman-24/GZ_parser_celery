# script.py
from tasks import parse_page, parse_xml

def decorate_print(func):
    from art import tprint

    def wrapper(*args, **kwargs):
        print("### Начинаем парсинг ###")
        result = func()
        print("### Данные получены ###")
        tprint("ALL  DONE")
        return result
    return wrapper

@decorate_print
def main():
    page_range = 2
    main_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="

    results = []
    counter = 1
    for page in range(1, page_range + 1):
        url = f"{main_url}{page}"
        res = parse_page.delay(url).get()

        for link in res:
            results.append((link, parse_xml.delay(link)))
        
    for res in results:
        print(f"[{counter}] https://zakupki.gov.ru{res[0]}: {res[1].get()}")
        counter += 1

if __name__ == "__main__":
    main()