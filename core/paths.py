import sys
import os
from pathlib import Path

def get_base_path() -> Path:
    """Возвращает базовый путь в зависимости от режима запуска"""
    if getattr(sys, 'frozen', False):
        # Режим исполняемого файла
        return Path(sys.executable).parent
    else:
        # Режим разработки
        return Path(__file__).parent.parent

BASE_PATH = get_base_path()

def resolve_path(relative_path: str) -> Path:
    """Преобразует относительный путь в абсолютный"""
    return BASE_PATH / relative_path