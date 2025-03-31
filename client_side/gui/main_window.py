from PyQt5.QtWidgets import QMainWindow
from common import consts
from PyQt5 import uic


Form, Base = uic.loadUiType(f"{consts.UI}/main_window.ui")

class MainWindow(QMainWindow, Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.response = ""
        self.setupUi(self)