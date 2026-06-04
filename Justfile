#!/usr/bin/env just --justfile
export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

app_module := "app.main:app"


start:
    uv run uvicorn {{app_module}} --reload --host 127.0.0.1 --port 8000

migrate msg:
    PYTHONPATH=order-service uv run alembic revision --autogenerate -m "{{msg}}"


fix:
    uv run ruff check . --fix
    uv run ruff format .
    uv run ruff check --select I --fix
