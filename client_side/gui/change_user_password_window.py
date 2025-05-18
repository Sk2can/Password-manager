import bcrypt
import pywinstyles
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog
from common import consts, interaction


class ChangeUserPasswordWindow(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.current_user = user
        self.base_style = None
        self.settings = QSettings("KVA", "Vaultary")
        self.color = self.settings.value("theme", "dark")
        self.language = self.settings.value("language", "en")
        self.load_ui("user_password_change_window.ui")

    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """

        uic.loadUi(f"{consts.UI}/{ui_file}", self)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        if self.settings.value("theme", "dark") == "dark": pywinstyles.apply_style(self, "dark")

        # Подключение сигналов
        if hasattr(self, "confirm_pushButton"):
            self.confirm_pushButton.clicked.connect(lambda i:self.change_password())

    def change_password(self):
        status = self.auth()
        if status == "ok":
            if self.new_password_lineEdit.text() == self.repeated_password_lineEdit.text():
                if len(self.new_password_lineEdit.text()) >= 16:
                    self.edit_entry_local()
                else:
                    self.error_label.setText("The password must be longer than 16 characters!")
            else:
                self.error_label.setText("The new passwords don't match!")
        else:
            self.error_label.setText(status)

    def auth(self):
        """
        Функция авторизации в приложении.
        """

        response = interaction.send_to_server(f"AUTH|{self.current_user}|{self.old_password_lineEdit.text()}")
        if response.split("|")[0] == "1": # Неверный логин или пароль
            return "Incorrect password!"
        elif response.split("|")[0] == "2":
            return "Server is unreachable!"
        else:
            return "ok"

    def edit_entry_local(self):
        new_pass = self.new_password_lineEdit.text()
        new_pass_hash = bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.edit_category(table="users", updates={"password_hash": new_pass_hash}, where_clause=("username",),
                           where_params=(self.current_user,))
        self.close()

    def edit_category(self, **kwargs):
        data = "|".join(f"{key}={value}" for key, value in kwargs.items())
        message = f"EDIT_ENTRY|{data}"
        print(message)
        interaction.send_to_server(message)