"""全局配置：从 server/config/*.json 统一读取

- main_leaner.json : 应用 + JWT
- database.json    : MySQL + Redis
"""
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

def load_json(filename: str) -> dict:
    with open(CONFIG_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


APP_CONFIG = load_json("main_leaner.json")
DB_CONFIG = load_json("database.json")
# API 前缀
# 应用
APP_NAME = APP_CONFIG["main"]["app_name"]
ENV = APP_CONFIG["main"]["env"]
HOST = APP_CONFIG["main"]["host"]
PORT = APP_CONFIG["main"]["port"]
API_PREFIX = "/api/v1"
CORS_ORIGINS = APP_CONFIG["main"].get("cors_origins", ["*"])

# JWT
JWT_SECRET_KEY = APP_CONFIG["jwt"]["secret_key"]
JWT_ALGORITHM = APP_CONFIG["jwt"]["algorithm"]
JWT_EXPIRE_DAYS = APP_CONFIG["jwt"]["expire_days"]

# MySQL / Redis
MYSQL = DB_CONFIG["mysql"]
REDIS = DB_CONFIG.get("redis", {})
