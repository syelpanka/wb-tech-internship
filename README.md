# 🛍 Интернет-магазин на Django REST API

Тестовое задание для стажёра Backend в WB Tech. Проект представляет собой REST API для интернет-магазина с функционалом пользователей, товаров, корзины и заказов. Реализована JWT-аутентификация, PostgreSQL, Docker-контейнеризация и базовые тесты.

## 📋 Стек технологий

- Python 3.12
- Django 6.0.3
- Django REST Framework 3.16.1
- PostgreSQL 15
- JWT (djangorestframework-simplejwt)
- Docker + Docker Compose
- Тесты: Django TestCase / unittest
- Документация: drf-spectacular (Swagger UI, ReDoc)

## ⚙️ Функциональность

### 🔐 Пользователи
- Регистрация, авторизация (JWT), профиль
- Личный баланс (пополнение через `/api/auth/deposit/`)

### 🎁 Товары
- CRUD для товаров (только админ)
- Просмотр списка и деталей доступен всем
- Название товара уникально (ограничение на уровне БД)

### 🧺 Корзина
- Добавление, удаление, изменение количества товаров
- Просмотр текущей корзины с итоговой суммой и стоимостью каждой позиции

### 🛒 Заказы
- Создание заказа из корзины с проверкой остатков и баланса
- Списание средств, уменьшение остатков, очистка корзины
- Логирование успешных заказов в консоль (согласно требованию Email/log)

---

## 🐳 Запуск проекта через Docker

### Требования
- Установленные Docker и Docker Compose
- Git

### Шаги

1. **Клонирование репозитория**
   ```bash
   git clone https://github.com/ваш-username/wb-tech-internship.git
   cd wb-tech-internship
   ```

2. **Настройка переменных окружения**
   Создайте файл `.env` в корне проекта (или используйте предоставленный пример):
   ```env
   DEBUG=1
   SECRET_KEY=your-secret-key-here
   DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
   DATABASE_NAME=postgres
   DATABASE_USER=postgres
   DATABASE_PASSWORD=postgres
   DATABASE_HOST=db
   DATABASE_PORT=5432
   ```
   Для тестового задания можно оставить значения по умолчанию.

3. **Запуск контейнеров**
   ```bash
   docker-compose up --build
   ```
   Приложение будет доступно по адресу `http://localhost:8000`.

4. **Применение миграций** (в отдельном терминале)
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Создание суперпользователя** (для админ-доступа)
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

---

## 📖 Документация API

После запуска доступны:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI схема: http://localhost:8000/api/schema/

Документация автоматически сгенерирована с помощью drf-spectacular и включает все эндпоинты с описаниями.

---

## 🧪 Тестирование

Запуск всех тестов:
```bash
docker-compose exec web python manage.py test
```

Запуск тестов для конкретного приложения:
```bash
docker-compose exec web python manage.py test apps.users
```
Для более подробного вывода добавьте флаг -v 2.

---

## 🔍 Примеры запросов (curl)

### Регистрация
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass123", "email": "user@example.com"}'
```

### Логин (получение токена)
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass123"}'
```
Сохраните access-токен из ответа.

### Пополнение баланса
```bash
curl -X POST http://localhost:8000/api/auth/deposit/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000}'
```

### Создание товара (только админ)
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Телефон", "description": "Смартфон", "price": 29999.99, "stock": 10}'
```

### Добавление в корзину
```bash
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### Просмотр корзины
```bash
curl -X GET http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer <access_token>"
```

### Создание заказа
```bash
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "Authorization: Bearer <access_token>"
```

### Проверка профиля (баланс)
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer <access_token>"
```

---

**Автор:** syelpanka  
**Дата:** Март 2026