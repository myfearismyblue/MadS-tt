# Загрузка мемов
![Python >= 3.10](https://img.shields.io/pypi/pyversions/django?style=plastic)
![PostgreSQL == 14](https://img.shields.io/static/v1?label=PostgreSQL&message=14&color=darkblue&style=plastic)
![pydantic == 2.7.4](https://img.shields.io/static/v1?label=pydantic&message=2.7.4&color=red&style=plastic)
![FastAPI == 0.110](https://img.shields.io/static/v1?label=FastAPI&message=0.110&color=darkgreen&style=plastic)
![uvicorn == 0.29](https://img.shields.io/static/v1?label=uvicorn&message=0.29&color=brightgreen&style=plastic)

Реализация задания на должность Python-разработчик.
## Содержание
* [Общая информация](#общая-информация)
* * [База данных](#база-данных)
* * [Архитектура веб-приложений](#архитектура-веб-приложений)
* [Технологии](#технологии)
* [Настройка](#настройка)
* [Api](#api)
* [Нагрузки](#нагрузки)

## Общая информация
Система реализует web API загрузки мемов на сервер.
Приложение имеет следующие компоненты: 
- публичное web приложение;
- приватное web приложение;
- база данных (postgres 14);
- объектное s3-хранилище MinIO

Компоненты разворачиваются в docker'e.


### База данных
В качестве БД выбран postgres известный своей устойчивостью, ссылочной и транзакционной целостностью. Как клиент для 
него в виде web приложения разворачивается pgAdmin4 (на порту ```5050```).
В бд помимо таблицы миграций, присутствуют таблица с информаций о мемах. В таблице накинуты индексы на атрибуты 
```title``` и ```etag``` (помимо индекса на ```pk```).
Директория ```pgdata``` смонтирована в ```./db ``` проекта.

Хранилище MinIO смонтировано локально в ```./minio-storage```. На порту ```9001``` крутится web клиент.


### Архитектура веб-приложений
В проекте реализован паттерн Репозиторий. [Домен](src%2Fcore) содержит в себе два репозитория, абстрагирующих работу с 
записями в БД и с файлами в в s3. Домен предоставляет интерфейсы ```AbstractMemeDbRepo```  и ```AbstractFileRepo``` для 
работы контроллеров FastApi. Сами репозитории используют ORM для работы с БД.
![dia.png](..%2F..%2F..%2Fhome%2Fandrey%2FPictures%2Fdia.png)


## Технологии
Использовались:
- Python 3.11
- PostgreSQL 14
- FastApi 0.110
- uvicorn 0.29
- SQLAlchemy 2.0.31
- Pydantic 2.7.4
- minio 7.27

	
## Настройка
Запуск происходит в несколько этапов:

- клонирование репозитория
```commandline
git clone https://github.com/myfearismyblue/MadS-tt.git
```
- перейти в директорию проекта
```commandline
cd MadS-tt
```
- создать [.env](.env) файл по образцу [.env.example](.env.example), напр:
```commandline
cp .env.example .env
```

- запуск проекта с помощью docker'a:
```commandline
docker-compose up -d --build
```
Директория проекта ```src/``` смонтирована как внешняя, поэтому ребилд docker образа не требуется в случае изменения проектных файлов.

- обычно, хост docker машины - ```localhost```, но в зависимости от настроек docker'a, ip может отличаться (напр. ```192.168.99.100```). Узнать его можно командой:
```docker-machine ip```

Сваггеры приложений находятся

- [```http://localhost:8000/api/swagger-ui```](http://localhost:8000/api/swagger-ui)
![pub.png](.github%2F_media%2Fpub.png)

- [```http://localhost:8001/api/swagger-ui```](http://localhost:8001/api/swagger-ui)
![priv.png](.github%2F_media%2Fpriv.png)



- доступ к БД через web клиента [```http://localhost:5050```](http://localhost:5050)
![pgadmin.png](.github%2F_media%2Fpgadmin.png)

- доступ к s3 хранилищу через web клиента [```http://localhost:9001```](http://localhost:9001)
![minio.png](.github%2F_media%2Fminio.png)
	
## API
Реализованы эндпоинты в соответствии с заданием.

Для [публичного API](http://localhost:8000/api/swagger-ui) реализованы: 
- ```GET /api/v1/memes```
- ```GET /api/v1/memes/{meme_id}```
- ```POST /api/v1/memes```


Для доступа к [администраторскому приватному API](http://localhost:8000/api/swagger-ui) требуется передать заголовок ```Authorization: Bearer <API-KEY>```. Ключ
определен переменной окружения ```WEB_PRIVATE_APP_API_KEY```
![bearer.png](.github%2F_media%2Fbearer.png)

Реализованы эндпоинты:

- ```PUT /api/v1/memes/{meme_id}```
- ```DELETE /api/v1/memes/{meme_id}```

## Нагрузки
Собственная память uvicorn-воркера на холостом ходу ~75MB.
Показания htop
![htop.png](.github%2F_media%2Fhtop.png)







