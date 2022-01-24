# available value for APP_ENV are `development` and `production`
# `production`-image doesn`t include test dependecies
ARG APP_ENV=development

# ---------------------------------------------------------------
# base-builder-layer
FROM python:3.8@sha256:4c4e6735f46e7727965d1523015874ab08f71377b3536b8789ee5742fc737059 as base-builder

WORKDIR /builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ---------------------------------------------------------------
# production image includes only dependencies which are in requirements.txt
FROM base-builder AS production-builder

COPY requirements.txt .

RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---------------------------------------------------------------
# development image contains production requirements and test requirements.
FROM production-builder AS development-builder

COPY requirements.tests.txt .

RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.tests.txt

# ---------------------------------------------------------------
# choose builder image by APP_ENV
FROM ${APP_ENV}-builder AS builder

# ---------------------------------------------------------------
# base image for dependencies installation
FROM python:3.8-slim@sha256:d20122663d629b8b0848e2bb78d929c01aabab37c920990b37bb32bc47328818 as base

# create non-root user for safety
# 717 is known uid of non-root user. It can be any, not only 717
ARG APP_USER=appuser
ARG APP_USER_UID=717

RUN addgroup --gid $APP_USER_UID --system $APP_USER && \
    adduser --uid $APP_USER_UID --system --group $APP_USER
USER $APP_USER

# installing app dependencies
COPY --from=builder /wheels /wheels
RUN pip install --user --no-cache /wheels/*
RUN pip check

# ---------------------------------------------------------------
# image for tests
FROM base AS test

USER $APP_USER

# copying application-data
COPY /app ./app
COPY /tests ./tests

ENTRYPOINT ["python", "-m", "pytest", "tests/"]

# ---------------------------------------------------------------
# image for app
FROM base AS app

USER $APP_USER

# we launch application via gunicorn
# gunicorn shouldn`t be in requirements.txt because we can launch app without it
RUN pip install --user gunicorn==20.1.0
# add /.local/bin to PATH to use gunicorn inline
ENV PATH="/home/${APP_USER}/.local/bin:${PATH}"

# copying application-data
COPY /app ./app
COPY main.py .

# configuring application run
HEALTHCHECK CMD curl --fail http://localhost:8080/ || exit 1

# using exec-form to correctly handle Ctrl+C
ENTRYPOINT ["gunicorn", "main:startup_app", "--bind", "0.0.0.0:8080", "--worker-class", "aiohttp.GunicornWebWorker"]
