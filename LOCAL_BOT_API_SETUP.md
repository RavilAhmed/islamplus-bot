# Настройка локального Bot API сервера для отправки файлов до 1GB

Локальный Bot API сервер позволяет отправлять файлы до 2GB вместо стандартного лимита 50MB.

## Установка на Ubuntu 24.04

### Шаг 1: Установка зависимостей

```bash
sudo apt-get update
sudo apt-get install -y make git zlib1g-dev libssl-dev gperf cmake clang-14 libc++-14-dev libc++abi-14-dev
```

### Шаг 2: Клонирование репозитория

```bash
cd /opt
sudo git clone --recursive https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api
```

### Шаг 3: Компиляция

```bash
sudo mkdir build
cd build
sudo cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=/usr/local ..
sudo cmake --build . --target install
```

Это займет 10-30 минут.

### Шаг 4: Получение API ID и API Hash

1. Перейдите на https://my.telegram.org/apps
2. Войдите с вашим номером телефона
3. Создайте приложение
4. Скопируйте **api_id** и **api_hash**

### Шаг 5: Запуск локального Bot API сервера

```bash
sudo mkdir -p /var/lib/telegram-bot-api
sudo chown $USER:$USER /var/lib/telegram-bot-api

# Запуск сервера
telegram-bot-api --api-id=YOUR_API_ID --api-hash=YOUR_API_HASH --local
```

Сервер запустится на `http://localhost:8081`

### Шаг 6: Создание systemd service

Создайте файл `/etc/systemd/system/telegram-bot-api.service`:

```bash
sudo nano /etc/systemd/system/telegram-bot-api.service
```

Содержимое:

```ini
[Unit]
Description=Telegram Bot API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/lib/telegram-bot-api
ExecStart=/usr/local/bin/telegram-bot-api --api-id=YOUR_API_ID --api-hash=YOUR_API_HASH --local
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**ВАЖНО:** Замените `YOUR_API_ID` и `YOUR_API_HASH` на ваши реальные значения!

### Шаг 7: Запуск и автозапуск

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-api
sudo systemctl start telegram-bot-api
sudo systemctl status telegram-bot-api
```

### Шаг 8: Настройка бота

Отредактируйте файл `.env`:

```bash
nano /opt/islamplus-bot/.env
```

Добавьте или измените строку:

```env
BOT_API_URL=http://localhost:8081/bot
```

### Шаг 9: Перезапуск бота

```bash
sudo systemctl restart islamplus-bot
```

### Проверка работы

```bash
# Проверка статуса Bot API сервера
sudo systemctl status telegram-bot-api

# Проверка логов
sudo journalctl -u telegram-bot-api -n 50

# Проверка статуса бота
sudo systemctl status islamplus-bot
```

## Полезные команды

```bash
# Остановка Bot API
sudo systemctl stop telegram-bot-api

# Запуск Bot API
sudo systemctl start telegram-bot-api

# Перезапуск Bot API
sudo systemctl restart telegram-bot-api

# Логи Bot API
sudo journalctl -u telegram-bot-api -f
```

## Альтернативный способ (Docker)

Если компиляция вызывает проблемы, можно использовать Docker:

```bash
docker run -d \
  --name telegram-bot-api \
  --restart=always \
  -v /var/lib/telegram-bot-api:/var/lib/telegram-bot-api \
  -p 8081:8081 \
  aiogram/telegram-bot-api:latest \
  --api-id=YOUR_API_ID \
  --api-hash=YOUR_API_HASH \
  --local
```

Затем в `.env` укажите:
```env
BOT_API_URL=http://localhost:8081/bot
```
