import pywinstyles
from PyQt5.QtCore import QSettings
from totp_setup_window import TOTPSetupWindow
from common import consts, interaction
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic, QtCore
import re


class RegistrationWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui("registration_window.ui")

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
        if hasattr(self, "register_pushButton"):
            self.register_pushButton.clicked.connect(self.create_user)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    def create_user(self):
        """
        Функция регистрации нового пользователя.
        """

        if not ((self.password_lineEdit.text()) and (self.password_conf_lineEdit.text()) and (self.login_lineEdit.text())):
            self.error_label.setText(self.tr("Fill in all the required fields!")); return
        elif self.password_lineEdit.text() != self.password_conf_lineEdit.text():
            self.error_label.setText(self.tr("Passwords don't match!")); return
        elif len(self.password_lineEdit.text()) < 16:
            self.error_label.setText(self.tr("The password must be at least 16 characters long!")); return
        response = interaction.send_to_server(f"REG|{self.login_lineEdit.text()}|{self.password_lineEdit.text()}")
        if re.search("^0\|.*", response):
            self.close()
            self.totp_setup_window = TOTPSetupWindow(self.login_lineEdit.text())
            self.totp_setup_window.exec_()
        else:
            self.error_label.setText(self.tr("The login already exists!"))