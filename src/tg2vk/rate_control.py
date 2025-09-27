import json
import os
from datetime import datetime, timedelta
import zoneinfo


STATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
RATE_PATH = os.path.join(STATE_DIR, "rate_state.json")
METRICS_PATH = os.path.join(STATE_DIR, "metrics.json")


def _now_msk():
    return datetime.now(zoneinfo.ZoneInfo("Europe/Moscow"))


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as r:
            return json.load(r)
    except Exception:
        return {}


def _save_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as w:
        json.dump(data, w, ensure_ascii=False)
    os.replace(tmp, path)


def can_post(now: datetime, min_interval_min: int, max_per_day: int) -> bool:
    # Временно отключаем rate limiting для тестирования
    return True


def get_daily_count(now: datetime) -> int:
    """Получить количество постов за сегодня"""
    state = _load_json(RATE_PATH)
    day_key = now.strftime("%Y-%m-%d")
    per_day = state.get("per_day", {})
    return int(per_day.get(day_key) or 0)


def mark_posted(now: datetime) -> None:
    state = _load_json(RATE_PATH)
    state["last_post_iso"] = now.isoformat()
    day_key = now.strftime("%Y-%m-%d")
    per_day = state.get("per_day", {})
    per_day[day_key] = int(per_day.get(day_key) or 0) + 1
    state["per_day"] = per_day
    _save_json(RATE_PATH, state)


def inc_metric(key: str) -> None:
    m = _load_json(METRICS_PATH)
    m[key] = int(m.get(key) or 0) + 1
    _save_json(METRICS_PATH, m)


