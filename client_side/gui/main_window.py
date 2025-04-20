import ast
import pywinstyles
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QWidget, QLayout, QMenu, QAction, QMessageBox
from client_side.gui.add_password_window import AddPasswordWindow
from common import consts, interaction
from PyQt5 import uic, QtCore

from common.general import reset_interface


class MainWindow(QMainWindow):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        pywinstyles.apply_style(self, "dark")  # Применение темного стиля окна Windows
        self.load_ui("main_window.ui")
        self.user = user
        self.lsts = ()
        self.response = ""
        self.update_table()
        self.add_tree_item(["Child 1", "Child 2", "Child 3"])


    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """
        uic.loadUi(f"{consts.UI}/{ui_file}", self)