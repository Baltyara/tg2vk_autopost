import os
import sys
from typing import Optional
import time

import typer
from rich.console import Console
from dotenv import load_dotenv
from .logging_setup import setup_logging
from .config import AppConfig
from .telegram_source import backfill_all
from .syncer import sync_publish
from .batch_processor import process_batch, run_continuous

app = typer.Typer(add_completion=False, help="TG→VK автопостинг вертикальных видео")
console = Console()


def init_env(env_file: Optional[str] = None) -> None:
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file, override=True)
    else:
        load_dotenv(override=True)


@app.callback()
def main(
    env_file: Optional[str] = typer.Option(None, "--env", help="Путь к .env"),
):
    init_env(env_file)
    setup_logging()
    # Load config to validate env early
    AppConfig()


@app.command()
def run():
    cfg = AppConfig()
    console.print("Старт демона: периодический sync в дневное окно")
    while True:
        try:
            sync_publish(cfg)
        except Exception as e:
            console.print(f"[red]Ошибка в sync:[/] {e}")
        time.sleep(300)


@app.command()
def sync(ignore_day_window: bool = typer.Option(False, "--ignore-day-window", help="Публикация вне дневного окна")):
    cfg = AppConfig()
    console.print("Публикую непостченные записи в VK…")
    sync_publish(cfg, ignore_day_window=ignore_day_window)
    console.print("Готово")


@app.command()
def backfill():
    cfg = AppConfig()
    console.print("Начинаю бэкфилл из Telegram…")
    import asyncio

    asyncio.run(backfill_all(cfg))
    console.print("Готово")


@app.command()
def batch(ignore_day_window: bool = typer.Option(False, "--ignore-day-window", help="Обработка вне дневного окна")):
    """Обрабатывает пакет видео: скачивает, публикует, удаляет"""
    cfg = AppConfig()
    console.print("Начинаю пакетную обработку…")
    process_batch(cfg, ignore_day_window)
    console.print("Готово")


@app.command()
def daemon():
    """Запускает непрерывную пакетную обработку"""
    cfg = AppConfig()
    console.print("Запуск демона пакетной обработки…")
    run_continuous(cfg)


@app.command()
def status():
    from .syncer import iter_state_records
    count_total = 0
    count_published = 0
    for rec in iter_state_records() or []:
        count_total += 1
        if rec.get("vk_post"):
            count_published += 1
    console.print(f"Всего записей: {count_total}, опубликовано: {count_published}, в очереди: {count_total - count_published}")


@app.command()
def inspect(tg_message_id: int):
    from .syncer import iter_state_records
    for rec in iter_state_records() or []:
        if int(rec.get("tg_message_id") or 0) == tg_message_id:
            console.print(rec)
            return
    console.print("Не найдено")


if __name__ == "__main__":
    app()


