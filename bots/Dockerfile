# bots/Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY bots/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bots/ .

# старый CMD остаётся рабочим
CMD ["sh", "-c", "exec python -u ${BOT_MODE:-client}/bot.py"]
