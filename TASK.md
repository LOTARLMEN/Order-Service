## Цель

Создать Order Service, который интегрируется с сервисами Capashino (Catalog, Payments, Shipping, Notifications) используя принципы чистой архитектуры. Задание разбито на несколько шагов для постепенного развития функциональности.

## Общая архитектура

Order Service должен обрабатывать заказы и интегрироваться с внешними сервисами:

- **Catalog Service** - проверка наличия товаров
- **Payments Service** - обработка платежей
- **Shipping Service** - отправка заказов в доставку
- **Notifications Service** - отправка уведомлений пользователям

## Статусы заказа

- `NEW` - заказ создан
- `PAID` - платеж успешен
- `SHIPPED` - заказ отправлен
- `CANCELLED` - заказ отменен

## API Capashino сервисов

**Важно:**

- Все API запросы к сервисам Capashino требуют авторизации через API токен в заголовке `X-API-Key: {api_token}`
- Используйте свой токен, который можно найти на вкладке профиль
- Базовый URL сервиса Capashino: `https://capashino.dev-2.python-labs.ru` (для доступа из кластера использовать внутренний хостнейм - `http://student-system-capashino-web.student-system-capashino.svc:8000`)

### Catalog Service

**Получить товар:**

```
GET /api/catalog/items/{item_id}
Headers: X-API-Key: {api_token}
```

**Response:**

```json
{
  "id": "item-uuid",
  "name": "Product Name",
  "price": "100.00",
  "available_qty": 10,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Payments Service

**Создать платеж:**

```
POST /api/payments
Headers: X-API-Key: {api_token}
```

**Request:**

```json
{
  "order_id": "order-uuid",
  "amount": "200.00",
  "callback_url": "http://order-service/api/orders/payment-callback",
  "idempotency_key": "unique-key"
}
```

**Примечание:** В `callback_url` необходимо передать **внутренний адрес** вашего сервиса — тот, который выдает Kubernetes при размещении в кластере. Именно этот адрес будет использоваться другими сервисами внутри кластера для связи.

> Важно: Разберитесь, как Kubernetes формирует внутренние доменные имена сервисов. Поймите принцип работы internal DNS, чтобы корректно определить адрес: `<service-name>.<namespace>.svc:порт`. Например, в поле `callback_url` указывайте полный путь до endpoint-а обратного вызова, такой как: `http://your-service-name.your-service-namespace.svc:8000/api/orders/payment-callback`.

Не используйте внешний домен (`*.python-labs.ru`), если ожидается вызов из другого сервиса внутри кластера; используйте всегда внутренний Kubernetes hostname!

**Response:**

