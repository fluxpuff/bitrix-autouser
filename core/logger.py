from datetime import datetime
from .paths import resolve_path

def log_account_creation(data: dict):
    log_path = resolve_path("accounts.log")
    with open(log_path, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} | {data['fio']} | {data['email']} | {data.get('user_id', 'N/A')}\n")

def log_error(exception: Exception):
    import traceback
    error_path = resolve_path("error.log")
    with open(error_path, "a") as error_file:
        error_file.write(f"\n[{datetime.now()}] Ошибка:\n")
        traceback.print_exc(file=error_file)