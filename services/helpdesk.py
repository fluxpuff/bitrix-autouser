import requests
from core.config import get_env
from requests.auth import HTTPBasicAuth

def fetch_helpdesk_data(request_id: str) -> dict:
    """Получает данные заявки из Helpdesk API"""
    vsDesk_login = get_env("VSDESK_LOGIN")
    vsDesk_passwd = get_env("VSDESK_PASSWORD")
    vsDesk_api_url = get_env("VSDESK_API_URL")
    
    if not all([vsDesk_login, vsDesk_passwd, vsDesk_api_url]):
        raise EnvironmentError("Не настроены переменные окружения для Helpdesk")
    
    api_url = f"{vsDesk_api_url}/requests/{request_id}"
    auth = HTTPBasicAuth(vsDesk_login, vsDesk_passwd)
    response = requests.get(api_url, auth=auth)
    
    # Проверка статуса ответа
    if response.status_code == 401:
        raise PermissionError("Ошибка 401: Неверные учетные данные для vsDesk")
    
    response.raise_for_status()
    
    # Исправляем проблему с BOM (Byte Order Mark)
    if response.text.startswith('\ufeff'):
        response.encoding = 'utf-8-sig'
    
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        content = response.text.lstrip('\ufeff')
        data = requests.models.complexjson.loads(content)
    
    # Извлекаем необходимые поля
    fio, position, phone, department = None, None, None, None
    
    for field in data.get('flds', []):
        if field['name'] == 'Фамилия':
            fio = field['value']
        elif field['name'] == 'Имя':
            fio += f' {field['value']}'
        elif field['name'] == 'Отчество':
            fio += f' {field['value']}'
        elif field['name'] == 'Должность':
            position = field['value']
        elif field['name'] == 'Номер телефона':
            phone = field['value']
        elif field['name'] == 'Подразделение | город':
            department = field['value']

    if not all([fio, position, phone, department]):
        missing = []
        if fio is None: missing.append('ФИО сотрудника')
        if position is None: missing.append('Должность')
        if phone is None: missing.append('Номер телефона')
        if department is None: missing.append('Подразделение')
        raise ValueError(f"Отсутствуют обязательные поля: {', '.join(missing)}")
    
    return {
        'fio': fio,
        'position': position,
        'phone': phone,
        'department': department
    }