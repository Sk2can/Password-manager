import ast
import pywinstyles
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QDialog
from common import consts, interaction


class CreateCategoryWindow(QDialog):
    def __init__(self,user, parent=None):
        super().__init__(parent)
        self.user = user
        self.load_ui("category_create.ui")

    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """

        uic.loadUi(f"{consts.UI}/{ui_file}", self)
        # Подключение сигналов
        if hasattr(self, "create_pushButton"):
            self.create_pushButton.clicked.connect(self.add_entry_local)
        pywinstyles.apply_style(self, "dark")  # Применение темного стиля окна Windows
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    def add_entry_local(self):
        categories = interaction.send_to_server(f"GET_CATEGORIES|{self.user}")
        categories_list = ast.literal_eval(categories)
        if self.category_lineEdit.text() not in categories_list:
            if self.category_lineEdit.text():
                self.add_category(table="categories", name=self.category_lineEdit.text(), user_fk=self.user)
                self.close()
            else:
                self.error_label.setText("The field must be filled!")
        else:
            self.error_label.setText("This category already exists!")

    def add_category(self, **kwargs):
        data = "|".join(f"{key}={value}" for key, value in kwargs.items())
        message = f"ADD_ENTRY|{data}"
        interaction.send_to_server(message)