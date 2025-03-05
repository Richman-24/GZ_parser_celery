'''
1. Получить список ссылок +
2. Модифицировать их в Xml +
3. Пройти по каждой ссылке и найти значение publishDTInEIS
4. Вывести в консоль: f"{publishDTInEIS}: {link}"

5. Распараллелить задачи через Celery.

6. Составить документацию readme
'''
import time

from bs4 import BeautifulSoup
import requests
import xmltodict


PAGE_RANGE = 2

def replace_url_part(url):
    """Модифицирует ссылку """
    new_url = url.replace('view.html', 'viewXml.html')
    return new_url


def parse_for_url(page_range):
    res = []
    
    for page in range(1, page_range+1):
        url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber={page}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            print("Запрос успешен!")
        else:
            print("parse_for_url: Ошибка при запросе:", response.status_code)
            exit()
   
        soup = BeautifulSoup(response.content, 'lxml')

        links = soup.select("div.registry-entry__header-top__icon a")
        
        if links:
            for id, link in enumerate(links):
                if id % 2 != 0:
                    href = link.get('href')
                    if href:
                        href_w = replace_url_part(href)
                        res.append(href_w)
                        print("Ссылка записана:", href_w)
        else:
            print("Ссылки не найдены на странице.")
        
        time.sleep(5)
    return res


def parse_pub_date(links):
    res = {}

    for idx, link in enumerate(links):
        url = "https://zakupki.gov.ru" + link
        print(url)
        
        response = requests.get(url)

        if response.status_code == 200:
            print(f"{idx} parse_pub_date - OK")
        else:
            print(f"Ошибка при запросе: {response.status_code}, {url}")
            continue

        xml_content = response.content
        xml_dict = xmltodict.parse(xml_content)
        
        root_key = next(iter(xml_dict))
        common_info = xml_dict[root_key].get("commonInfo", {})
        publish_dt_in_eis = common_info.get("publishDTInEIS")

        res[url] = publish_dt_in_eis
        time.sleep(5)
    
    return res


if __name__ == "__main__":
    links = parse_for_url(PAGE_RANGE)
    print()
    result = parse_pub_date(links)

    for k, v in result.items():
        print(f"{k}: {v}")