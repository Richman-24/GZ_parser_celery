# tasks.py
from typing import List
import requests
import xmltodict
from bs4 import BeautifulSoup
from celery import Celery, Task


celery_app = Celery(
    "parser",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


class BaseTask(Task):
    """Базовый класс тасков с общей логикой."""

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.210 Safari/537.36",
        "Accept-Language": "ru",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
    }

    def make_request(self, url: str):
        """Общая логика для выполнения HTTP-запросов."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе {url}: {e}")
            return None


class ParsePageTask(BaseTask):
    """
    Парсит страницу с закупками. Возвращает список ссылок на печатные формы.
    """

    autoretry_for = (requests.exceptions.RequestException,)
    retry_kwargs = {"max_retries": 3, "countdown": 5}

    def run(self, url: str) -> List[str]:
        result = []

        try:
            response = self.make_request(url)
            soup = BeautifulSoup(response.content, "lxml")
            links = soup.select("div.registry-entry__header-top__icon a")

            for id, link in enumerate(links):
                if id % 2 != 0:
                    href = link.get("href")
                    if href:
                        result.append(href)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе {url}: {e}")

        return result


class ParseXmlTask(BaseTask):
    """Парсит XML-форму возвращает дату регистрации закупки."""

    autoretry_for = (requests.exceptions.RequestException,)
    retry_kwargs = {"max_retries": 3, "countdown": 5}

    def run(self, link: str) -> str:
        url = self.modify_url(link)
        response = self.make_request(url)

        xml_content = response.content
        xml_dict = xmltodict.parse(xml_content)

        root_key = next(iter(xml_dict))
        common_info = xml_dict[root_key].get("commonInfo", {})
        publish_dt_in_eis = common_info.get("publishDTInEIS")

        return publish_dt_in_eis

    @staticmethod
    def modify_url(link: str) -> str:
        """Модифицирует ссылку печатной формы на XML печатной формы."""
        url = "https://zakupki.gov.ru" + link.replace("view.html", "viewXml.html")
        return url


parse_page = celery_app.register_task(ParsePageTask())
parse_xml = celery_app.register_task(ParseXmlTask())
