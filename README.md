## Описание
«Фудграм» — сайт, на котором зарегистрированные пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и 
подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать 
список продуктов, которые нужно купить для приготовления выбранных блюд. Незарегистрированным пользователям доступен просмотр
списка рецептов или отдельного рецепта.


## Технологии
- Python
- Django
- Django rest framework
- Djoser 
- Gunicorn
- Docker

К проекту подключена база PostgreSQL.


## Установка проекта на удалённом сервере

1. ### Установите Docker Compose на сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

2. ### Создайте папку foodgram:
```
sudo mkdir foodgram-project-react
```

4. ### В папке foodgram создайте файл docker-compose.production.yml и .env скопируйте туда содержимое файла docker-compose.production.yml из проекта:
```
cd foodgram
sudo touch docker-compose.production.yml 
sudo nano docker-compose.production.yml
sudo touch .env
sudo nano .env
```
5. ### Пример наполнения .env
```
  GNU nano 6.2                                                                                                                                            .env
POSTGRES_DB=django
POSTGRES_USER=django
POSTGRES_PASSWORD=django
DB_NAME=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY='django-insecure........'
ALLOWED_HOSTS='айпи_сервера 127.0.0.1 localhost название_сайта.ru'
DEBUG=False
```

6. ### В файл настроек nginx добавить домен сайта:
```
sudo nano /etc/nginx/sites-enabled/default
```

7. ### После корректировки файла nginx выполнить команды:
```
sudo nginx -t
sudo service nginx reload
```

8. ### Из дирректории foodgram выполнить команды:
```
sudo docker compose -f docker-compose.production.yml pull
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
sudo docker system prune -a
```

Если необходимо создать суперпользователя:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

## Автоматический деплой проекта на сервер.

Предусмотрен автоматический деплой проекта на сервер с помощью GitHub actions. Для этого описан workflow файл:
.github/workflows/main.yml
После деплоя в проекте предусмотрена отправка сообщения в телеграм чат.

## Документация API :
находясь в корне проекта, локально, выполните команду docker-compose up.
http://localhost/api/docs/ — спецификация API. 

## Примеры запросов к API проекта:
**`POST` | Регистриация пользователя: `http://127.0.0.1:8000/api/users/`**

Request:
```
{
"email": "a@a.ru",
"id": 5,
"username": "aaa",
"first_name": "a",
"last_name": "a",
 "is_subscribed": false
},
```
Response:
```
{
"email": "diman.96@mail.ru",
"id": 4,
"username": "dima",
"first_name": "dima",
"last_name": "dima",
"is_subscribed": false
},
```

**`POST` | Получение ингредиентов: `http://127.0.0.1:8000/api/ingredients/`**

Response:
```
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "id": 1,
        "name": "абрикосовое варенье",
        "measurement_unit": "г"
    },
    {
        "id": 2,
        "name": "абрикосовое пюре",
        "measurement_unit": "г"
    },
    {
        "id": 3,
        "name": "абрикосовый джем",
        "measurement_unit": "г"
    },
    {
        "id": 4,
        "name": "абрикосовый сок",
        "measurement_unit": "стакан"
    },
]
```

**`GET` | Вывод списка тегов: `http://127.0.0.1:8000/api/tags/`**

Response:
```
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "id": 2,
        "name": "Cold",
        "color": "#9FD3FF",
        "slug": "Cold"
    },
    {
        "id": 1,
        "name": "Hot",
        "color": "#FF0000",
        "slug": "Hot"
    }
]
```

**`GET` | Вывод списка тегов: `http://127.0.0.1:8000/api/recipes/`**

Response:
```

{
    "count": 9,
    "next": "http://meowtube.ddns.net/api/recipes/?page=2",
    "previous": null,
    "results": [
        {
            "id": 9,
            "tags": [
                {
                    "id": 2,
                    "name": "Cold",
                    "color": "#9FD3FF",
                    "slug": "Cold"
                },
                {
                    "id": 1,
                    "name": "Hot",
                    "color": "#FF0000",
                    "slug": "Hot"
                }
            ],
            "author": {
                "email": "a@a.ru",
                "id": 5,
                "username": "aaa",
                "first_name": "a",
                "last_name": "a",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 1925,
                    "name": "фасоль красная",
                    "measurement_unit": "г",
                    "amount": 1
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false,
            "name": "123",
            "image": "http://meowtube.ddns.net/backend_media/recipes/fbf0b033-97d5-4876-a768-32761aea9300.jpg",
            "text": "213",
            "cooking_time": 123
        }
    ]
}

## Авторы
Дмитрий Морозов
github.com/tivago