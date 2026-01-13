#!/bin/bash
# Скрипт для настройки локального Bot API на сервере

SERVER="root@194.67.127.172"

echo "🔧 Настройка локального Bot API на сервере..."

ssh $SERVER << 'ENDSSH'
set -e

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
sudo docker stop telegram-bot-api 2>/dev/null || true
sudo docker rm telegram-bot-api 2>/dev/null || true

# 4. Запустить systemd service
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-api
sudo systemctl start telegram-bot-api

sleep 5

# 5. Настроить .env
sudo sed -i 's|^BOT_API_URL=.*|BOT_API_URL=http://localhost:8081|' /opt/islamplus-bot/.env
if ! grep -q "^BOT_API_URL=" /opt/islamplus-bot/.env; then
    echo "BOT_API_URL=http://localhost:8081" | sudo tee -a /opt/islamplus-bot/.env > /dev/null
fi

# 6. Перезапустить бота
sudo systemctl restart islamplus-bot
sleep 3

# 7. Показать статус
echo ""
echo "📊 Статус Bot API:"
sudo systemctl status telegram-bot-api --no-pager | head -10

echo ""
echo "📊 Статус бота:"
sudo systemctl status islamplus-bot --no-pager | head -15

echo ""
echo "✅ Готово!"
ENDSSH
