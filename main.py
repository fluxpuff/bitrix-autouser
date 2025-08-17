from core.config import load_config
from cli.interactive import main_flow

if __name__ == "__main__":
    load_config()
    main_flow()