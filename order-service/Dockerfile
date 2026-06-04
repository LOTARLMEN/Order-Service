FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY order-service .

RUN uv sync --frozen

RUN chmod +x scripts/run.sh

CMD ["/bin/sh", "scripts/run.sh"]
