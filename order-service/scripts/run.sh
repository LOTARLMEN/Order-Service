set -e

alembic upgrade head

export PYTHONPATH=.
exec python app/main.py
