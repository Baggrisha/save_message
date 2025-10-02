#!/bin/bash

echo "=== Установка бота ==="
read -p "Введите BOT_TOKEN: " BOT_TOKEN
read -p "Введите ADMINS: " ADMINS

# Записываем данные в .env
cat > .env <<EOL
BOT_TOKEN=$BOT_TOKEN
ADMINS=$ADMINS
EOL

# Запуск docker compose
docker compose up -d --build
