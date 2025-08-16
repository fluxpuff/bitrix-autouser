from datetime import datetime

def log_account_creation(data: dict):
    with open("accounts.log", "a", encoding="utf-8") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} | {data['fio']} | {data['email']} | {data.get('user_id', 'N/A')}\n")

def log_error(exception: Exception):
    import traceback
    with open("error.log", "a", encoding="utf-8") as error_file:
        error_file.write(f"\n[{datetime.now()}] Ошибка:\n")
        traceback.print_exc(file=error_file)