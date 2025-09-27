from datetime import datetime
import zoneinfo


def is_within_moscow_day_window(start_hour: int, end_hour: int) -> bool:
    tz = zoneinfo.ZoneInfo("Europe/Moscow")
    now = datetime.now(tz)
    return start_hour <= now.hour < end_hour


