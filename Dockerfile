FROM python:3.12-slim

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh
RUN chmod a+x /fastapi_app
