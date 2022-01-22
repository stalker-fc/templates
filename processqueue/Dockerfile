FROM python:3.8

WORKDIR /app

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV N_WORKERS 2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip check

COPY main.py .

COPY /app ./app

ENTRYPOINT /bin/bash -c "python run_app.py"
