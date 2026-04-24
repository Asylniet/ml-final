FROM python:3.13-slim-bookworm

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6.6 /uv /uvx /bin/

ENV PYTHONPATH="${PYTHONPATH}:/app/code"

COPY ./pyproject.toml ./uv.lock ./

RUN uv sync --frozen --no-install-project

COPY scripts/start.sh .

RUN chmod +x start.sh

COPY ./src ./code

CMD ["./start.sh"]
