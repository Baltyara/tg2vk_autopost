import os
import logging
from typing import List, Tuple
from datetime import datetime
import zoneinfo

from .config import AppConfig
from .telegram_source import backfill_all
from .syncer import sync_publish
from .rate_control import get_daily_count, can_post
from .time_utils import is_within_moscow_day_window

log = logging.getLogger(__name__)


def process_batch(cfg: AppConfig, ignore_day_window: bool = False) -> None:
    """
    Обрабатывает видео по одному: скачивает 1 видео, публикует его, удаляет, повторяет до лимита
    """
    now = datetime.now(zoneinfo.ZoneInfo(cfg.tz))
    
    # Проверяем дневной лимит
    daily_count = get_daily_count(now)
    if daily_count >= cfg.policy.max_daily_posts:
        log.info(f"Достигнут дневной лимит: {daily_count}/{cfg.policy.max_daily_posts}")
        return
    
    # Проверяем дневное окно
    if not ignore_day_window and not is_within_moscow_day_window(cfg.policy.day_start_hour, cfg.policy.day_end_hour):
        log.info(f"Вне дневного окна публикации: {now.hour}:{now.minute:02d}")
        return
    
    # Определяем сколько видео можно обработать
    remaining_daily = cfg.policy.max_daily_posts - daily_count
    max_videos = min(20, remaining_daily)  # Максимум 20 видео за раз
    
    if max_videos <= 0:
        log.info("Нет места для обработки новых видео")
        return
    
    log.info(f"Начинаем обработку: {max_videos} видео по одному (осталось в дне: {remaining_daily})")
    
    published_count = 0
    
    # Обрабатываем видео по одному
    for i in range(max_videos):
        log.info(f"Обработка видео {i+1}/{max_videos}")
        
        # Скачиваем одно видео
        downloaded_count = _download_single_video(cfg)
        if downloaded_count == 0:
            log.info("Нет новых видео для обработки")
            break
        
        # Публикуем это видео
        published_count += _publish_videos(cfg, ignore_day_window)
        
        # Удаляем опубликованное видео
        if cfg.policy.auto_cleanup:
            _cleanup_published()
    
    log.info(f"Обработка завершена: опубликовано {published_count} видео")


def _download_single_video(cfg: AppConfig) -> int:
    """Скачивает одно новое видео из Telegram"""
    try:
        import asyncio
        return asyncio.run(backfill_all(cfg, 1))
    except Exception as e:
        log.error(f"Ошибка при скачивании видео: {e}")
        return 0


def _download_batch(cfg: AppConfig, max_count: int) -> int:
    """Скачивает до max_count новых видео из Telegram"""
    try:
        # Запускаем backfill с ограничением
        import asyncio
        return asyncio.run(backfill_all(cfg, max_count))
    except Exception as e:
        log.error(f"Ошибка при скачивании видео: {e}")
        return 0


def _publish_videos(cfg: AppConfig, ignore_day_window: bool) -> int:
    """Публикует доступные видео из очереди"""
    try:
        from .syncer import sync_publish
        sync_publish(cfg, ignore_day_window)
        return 1
    except Exception as e:
        log.error(f"Ошибка при публикации: {e}")
        return 0


def _cleanup_published() -> int:
    """Удаляет опубликованные видео из файловой системы"""
    cleaned_count = 0
    inbox_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "inbox")
    
    if not os.path.exists(inbox_dir):
        return 0
    
    # Читаем состояние опубликованных видео
    state_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "state.jsonl")
    published_videos = set()
    
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        import json
                        data = json.loads(line)
                        if data.get("status") == "published":
                            video_file = data.get("video_file")
                            if video_file:
                                published_videos.add(video_file)
                    except Exception as e:
                        log.warning(f"Ошибка при чтении строки состояния: {e}")
    
    # Удаляем опубликованные видео
    for filename in os.listdir(inbox_dir):
        if filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            file_path = os.path.join(inbox_dir, filename)
            if file_path in published_videos:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                    log.info(f"Удален опубликованный файл: {filename}")
                except Exception as e:
                    log.error(f"Ошибка при удалении файла {filename}: {e}")
    
    return cleaned_count


def run_continuous(cfg: AppConfig) -> None:
    """Запускает обработку: 20 видео, затем перерыв на сутки"""
    log.info("Запуск обработки: 20 видео, затем перерыв на сутки")
    
    while True:
        try:
            # Обрабатываем 20 видео
            process_batch(cfg)
            
            # Проверяем, достигли ли дневного лимита
            now = datetime.now(zoneinfo.ZoneInfo(cfg.tz))
            daily_count = get_daily_count(now)
            
            if daily_count >= cfg.policy.max_daily_posts:
                log.info(f"Достигнут дневной лимит ({daily_count}/{cfg.policy.max_daily_posts}). Перерыв до завтра.")
                # Ждем до следующего дня (24 часа)
                import time
                time.sleep(24 * 60 * 60)  # 24 часа
            else:
                # Ждем 5 минут перед следующей проверкой
                import time
                time.sleep(300)
            
        except KeyboardInterrupt:
            log.info("Остановка по сигналу пользователя")
            break
        except Exception as e:
            log.error(f"Ошибка в непрерывной обработке: {e}")
            import time
            time.sleep(60)  # Ждем минуту при ошибке
