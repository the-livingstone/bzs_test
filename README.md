# Payment Processing Service

Асинхронный микросервис обработки платежей: REST API, transactional outbox, RabbitMQ (FastStream), webhook-уведомления.

## Стек

- FastAPI + Pydantic v2
- SQLAlchemy 2.0 (async) + PostgreSQL
- RabbitMQ + FastStream
- Alembic, Docker Compose

## Быстрый старт

скопировать .env.example в .env

```bash
docker compose up --build
```

- API: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672 (guest / guest)

## API

Все запросы требуют заголовок `X-API-Key` (задаётся в .env).

### Создание платежа

```bash
curl -s -X POST http://localhost:8000/api/v1/payments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: API-KEY" \
  -H "Idempotency-Key: order-001" \
  -d '{
    "amount": "100.50",
    "currency": "RUB",
    "description": "Test payment",
    "metadata": {"order_id": "42"},
    "webhook_url": "https://webhook.site/your-unique-id"
  }'
```

Ответ `202 Accepted`:

```json
{
  "payment_id": "...",
  "status": "pending",
  "created_at": "..."
}
```

Повтор запроса с тем же `Idempotency-Key` вернёт тот же платёж без дубля.

### Получение платежа

```bash
curl -s http://localhost:8000/api/v1/payments/{payment_id} \
  -H "X-API-Key: API-KEY"
```

## Архитектура

1. **POST /payments** — в одной транзакции создаётся запись `payments` и событие в `outbox`.
2. **Outbox publisher** (фоновая задача в процессе `api`) публикует неотправленные события в очередь `payments.new`.
3. **Consumer** читает очередь, эмулирует шлюз (с задержкой и не всегда успешно), обновляет статус, шлёт вебхук с 3 повторами и экспоненциальной задержкой.
4. При ошибках обработки сообщения до 3 повторов, затем сообщение уходит в DLQ `payments.new.dlq` (exchange `payments.dlx`).

## Структура

```
app/                         # API
  main.py                    # FastAPI и цикл outbox publisher
  config.py
  api/
    payments.py              # эндпоинты
    deps.py                  # зависимости эндпоинтов
  db/                        # engine и сессия
  models/                    # SQLAlchemy модели
  schemas/                   # Pydantic схемы для запросов
  services/
    payments.py              # обработка платёжа
    outbox_publisher.py      # публикация в брокер
consumer/                    # FastStream worker
  main.py                    # очередь payments.new, повторы, DLQ
  handlers.py                # обработка платежа и вебхук
  gateway.py                 # эмуляция шлюза
  webhook.py                 # отправка вебхука с повторами
  session.py
alembic/                     # миграции
docker/                      # entrypoint API и consumer
```
