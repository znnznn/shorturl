FROM python:3.10.0-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
COPY . /app/
WORKDIR /app

RUN apt-get update &&  \
    apt-get upgrade -y && \
    apt-get install -y  \
        curl \
        libpq-dev \
        gcc
RUN pip install -r requirements.txt