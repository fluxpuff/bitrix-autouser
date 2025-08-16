import string
import random

translit_map = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
    'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    ' ': ''
}

def translit_name(name: str) -> str:
    """Транслитерирует ФИО в формат первая буква имени + фамилия"""
    parts = name.split()
    if len(parts) < 2:
        raise ValueError("ФИО должно содержать минимум два слова")

    surname = parts[0].lower()
    first_name = parts[1].lower()

    # Транслитим фамилию
    translit_surname = []
    for char in surname:
        if char in translit_map:
            translit_surname.append(translit_map[char])
        elif char in string.ascii_letters or char in string.digits:
            translit_surname.append(char)
    
    first_letter = translit_map.get(first_name[0], first_name[0])
    
    return first_letter + ''.join(translit_surname)

def generate_password(length: int = 12) -> str:
    """Генерирует случайный сложный пароль"""
    chars = string.ascii_letters + string.digits + string.punctuation
    safe_chars = [c for c in chars if c not in {'&', '?', '=', '+', '#', '%'}]
    return ''.join(random.choice(safe_chars) for _ in range(length))
