set -e

uv run alembic upgrade head

exec uv run python app/main
