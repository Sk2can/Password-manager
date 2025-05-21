import ast
import pywinstyles
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog
from common import consts, interaction


class EditCategoryWindow(QDialog):
    def __init__(self,user, parent=None):
        super().__init__(parent)
        self.user = user
        self.categories = []
        self.load_ui("category_edit.ui")

    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """

        uic.loadUi(f"{consts.UI}/{ui_file}", self)
        settings = QSettings("KVA", "Vaultary")
        if settings.value("theme", "dark") == "dark": pywinstyles.apply_style(self, "dark")
        # Подключение сигналов
        if hasattr(self, "edit_pushButton"):
            self.edit_pushButton.clicked.connect(self.edit_entry_local)
        self.categories = ast.literal_eval(interaction.send_to_server(f"GET_CATEGORIES|{self.user}"))
        for category in self.categories:
            self.current_categories_comboBox.addItem(category)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    def edit_entry_local(self):
        old_name = self.categories[self.current_categories_comboBox.currentIndex()]
        new_name = self.current_categories_comboBox.currentTet()
        if new_name not in self.categories:
            if new_name:
                self.edit_category(table="categories", updates={"name": new_name}, where_clause=("user_fk", "name"),
                                   where_params=(self.user, old_name,))
                self.close()
            else:
                self.error_label.setText(self.tr("The field must be filled!"))
        else:
            self.error_label.setText(self.tr("This category already exists!"))

    def edit_category(self, **kwargs):
        data = "|".join(f"{key}={value}" for key, value in kwargs.items())
        message = f"EDIT_ENTRY|{data}"
        print(message)
        interaction.send_to_server(message)