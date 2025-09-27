from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostingPolicy(BaseModel):
    day_start_hour: int = Field(default=10)
    day_end_hour: int = Field(default=22)
    posts_per_day_min: int = Field(default=8)
    posts_per_day_max: int = Field(default=12)
    interval_min_minutes: int = Field(default=60)
    interval_max_minutes: int = Field(default=120)
    max_daily_posts: int = Field(default=20)  # Максимум 20 постов в день
    batch_size: int = Field(default=20)  # Размер пакета для обработки
    auto_cleanup: bool = Field(default=True)  # Автоматическое удаление опубликованных видео


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="POSTING_POLICY__", extra="ignore")

    tz: str = Field(default="Europe/Moscow", alias="TZ")

    tg_api_id: int | None = Field(default=None, alias="TG_API_ID")
    tg_api_hash: str | None = Field(default=None, alias="TG_API_HASH")
    tg_session_string: str | None = Field(default=None, alias="TG_SESSION_STRING")
    tg_invite_link: str | None = Field(default=None, alias="TG_INVITE_LINK")

    vk_group_token: str | None = Field(default=None, alias="VK_GROUP_TOKEN")
    vk_group_id: str | None = Field(default=None, alias="VK_GROUP_ID")

    @property
    def policy(self) -> PostingPolicy:
        return PostingPolicy()