```json
{
  "id": "payment-uuid",
  "user_id": "user-uuid",
  "order_id": "order-uuid",
  "amount": "200.00",
  "status": "pending",
  "idempotency_key": "unique-key",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Важно:** Payments Service обрабатывает платеж асинхронно и отправляет request на `callback_url` когда платеж обработан.

### Notifications Service

**Отправить уведомление:**

```
POST /api/notifications
Headers: X-API-Key: {api_token}
```

**Request:**

```json
{
  "message": "Your order has been shipped!",
  "reference_id": "order-uuid",
  "idempotency_key": "unique-key"
}
```

**Response:**

```json
{
  "id": "notification-uuid",
  "user_id": "user-uuid",
  "message": "Your order has been shipped!",
  "reference_id": "order-uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Kafka события

**Подключение к Kafka:**

- Адрес брокера: `kafka.kafka.svc.cluster.local:9092`
- Добавьте его в **переменные окружения** на детальной странице своего сервиса в LMS Portal (раздел «Переменные окружения»). Рекомендуемое имя переменной: `KAFKA_BOOTSTRAP_SERVERS`.
- В коде подключайтесь к Kafka, читая эту переменную из окружения (например, `os.environ["KAFKA_BOOTSTRAP_SERVERS"]` или через конфиг приложения). Не хардкодьте адрес брокера в коде.

### Публикация событий (Order Service → другие сервисы)

**Топик:** `student_system-order.events`

**Событие `ORDER.PAID`:**

```json
{
  "event_type": "order.paid",
  "order_id": "order-uuid",
  "item_id": "item-uuid",
  "quantity": 10,
  "idempotency_key": "idempotency_key-uuid"
}
```

### Подписка на события (Shipping Service → Order Service)

**Топик:** `student_system-shipment.events`

**Событие `ORDER.SHIPPED`:**

```json
{
  "event_type": "order.shipped",
  "order_id": "order-uuid",
  "item_id": "item-uuid",
  "quantity": 2,
  "shipment_id": "shipment-uuid"
}
```

**Событие `ORDER.CANCELLED`:**

```json
{
  "event_type": "order.cancelled",
  "order_id": "order-uuid",
  "item_id": "item-uuid",
  "quantity": 2,
  "reason": "Insufficient stock"
}
```

* * *

## Шаг 1: Интеграция с Catalog Service и создание API заказов

### Цель шага

Создать базовую структуру Order Service с интеграцией Catalog Service, реализовать API для создания заказов и задеплоить сервис.

### Задачи

1. **Создать структуру проекта** с использованием принципов чистой архитектуры:
   
   - Domain слой: модели заказа
   - Application слой: use case для создания заказа
   - Infrastructure слой: клиент для Catalog Service, репозиторий для заказов
   - Presentation слой: API endpoint для создания заказа
2. **Реализовать API создания заказа:**
   
   **Endpoint:** `POST /api/orders` 201 status code
   
   **Request:**
   
   ```json
   {
     "user_id": "user-123",
     "quantity": 10,
     "item_id": "item-uuid",
     "idempotency_key": "some-uuid"
   }
   ```
   
   **Response:**
   
   ```json
   {
     "id": "c8501322-290d-457e-b473-b7ebdc8",
     "user_id": "user_1",
     "quantity": 1,
     "item_id": "item-uuid",
     "status": "NEW",
     "created_at": "2024-01-01T00:00:00Z",
     "update_at": "2024-01-01T00:00:00Z"
   }
   ```
3. **Реализовать API получения заказа:**
   
   **Endpoint:** `GET /api/orders/{order_id}` 200 status code
   
   **Response:**
   
   ```json
   {
     "id": "c8501322-290d-457e-b473-b7ebdc8",
     "user_id": "user_1",
     "quantity": 1,
     "item_id": "item-uuid",
     "status": "NEW",
     "created_at": "2024-01-01T00:00:00Z",
     "update_at": "2024-01-01T00:00:00Z"
   }
   ```
4. **Интегрироваться с Catalog Service:**
   
   - При создании заказа проверить наличие товара через Catalog Service
   - Проверить доступное количество (`available_qty`), если товара нет в наличии отдавать 400 status code
   - Если товара нет или недостаточно - вернуть ошибку
5. **Обеспечить идемпотентность:**
   
   - Использовать `idempotency_key` для предотвращения дублирования заказов
6. **Задеплоить сервис:**
   
   - Настроить Dockerfile
   - Задеплоить в Kubernetes (или другую платформу)
   - Убедиться, что сервис доступен и работает

### Требования

- Использовать принципы чистой архитектуры
- Применить паттерн Repository для работы с данными
- Обработать ошибки от Catalog Service
- Обеспечить валидацию входных данных

### Критерии готовности

- ✅ API создания заказа работает
- ✅ Интеграция с Catalog Service реализована
- ✅ Проверка наличия товара работает корректно
- ✅ Идемпотентность обеспечена
- ✅ Сервис задеплоен и доступен

* * *

## Шаг 2: Интеграция с Payments Service

### Цель шага

Добавить интеграцию с Payments Service для обработки платежей заказов.

### Задачи

1. **Добавить клиент для Payments Service** в Infrastructure слой
2. **Расширить use case создания заказа:**
   
   - После проверки товара через Catalog Service
   - Создать платеж через Payments Service
   - При создании платежа передать `callback_url` - URL вашего сервиса для получения callback от Payments Service
   - URL вашего сервиса можно получить командой: `kubectl get ingress -n student-system-capashi`
   - Если платеж не создан - отменить заказ со статусом `CANCELLED`
3. **Реализовать callback endpoint:**
   
   **Endpoint:** `POST /api/orders/payment-callback`
   
   **Request (успешный платеж):**
   
   ```json
   {
     "payment_id": "payment-uuid",
     "order_id": "order-uuid",
     "status": "succeeded",
     "amount": "200.00",
     "error_message": null
   }
   ```
   
   **Request (неуспешный платеж):**
   
   ```json
   {
     "payment_id": "payment-uuid",
     "order_id": "order-uuid",
     "status": "failed",
     "amount": "200.00",
     "error_message": "Payment processing failed"
   }
   ```
   
   **Response:** `200 OK`
4. **Обработать callback от Payments Service:**
   
   - Обновить статус заказа на `PAID` при успешном платеже
   - Обновить статус заказа на `CANCELLED` при неуспешном платеже
   - Обеспечить идемпотентность обработки callback'ов
5. **Задеплоить обновленную версию сервиса**

### Требования

- Использовать паттерн Unit of Work для транзакционности
- Обеспечить надежную обработку callback'ов
- Обработать случаи, когда callback приходит несколько раз

### Критерии готовности

- ✅ Интеграция с Payments Service реализована
- ✅ Платеж создается при создании заказа
- ✅ Callback endpoint работает корректно
- ✅ Статусы заказа обновляются правильно
- ✅ Обновленная версия задеплоена

* * *

## Шаг 3: Интеграция с Shipping Service через Kafka

### Цель шага

Добавить интеграцию с Shipping Service через Kafka события для отправки заказов в доставку.

### Задачи

1. **Настроить Kafka producer** в Infrastructure слой
2. **Реализовать Outbox паттерн:**
   
   - Сохранять события в таблицу outbox при изменении статуса заказа
   - Публиковать события из outbox в Kafka топик `student_system-order.events`
3. **Расширить обработку callback от Payments Service:**
   
   - При успешном платеже (статус `PAID`) отправить событие в Shipping Service
   - Событие должно быть типа `order.paid` в топик `student_system-order.events`
4. **Реализовать Kafka consumer для событий от Shipping Service:**
   
   - Подписаться на топик `student_system-shipment.events`
   - Реализовать Inbox паттерн для обеспечения идемпотентности
5. **Обработать события от Shipping Service:**
   
   - Событие `order.shipped`: обновить статус заказа на `SHIPPED`
   - Событие `order.cancelled`: обновить статус заказа на `CANCELLED`
6. **Задеплоить обновленную версию сервиса**

### Требования

- Использовать Outbox паттерн для надежной публикации событий
- Использовать Inbox паттерн для надежной обработки событий
- Обеспечить идемпотентность обработки всех событий
- Обработать ошибки при работе с Kafka

### Формат событий

**Публикация события `ORDER.PAID`:**

```json
{
  "event_type": "order.paid",
  "order_id": "order-uuid",
  "item_id": "item-uuid",
  "quantity": 10,
  "idempotency_key": "idempotency_key-uuid"
}
```

**Обработка события `ORDER.SHIPPED`:**

```json
{
  "event_type": "order.shipped",
  "order_id": "order-uuid",
  "item_id": "item-uuid",
  "quantity": 2,
  "shipment_id": "shipment-uuid"
}
```

**Обработка события `ORDER.CANCELLED`:**

```json
{
  "event_type": "order.cancelled",
  "order_id": "order-uuid",
  "item_id": "item-uuid",
  "quantity": 2,
  "reason": "Insufficient stock"
}
```

### Критерии готовности

- ✅ Outbox паттерн реализован
- ✅ События публикуются в Kafka при изменении статуса на PAID
- ✅ Inbox паттерн реализован
- ✅ События от Shipping Service обрабатываются корректно
- ✅ Статусы заказа обновляются при получении событий
- ✅ Обновленная версия задеплоена

* * *

## Шаг 4: Интеграция с Notifications Service

### Цель шага

Добавить отправку уведомлений пользователям при изменении статуса заказа.

### Задачи

1. **Добавить клиент для Notifications Service** в Infrastructure слой
2. **Расширить обработку изменений статуса заказа:**
   
   - При создании заказа (статус `NEW`) - отправить уведомление
   - При успешной оплате (статус `PAID`) - отправить уведомление
   - При отправке в доставку (статус `SHIPPED`) - отправить уведомление
   - При отмене заказа (статус `CANCELLED`) - отправить уведомление
3. **Обеспечить идемпотентность отправки уведомлений:**
   
   - Использовать `idempotency_key` при отправке уведомлений
   - Предотвратить дублирование уведомлений
4. **Обработать ошибки от Notifications Service:**
   
   - Если уведомление не отправилось - логировать ошибку, но не блокировать основной процесс
5. **Задеплоить финальную версию сервиса**

### Требования

- Уведомления не должны блокировать основной процесс обработки заказа
- Обеспечить идемпотентность отправки уведомлений
- Обработать случаи недоступности Notifications Service

### Примеры уведомлений

- `NEW`: "Ваш заказ создан и ожидает оплаты"
- `PAID`: "Ваш заказ успешно оплачен и готов к отправке"
- `SHIPPED`: "Ваш заказ отправлен в доставку"
- `CANCELLED`: "Ваш заказ отменен. Причина: {reason}"

### Критерии готовности

- ✅ Интеграция с Notifications Service реализована
- ✅ Уведомления отправляются при всех изменениях статуса
- ✅ Идемпотентность отправки обеспечена
- ✅ Ошибки обрабатываются корректно
- ✅ Финальная версия задеплоена

* * *

## Общие требования ко всем шагам

- Использовать принципы чистой архитектуры
- Применить паттерны: Repository, Unit of Work, Outbox, Inbox
- Обеспечить надежность и идемпотентность
- Обработать ошибки от внешних сервисов
- Писать чистый и поддерживаемый код
- Добавлять логирование для отладки

## Процесс работы

1. **Реализуйте Шаг** и задеплойте сервис
2. **Автотесты** - убедитесь, что часть из них проходит
3. **Реализуйте След Шаг** и задеплойте сервис
4. **Автотесты** - убедитесь, что следующая часть из них проходит
5. **Реализуйте Финальный Шаг** - задеплойте сервис
6. **Автотесты** - убедитесь, что все автотесты зеленые
7. **Отправьте на ревью**

## Пример реализации

Для референса вы можете посмотреть пример реализации event-driven системы заказов:

**Репозиторий:** [online-store](https://github.com/edu-k3scluster-tech/online-store)

Этот проект демонстрирует:

- Event-driven архитектуру с использованием Kafka
- Реализацию паттерна Inbox для обеспечения идемпотентности
- Взаимодействие между микросервисами через события
- Структуру проекта с разделением на слои (application, domain, infrastructure, presentation)

**Примечание:** Это референсный пример для изучения подходов и паттернов. Ваша реализация может отличаться в зависимости от конкретных требований задания.

* * *

**Удачи в реализации!**