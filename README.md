# Order Service

Микросервис заказов, реализованный на **FastAPI** с соблюдением принципов **Clean Architecture**. Сервис обеспечивает полный жизненный цикл заказа: от создания и проверки остатков в каталоге до интеграции с платежной системой и уведомлений пользователя.

## Ключевой функционал

- **Управление заказами:** Создание, получение и обновление статусов заказов.
- **Reliable Messaging (Inbox/Outbox):** Гарантированная доставка событий в Kafka через паттерн Outbox и надежная обработка входящих событий (например, от службы доставки) через паттерн Inbox.
- **Идемпотентность:** Защита от дублирования операций (создание заказа, проведение платежей) с использованием ключей идемпотентности.
- **Интеграция с Kafka:** Асинхронное взаимодействие с другими микросервисами через шину сообщений.
- **Внешние интеграции (Capashino):**
    - **Catalog Service:** Проверка наличия и резервирование товаров.
    - **Payments Service:** Проведение и проверка транзакций.
    - **Notifications Service:** Отправка уведомлений пользователям.

## Архитектура

Проект следует принципам Чистой Архитектуры, что обеспечивает слабую связанность и высокую тестируемость:

- **Core (Ядро):** Определение бизнес-моделей и базовых типов данных (`app/core/models.py`).
- **Application (Слой бизнес-логики):** Реализация Use Cases (вариантов использования). Здесь сосредоточена основная логика приложения (`app/application/use_cases`).
- **Infrastructure (Инфраструктура):** Реализация внешних интерфейсов: доступ к БД (SQLAlchemy), реализация репозиториев, клиенты к внешним API (HTTPX) и Kafka (`app/infrastructure`).
- **Presentation (Слой представления):** REST API на базе FastAPI и фоновые воркеры (`app/presentation`).

## Технологический стек

- **Python 3.12+**
- **FastAPI** — веб-фреймворк.
- **SQLAlchemy & asyncpg** — асинхронная работа с PostgreSQL.
- **Alembic** — миграции базы данных.
- **AIOKafka** — асинхронный клиент для Apache Kafka.
- **Pydantic & Pydantic Settings** — валидация данных и управление конфигурацией.
- **Dependency Injector** — внедрение зависимостей.
- **uv** — современный менеджер пакетов и среды выполнения.

## Запуск проекта

### Предварительные требования
- Установленный [uv](https://docs.astral.sh/uv/)
- PostgreSQL и Kafka (можно запустить через Docker)

### Конфигурация
Создайте файл `.env` в корне проекта (или используйте переменные окружения):
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DATABASE_NAME=order_service

KAFKA_BOOTSTRAP_SERVERS=localhost:9092

CAPASHINO_BASE_URL=https://api.example.com
CAPASHINO_X_API_KEY=your_secret_key

ORDER_SERVICE_NAME=OrderService
ORDER_SERVICE_HOST=0.0.0.0
ORDER_SERVICE_PORT=8000
```

### Команды для запуска

1. **Установка зависимостей:**
   ```bash
   uv sync
   ```

2. **Применение миграций:**
   ```bash
   uv run alembic upgrade head
   ```

3. **Запуск сервера:**
   ```bash
   uv run python app/main.py
   ```