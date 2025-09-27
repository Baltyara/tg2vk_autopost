import logging
import os
import requests
from typing import Optional

import vk_api
from vk_api.upload import VkUpload

from .config import AppConfig


log = logging.getLogger(__name__)


class VKPublisherImproved:
    def __init__(self, cfg: AppConfig) -> None:
        if not cfg.vk_group_token:
            raise RuntimeError("VK_GROUP_TOKEN не задан")
        self.group_id = _parse_group_id(cfg.vk_group_id)
        self.session = vk_api.VkApi(token=cfg.vk_group_token)
        self.vk = self.session.get_api()
        self.upload = VkUpload(self.session)

    def upload_video(self, file_path: str, name: str, description: str) -> dict:
        """
        Загружает видео в VK группу используя правильный процесс:
        1. Получает upload_url через video.save
        2. Загружает файл на сервер VK
        3. Сохраняет видео через video.save с результатом загрузки
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        
        try:
            # Шаг 1: Получаем upload_url
            log.info(f"Получаем upload_url для видео: {name}")
            video_info = self.vk.video.save(
                name=name,
                description=description,
                group_id=abs(self.group_id),
                wallpost=True  # Публикуем сразу на стену группы
            )
            
            upload_url = video_info['upload_url']
            video_id = video_info['video_id']
            owner_id = video_info['owner_id']
            
            log.info(f"Получен upload_url для video_id={video_id}, owner_id={owner_id}")
            
            # Шаг 2: Загружаем файл на сервер VK
            log.info(f"Загружаем файл {file_path} на сервер VK...")
            with open(file_path, 'rb') as video_file:
                files = {'video_file': video_file}
                response = requests.post(upload_url, files=files)
                response.raise_for_status()
            
            log.info(f"Файл успешно загружен, response: {response.text}")
            
            # Шаг 3: Сохраняем видео (если нужно)
            # VK автоматически обрабатывает загруженное видео
            # и публикует его на стену группы благодаря wallpost=True
            
            return {
                "post_id": video_info.get("post_id"),
                "video_id": video_id,
                "owner_id": owner_id,
                "upload_response": response.text
            }
            
        except Exception as e:
            log.error(f"Ошибка при загрузке видео: {e}")
            raise

    def upload_video_to_group_videos(self, file_path: str, name: str, description: str) -> dict:
        """
        Загружает видео в раздел "Видео" группы (не на стену)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        
        try:
            # Получаем upload_url для загрузки в группу без публикации на стену
            log.info(f"Получаем upload_url для видео в группу: {name}")
            video_info = self.vk.video.save(
                name=name,
                description=description,
                group_id=abs(self.group_id),
                wallpost=False  # НЕ публикуем на стену, только в раздел видео
            )
            
            upload_url = video_info['upload_url']
            video_id = video_info['video_id']
            owner_id = video_info['owner_id']
            
            log.info(f"Получен upload_url для video_id={video_id}, owner_id={owner_id}")
            
            # Загружаем файл
            with open(file_path, 'rb') as video_file:
                files = {'video_file': video_file}
                response = requests.post(upload_url, files=files)
                response.raise_for_status()
            
            log.info(f"Видео загружено в раздел 'Видео' группы")
            
            return {
                "video_id": video_id,
                "owner_id": owner_id,
                "upload_response": response.text
            }
            
        except Exception as e:
            log.error(f"Ошибка при загрузке видео в группу: {e}")
            raise

    def upload_video_to_wall_and_videos(self, file_path: str, name: str, description: str) -> dict:
        """
        Загружает видео в раздел "Видео" группы (токены групп не могут публиковать на стену)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        
        try:
            # Загружаем только в раздел видео (токены групп не могут публиковать на стену)
            video_result = self.upload_video_to_group_videos(file_path, name, description)
            
            log.info(f"Видео загружено в раздел видео группы: {video_result['video_id']}")
            
            return {
                "video_id": video_result['video_id'],
                "owner_id": video_result['owner_id'],
                "post_id": None,  # Токены групп не могут публиковать на стену
                "upload_response": video_result.get("upload_response")
            }
            
        except Exception as e:
            log.error(f"Ошибка при загрузке видео в раздел видео: {e}")
            raise

    def upload_video_to_stories(self, file_path: str, name: str, description: str) -> dict:
        """
        Загружает видео в раздел "Видео" группы (Stories недоступны для токенов групп)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        
        try:
            # Токены групп не могут загружать в Stories, загружаем в раздел видео
            log.info(f"Stories недоступны для токенов групп, загружаем в раздел видео: {name}")
            return self.upload_video_to_group_videos(file_path, name, description)
            
        except Exception as e:
            log.error(f"Ошибка при загрузке видео: {e}")
            raise

    def post_to_wall(self, message: str, attachments: Optional[list[str]] = None) -> dict:
        attachments_str = ",".join(attachments or [])
        # простые ретраи
        last_err = None
        for _ in range(3):
            try:
                return self.vk.wall.post(owner_id=-self.group_id, message=message, attachments=attachments_str)
            except Exception as e:
                last_err = e
        raise last_err


def _parse_group_id(group: Optional[str]) -> int:
    if not group:
        raise RuntimeError("VK_GROUP_ID не задан")
    g = str(group)
    if g.startswith("club"):
        return int(g.replace("club", ""))
    if g.startswith("public"):
        return int(g.replace("public", ""))
    return int(g)
