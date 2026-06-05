FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /order-service

RUN apk add --no-cache gcc musl-dev zlib-dev

COPY ./pyproject.toml ./uv.lock ./

RUN uv sync --frozen --no-install-project

COPY . .

RUN uv sync --frozen

RUN chmod +x scripts/run.sh

CMD ["/bin/sh", "scripts/run.sh"]
