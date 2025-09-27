# TG2VK AutoPost

Автоматический постинг вертикальных видео из Telegram канала в VK группу с пакетной обработкой и ограничениями.

## 🚀 Быстрый старт

### Развертывание на сервер

```bash
# Клонируйте репозиторий
git clone <repository_url>
cd tg2vk_autopost

# Разверните на сервер
./quick_deploy.sh
```

### Настройка

1. Подключитесь к серверу: `ssh root@5.129.229.223`
2. Перейдите в директорию: `cd /opt/tg2vk_autopost`
3. Скопируйте конфигурацию: `cp configs/config.prod.env .env`
4. Отредактируйте `.env` файл с вашими токенами
5. Запустите сервис: `systemctl start tg2vk-autopost.service`

## 📋 Основные возможности

- **Пакетная обработка**: Скачивает до 20 видео за раз, публикует их, удаляет опубликованные
- **Дневные ограничения**: Максимум 20 постов в день
- **Временные окна**: Работает только с 10:00 до 22:00 по Москве
- **Автоматическая очистка**: Удаляет опубликованные видео
- **Фильтрация контента**: Проверяет вертикальность, модерация через GigaChat
- **Дедупликация**: Предотвращает повторную публикацию

## 🛠 Управление

### Локальные команды

```bash
# Управление сервисом
./scripts/server_control.sh start|stop|restart|status|logs

# Ручные команды
./scripts/server_control.sh batch    # Пакетная обработка
./scripts/server_control.sh sync     # Синхронизация
./scripts/server_control.sh backfill # Бэкфилл из Telegram
```

### Команды на сервере

```bash
cd /opt/tg2vk_autopost
source .venv/bin/activate

python -m tg2vk batch      # Пакетная обработка
python -m tg2vk sync       # Синхронизация
python -m tg2vk backfill   # Бэкфилл
python -m tg2vk status     # Статус
python -m tg2vk daemon     # Демон
```

## ⚙️ Конфигурация

### Основные параметры

```env
# Telegram API
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash
TG_SESSION_STRING=your_session_string
TG_INVITE_LINK=https://t.me/joinchat/AAAAAFElevcbuyK0EeBX9Q

# VK API
VK_GROUP_TOKEN=your_vk_token
VK_GROUP_ID=club147630752

# Политика публикации
POSTING_POLICY__MAX_DAILY_POSTS=20
POSTING_POLICY__BATCH_SIZE=20
POSTING_POLICY__AUTO_CLEANUP=true
```

### Политика ссылок

- **Разрешены**: только `https://t.me/joinchat/AAAAAFElevcbuyK0EeBX9Q`
- **Блокируются**: все остальные ссылки
- **Удаляется**: фраза "Подписывайся 👉 PZDC (https://t.me/joinchat/AAAAAFElevcbuyK0EeBX9Q)"

## 📊 Мониторинг

### Логи

```bash
# Логи сервиса
journalctl -u tg2vk-autopost.service -f

# Логи приложения
tail -f /opt/tg2vk_autopost/logs/app.log
```

### Статистика

```bash
# Статус приложения
python -m tg2vk status

# Статус сервиса
systemctl status tg2vk-autopost.service
```

## 🔧 Архитектура

```
tg2vk_autopost/
├── src/tg2vk/           # Исходный код
│   ├── batch_processor.py    # Пакетная обработка
│   ├── telegram_source.py    # Telegram API
│   ├── vk_publisher.py       # VK API
│   ├── syncer.py             # Синхронизация
│   └── config.py             # Конфигурация
├── scripts/              # Скрипты развертывания
├── configs/              # Конфигурации
└── docs/                 # Документация
```

## 📚 Документация

- [DEPLOYMENT.md](DEPLOYMENT.md) - Подробное руководство по развертыванию
- [docs/SETUP.md](docs/SETUP.md) - Настройка API ключей
- [docs/USAGE.md](docs/USAGE.md) - Использование команд
- [docs/roadmap.md](docs/roadmap.md) - План разработки

## 🚨 Устранение неполадок

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

## 📈 Производительность

- **Пакетная обработка**: 20 видео за раз
- **Дневной лимит**: 20 постов максимум
- **Интервалы**: 60-120 минут между постами
- **Временное окно**: 10:00-22:00 МСК
- **Автоочистка**: Удаление опубликованных видео

## 🔄 Обновление

```bash
# Пересоздать архив и развернуть
./scripts/deploy.sh

# Перезапустить сервис
./scripts/server_control.sh restart
```

## 📝 Лицензия

MIT License
