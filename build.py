import PyInstaller.__main__
import shutil
import os
import platform

# Определяем разделитель путей в зависимости от ОС
sep = ";" if platform.system() == "Windows" else ":"

# Очистка предыдущих сборок
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

# Конфигурация сборки
args = [
    "main.py",
    "--onefile",
    "--name=Bitrix-autouser",
    f"--add-data=.env.example{sep}.",  # Правильный формат
    "--noconsole",
    "--clean",
    "--exclude-module=tkinter",
    "--exclude-module=unittest",
    
    # Явное указание скрытых импортов
    "--hidden-import=dotenv",
    "--hidden-import=requests",
    "--hidden-import=bs4",
    "--hidden-import=xml.etree.ElementTree",
    "--hidden-import=core",
    "--hidden-import=services",
    "--hidden-import=cli",
]

# Добавляем дополнительные параметры для Linux/Mac
if platform.system() != "Windows":
    args.append("--strip")  # Уменьшаем размер файла
    args.append("--collect-submodules=core")
    args.append("--collect-submodules=services")
    args.append("--collect-submodules=cli")

PyInstaller.__main__.run(args)