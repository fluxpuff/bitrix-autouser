import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    
def get_env(key: str, default=None) -> str:
    return os.getenv(key, default)