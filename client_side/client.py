import pywinstyles
from common.consts import STYLE
from gui.auth_window import AuthWindow
from PyQt5.QtWinExtras import QtWin
from PyQt5.QtGui import QIcon, QFontDatabase, QFont
from PyQt5 import QtWidgets
import sys
import os

# TODO: План для разработки всего проекта:
#  Добавить стиль к проекту, пример закомментирован выше;
#  Генератор случайных паролей для пользователя;
#  Хранение паролей пользователя;

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AuthWindow()
    # Применение стиля из css файла
    with open(STYLE, "r") as file:
        style = file.read()
        app.setStyleSheet(style)
    # Установка id приложения для корректного отображения в ОС
    try:
        myappid = 'KVA.password_manager.project.dev'
        QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
    # Загружаем шрифт из ресурсов
    font_id = QFontDatabase.addApplicationFont(":/Fonts/OpenSans.ttf")
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    #app.setFont(QFont(font_family)) # Применяем его глобально
    app.setWindowIcon(QIcon(":/png/icons/key.png")) # Установка иконки окна
    pywinstyles.apply_style(window, "dark") # Применение темного стиля окна Windows
    os.makedirs("./temp", exist_ok=True) # Создание каталога для временных файлов
    window.show()
    sys.exit(app.exec_())