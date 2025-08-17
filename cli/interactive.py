from core.utils import translit_name, generate_password
from core.config import get_env
from services import helpdesk, mail, bitrix
from core.logger import log_account_creation, log_error
import os
from datetime import datetime
import sys
import string

def get_confirmed_data(fio: str, phone: str, position: str, department: str, email_local: str) -> tuple:
    """Интерактивное подтверждение и редактирование данных"""
    domain = os.getenv("DOMAINNAME")
    email_full = f"{email_local}@{domain}"
    
    while True:
        print("\n" + "="*50)
        print("Проверьте данные перед созданием учетных записей:")
        print(f"1. ФИО: {fio}")
        print(f"2. Телефон: {phone}")
        print(f"3. Должность: {position}")
        print(f"4. Отдел: {department}")
        print(f"5. Email: {email_full}")
        print("="*50)
        
        confirm = input("\nВсе верно? [Y/N] ").strip().upper()
        
        if confirm == 'Y':
            return fio, phone, position, department, email_local
            
        elif confirm == 'N':
            print("\nВведите новые значения (оставьте пустым, чтобы оставить текущее):")
            
            # Редактирование ФИО
            parts = fio.split()
            surname = parts[0] if len(parts) > 0 else ""
            name = parts[1] if len(parts) > 1 else ""
            patronymic = parts[2] if len(parts) > 2 else ""
            
            new_surname = input(f"Фамилия [{surname}]: ").strip()
            new_name = input(f"Имя [{name}]: ").strip()
            new_patronymic = input(f"Отчество [{patronymic}]: ").strip()
            
            # Собираем новое ФИО
            fio_parts = [
                new_surname if new_surname else surname,
                new_name if new_name else name,
                new_patronymic if new_patronymic else patronymic
            ]
            fio = ' '.join([p for p in fio_parts if p]).strip()
            
            # Редактирование других полей
            phone = input(f"Номер телефона [{phone}]: ").strip() or phone
            position = input(f"Должность [{position}]: ").strip() or position
            department = input(f"Отдел [{department}]: ").strip() or department
            
            # Редактирование email
            new_email_local = input(f"Логин для email (без домена) [{email_local}]: ").strip()
            if new_email_local:
                email_local = new_email_local
                email_full = f"{email_local}@{domain}"
                
            # Перегенерация логина при изменении ФИО
            elif new_surname or new_name:
                regen = input("Сгенерировать новый логин на основе ФИО? [Y/N] ").strip().upper()
                if regen == 'Y':
                    email_local = translit_name(fio)
                    email_full = f"{email_local}@{domain}"
                    print(f"Новый логин: {email_full}")
        else:
            print("Пожалуйста, введите Y или N.")

def manual_input() -> dict:
    """Режим ручного ввода данных"""
    print("\n" + "="*50)
    print("Режим ручного ввода данных")
    print("="*50)
    
    # Запрос основных данных
    fio = input("Введите ФИО: ").strip()
    phone = input("Введите номер телефона: ").strip()
    position = input("Введите должность: ").strip()
    department = input("Введите отдел: ").strip()
    
    # Генерация логина
    email_local = translit_name(fio)
    
    # Подтверждение и редактирование данных
    fio, phone, position, department, email_local = get_confirmed_data(
        fio, phone, position, department, email_local
    )
    
    # Выбор способа задания пароля
    password_choice = input("\nСгенерировать пароль автоматически? [Y/N] ").strip().upper()
    if password_choice == 'Y':
        password = generate_password()
        print(f"Сгенерированный пароль: {password}")
    else:
        password = input("Введите пароль: ").strip()
        # Проверка сложности пароля
        if len(password) < 8:
            print("Внимание: пароль слишком короткий! Рекомендуется не менее 8 символов.")
        if not any(char.isdigit() for char in password):
            print("Внимание: рекомендуется добавить цифры в пароль!")
        if not any(char in string.punctuation for char in password):
            print("Внимание: рекомендуется добавить специальные символы в пароль!")
    
    return {
        'fio': fio,
        'phone': phone,
        'position': position,
        'department': department,
        'email': f"{email_local}@{os.getenv('DOMAINNAME')}",
        'password': password
    }

def main_flow():
    print("\n" + "="*50)
    print(" Система создания учетных записей ")
    print("="*50)
    print("Выберите режим работы:")
    print("1. Создать учетные записи по заявке из Helpdesk")
    print("2. Ручной ввод данных")
    print("3. Выход")
    
    mode = input("\nВаш выбор [1-3]: ").strip()
    
    if mode == '3':
        print("\nЗавершение работы.")
        return
    
    try:
        if mode == '1':
            # Режим работы по заявке
            request_id = input("\nВведите ID заявки из Helpdesk: ").strip()
            print(f"\nПолучение данных заявки #{request_id}...")
            
            # Получаем данные из Helpdesk
            helpdesk_data = helpdesk.fetch_helpdesk_data(request_id)
            print("Данные успешно получены из Helpdesk!")
            
            # Генерация начальных значений
            email_local = translit_name(helpdesk_data['fio'])
            password = generate_password()
            
            # Интерактивное подтверждение данных
            fio, phone, position, department, email_local = get_confirmed_data(
                helpdesk_data['fio'],
                helpdesk_data['phone'],
                helpdesk_data['position'],
                helpdesk_data['department'],
                email_local
            )
            
            email_full = f"{email_local}@{os.getenv('DOMAINNAME')}"
            
            data = {
                'fio': fio,
                'phone': phone,
                'position': position,
                'department': department,
                'email': email_full,
                'password': password
            }
            
        elif mode == '2':
            # Режим ручного ввода
            data = manual_input()
            
        else:
            print("\nНеверный выбор. Пожалуйста, запустите скрипт снова.")
            return
        
        # Создание почтового ящика
        print("\nСоздание почтового ящика...")
        email_local_part = data['email'].split('@')[0]
        email_full = mail.create_email_account(email_local_part, data['password'])
        data['email'] = email_full
        print(f"Почтовый ящик успешно создан: {email_full}")
        
        # Создание пользователя в Bitrix
        print("\nСоздание пользователя в Bitrix24...")
        user_id = bitrix.create_bitrix_user(
            fio=data['fio'],
            email=data['email'],
            password=data['password'],
            phone=data['phone'],
            position=data['position'],
            department=data['department']
        )
        
        print("\n" + "="*50)
        print("Учетные записи успешно созданы!")
        print(f"Bitrix ID: {user_id}")
        print(f"Email: {data['email']}")
        print(f"Пароль: {data['password']}")
        print("="*50)
        
        # Запись в лог
        with open("accounts.log", "a", encoding="utf-8") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp} | {data['fio']} | {data['email']} | {user_id}\n")
        print("\nИнформация сохранена в accounts.log")
        
    except Exception as e:
        print("\n" + "!"*50)
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        print("!"*50)
        
        # Вывод traceback для отладки
        import traceback
        with open("error.log", "a", encoding="utf-8") as error_file:
            error_file.write(f"\n[{datetime.now()}] Ошибка:\n")
            traceback.print_exc(file=error_file)
        
        sys.exit(1)