#!/bin/bash
set -e

echo "📤 Копирую исправленный файл на сервер..."
scp "src/handlers/quran.py" root@194.67.127.172:/opt/islamplus-bot/src/handlers/quran.py

echo "🔄 Перезапускаю бота..."
ssh root@194.67.127.172 "systemctl restart islamplus-bot"

echo "⏳ Жду 3 секунды..."
sleep 3

echo "📊 Статус бота:"
ssh root@194.67.127.172 "systemctl status islamplus-bot --no-pager -l | head -15"

echo ""
echo "✅ Готово! Бот обновлен и перезапущен."
