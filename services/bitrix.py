import requests
import re
from bs4 import BeautifulSoup
from core.config import get_env

def create_bitrix_user(fio: str, email: str, password: str, phone: str, position: str, department: str) -> str:
    """Создает пользователя в Bitrix24"""
    portal_url = os.getenv("BX_PORTAL_URL")
    admin_login = os.getenv("BX_ADMIN_LOGIN")
    admin_pass = os.getenv("BX_ADMIN_PASSWORD")
    
    if not all([portal_url, admin_login, admin_pass]):
        raise EnvironmentError("Не настроены переменные окружения для Bitrix24")
    
    # Разбиваем ФИО на компоненты
    parts = fio.split()
    last_name = parts[0] if len(parts) > 0 else ""
    first_name = parts[1] if len(parts) > 1 else ""
    second_name = parts[2] if len(parts) > 2 else ""

    # Авторизация в админ-панели
    session = requests.Session()
    login_url = f"{portal_url}/bitrix/admin/"
    login_data = {
        "AUTH_FORM": "Y",
        "TYPE": "AUTH",
        "USER_LOGIN": admin_login,
        "USER_PASSWORD": admin_pass,
        "Login": "Войти"
    }
    
    login_response = session.post(login_url, data=login_data)
    
    # Проверка успешной авторизации
    if "authorize" in login_response.url:
        raise PermissionError("Ошибка авторизации администратора в Bitrix")
    
    # Получение CSRF-токена
    admin_page = session.get(f"{portal_url}/bitrix/admin/user_edit.php")
    soup = BeautifulSoup(admin_page.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'sessid'})
    
    if not csrf_input or 'value' not in csrf_input.attrs:
        raise RuntimeError("Не удалось получить CSRF токен")
    
    csrf_token = csrf_input['value']
    
    # Создание пользователя
    user_data = {
        "sessid": csrf_token,
        "lang": "ru",
        "ACTION": "ADD",
        "LOGIN": email,
        "EMAIL": email,
        "NAME": first_name,
        "LAST_NAME": last_name,
        "SECOND_NAME": second_name,
        "PERSONAL_GENDER": "M",
        "NEW_PASSWORD": password,
        "NEW_PASSWORD_CONFIRM": password,
        "GROUP_ID[]": [
        {
            "GROUP_ID": 3,
            "DATE_ACTIVE_FROM": "",
            "DATE_ACTIVE_TO": ""
        },
        {
            "GROUP_ID": 4,
            "DATE_ACTIVE_FROM": "",
            "DATE_ACTIVE_TO": ""
        },
        {
            "GROUP_ID": 12,
            "DATE_ACTIVE_FROM": "",
            "DATE_ACTIVE_TO": ""
        }],
        "ACTIVE": "Y",
        "UF_DEPARTMENT[]": [43],    # ID главного отдела
        "WORK_DEPARTMENT": department,
        "WORK_POSITION": position,
        "WORK_PHONE": phone,
        "apply": "Y",  # Сохранить и остаться на странице
    }
    
    # Отправка запроса
    create_response = session.post(
        f"{portal_url}/bitrix/admin/user_edit.php",
        data=user_data
    )
    
    # Обработка ответа
    soup = BeautifulSoup(create_response.text, 'html.parser')
    title_tag = soup.title
    if title_tag:
        title_text = title_tag.text
        id_match = re.search(r'#\s*(\d+)', title_text)
        if id_match:
            return id_match.group(1)
    
    # Если не удалось извлечь ID
    raise RuntimeError("Ошибка создания пользователя. Проверьте данные администратора")