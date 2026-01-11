# Инструкция по установке

## Быстрый старт

1. **Клонирование и установка зависимостей:**
```bash
pip install -r requirements.txt
```

2. **Настройка переменных окружения:**
```bash
cp .env.example .env
# Отредактируйте .env и укажите BOT_TOKEN
```

3. **Запуск PostgreSQL и Redis:**
```bash
docker-compose up -d
```

4. **Инициализация базы данных:**
```bash
python init_db.py
```

5. **Запуск бота:**
```bash
python run.py
```

## Настройка .env файла

Обязательно установите:
- `BOT_TOKEN` - токен бота от @BotFather
- `DATABASE_URL` - URL базы данных (по умолчанию используется из docker-compose)
- `ADMIN_IDS` - ID администраторов через запятую

## Структура БД

База данных будет автоматически создана при первом запуске через `init_db.py` или при использовании миграций Alembic:

```bash
alembic upgrade head
```

## Разработка

Для разработки рекомендуется использовать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

## Примечания

- Убедитесь, что PostgreSQL запущен перед запуском бота
- Для продакшена используйте миграции Alembic вместо прямого создания таблиц
- Redis опционален, но рекомендуется для кэширования в будущем