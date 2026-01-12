#!/bin/bash
# Полное исправление локального Bot API для файлов до 1GB

set -e

echo "🔧 Исправление локального Bot API..."

# 1. Остановка и удаление старого контейнера
if sudo docker ps -a | grep -q telegram-bot-api; then
    echo "🛑 Остановка старого контейнера..."
    sudo docker stop telegram-bot-api 2>/dev/null || true
    sudo docker rm telegram-bot-api 2>/dev/null || true
fi

# 2. Запуск нового контейнера с правильными настройками
echo "🚀 Запуск нового контейнера Bot API..."
sudo docker run -d \
  --name telegram-bot-api \
  --restart=always \
  -v /var/lib/telegram-bot-api:/var/lib/telegram-bot-api \
  -p 8081:8081 \
  -e TELEGRAM_API_ID=39503908 \
  -e TELEGRAM_API_HASH=d6828cda82c1e29a934d22df8ec2616c \
  aiogram/telegram-bot-api:latest \
  --local

echo "⏳ Ожидание запуска Bot API (10 секунд)..."
sleep 10

# 3. Проверка статуса контейнера
if ! sudo docker ps | grep -q telegram-bot-api; then
    echo "❌ Ошибка запуска Bot API. Логи:"
    sudo docker logs telegram-bot-api --tail 20
    exit 1
fi

echo "✅ Bot API контейнер запущен"

# 4. Проверка доступности Bot API
if curl -s http://localhost:8081/bot8184893042:AAHMmM12gTY9bVsjXaLcFw2g4uHDC28YSVY/getMe > /dev/null 2>&1; then
    echo "✅ Bot API доступен"
else
    echo "⚠️  Bot API запущен, но проверка не прошла (это может быть нормально)"
fi

# 5. Настройка .env файла
echo "📝 Настройка .env файла..."
if [ -f /opt/islamplus-bot/.env ]; then
    # Убеждаемся, что BOT_API_URL правильный (код автоматически уберет /bot если есть)
    if grep -q "^BOT_API_URL=" /opt/islamplus-bot/.env; then
        sudo sed -i 's|^BOT_API_URL=.*|BOT_API_URL=http://localhost:8081/bot|' /opt/islamplus-bot/.env
    else
        echo "BOT_API_URL=http://localhost:8081/bot" | sudo tee -a /opt/islamplus-bot/.env > /dev/null
    fi
    
    # Убеждаемся, что BOT_TOKEN правильный
    if ! grep -q "^BOT_TOKEN=8184893042:AAHMmM12gTY9bVsjXaLcFw2g4uHDC28YSVY" /opt/islamplus-bot/.env; then
        if grep -q "^BOT_TOKEN=" /opt/islamplus-bot/.env; then
            sudo sed -i 's|^BOT_TOKEN=.*|BOT_TOKEN=8184893042:AAHMmM12gTY9bVsjXaLcFw2g4uHDC28YSVY|' /opt/islamplus-bot/.env
        else
            echo "BOT_TOKEN=8184893042:AAHMmM12gTY9bVsjXaLcFw2g4uHDC28YSVY" | sudo tee -a /opt/islamplus-bot/.env > /dev/null
        fi
    fi
    
    echo "✅ .env файл обновлен"
else
    echo "❌ Файл .env не найден!"
    exit 1
fi

# 6. Перезапуск бота
echo "🔄 Перезапуск бота..."
sudo systemctl restart islamplus-bot
sleep 5

# 7. Проверка статуса бота
echo ""
echo "📊 Статус бота:"
sudo systemctl status islamplus-bot --no-pager | head -15

echo ""
echo "📋 Последние логи бота:"
sudo journalctl -u islamplus-bot -n 20 --no-pager | tail -10

echo ""
echo "✅ Готово! Проверьте статус выше."
echo "Если бот работает (active running), проверьте отправку файла в боте."
