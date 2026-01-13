#!/bin/bash
# Автоматическая установка и запуск локального Bot API

set -e

echo "🔧 Настройка локального Bot API..."

# 1. Создать директорию
sudo mkdir -p /var/lib/telegram-bot-api

# 2. Создать systemd service
sudo tee /etc/systemd/system/telegram-bot-api.service > /dev/null <<'EOF'
[Unit]
Description=Telegram Bot API Server
After=network.target
[Service]
Type=simple
User=root
WorkingDirectory=/var/lib/telegram-bot-api
ExecStart=/usr/local/bin/telegram-bot-api --api-id=39503908 --api-hash=d6828cda82c1e29a934d22df8ec2616c --local
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF

# 3. Остановить Docker контейнер (если есть)
if sudo docker ps -a | grep -q telegram-bot-api; then
    sudo docker stop telegram-bot-api 2>/dev/null || true
    sudo docker rm telegram-bot-api 2>/dev/null || true
    echo "✅ Docker контейнер остановлен"
fi

# 4. Запустить systemd service
echo "🚀 Запуск Bot API..."
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-api
sudo systemctl start telegram-bot-api

sleep 5

# 5. Проверить статус
echo "📊 Статус Bot API:"
sudo systemctl status telegram-bot-api --no-pager | head -10

# 6. Настроить .env
if [ -f /opt/islamplus-bot/.env ]; then
    sudo sed -i 's|^BOT_API_URL=.*|BOT_API_URL=http://localhost:8081|' /opt/islamplus-bot/.env
    if ! grep -q "^BOT_API_URL=" /opt/islamplus-bot/.env; then
        echo "BOT_API_URL=http://localhost:8081" | sudo tee -a /opt/islamplus-bot/.env > /dev/null
    fi
    echo "✅ .env файл обновлен"
fi

# 7. Перезапустить бота
echo "🔄 Перезапуск бота..."
sudo systemctl restart islamplus-bot
sleep 3

echo "📊 Статус бота:"
sudo systemctl status islamplus-bot --no-pager | head -15

echo ""
echo "✅ Готово! Проверьте статус выше."
