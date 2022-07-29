FROM python:3.11.0b4-slim-buster

RUN mkdir -p /app/article_tgbot

COPY . /app/article_tgbot

WORKDIR /app/article_tgbot

RUN apt-get update && apt-get -y install libpq-dev gcc
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir /logs

EXPOSE 8080

CMD ["python", "src/bot.py"]