import pywinstyles
from PyQt5.QtWidgets import QMainWindow
from common import consts
from PyQt5 import uic


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        pywinstyles.apply_style(self, "dark")  # Применение темного стиля окна Windows
        self.load_ui("main_window.ui")
        self.response = ""
        #self.setupUi(self)

    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """
        uic.loadUi(f"{consts.UI}/{ui_file}", self)