FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home-dir /app app
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip && python -m pip install ".[aws]" \
    && mkdir -p /reports && chown app:app /reports

USER app
ENV HOME=/app
ENTRYPOINT ["python", "-m", "cost_optimizer"]
