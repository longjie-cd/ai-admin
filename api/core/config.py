import yaml
from pathlib import Path
from pydantic_settings import BaseSettings


def _load_yaml_config() -> dict:
    """加载项目根目录下的 config.yaml"""
    config_path = Path(__file__).resolve().parent.parent.parent / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_yaml_config = _load_yaml_config()


class Settings(BaseSettings):
    app_name: str = _yaml_config.get("app", {}).get("name", "AI Admin")
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    class Config:
        env_file = ".env"


class OssSettings:
    """阿里云 OSS 对象存储配置"""

    def __init__(self):
        oss_cfg = _yaml_config.get("oss", {})
        self.access_key_id: str = oss_cfg.get("access_key_id", "")
        self.access_key_secret: str = oss_cfg.get("access_key_secret", "")
        self.endpoint: str = oss_cfg.get("endpoint", "")
        self.bucket_name: str = oss_cfg.get("bucket_name", "")
        self.prefix: str = oss_cfg.get("prefix", "")
        self.custom_domain: str = oss_cfg.get("custom_domain", "")

    @property
    def is_configured(self) -> bool:
        """检查 OSS 是否已正确配置"""
        return bool(self.access_key_id and self.access_key_secret and self.endpoint and self.bucket_name)


settings = Settings()
oss_settings = OssSettings()
