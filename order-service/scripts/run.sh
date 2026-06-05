set -e

uv run alembic upgrade head

export PYTHONPATH=.
exec uv run python app/main.py
