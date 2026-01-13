#!/bin/bash
set -e

echo "📤 Копирую файлы рассылок на сервер..."

# Копируем обновленные файлы
scp "src/services/notification_service.py" root@194.67.127.172:/opt/islamplus-bot/src/services/notification_service.py
scp "src/handlers/broadcast.py" root@194.67.127.172:/opt/islamplus-bot/src/handlers/broadcast.py
scp "src/handlers/__init__.py" root@194.67.127.172:/opt/islamplus-bot/src/handlers/__init__.py
scp "src/bot.py" root@194.67.127.172:/opt/islamplus-bot/src/bot.py

# Копируем изображение, если его нет на сервере
echo "📸 Копирую изображение для рассылок..."
ssh root@194.67.127.172 "mkdir -p /opt/islamplus-bot/images"
scp "images/islam_praktika_banner 1.jpg" root@194.67.127.172:/opt/islamplus-bot/images/

echo "🔄 Перезапускаю бота..."
ssh root@194.67.127.172 "systemctl restart islamplus-bot"

echo "⏳ Жду 3 секунды..."
sleep 3

echo "📊 Статус бота:"
ssh root@194.67.127.172 "systemctl status islamplus-bot --no-pager -l | head -15"

echo ""
echo "✅ Готово! Система рассылок установлена и бот перезапущен."
echo ""
echo "📝 Инструкция:"
echo "  - Автоматические рассылки о посте: каждое воскресенье и среду в 6:00 МСК"
echo "  - Ручные рассылки: используйте команду /broadcast (только для админов)"
echo "  - Убедитесь, что ваш Telegram ID добавлен в ADMIN_IDS в .env файле"
