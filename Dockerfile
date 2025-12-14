# ----------------------------
#  builder
# ----------------------------
FROM python:3.13.5-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN pip install --no-cache-dir --disable-pip-version-check uv

COPY pyproject.toml /app

RUN uv lock && uv sync --frozen --no-dev
# ----------------------------
#  runtime
# ----------------------------
FROM python:3.13.5-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
VOLUME /app/resources
VOLUME /app/data

ENV PATH="/app/.venv/bin:${PATH}"

COPY . /app
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/.venv /app/.venv

EXPOSE 8000
CMD ["python", "main.py"]
