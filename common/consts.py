import os
import sys


# Константы для хранения путей проекта
ROOT=os.path.dirname(os.getcwd())
UI=f"{ROOT}/client_side/resources/ui/"
GUI=f"{ROOT}/client_side/gui/"
TEMP=f"{ROOT}/client_side/temp/"
STYLE=f"{ROOT}/client_side/resources/style.qss"
FONT=f"{ROOT}/client_side/resources/OpenSans.ttf"
RU_LANG=f"{ROOT}/client_side/resources/translate/ru_RU.qm"

# Добавление путей для импорта модулей проекта
sys.path.append(f"{ROOT}/client_side/resources/")
sys.path.append(f"{ROOT}/client_side/gui/")

# Цвета темной темы интерфейса
colors = {
    "bg": "#202020",             # Очень тёмно-серый / почти чёрный (фон)
    "fg": "#2b2b2b",             # Светло-серый / почти белый (основной текст)
    "fg_light": "#454545",
    "borders": "#2b2b2b",        # Тёмно-серый (границы и разделители)
    "main_text": "#ffffff",      # Светло-серый / почти белый (основной текст)
    "secondary_text": "#c4c78e", # Средне-серый (вторичный текст)
    "error": "#EF5350",          # Красный (ошибки, опасность)
    "success": "#66BB6A",        # Зелёный (успех, подтверждение)
    "warn": "#FFA726",           # Оранжевый (предупреждения)
    "accent": "#c4c78e",         # Бирюзовый / ярко-сине-зелёный (акцент)
    "accent_hover": "#a7aa72",   # Светлый бирюзовый / неоново-зелёный (hover акцент)
}

# Цвета светлой темы интерфейса
colors_light = {
    "bg": "#F5F5F5",             # Светло-серый / почти белый (фон)
    "fg": "#9f9f9f",             # Почти чёрный (основной текст)
    "fg_light": "#bfbfbf",
    "borders": "#9f9f9f",        # Светло-серый (границы и разделители)
    "main_text": "#000000",      # Почти чёрный (основной текст)
    "secondary_text": "#387210", # Средне-серый (вторичный текст)
    "error": "#EF5350",          # Тёмно-красный (ошибки, опасность)
    "success": "#66BB6A",        # Тёмно-зелёный (успех, подтверждение)
    "warn": "#FFA726",           # Тёмно-оранжевый (предупреждения)
    "accent": "#387210",         # Ярко-сине-зелёный (акцент)
    "accent_hover": "#1f4408",   # Светло-бирюзовый (hover акцент)
}