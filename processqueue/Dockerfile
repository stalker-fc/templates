# builder-layer
FROM python:3.8@sha256:4c4e6735f46e7727965d1523015874ab08f71377b3536b8789ee5742fc737059 as builder

WORKDIR /builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# app-layer
FROM python:3.8-slim@sha256:d20122663d629b8b0848e2bb78d929c01aabab37c920990b37bb32bc47328818 as app

# create non-root user for safety
# 717 is known uid of non-root user. It can be any, not only 717
RUN addgroup --gid 717 --system appuser && \
    adduser --uid 717 --system --group appuser
USER appuser

# we launch application via gunicorn so installing it separately
# gunicorn shouldn`t be in requirements.txt because we can launch app without it
RUN pip install --user gunicorn==20.1.0
# add /.local/bin to PATH to use gunicorn inline
ENV PATH="/home/appuser/.local/bin:${PATH}"

# installing app dependencies
COPY --from=builder /wheels /wheels
RUN pip install --user --no-cache /wheels/*
RUN pip check

# copying application-data
COPY /app ./app
COPY main.py .

# configuring application run
HEALTHCHECK CMD curl --fail http://localhost:8080/ || exit 1

# using exec-form to correctly handle Ctrl+C
ENTRYPOINT ["gunicorn", "main:startup_app", "--bind", "0.0.0.0:8080", "--worker-class", "aiohttp.GunicornWebWorker"]
