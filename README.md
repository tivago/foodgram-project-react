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
После деплоя в проекте предусмотрена отправка смс в телеграм чат.

## Документация API :
находясь в корне проекта, локально, выполните команду docker-compose up.
http://localhost/api/docs/ — спецификация API. 

## Авторы
Дмитрий Морозов
github.com/tivago