#!/bin/bash
# Скрипт для установки локального Telegram Bot API через Docker

set -e

echo "🔧 Установка Docker..."

# Проверка, установлен ли Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker уже установлен"
else
    # Установка Docker
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    sudo systemctl start docker
    sudo systemctl enable docker
    
    echo "✅ Docker установлен"
fi

# Остановка и удаление старого контейнера (если есть)
if sudo docker ps -a | grep -q telegram-bot-api; then
    echo "🛑 Остановка старого контейнера..."
    sudo docker stop telegram-bot-api 2>/dev/null || true
    sudo docker rm telegram-bot-api 2>/dev/null || true
fi

# Запрос API ID и API Hash
echo ""
echo "📋 Нужны данные от https://my.telegram.org/apps"
echo ""
read -p "Введите API ID: " API_ID
read -p "Введите API Hash: " API_HASH

# Запуск локального Bot API
echo "🚀 Запуск локального Bot API..."
sudo docker run -d \
  --name telegram-bot-api \
  --restart=always \
  -v /var/lib/telegram-bot-api:/var/lib/telegram-bot-api \
  -p 8081:8081 \
  aiogram/telegram-bot-api:latest \
  --api-id="$API_ID" \
  --api-hash="$API_HASH" \
  --local

echo "✅ Локальный Bot API запущен!"

# Добавление в .env
echo ""
echo "📝 Добавление настройки в .env..."
if [ -f /opt/islamplus-bot/.env ]; then
    if grep -q "BOT_API_URL" /opt/islamplus-bot/.env; then
        sudo sed -i 's|BOT_API_URL=.*|BOT_API_URL=http://localhost:8081/bot|' /opt/islamplus-bot/.env
    else
        echo "BOT_API_URL=http://localhost:8081/bot" | sudo tee -a /opt/islamplus-bot/.env > /dev/null
    fi
    echo "✅ .env файл обновлен"
else
    echo "⚠️  Файл .env не найден. Создайте его вручную и добавьте:"
    echo "BOT_API_URL=http://localhost:8081/bot"
fi

echo ""
echo "✅ Готово! Перезапустите бота:"
echo "   sudo systemctl restart islamplus-bot"
