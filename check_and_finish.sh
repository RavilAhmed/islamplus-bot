#!/bin/bash
# Проверка и завершение настройки Bot API

SERVER="root@194.67.127.172"

echo "🔍 Проверка статуса и завершение настройки..."

ssh $SERVER << 'ENDSSH'
# Запустить Bot API если не запущен
sudo systemctl start telegram-bot-api 2>/dev/null || true
sleep 3

# Настроить .env
sudo sed -i 's|^BOT_API_URL=.*|BOT_API_URL=http://localhost:8081|' /opt/islamplus-bot/.env
if ! grep -q "^BOT_API_URL=" /opt/islamplus-bot/.env; then
    echo "BOT_API_URL=http://localhost:8081" | sudo tee -a /opt/islamplus-bot/.env > /dev/null
fi

# Перезапустить бота
sudo systemctl restart islamplus-bot
sleep 3

# Показать статус
echo ""
echo "📊 Статус Bot API:"
sudo systemctl status telegram-bot-api --no-pager | head -10

echo ""
echo "📊 Статус бота:"
sudo systemctl status islamplus-bot --no-pager | head -15

echo ""
echo "✅ Готово!"
ENDSSH
