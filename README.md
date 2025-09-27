# TG2VK AutoPost

Автоматический постинг вертикальных видео из Telegram канала в VK группу с пакетной обработкой и ограничениями.

## 🚀 Быстрый старт

### Развертывание на сервер

```bash
# Клонируйте репозиторий
git clone https://github.com/Baltyara/tg2vk_autopost.git
cd tg2vk_autopost

# Разверните на сервер
./quick_deploy.sh
```

### Настройка

1. **Получите токены API:**
   - Следуйте инструкции в [TOKEN_SETUP_GUIDE.md](TOKEN_SETUP_GUIDE.md)
   - Получите Telegram API ключи (api_id, api_hash, session_string)
   - Получите VK токен группы (group_token, group_id)

2. **Настройте конфигурацию:**
   - Скопируйте конфигурацию: `cp configs/config.sample.env .env`
   - Отредактируйте `.env` файл с вашими токенами
   - Проверьте настройки: `python3 -m tg2vk --help`

3. **Запустите сервис:**
   - `systemctl start tg2vk-autopost.service`
   - Проверьте статус: `systemctl status tg2vk-autopost.service`

## 📋 Основные возможности

- **Пакетная обработка**: Скачивает до 20 видео за раз, публикует их, удаляет опубликованные
- **Дневные ограничения**: Максимум 20 постов в день
- **Временные окна**: Работает только с 10:00 до 22:00 по Москве
- **Автоматическая очистка**: Удаляет опубликованные видео
- **Фильтрация контента**: Проверяет вертикальность, базовая модерация по ключевым словам
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
TG_INVITE_LINK=https://t.me/joinchat/your_invite_link

# VK API
VK_GROUP_TOKEN=your_vk_token
VK_GROUP_ID=your_group_id

# Политика публикации
POSTING_DAY_START_HOUR=10
POSTING_DAY_END_HOUR=22
POSTS_PER_DAY_MIN=8
POSTS_PER_DAY_MAX=12
POSTING_INTERVAL_MIN_MINUTES=60
POSTING_INTERVAL_MAX_MINUTES=120
```

### Получение токенов

#### Telegram API ключи

1. **Создайте приложение:**
   - Перейдите на https://my.telegram.org/apps
   - Войдите в аккаунт Telegram
   - Нажмите "Create application"
   - Заполните форму:
     - App title: `tg2vk_autopost`
     - Short name: `tg2vk`
     - Platform: `Desktop`
   - Получите `api_id` и `api_hash`

2. **Получите session_string:**
   - Откройте https://web.telegram.org/a/
   - Войдите в аккаунт
   - Нажмите F12 → Console
   - Выполните код:
   ```javascript
   const authKey = localStorage.getItem('dc2_auth_key');
   console.log('Session string:', authKey);
   ```

#### VK токены

1. **Создайте VK приложение:**
   - Перейдите на https://vk.com/apps?act=manage
   - Нажмите "Создать приложение"
   - Заполните:
     - Название: `tg2vk_autopost`
     - Платформа: "Веб-сайт"
     - Адрес сайта: `https://example.com`
   - Получите App ID

2. **Получите токен группы:**
   - Откройте ссылку (замените YOUR_APP_ID):
   ```
   https://oauth.vk.com/authorize?client_id=YOUR_APP_ID&redirect_uri=https://oauth.vk.com/blank.html&scope=video,wall,groups&response_type=token&v=5.131&display=page
   ```
   - Войдите в VK и разрешите доступ
   - Скопируйте `access_token` из URL
   - Укажите ID группы в `VK_GROUP_ID`

**Подробная инструкция:** [TOKEN_SETUP_GUIDE.md](TOKEN_SETUP_GUIDE.md)

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

- [TOKEN_SETUP_GUIDE.md](TOKEN_SETUP_GUIDE.md) - Подробная инструкция по получению токенов
- [DEPLOYMENT.md](DEPLOYMENT.md) - Подробное руководство по развертыванию
- [docs/SETUP.md](docs/SETUP.md) - Настройка API ключей
- [docs/USAGE.md](docs/USAGE.md) - Использование команд
- [roadmap.md](roadmap.md) - План разработки

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
