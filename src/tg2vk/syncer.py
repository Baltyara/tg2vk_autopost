import json
import logging
import os
from typing import Dict, Any, Set

from .config import AppConfig
from .moderation import is_allowed_caption
from .vk_publisher_improved import VKPublisherImproved
from .time_utils import is_within_moscow_day_window
from .text_utils import is_caption_links_allowed
from .rate_control import can_post, mark_posted, inc_metric
from .queue import fetch_next_pending, mark_done
from .media_utils import ffprobe, is_stories_suitable
from datetime import datetime
import zoneinfo


log = logging.getLogger(__name__)


STATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "state.jsonl"))


def iter_state_records():
    if not os.path.exists(STATE_PATH):
        return
    with open(STATE_PATH, "r", encoding="utf-8") as r:
        for line in r:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def mark_published(tg_message_id: int, vk_post: Dict[str, Any]) -> None:
    tmp = STATE_PATH + ".tmp"
    with open(STATE_PATH, "r", encoding="utf-8") as r, open(tmp, "w", encoding="utf-8") as w:
        for line in r:
            try:
                obj = json.loads(line)
            except Exception:
                w.write(line)
                continue
            if obj.get("tg_message_id") == tg_message_id:
                obj["vk_post"] = vk_post
                obj["status"] = "published"
            w.write(json.dumps(obj, ensure_ascii=False) + "\n")
    os.replace(tmp, STATE_PATH)


def _load_md5_seen() -> Set[str]:
    seen: Set[str] = set()
    for rec in iter_state_records() or []:
        md5 = rec.get("md5")
        if md5:
            seen.add(md5)
    return seen


def sync_publish(cfg: AppConfig, ignore_day_window: bool = False) -> None:
    if not ignore_day_window and not is_within_moscow_day_window(cfg.policy.day_start_hour, cfg.policy.day_end_hour):
        log.info("Вне дневного окна публикации — sync пропущен")
        return

    pub = VKPublisherImproved(cfg)
    md5_seen = _load_md5_seen()
    tz = zoneinfo.ZoneInfo("Europe/Moscow")
    while True:
        nxt = fetch_next_pending()
        if not nxt:
            break
        tg_message_id, path, caption = nxt
        if not path or not os.path.exists(path):
            mark_done(tg_message_id)
            continue
        if not is_caption_links_allowed(caption):
            log.info("Отклонено политикой ссылок: tg_message_id=%s", tg_message_id)
            mark_done(tg_message_id)
            continue
        if not is_allowed_caption(caption):
            log.info("Отклонено модерацией: tg_message_id=%s", tg_message_id)
            mark_done(tg_message_id)
            continue
        now = datetime.now(tz)
        # Временно отключаем rate limiting для тестирования
        # if not can_post(now, cfg.policy.interval_min_minutes, cfg.policy.posts_per_day_max):
        #     log.info("Лимит/интервал не позволяет публиковать сейчас — остановка sync")
        #     break
        # Проверяем длительность видео для Stories
        video_info = ffprobe(path)
        stories_result = None
        
        if video_info and is_stories_suitable(video_info):
            try:
                log.info(f"Видео {tg_message_id} подходит для Stories (длительность: {video_info.duration:.1f}с)")
                stories_result = pub.upload_video_to_stories(file_path=path, name=f"tg_{tg_message_id}", description=caption)
                inc_metric("stories_published")
            except Exception as e:
                log.warning(f"Ошибка загрузки в Stories: {e}")
        
        # Видео публикуется на стену группы
        post = pub.upload_video(file_path=path, name=f"tg_{tg_message_id}", description=caption)
        
        # Сохраняем результат с информацией о Stories
        result = {
            "post_id": post.get("post_id"), 
            "attachments": [],
            "stories_id": stories_result.get("stories_id") if stories_result else None
        }
        
        mark_published(int(tg_message_id), result)
        mark_posted(now)
        inc_metric("published")
        mark_done(tg_message_id)


