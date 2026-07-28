"""Общие константы и пользовательские настройки."""
import json
import os
from pathlib import Path

DEFAULT_IMAGE = "linux-trainer:1"
CONTAINER = "linux-trainer"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATE_DIR = Path.home() / ".config" / "linux-trainer"
PROGRESS_FILE = STATE_DIR / "progress.json"
CONFIG_FILE = STATE_DIR / "config.json"

# Пути внутри контейнера
HISTORY_FILE = "/var/log/ltrain/history.log"
CWD_FILE = "/var/log/ltrain/cwd"
LAB_DIR = "/root/lab"

TMUX_SESSION = "ltrain"


def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {}


def save_config(data: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def image() -> str:
    """Какой образ использовать.

    По умолчанию собирается локально. Если указан образ с реестром
    (например ghcr.io/user/linux-trainer:latest) — он будет скачан.
    """
    return os.environ.get("LTRAIN_IMAGE") or load_config().get("image", DEFAULT_IMAGE)


def docker_host() -> str:
    """Куда обращаться docker-клиенту.

    Пусто  -> локальный Docker на этой машине.
    ssh://user@host -> демон Docker на удалённом сервере (VPS).
    Переменная окружения LTRAIN_DOCKER_HOST имеет приоритет над файлом конфигурации.
    """
    return os.environ.get("LTRAIN_DOCKER_HOST") or load_config().get("docker_host", "")
