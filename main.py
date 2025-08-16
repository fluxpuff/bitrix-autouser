from core.config import load_config
from core.logger import setup_logger
from cli.interactive import main_flow

if __name__ == "__main__":
    load_config()
    setup_logger()
    main_flow()