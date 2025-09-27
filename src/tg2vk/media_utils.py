import json
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoInfo:
    width: int
    height: int
    duration: float
    size_bytes: int


def ffprobe(path: str) -> Optional[VideoInfo]:
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height:format=duration,size",
            "-of",
            "json",
            path,
        ]
        out = subprocess.check_output(cmd)
        data = json.loads(out)
        stream = (data.get("streams") or [{}])[0]
        fmt = data.get("format") or {}
        return VideoInfo(
            width=int(stream.get("width") or 0),
            height=int(stream.get("height") or 0),
            duration=float(fmt.get("duration") or 0.0),
            size_bytes=int(fmt.get("size") or 0),
        )
    except Exception:
        return None


def is_vertical_viable(info: VideoInfo) -> bool:
    if info.width <= 0 or info.height <= 0:
        return False
    aspect = info.height / max(1, info.width)
    if aspect < 1.6:
        return False
    # VK безопасные пределы: длительность <= 15 мин, размер <= 2GB (практично меньше)
    if info.duration > 15 * 60:
        return False
    if info.size_bytes > 1_800_000_000:
        return False
    return True


def is_stories_suitable(info: VideoInfo) -> bool:
    """Проверяет подходит ли видео для Stories (длительность < 1 минуты)"""
    return info.duration < 60.0


