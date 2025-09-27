# Развертывание TG2VK AutoPost

## Быстрый старт

### 1. Развертывание на сервер

```bash
# Из корня проекта
./scripts/deploy.sh
```

### 2. Настройка на сервере

```bash
# Подключитесь к серверу
ssh user@your-server.com

# Перейдите в директорию приложения
cd /opt/tg2vk_autopost

# Скопируйте конфигурацию
cp configs/config.prod.env .env

# Отредактируйте .env файл
nano .env
```

### 3. Заполните .env файл

```env
# Telegram API (уже заполнены)
TG_API_ID=27435631
TG_API_HASH=c88866acc346c546dc2061f33414ff9c
TG_SESSION_STRING=ваш_session_string_здесь
TG_INVITE_LINK=https://t.me/joinchat/AAAAAFElevcbuyK0EeBX9Q

# VK API
VK_GROUP_TOKEN=ваш_vk_token_здесь
VK_GROUP_ID=club147630752

# GigaChat (опционально)
GIGACHAT_CLIENT_ID=e207f4c0-3fc6-4725-8cc3-629d726dd522
GIGACHAT_CLIENT_SECRET=ваш_secret_здесь
```

### 4. Запуск сервиса

```bash
# Включить автозапуск
systemctl enable tg2vk-autopost.service

# Запустить сервис
systemctl start tg2vk-autopost.service

# Проверить статус
systemctl status tg2vk-autopost.service
```

## Управление сервисом

### Локальные команды (с вашего компьютера)

```bash
# Запуск/остановка
./scripts/server_control.sh start
./scripts/server_control.sh stop
./scripts/server_control.sh restart

# Статус и логи
./scripts/server_control.sh status
./scripts/server_control.sh logs

# Ручные команды
./scripts/server_control.sh batch    # Пакетная обработка
./scripts/server_control.sh sync     # Синхронизация
./scripts/server_control.sh backfill # Бэкфилл из Telegram
./scripts/server_control.sh status-app # Статус приложения
```

### Команды на сервере

```bash
# Подключение к серверу
ssh user@your-server.com

# Переход в директорию приложения
cd /opt/tg2vk_autopost

# Активация виртуального окружения
source .venv/bin/activate

# Запуск команд
python -m tg2vk batch      # Пакетная обработка
python -m tg2vk sync       # Синхронизация
python -m tg2vk backfill   # Бэкфилл
python -m tg2vk status     # Статус
python -m tg2vk daemon     # Демон (непрерывная работа)
```

## Особенности работы

### Пакетная обработка
- Скачивает до 20 видео за раз
- Публикует их в VK
- Автоматически удаляет опубликованные видео
- Соблюдает дневной лимит (максимум 20 постов в день)

### Временные ограничения
- Работает только с 10:00 до 22:00 по Москве
- Интервал между постами: 60-120 минут
- Максимум 20 постов в день

### Мониторинг
- Логи: `journalctl -u tg2vk-autopost.service -f`
- Статус: `systemctl status tg2vk-autopost.service`
- Статистика: `python -m tg2vk status`

## Обновление

```bash
# Пересоздать архив и развернуть
./scripts/deploy.sh

# Перезапустить сервис
./scripts/server_control.sh restart
```

## Устранение неполадок

### Сервис не запускается
```bash
# Проверить логи
journalctl -u tg2vk-autopost.service -n 50

# Проверить конфигурацию
cd /opt/tg2vk_autopost
source .venv/bin/activate
python -m tg2vk status
```

### Проблемы с Telegram
```bash
# Проверить сессию
python -m tg2vk backfill
```

### Проблемы с VK
```bash
# Проверить токен
python -m tg2vk sync --ignore-day-window
```

## Структура файлов на сервере

```
/opt/tg2vk_autopost/
├── .venv/                 # Виртуальное окружение
├── data/
│   ├── inbox/            # Скачанные видео
│   ├── state.jsonl       # Состояние обработки
│   └── rate_state.json   # Статистика публикаций
├── logs/
│   └── app.log          # Логи приложения
├── .env                 # Конфигурация
└── src/                 # Исходный код
```
