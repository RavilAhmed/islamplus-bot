#!/bin/bash
# Скрипт для первоначальной установки бота на VPS

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Переменные (можно изменить)
PROJECT_DIR="${PROJECT_DIR:-/opt/islamplus-bot}"
REPO_URL="${REPO_URL:-}"  # URL вашего Git репозитория
SERVICE_NAME="${SERVICE_NAME:-islamplus-bot}"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  Установка IslamPlus.Practice Bot${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Пожалуйста, запустите скрипт с правами root (sudo)${NC}"
    exit 1
fi

# 1. Установка системных зависимостей
echo -e "${YELLOW}📦 Установка системных зависимостей...${NC}"
apt-get update
apt-get install -y python3 python3-pip python3-venv git postgresql-client curl

# 2. Создание пользователя (если не существует)
if ! id "www-data" &>/dev/null; then
    echo -e "${YELLOW}👤 Создание пользователя www-data...${NC}"
    useradd -r -s /bin/bash www-data
fi

# 3. Клонирование репозитория
if [ -z "$REPO_URL" ]; then
    echo -e "${YELLOW}📥 Введите URL вашего Git репозитория:${NC}"
    read -r REPO_URL
fi

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Директория $PROJECT_DIR уже существует${NC}"
    echo -e "${YELLOW}Удалить и создать заново? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        rm -rf "$PROJECT_DIR"
    else
        echo -e "${RED}❌ Установка отменена${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}📥 Клонирование репозитория...${NC}"
mkdir -p "$(dirname $PROJECT_DIR)"
git clone "$REPO_URL" "$PROJECT_DIR" || {
    echo -e "${RED}❌ Ошибка клонирования репозитория${NC}"
    exit 1
}

# 4. Создание виртуального окружения
echo -e "${YELLOW}🔧 Создание виртуального окружения...${NC}"
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate

# 5. Установка зависимостей Python
echo -e "${YELLOW}📥 Установка зависимостей Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 6. Настройка .env файла
echo -e "${YELLOW}⚙️  Настройка переменных окружения...${NC}"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo -e "${GREEN}✅ Файл .env создан из .env.example${NC}"
        echo -e "${YELLOW}⚠️  ВАЖНО: Отредактируйте файл .env и укажите BOT_TOKEN!${NC}"
        echo -e "${YELLOW}   nano $PROJECT_DIR/.env${NC}"
    else
        echo -e "${YELLOW}⚠️  Создайте файл .env вручную${NC}"
    fi
else
    echo -e "${GREEN}✅ Файл .env уже существует${NC}"
fi

# 7. Настройка PostgreSQL
echo -e "${YELLOW}🗄️  Настройка базы данных...${NC}"
echo -e "${YELLOW}У вас уже настроена PostgreSQL? (y/n)${NC}"
read -r has_db
if [[ ! "$has_db" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}📦 Установка PostgreSQL...${NC}"
    apt-get install -y postgresql postgresql-contrib
    
    echo -e "${YELLOW}Создание базы данных...${NC}"
    sudo -u postgres psql <<EOF
CREATE DATABASE islamplus;
CREATE USER islamplus WITH PASSWORD 'islamplus_password';
GRANT ALL PRIVILEGES ON DATABASE islamplus TO islamplus;
\q
EOF
    
    # Обновление .env
    if [ -f "$PROJECT_DIR/.env" ]; then
        sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://islamplus:islamplus_password@localhost:5432/islamplus|" "$PROJECT_DIR/.env"
    fi
    
    echo -e "${GREEN}✅ База данных создана${NC}"
    echo -e "${YELLOW}⚠️  ВАЖНО: Измените пароль БД в .env файле!${NC}"
fi

# 8. Инициализация базы данных
echo -e "${YELLOW}🗄️  Инициализация таблиц базы данных...${NC}"
python3 init_db.py || echo -e "${YELLOW}⚠️  Ошибка инициализации БД (возможно, нужно настроить .env)${NC}"

# 9. Установка systemd service
echo -e "${YELLOW}🔧 Настройка systemd service...${NC}"
if [ -f "$PROJECT_DIR/islamplus-bot.service" ]; then
    # Обновление путей в service файле
    sed -i "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_DIR|g" "$PROJECT_DIR/islamplus-bot.service"
    sed -i "s|Environment=\"PATH=.*|Environment=\"PATH=$PROJECT_DIR/venv/bin\"|g" "$PROJECT_DIR/islamplus-bot.service"
    sed -i "s|ExecStart=.*|ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/run.py|g" "$PROJECT_DIR/islamplus-bot.service"
    sed -i "s|ReadWritePaths=.*|ReadWritePaths=$PROJECT_DIR|g" "$PROJECT_DIR/islamplus-bot.service"
    
    cp "$PROJECT_DIR/islamplus-bot.service" "/etc/systemd/system/$SERVICE_NAME.service"
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    echo -e "${GREEN}✅ Systemd service установлен${NC}"
else
    echo -e "${RED}❌ Файл islamplus-bot.service не найден${NC}"
fi

# 10. Настройка прав доступа
echo -e "${YELLOW}🔐 Настройка прав доступа...${NC}"
chown -R www-data:www-data "$PROJECT_DIR"
chmod +x "$PROJECT_DIR/deploy.sh"
chmod +x "$PROJECT_DIR/run.py"
chmod +x "$PROJECT_DIR/init_db.py"

# 11. Запуск сервиса
echo -e "${YELLOW}🚀 Запуск бота...${NC}"
systemctl start "$SERVICE_NAME"

sleep 3

if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ Бот успешно запущен!${NC}"
else
    echo -e "${RED}❌ Бот не запустился. Проверьте логи:${NC}"
    echo -e "${YELLOW}   sudo journalctl -u $SERVICE_NAME -n 50${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Установка завершена!${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📝 Следующие шаги:${NC}"
echo -e "1. Отредактируйте .env файл: ${BLUE}nano $PROJECT_DIR/.env${NC}"
echo -e "2. Укажите ваш BOT_TOKEN от @BotFather"
echo -e "3. Перезапустите бота: ${BLUE}sudo systemctl restart $SERVICE_NAME${NC}"
echo ""
echo -e "${YELLOW}📊 Полезные команды:${NC}"
echo -e "  Статус:     ${BLUE}sudo systemctl status $SERVICE_NAME${NC}"
echo -e "  Логи:       ${BLUE}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo -e "  Перезапуск: ${BLUE}sudo systemctl restart $SERVICE_NAME${NC}"
echo -e "  Остановка:  ${BLUE}sudo systemctl stop $SERVICE_NAME${NC}"
echo ""
echo -e "${YELLOW}🔄 Для обновления бота:${NC}"
echo -e "  ${BLUE}cd $PROJECT_DIR && sudo ./deploy.sh${NC}"
echo ""