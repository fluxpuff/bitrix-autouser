import os
from dotenv import load_dotenv

def load_config():
    from .paths import resolve_path
    load_dotenv(dotenv_path=resolve_path('.env'))
    
def get_env(key: str, default=None) -> str:
    return os.getenv(key, default)