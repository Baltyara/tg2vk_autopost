# Инструкция по получению токенов для tg2vk_autopost

## Telegram токены

### 1. Получение API ID и API Hash

1. **Перейдите на сайт разработчика Telegram:**
   - Откройте https://my.telegram.org/apps в браузере
   - Войдите в свой аккаунт Telegram (введите номер телефона и код подтверждения)

2. **Создайте новое приложение:**
   - Нажмите кнопку "Create application"
   - Заполните форму:
     - **App title**: `tg2vk_autopost` (или любое другое название)
     - **Short name**: `tg2vk` (или любое другое короткое название)
     - **Platform**: выберите `Desktop`
     - **Description**: можно оставить пустым или написать "Автопостинг видео"
   - Нажмите "Create application"

3. **Получите API ключи:**
   - После создания приложения вы увидите:
     - **App api_id**: числовой идентификатор (например: 12345678)
     - **App api_hash**: строковый хеш (например: abc123def456...)
   - Скопируйте эти значения - они понадобятся для настройки

### 2. Получение Session String

1. **Откройте Telegram Web:**
   - Перейдите на https://web.telegram.org/a/
   - Войдите в свой аккаунт Telegram

2. **Откройте инструменты разработчика:**
   - Нажмите F12 или правой кнопкой мыши → "Исследовать элемент"
   - Перейдите во вкладку "Console"

3. **Получите данные сессии:**
   - Вставьте и выполните следующий код:

```javascript
// Получаем auth_key из localStorage
const authKey = localStorage.getItem('dc2_auth_key');
console.log('Auth key:', authKey);

// Получаем user_auth
const userAuth = localStorage.getItem('user_auth');
console.log('User auth:', userAuth);

// Если dc2_auth_key не найден, попробуйте другие варианты
const altAuthKey = localStorage.getItem('auth_key');
console.log('Alternative auth key:', altAuthKey);
```

4. **Скопируйте полученные значения:**
   - Используйте полученный `auth_key` как `TG_SESSION_STRING`
   - Если `dc2_auth_key` не найден, попробуйте `auth_key`

## VK токены

### 1. Создание VK приложения

1. **Перейдите в VK для разработчиков:**
   - Откройте https://vk.com/apps?act=manage
   - Войдите в свой аккаунт VK

2. **Создайте новое приложение:**
   - Нажмите "Создать приложение"
   - Заполните форму:
     - **Название**: `tg2vk_autopost` (или любое другое)
     - **Платформа**: выберите "Веб-сайт"
     - **Адрес сайта**: `https://example.com` (можно любой)
   - Нажмите "Подключить приложение"

3. **Получите App ID:**
   - После создания приложения вы увидите **ID приложения** (число)
   - Запишите этот ID - он понадобится для получения токена

### 2. Получение Group Token

1. **Откройте страницу авторизации VK:**
   ```
   https://oauth.vk.com/authorize?client_id=ВАШ_APP_ID&redirect_uri=https://oauth.vk.com/blank.html&scope=video,wall,groups&response_type=token&v=5.131&display=page
   ```
   Замените `ВАШ_APP_ID` на ID приложения, полученный в предыдущем шаге

2. **Авторизуйтесь:**
   - Войдите в свой аккаунт VK
   - Разрешите доступ приложению (поставьте галочки на нужные права)

3. **Получите токен:**
   - После авторизации вы будете перенаправлены на страницу с токеном в URL
   - Скопируйте `access_token` из URL (часть после `access_token=`)
   - Скопируйте `user_id` из URL (часть после `user_id=`)

### 2. Настройка файла .env

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
TZ=Europe/Moscow

# Telegram (Telethon)
TG_API_ID=ваш_api_id
TG_API_HASH=ваш_api_hash
TG_SESSION_STRING=ваш_session_string
TG_INVITE_LINK=https://t.me/joinchat/ваша_ссылка

# VK
VK_GROUP_TOKEN=ваш_group_token
VK_GROUP_ID=ваш_group_id

# Posting policy
POSTING_DAY_START_HOUR=10
POSTING_DAY_END_HOUR=22
POSTS_PER_DAY_MIN=8
POSTS_PER_DAY_MAX=12
POSTING_INTERVAL_MIN_MINUTES=60
POSTING_INTERVAL_MAX_MINUTES=120
```

## Безопасность

⚠️ **ВАЖНО**: Никогда не публикуйте токены в открытом доступе!

- Добавьте `.env` в `.gitignore`
- Не коммитьте файлы с токенами в Git
- Используйте переменные окружения в продакшене
- Регулярно обновляйте токены

## Проверка токенов

После настройки токенов проверьте их работоспособность:

```bash
python3 -m tg2vk --help
```

Если команда выполняется без ошибок, токены настроены корректно.
