import os
import sys


# Константы для хранения путей проекта
ROOT=os.path.dirname(os.getcwd())
UI=f"{ROOT}/client_side/resources/ui/"
GUI=f"{ROOT}/client_side/gui/"
TEMP=f"{ROOT}/client_side/temp/"
STYLE=f"{ROOT}/client_side/resources/style.qss"
FONT=f"{ROOT}/client_side/resources/OpenSans.ttf"

# Добавление путей для импорта модулей проекта
sys.path.append(f"{ROOT}/client_side/resources/")
sys.path.append(f"{ROOT}/client_side/gui/")

# Цвета темной темы интерфейса
colors = {
    "bg": "#171717",             # Очень тёмно-серый / почти чёрный (фон)
    "fg": "#EAEAEA",             # Светло-серый / почти белый (основной текст)
    "borders": "#333333",        # Тёмно-серый (границы и разделители)
    "main_text": "#EAEAEA",      # Светло-серый / почти белый (основной текст)
    "secondary_text": "#AAAAAA", # Средне-серый (вторичный текст)
    "error": "#EF5350",          # Красный (ошибки, опасность)
    "success": "#66BB6A",        # Зелёный (успех, подтверждение)
    "warn": "#FFA726",           # Оранжевый (предупреждения)
    "accent": "#00BFA5",         # Бирюзовый / ярко-сине-зелёный (акцент)
    "accent_hover": "#1DE9B6",   # Светлый бирюзовый / неоново-зелёный (hover акцент)
}