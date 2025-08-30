
# Foodgram

REST API для проекта **Foodgram** - платформы для любителей кулинарии.  


## Оглавление

- [Описание](#описание)
- [Технологии](#технологии)
- [Роли пользователей](#роли-пользователей)
- [Установка и запуск](#установка-и-запуск)
- [Демонстрация](#демонстрация)
- [Документация](#документация)
- [Авторы](#авторы)


## Описание

Проект Foodgram позволяет публиковать свои рецепты, сохранять понравившиеся блюда в избранное и подписываться на авторов. Рецепты помечаются тегами, которые помогают облегчить процесс поиска нужного рецепта (например, завтрак, обед или ужин). Зарегистрированные пользователи также получают доступ к функции «Список покупок», которая позволяет формировать список продуктов для выбранных рецептов.
## Технологии
- Python 3.12.7
- Django 5.2.5
- Django REST Framework 3.16.1
- Djoser 2.3.3
- Simple JWT 5.5.1
- PostgreSQL 17
- Gunicorn 23.0.0
- Docker & Docker Compose
## Роли пользователей

**Гость** - анонимный пользователь, который может просматривать рецепты, но не имеет возможности добавлять их в избранное или публиковать свои.

**Аутентифицированный пользователь** - зарегистрированный и вошедший в систему пользователь, который может публиковать рецепты, сохранять понравившиеся блюда в избранное, подписываться на авторов и формировать «Список покупок».

**Администратор** - пользователь с полными правами, который может управлять всеми рецептами, тегами и пользователями.
## Установка и запуск
### Локальная разработка
```
git clone https://github.com/aksianchuk/foodgram.git
cd foodgram
cp .env.example .env # создайте и укажите настройки
docker-compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
docker compose exec backend python manage.py load_ingredients --path data/ingredients.json
docker-compose exec backend python manage.py createsuperuser
```
Проект будет доступен по адресу:  
http://localhost:8000

### Продакшн
```
git clone https://github.com/aksianchuk/foodgram.git
cd foodgram
cp .env.example .env # создайте и укажите настройки
sudo docker-compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients --path data/ingredients.json
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
Проект будет доступен по адресу вашего сервера.  

**Примечание:** рекомендуется использовать nginx как обратный прокси перед Gunicorn для обслуживания статических и медиа-файлов, а также для подключения HTTPS.
## Демонстрация
https://fooodgram.onthewifi.com  

https://fooodgram.onthewifi.com/admin/  
Пользователь: admin  
Пароль: 12345678!  
Пользователь: second  
Пароль: 12345678!  
Пользователь: third  
Пароль: 12345678!  

https://fooodgram.onthewifi.com/api/docs/

## Документация
Документация доступна после запуска проекта по адресу:   
http://localhost:8000/api/docs/
## Авторы
**Бэкенд:**  
https://github.com/aksianchuk (Никита Оксенчук)  
**Фронтенд:**  
https://practicum.yandex.com (команда Яндекс Практикум)