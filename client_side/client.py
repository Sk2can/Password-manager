import pywinstyles
from PyQt5.QtCore import QTranslator, QSettings
from common.consts import STYLE, colors, FONT, RU_LANG, colors_light
from gui.auth_window import AuthWindow
from PyQt5.QtWinExtras import QtWin
from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5 import QtWidgets
import sys
import os


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    settings = QSettings("KVA", "Vaultary")
    window = AuthWindow()

    # Прочитать настройки
    language = settings.value("language", "en")  # по умолчанию "en"
    theme = settings.value("theme", "dark") # по умолчанию "dark"

    if language == "ru":
        translator = QTranslator()
        translator.load(RU_LANG)
        app.installTranslator(translator)

    # Загружаем сторонние шрифты
    font_id = QFontDatabase.addApplicationFont(FONT)
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

    # Загрузим .qss файл с плейсхолдерами
    if theme == "dark":
        app.setWindowIcon(QIcon(":/png/icons/key.png"))  # Установка иконки окна
        with open(STYLE, "r") as file:
            qss_template = file.read()
        # Заменим переменные на конкретные значения из словаря
        qss = qss_template.format(**colors)
        app.setStyleSheet(qss)
        pywinstyles.apply_style(window, "dark")
    elif theme == "light":
        app.setWindowIcon(QIcon(":/png/icons/key_dark.png"))  # Установка иконки окна
        with open(STYLE, "r") as file:
            qss_template = file.read()
        # Заменим переменные на конкретные значения из словаря
        qss = qss_template.format(**colors_light)
        app.setStyleSheet(qss)

    # Установка id приложения для корректного отображения в ОС
    try:
        myappid = 'KVA.password_manager.project.dev'
        QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    os.makedirs("./temp", exist_ok=True) # Создание каталога для временных файлов
    window.show()
    sys.exit(app.exec_())