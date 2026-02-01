**REST API с Sanic + PostgreSQL + JWT + Webhook**

**1: Docker Compose**

1. Склонировать проект
```bash
git clone https://github.com/algizn97/rest_api_web_app.git
```
2. Настроить конфигурацию
```bash
cp .env.sample .env
```
3. Применить миграцию (создает тестовые данные)
```bash
alembic upgrade head
```
4. Запустить
```bash
docker compose up --build -d
```
4. Проверить
```bash
curl http://localhost:8000/
```
**2: Локальный запуск**
1. Установить зависимости
```bash
pip install -r requirements.txt
```
2. Настроить конфигурацию
```bash
cp .env.sample .env
```
3. Запустить PostgreSQL
```bash
docker build -t sanic-api .
docker run -d --name sanic-app -p 8000:8000 \
  --link local_db \
  -e DATABASE_URL="postgresql+asyncpg://postgres:password@local_db:5432/appdb" \
  -e PYTHONPATH=/app \
  sanic-api
```
4. Применить миграцию
```bash
alembic upgrade head
```
5. Запустить API

```bash
python app/main.py
```

**🔑 Тестовые учетные данные**

Пользователь:	логин -> user@test.com;	пароль -> password123

Администратор:	логин -> admin@test.com; пароль -> password123

**🧪 Тестирование API**

*Health check
```bash
curl http://localhost:8000/ 
```
→ {"status": "OK", "message": "REST API ready!"}

*Логин пользователя

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"password123"}'
```

→ {"access_token": "jwt...", "user": {"id":1,"email":"user@test.com"}}

*Защищенный endpoint (с токеном)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"password123"}' | jq -r .access_token)
```
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/me
```

→ {"id":1,"email":"user@test.com","full_name":"Test User"}

*Webhook тест (требует правильную SHA256 подпись)

```bash
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test-123",
    "user_id": 1,
    "account_id": 1,
    "amount": 100.0,
    "signature": "ваша_sha256_подпись"
  }'
```
→ "OK"

**📋 Полный список эндпоинтов**


GET	/	Health check	Нет 

POST	/api/auth/login	Получить JWT	Нет 

GET	/api/users/me	Данные пользователя	Bearer JWT

GET	/api/users/accounts	Счета пользователя	Bearer JWT

GET	/api/users/payments	Платежи пользователя	Bearer JWT

POST	/api/webhook	Обработка платежей (SHA256)	Подпись

GET	/api/admin/users	Список пользователей	Admin JWT

POST	/api/admin/users	Создать пользователя	Admin JWT

PUT	/api/admin/users/1	Обновить пользователя	Admin JWT

DELETE	/api/admin/users/1	Удалить пользователя	Admin JWT


**🛠️ Управление проектом**

**Остановить контейнеры
```bash
docker compose down
```

**Полная очистка (БД + контейнеры)
```bash
docker compose down -v
```

**Пересобрать с изменениями
```bash
docker compose up --build -d
```

**Логи приложения
```bash
docker compose logs -f app
```

**Логи БД
```bash
docker compose logs -f db
```

**Миграции
```bash
docker compose exec app alembic revision --autogenerate -m "description"
docker compose exec app alembic upgrade head
docker compose exec app alembic downgrade -1
```


**🔧 Требования**

Docker 20.10+

Docker Compose 2.0+

Python 3.12 (для локального запуска)