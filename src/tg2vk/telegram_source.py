import asyncio
import os
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Message, DocumentAttributeVideo

from .config import AppConfig
from .text_utils import sanitize_caption
from .media_utils import ffprobe, is_vertical_viable
import json
from datetime import datetime, timezone
from .hash_utils import file_md5
from .queue import enqueue_if_missing


INBOX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "inbox"))


def _ensure_dirs() -> None:
    os.makedirs(INBOX_DIR, exist_ok=True)


def build_client(cfg: AppConfig) -> TelegramClient:
    if not cfg.tg_api_id or not cfg.tg_api_hash:
        raise RuntimeError("TG_API_ID/TG_API_HASH не заданы")
    if not cfg.tg_session_string:
        raise RuntimeError("TG_SESSION_STRING не задан. Сгенерируйте строковую сессию Telethon.")
    return TelegramClient(StringSession(cfg.tg_session_string), cfg.tg_api_id, cfg.tg_api_hash)


async def join_by_invite(client: TelegramClient, invite_link: str) -> None:
    if not invite_link:
        return
    # joinchat/<hash>
    hash_part = invite_link.rsplit("/", 1)[-1]
    if "joinchat" in invite_link and hash_part:
        try:
            await client(ImportChatInviteRequest(hash_part))
        except Exception:
            # возможно уже внутри канала
            pass


def _message_is_vertical_video(msg: Message) -> bool:
    # prefer attributes width/height
    if msg.video:
        for attr in (msg.video.attributes or []):
            if isinstance(attr, DocumentAttributeVideo) and attr.w and attr.h:
                w, h = int(attr.w), int(attr.h)
                if h == 0:
                    return False
                aspect = h / max(1, w)
                return aspect >= 1.6
    if msg.document and msg.document.attributes:
        for attr in msg.document.attributes:
            if isinstance(attr, DocumentAttributeVideo) and attr.w and attr.h:
                w, h = int(attr.w), int(attr.h)
                if h == 0:
                    return False
                aspect = h / max(1, w)
                return aspect >= 1.6
    return False


@dataclass
class DownloadResult:
    message_id: int
    path: Optional[str]
    caption: str


async def iter_vertical_videos(client: TelegramClient, entity: str) -> AsyncIterator[Message]:
    async for msg in client.iter_messages(entity, reverse=True):
        if getattr(msg, "video", None) or getattr(msg, "document", None):
            if _message_is_vertical_video(msg):
                yield msg


async def download_message_video(client: TelegramClient, msg: Message) -> DownloadResult:
    _ensure_dirs()
    filename = f"tg_{msg.id}.mp4"
    dest_path = os.path.join(INBOX_DIR, filename)
    path = await client.download_media(message=msg, file=dest_path)
    info = ffprobe(path) if path else None
    if not info or not is_vertical_viable(info):
        if path and os.path.exists(path):
            os.remove(path)
        return DownloadResult(message_id=msg.id, path=None, caption="")
    caption = sanitize_caption((msg.message or "").strip())
    return DownloadResult(message_id=msg.id, path=path, caption=caption)


async def backfill_all(cfg: AppConfig, max_count: int = None) -> int:
    client = build_client(cfg)
    async with client:
        await join_by_invite(client, cfg.tg_invite_link or "")
        entity = cfg.tg_invite_link or ""
        state_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "state.jsonl"))
        seen = set()
        if os.path.exists(state_path):
            with open(state_path, "r", encoding="utf-8") as r:
                for line in r:
                    try:
                        obj = json.loads(line)
                        seen.add(obj.get("tg_message_id"))
                    except Exception:
                        pass

        downloaded_count = 0
        with open(state_path, "a", encoding="utf-8") as w:
            async for msg in iter_vertical_videos(client, entity):
                if msg.id in seen:
                    continue
                
                # Проверяем лимит
                if max_count is not None and downloaded_count >= max_count:
                    break
                    
                res = await download_message_video(client, msg)
                if not res.path:
                    continue
                md5 = file_md5(res.path)
                rec = {
                    "tg_message_id": msg.id,
                    "date": msg.date.astimezone(timezone.utc).isoformat() if isinstance(msg.date, datetime) else None,
                    "caption": res.caption,
                    "file_path": res.path,
                    "md5": md5,
                    "status": "downloaded"
                }
                w.write(json.dumps(rec, ensure_ascii=False) + "\n")
                enqueue_if_missing(msg.id, res.path, res.caption)
                downloaded_count += 1
        
        return downloaded_count


