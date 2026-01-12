#!/bin/bash
# Быстрое исправление контейнера Bot API

set -e

echo "🔧 Исправление контейнера Bot API..."

# Остановка и удаление старого контейнера
if sudo docker ps -a | grep -q telegram-bot-api; then
    echo "🛑 Остановка старого контейнера..."
    sudo docker stop telegram-bot-api 2>/dev/null || true
    sudo docker rm telegram-bot-api 2>/dev/null || true
fi

# Запуск нового контейнера с правильными переменными окружения
echo "🚀 Запуск нового контейнера..."
sudo docker run -d \
  --name telegram-bot-api \
  --restart=always \
  -v /var/lib/telegram-bot-api:/var/lib/telegram-bot-api \
  -p 8081:8081 \
  -e TELEGRAM_API_ID=39503908 \
  -e TELEGRAM_API_HASH=d6828cda82c1e29a934d22df8ec2616c \
  aiogram/telegram-bot-api:latest \
  --local

echo "⏳ Ожидание запуска (5 секунд)..."
sleep 5

# Проверка статуса
if sudo docker ps | grep -q telegram-bot-api; then
    echo "✅ Контейнер запущен!"
    echo ""
    echo "🔄 Перезапуск бота..."
    sudo systemctl restart islamplus-bot
    sleep 2
    sudo systemctl status islamplus-bot --no-pager | head -10
else
    echo "❌ Ошибка запуска. Проверьте логи:"
    echo "   sudo docker logs telegram-bot-api"
fi
