import os
import sys


# Константы для хранения путей проекта
ROOT=os.path.dirname(os.getcwd())
UI=f"{ROOT}/client_side/resources/ui/"
GUI=f"{ROOT}/client_side/gui/"
TEMP=f"{ROOT}/client_side/temp/"

# Добавление путей для импорта модулей проекта
sys.path.append(f"{ROOT}/client_side/resources/")
sys.path.append(f"{ROOT}/client_side/gui/")