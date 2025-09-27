## Настройка окружения

1) Python 3.10+
2) Установите зависимости:
```
pip install -r requirements.txt
```
3) Скопируйте `configs/config.sample.env` в `.env` и заполните:
- TG_API_ID, TG_API_HASH, TG_SESSION_STRING
- TG_INVITE_LINK=https://t.me/joinchat/AAAAAFElevcbuyK0EeBX9Q
- VK_GROUP_TOKEN, VK_GROUP_ID (например, `club147630752`)
- TZ=Europe/Moscow
- (опц.) GigaChat: GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET, GIGACHAT_SCOPE=GIGACHAT_API_PERS

Проверка:
```
python -m tg2vk --env .env status
```


