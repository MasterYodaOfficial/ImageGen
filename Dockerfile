# Dockerfile
FROM python:3.12.3

WORKDIR /bot

RUN apt-get update && apt-get install -y build-essential libsqlite3-dev && rm -rf /var/lib/apt/lists/*

COPY . /bot

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/bot

RUN chmod +x /bot/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
