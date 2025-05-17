import ast
import pywinstyles
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog
from common import consts, interaction
from common.general import convert_string


class DeleteCategoryWindow(QDialog):
    def __init__(self,user, parent=None):
        super().__init__(parent)
        self.user = user
        self.categories = []
        self.is_confirmed = False
        self.load_ui("category_delete.ui")

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
        if hasattr(self, "delete_pushButton"):
            self.delete_pushButton.clicked.connect(self.delete_entry_local)
        if hasattr(self, "current_categories_comboBox"):
            self.current_categories_comboBox.currentIndexChanged.connect(lambda i: setattr(self, "is_confirmed", False))
        self.categories = ast.literal_eval(interaction.send_to_server(f"GET_CATEGORIES|{self.user}"))
        for category in self.categories:
            self.current_categories_comboBox.addItem(category)
        if len(self.categories) == 1:
            self.error_label.setText(self.tr("You can't delete the last category!"))
            self.delete_pushButton.setEnabled(False)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    def delete_entry_local(self):
        del_category = self.current_categories_comboBox.currentText()
        if del_category:
            if not self.is_confirmed:
                self.error_label.setText(self.tr("Are you sure? All passwords belonging to it will also be deleted!"))
                self.is_confirmed = True
            else:
                table = "categories"
                searching_column = "id"
                params = {"user_fk": self.user, "name": del_category}
                message = f"SEARCH_ENTRY|table={table}|searching_column={searching_column}|params={params}"
                field_id = convert_string(interaction.send_to_server(message))[0]
                message = f"DELETE_ENTRY|{table}|{searching_column}|{field_id}"
                interaction.send_to_server(message)
                self.close()
        else:
            self.error_label.setText(self.tr("Select a category to delete!"))