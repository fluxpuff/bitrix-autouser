import requests
import xml.etree.ElementTree as ET
from core.config import get_env
from requests.exceptions import RequestException

def create_email_account(email_local: str, password: str) -> str:
    """Создает почтовый ящик и возвращает полный email"""
    domain = get_env("DOMAINNAME")
    mail_login = get_env("MAIL_ISP_LOGIN")
    mail_password = get_env("MAIL_ISP_PASSWORD")
    mail_url = get_env("MAIL_ISP_MANAGER_URL")
    
    if not all([domain, mail_login, mail_password, mail_url]):
        raise EnvironmentError("Не настроены переменные окружения для почтового сервера")
    
    email_full = f"{email_local}@{domain}"
    
    # Авторизация на почтовом сервере
    auth_params = {
        'out': 'xml',
        'func': 'auth',
        'username': mail_login,
        'password': mail_password
    }
    
    try:
        auth_response = requests.get(mail_url, params=auth_params, verify=False)
        auth_response.raise_for_status()
        root = ET.fromstring(auth_response.content)
        auth_element = root.find('auth')
        
        if auth_element is None:
            raise ValueError("Элемент 'auth' не найден в XML")
            
        auth_id = auth_element.get('id')
        if not auth_id:
            raise ValueError("Атрибут 'id' отсутствует в элементе <auth>")
        
        # Создание почтового ящика
        create_params = {
            'auth': auth_id,
            'out': 'xml',
            'func': 'email.edit',
            'sok': 'ok',
            'name': email_local,
            'domainname': domain,
            'passwd': password
        }
        
        create_response = requests.get(mail_url, params=create_params, verify=False)
        create_response.raise_for_status()
        
        # Проверка результата
        if '<ok/>' in create_response.text:
            return email_full
        elif '<error>' in create_response.text:
            error_msg = create_response.text.split('<error>')[1].split('</error>')[0]
            raise RuntimeError(f"Ошибка создания почты: {error_msg}")
        else:
            raise RuntimeError(f"Неизвестный ответ сервера:\n{create_response.text}")
            
    except RequestException as e:
        raise ConnectionError(f"Ошибка сетевого запроса: {str(e)}")
    except ParseError as e:
        raise ValueError(f"Ошибка парсинга XML: {str(e)}\nОтвет сервера: {auth_response.text[:500]}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при создании почты: {str(e)}")