# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app/icad/

RUN pip install "pytest>7.2.0" "dukpy>=0.5.0" "beautifulsoup4>4.13.0" "pytest-cov>=6.0.0"

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY duty/database/base.py ./duty/database/base.py
COPY duty/database/models.py ./duty/database/models.py
COPY duty/database/sqlite.py ./duty/database/sqlite.py
COPY alembic.ini ./
COPY alembic ./alembic
RUN alembic upgrade head

COPY duty ./duty
COPY library ./library
COPY content ./content
COPY tests ./tests
COPY pytest.ini start.py ./

ENTRYPOINT ["pytest"]
