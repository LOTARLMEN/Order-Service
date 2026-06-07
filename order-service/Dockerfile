# --- Stage 1: Builder ---
# Используем официальный образ uv для сборки окружения
FROM ghcr.io/astral-sh/uv:0.5.1-python3.12-bookworm-slim AS builder

# Оптимизация uv: компиляция в байт-код для ускорения запуска и уменьшения размера
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Сначала копируем только файлы зависимостей. 
# Это позволяет кешировать установленные пакеты, если pyproject.toml и uv.lock не менялись.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# --- Stage 2: Runtime ---
# Для финального образа используем чистый slim образ Python без лишних инструментов сборки
FROM python:3.12-slim-bookworm

# Настройки Python для работы в контейнере
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Добавляем виртуальное окружение в PATH, чтобы python и alembic вызывались напрямую
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Безопасность: создаем системного пользователя, чтобы не запускать код от root
RUN groupadd -r app && useradd -r -g app app

# Копируем виртуальное окружение из билдера. 
# В нем уже установлены все зависимости без лишнего мусора (cache, uv binary).
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Копируем исходный код приложения
COPY --chown=app:app . .

# Делаем скрипт запуска исполняемым
RUN chmod +x scripts/run.sh

# Переключаемся на пользователя app
USER app

# Запускаем через shell-скрипт (убедись, что в нем нет uv run)
CMD ["/bin/sh", "scripts/run.sh"]
