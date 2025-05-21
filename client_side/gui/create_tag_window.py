import ast
import pywinstyles
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog
from common import consts, interaction


class CreateTagWindow(QDialog):
    def __init__(self,user, parent=None):
        super().__init__(parent)
        self.user = user
        self.load_ui("tag_create_window.ui")

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
        if hasattr(self, "create_pushButton"):
            self.create_pushButton.clicked.connect(self.add_entry_local)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    def add_entry_local(self):
        params = {"user_fk": self.user}
        result = interaction.send_to_server(f"SEARCH_ENTRY|table=tags|searching_column=name|params={params}")
        tags_list = ast.literal_eval(result)
        if self.tag_name_lineEdit.text() not in tags_list:
            if self.tag_name_lineEdit.text():
                self.add_tag(table="tags", name=self.tag_name_lineEdit.text(), user_fk=self.user)
                self.close()
            else:
                self.error_label.setText(self.tr("The field must be filled!"))
        else:
            self.error_label.setText(self.tr("This tag already exists!"))

    def add_tag(self, **kwargs):
        data = "|".join(f"{key}={value}" for key, value in kwargs.items())
        message = f"ADD_ENTRY|{data}"
        interaction.send_to_server(message)