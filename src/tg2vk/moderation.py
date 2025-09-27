import logging


log = logging.getLogger(__name__)


def is_allowed_caption(caption: str) -> bool:
    """Простая модерация по ключевым словам"""
    text = (caption or "").lower()
    banned = ["порно", "эротика", "18+", "лохотрон", "казино", "ставки"]
    if any(word in text for word in banned):
        return False
    return True


