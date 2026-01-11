# Инструкция по развертыванию на VPS

Это руководство поможет вам установить и настроить бота на VPS с автоматическим обновлением через Git.

## 🚀 Быстрая установка

### Вариант 1: Автоматическая установка (рекомендуется)

1. **Клонируйте репозиторий на сервер:**
```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> /opt/islamplus-bot
cd /opt/islamplus-bot
```

2. **Запустите скрипт установки:**
```bash
chmod +x install.sh
sudo ./install.sh
```

3. **Настройте переменные окружения:**
```bash
sudo nano /opt/islamplus-bot/.env
```

Обязательно укажите:
- `BOT_TOKEN` - токен бота от @BotFather
- `DATABASE_URL` - URL базы данных
- `ADMIN_IDS` - ваш Telegram ID

4. **Перезапустите бота:**
```bash
sudo systemctl restart islamplus-bot
```

### Вариант 2: Ручная установка

См. подробные инструкции в разделе "Ручная установка" ниже.

---

## 🔄 Обновление бота

### Автоматическое обновление (через Git)

После того как вы внесли изменения в код и запушили в Git:

```bash
cd /opt/islamplus-bot
sudo ./deploy.sh
```

Этот скрипт:
- ✅ Обновит код из Git
- ✅ Установит новые зависимости
- ✅ Инициализирует БД (если нужно)
- ✅ Перезапустит бот

### Простой вариант обновления

Если вы просто хотите обновить код:

```bash
cd /opt/islamplus-bot
sudo -u www-data git pull
sudo systemctl restart islamplus-bot
```

---

## 📋 Ручная установка

### 1. Установка системных зависимостей

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git postgresql postgresql-contrib
```

### 2. Клонирование репозитория

```bash
sudo mkdir -p /opt
sudo git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> /opt/islamplus-bot
sudo chown -R $USER:$USER /opt/islamplus-bot
cd /opt/islamplus-bot
```

### 3. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка базы данных

```bash
sudo -u postgres psql
```

В psql:
```sql
CREATE DATABASE islamplus;
CREATE USER islamplus WITH PASSWORD 'ваш_пароль';
GRANT ALL PRIVILEGES ON DATABASE islamplus TO islamplus;
\q
```

### 5. Настройка переменных окружения

```bash
cp .env.example .env
nano .env
```

Укажите:
- `BOT_TOKEN`
- `DATABASE_URL=postgresql+asyncpg://islamplus:ваш_пароль@localhost:5432/islamplus`
- `ADMIN_IDS`

### 6. Инициализация базы данных

```bash
source venv/bin/activate
python init_db.py
```

### 7. Установка systemd service

```bash
sudo cp islamplus-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/islamplus-bot.service
```

Убедитесь, что пути правильные:
- `WorkingDirectory=/opt/islamplus-bot`
- `ExecStart=/opt/islamplus-bot/venv/bin/python /opt/islamplus-bot/run.py`

```bash
sudo systemctl daemon-reload
sudo systemctl enable islamplus-bot
sudo systemctl start islamplus-bot
```

### 8. Проверка статуса

```bash
sudo systemctl status islamplus-bot
```

---

## 🔧 Полезные команды

### Управление сервисом

```bash
# Статус
sudo systemctl status islamplus-bot

# Запуск
sudo systemctl start islamplus-bot

# Остановка
sudo systemctl stop islamplus-bot

# Перезапуск
sudo systemctl restart islamplus-bot

# Просмотр логов
sudo journalctl -u islamplus-bot -f

# Последние 50 строк логов
sudo journalctl -u islamplus-bot -n 50
```

### Работа с Git

```bash
cd /opt/islamplus-bot

# Обновить код
sudo -u www-data git pull

# Посмотреть статус
git status

# Откатить изменения
git reset --hard origin/main
```

---

## 🔐 Безопасность

### Настройка прав доступа

```bash
sudo chown -R www-data:www-data /opt/islamplus-bot
sudo chmod 600 /opt/islamplus-bot/.env
```

### Firewall (если используете)

```bash
# Разрешить SSH (обязательно!)
sudo ufw allow 22/tcp

# PostgreSQL (только локально)
# В /etc/postgresql/*/main/pg_hba.conf убедитесь, что:
# local   all             all                                     peer
```

---

## 🐛 Решение проблем

### Бот не запускается

1. **Проверьте логи:**
```bash
sudo journalctl -u islamplus-bot -n 100
```

2. **Проверьте .env файл:**
```bash
sudo nano /opt/islamplus-bot/.env
```

3. **Проверьте права доступа:**
```bash
sudo chown -R www-data:www-data /opt/islamplus-bot
```

4. **Проверьте базу данных:**
```bash
sudo -u postgres psql -d islamplus -c "\dt"
```

### Ошибки при обновлении

Если `deploy.sh` выдает ошибки:

1. **Проверьте права на скрипт:**
```bash
sudo chmod +x /opt/islamplus-bot/deploy.sh
```

2. **Запустите вручную:**
```bash
cd /opt/islamplus-bot
sudo -u www-data git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart islamplus-bot
```

---

## 📝 Workflow для разработки

### Локальная разработка:

1. Редактируете код на компьютере
2. Тестируете локально (если нужно)
3. Коммитите и пушите в Git:
```bash
git add .
git commit -m "Описание изменений"
git push
```

### На сервере:

1. Подключаетесь к серверу (или используете deploy.sh)
2. Обновляете код:
```bash
cd /opt/islamplus-bot
sudo ./deploy.sh
```

Или просто:
```bash
cd /opt/islamplus-bot
sudo -u www-data git pull
sudo systemctl restart islamplus-bot
```

---

## 🌐 Автоматическое обновление через Webhook (опционально)

Если вы хотите, чтобы бот обновлялся автоматически при push в Git:

1. **Установите webhook сервер:**
```bash
# Используйте готовые решения или создайте простой скрипт
```

2. **Настройте GitHub/GitLab webhook:**
   - URL: `http://ваш-сервер:порт/webhook`
   - Событие: Push

3. **Создайте простой веб-сервер** (опционально, для продвинутых)

---

## ✅ Чеклист после установки

- [ ] Бот запущен и работает (`systemctl status`)
- [ ] Логи не показывают ошибок
- [ ] Бот отвечает на команду `/start` в Telegram
- [ ] База данных инициализирована
- [ ] Переменные окружения настроены
- [ ] Автозапуск включен (`systemctl is-enabled`)
- [ ] Права доступа настроены правильно

---

**Готово! 🎉 Теперь вы можете легко обновлять бота через Git.**