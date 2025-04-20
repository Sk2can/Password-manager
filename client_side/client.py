import pywinstyles
from common.consts import STYLE, colors, FONT
from gui.auth_window import AuthWindow
from PyQt5.QtWinExtras import QtWin
from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5 import QtWidgets
import sys
import os


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AuthWindow()

    # Загружаем сторонние шрифты
    font_id = QFontDatabase.addApplicationFont(FONT)
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    # Загрузим .qss файл с плейсхолдерами
    with open(STYLE, "r") as file:
        qss_template = file.read()
    # Заменим переменные на конкретные значения из словаря
    qss = qss_template.format(**colors)
    app.setStyleSheet(qss)

    # Установка id приложения для корректного отображения в ОС
    try:
        myappid = 'KVA.password_manager.project.dev'
        QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    app.setWindowIcon(QIcon(":/png/icons/key.png")) # Установка иконки окна
    pywinstyles.apply_style(window, "dark") # Применение темного стиля окна Windows
    os.makedirs("./temp", exist_ok=True) # Создание каталога для временных файлов
    window.show()
    sys.exit(app.exec_())