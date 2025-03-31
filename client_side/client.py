#from qt_material import apply_stylesheet
from gui.auth_window import AuthWindow
from PyQt5.QtWinExtras import QtWin
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
import sys
import os


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #apply_stylesheet(app, theme='dark_lightgreen.xml') # Установка темы для приложения
    window = AuthWindow()
    try:
        myappid = 'KVA.password_manager.project.dev'
        QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
    app.setWindowIcon(QIcon(":/png/icons/logo.png"))
    os.makedirs("./temp", exist_ok=True) # создание каталога для временных файлов
    window.show()
    sys.exit(app.exec_())