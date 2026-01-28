## PaperSkill - Платформа для публикации платного контента

### Описание
PaperSkill - это платформа для публикации контента, где пользователи могут создавать бесплатные и платные записи. Платный контент доступен только после оплаты через систему Stripe.

### Технологии
- Python 3.13
- Django 6.0.1
- Django REST Framework
- PostgreSQL
- Stripe API
- Bootstrap 5
- Docker
- 
### Установка
1. Клонируйте репозиторий:
```bash
git clone git@github.com:Gammpyr/PaperSkill.git
cd paperskill
```
2. Создайте файл .env на основе .env_sample и заполните параметры:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_NAME=paperskill
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=db
DATABASE_PORT=5432

STRIPE_API_KEY=your_stripe_api_key
```

3. Запустите приложение с помощью Docker:
```bash
docker-compose up --build
```
4. Выполните миграции:
```bash
docker-compose exec web python manage.py migrate
```
5. Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```


### Использование
После запуска приложение будет доступно по адресу: http://127.0.0.1:8000

#### Основные функции:
- Регистрация пользователей по номеру телефона
- Публикация бесплатного и платного контента
- Оплата подписки через Stripe
- Просмотр контента (бесплатного - всем, платного - только после оплаты)
- 
### Структура проекта

```
paperskill/
├── config/          # Настройки Django
├── paperskill/      # Основное приложение (контент)
├── users/          # Приложение пользователей
├── static/         # Статические файлы
├── templates/      # Шаблоны
└── media/          # Медиа файлы
```

### Тестирование
Запуск тестов:
```bash
docker-compose exec web python manage.py test
```
### Лицензия
Проект разработан в учебных целях.
