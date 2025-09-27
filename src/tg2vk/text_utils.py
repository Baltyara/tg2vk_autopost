import re

WHITELIST_URL = "https://t.me/joinchat/AAAAAFElevcbuyK0EeBX9Q"
BAN_PHRASE_REGEX = re.compile(r"Подписывайся\s*👉\s*PZDC\s*\(https?://t\.me/joinchat/[^)]+\)", re.IGNORECASE)
URL_REGEX = re.compile(r"https?://\S+")


def sanitize_caption(caption: str) -> str:
    if not caption:
        return ""
    text = BAN_PHRASE_REGEX.sub("", caption)
    # Политика: оставлять только WHITELIST_URL, все прочие ссылки удалять
    def _filter_url(match: re.Match) -> str:
        url = match.group(0)
        return url if url == WHITELIST_URL else ""

    text = URL_REGEX.sub(_filter_url, text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_caption_links_allowed(caption: str) -> bool:
    if not caption:
        return True
    urls = URL_REGEX.findall(caption)
    if not urls:
        return True
    return all(u == WHITELIST_URL for u in urls)

