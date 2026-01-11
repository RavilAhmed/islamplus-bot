#!/bin/bash
# Скрипт для автоматического развертывания и обновления бота

set -e  # Остановка при ошибке

echo "🚀 Начало развертывания бота..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Переменные (можно переопределить через переменные окружения)
PROJECT_DIR="${PROJECT_DIR:-/opt/islamplus-bot}"
VENV_DIR="${VENV_DIR:-$PROJECT_DIR/venv}"
SERVICE_NAME="${SERVICE_NAME:-islamplus-bot}"

# Переход в директорию проекта
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Ошибка: директория $PROJECT_DIR не найдена${NC}"
    exit 1
}

echo -e "${YELLOW}📦 Обновление кода из Git...${NC}"
git fetch origin
git reset --hard origin/main || git reset --hard origin/master

echo -e "${YELLOW}🔧 Активация виртуального окружения...${NC}"
source "$VENV_DIR/bin/activate" || {
    echo -e "${RED}❌ Ошибка: виртуальное окружение не найдено${NC}"
    echo -e "${YELLOW}💡 Создаю виртуальное окружение...${NC}"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
}

echo -e "${YELLOW}📥 Установка/обновление зависимостей...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}🗄️  Проверка базы данных...${NC}"
python3 init_db.py || echo -e "${YELLOW}⚠️  База данных уже инициализирована${NC}"

echo -e "${YELLOW}🔄 Перезапуск сервиса...${NC}"
sudo systemctl restart "$SERVICE_NAME" || {
    echo -e "${YELLOW}⚠️  Сервис не найден, попытка запуска...${NC}"
    sudo systemctl start "$SERVICE_NAME" || {
        echo -e "${RED}❌ Ошибка запуска сервиса. Проверьте конфигурацию systemd${NC}"
        exit 1
    }
}

# Проверка статуса
sleep 2
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ Бот успешно обновлен и запущен!${NC}"
    echo -e "${GREEN}📊 Статус: $(sudo systemctl status $SERVICE_NAME --no-pager -l | grep Active)${NC}"
else
    echo -e "${RED}❌ Бот не запустился. Проверьте логи: sudo journalctl -u $SERVICE_NAME -n 50${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Развертывание завершено!${NC}"