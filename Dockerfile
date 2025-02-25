# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app/icad/

RUN pip install "gunicorn>=23.0.0"

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY duty/database/base.py ./duty/database/base.py
COPY duty/database/models.py ./duty/database/models.py
COPY alembic.ini ./
COPY alembic ./alembic
RUN alembic upgrade head

COPY duty ./duty
COPY library ./library
COPY content ./content
COPY start.py ./

ENV IRCA_LOG_FILE=""
ENV IRCA_LOG_STDOUT="true"

ENTRYPOINT [\
    "gunicorn", "start:create_app()", \
    "--error-logfile", "-",\
    "--access-logfile", "-",\
    "--logger-class", "duty.utils.gunicorn.Logger"\
]
CMD ["--bind", "0.0.0.0:8000"]
