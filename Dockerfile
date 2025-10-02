FROM python:3.10

WORKDIR /save_message

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Запуск бота
CMD ["python", "bot.py"]
