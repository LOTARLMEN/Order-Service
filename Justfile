#!/usr/bin/env just --justfile
set working-directory := 'order-service/'
app_module := "app.main:app"


start:
    uv run uvicorn {{app_module}} --reload --host 127.0.0.1 --port 8000

migrate msg:
    uv run alembic revision --autogenerate -m "{{msg}}"

head:
    uv run alembic head


fix:
    uv run ruff check . --fix
    uv run ruff format .
    uv run ruff check --select I --fix
