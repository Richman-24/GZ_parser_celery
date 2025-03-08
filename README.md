# GZ_parser_test

## Описание проекта
Парсер сайта госзакупок.

Асинхронно собирает данные (при помощи Celery) с сайта госзакупок. 
Выбирает все заявки по 44ФЗ на сайте, выводит ссылку на печатную форму и дату публикации.

В качестве очереди использует redis (запускаем в докер контейнере)

## Cтэк: 
Python 3, Celery, Redis, Requests, BeautifulSoup4, xmltodict, art, Docker


## Установка:
1. склонировать репо: 
2. установить зависимости: 
3. запустить redis в контейнере:

```bash
docker run --rm -d --name redis -p 6379:6379 redis
```
4. Запустить воркера celery:

```bash
celery -A tasks worker --loglevel=info
```

5. запустить скрипт 
```bash
python3 script.py 
```

## Примечание: 
При запуске через терминал можно указать дополнительным аргументов число страниц для парсинга. (по-умолчанию = 2)
```bash 
python3 script.py 4
```

## Автор проекта
[Дреев Максим](https://github.com/richman-24) <br>
[telegram: @richman24](https://t.me/richman_24)
