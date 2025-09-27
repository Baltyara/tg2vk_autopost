## Использование

Бэкфилл истории из Telegram (скачивание вертикальных видео и формирование `data/state.jsonl`):
```
bash scripts/backfill.sh --env ./configs/config.sample.env
```

Публикация в VK (с соблюдением дневного окна, лимита и модерации):
```
bash scripts/run.sh sync --env ./configs/config.sample.env
```

Демон с периодическим sync каждые 5 минут:
```
bash scripts/run.sh --env ./configs/config.sample.env
```

Проверить очередь и опубликованные:
```
python -m tg2vk --env .env status
```

Посмотреть метрики:
- `data/metrics.json`


