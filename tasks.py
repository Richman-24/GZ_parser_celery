# tasks.py
from typing import List

import requests
import xmltodict
from bs4 import BeautifulSoup
from celery import Celery, shared_task

app = Celery('parser', broker='redis://localhost:6379/0')

app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_annotations={
        'tasks.parse_page': {'rate_limit': '1/s'},
        'tasks.parse_xml': {'rate_limit': '1/s'},
    },
)

@shared_task(
    autoretry_for=(requests.exceptions.RequestException,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
)
def parse_page(url: str) -> List[str]:
    """парсит страницу https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber={page}"""
    
    result = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.210 Safari/537.36',
        'Accept-Language': 'ru',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        links = soup.select("div.registry-entry__header-top__icon a")

        for id, link in enumerate(links):
            if id % 2 != 0:
                href = link.get("href")
                if href:
                    result.append(href)
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе {url}: {e}")
    
    return result


@shared_task(
    autoretry_for=(requests.exceptions.RequestException,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
)
def parse_xml(link: str) -> str:
    """парсит страницу https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338300006625000018"""
    url = modify_url(link)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.210 Safari/537.36',
        'Accept-Language': 'ru',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    xml_content = response.content
    xml_dict = xmltodict.parse(xml_content)

    root_key = next(iter(xml_dict))
    common_info = xml_dict[root_key].get("commonInfo", {})
    publish_dt_in_eis = common_info.get("publishDTInEIS")

    return publish_dt_in_eis


def modify_url(link: str) -> str:
    """Модифицирует ссылку печатной формы, на Xml печатной формы"""
    url = "https://zakupki.gov.ru" + link.replace("view.html", "viewXml.html")
    return url