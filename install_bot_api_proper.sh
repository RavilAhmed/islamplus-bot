#!/bin/bash
# Правильная установка локального Bot API через systemd (не Docker)

set -e

echo "🔧 Установка локального Telegram Bot API..."

# 1. Установка зависимостей
echo "📦 Установка зависимостей..."
sudo apt-get update
sudo apt-get install -y make git zlib1g-dev libssl-dev gperf cmake clang-14 libc++-14-dev libc++abi-14-dev

# 2. Клонирование и компиляция
echo "🔨 Компиляция telegram-bot-api..."
cd /opt
if [ -d telegram-bot-api ]; then
    sudo rm -rf telegram-bot-api
fi
sudo git clone --recursive https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api
sudo mkdir -p build
cd build
sudo cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=/usr/local ..
sudo cmake --build . --target install

# 3. Создание директории для данных
sudo mkdir -p /var/lib/telegram-bot-api
sudo chown root:root /var/lib/telegram-bot-api

# 4. Создание systemd service
echo "⚙️ Создание systemd service..."
sudo tee /etc/systemd/system/telegram-bot-api.service > /dev/null <<EOF
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

# 5. Остановка Docker контейнера (если есть)
if sudo docker ps -a | grep -q telegram-bot-api; then
    echo "🛑 Остановка Docker контейнера..."
    sudo docker stop telegram-bot-api 2>/dev/null || true
    sudo docker rm telegram-bot-api 2>/dev/null || true
fi

# 6. Запуск systemd service
echo "🚀 Запуск Bot API..."
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-api
sudo systemctl restart telegram-bot-api

sleep 5

# 7. Проверка статуса
echo "📊 Статус Bot API:"
sudo systemctl status telegram-bot-api --no-pager | head -10

# 8. Настройка .env
if [ -f /opt/islamplus-bot/.env ]; then
    echo "📝 Настройка .env..."
    sudo sed -i 's|^BOT_API_URL=.*|BOT_API_URL=http://localhost:8081|' /opt/islamplus-bot/.env
    if ! grep -q "^BOT_API_URL=" /opt/islamplus-bot/.env; then
        echo "BOT_API_URL=http://localhost:8081" | sudo tee -a /opt/islamplus-bot/.env > /dev/null
    fi
fi

# 9. Перезапуск бота
echo "🔄 Перезапуск бота..."
sudo systemctl restart islamplus-bot
sleep 5

echo "📊 Статус бота:"
sudo systemctl status islamplus-bot --no-pager | head -15

echo ""
echo "✅ Готово! Проверьте статус выше."
