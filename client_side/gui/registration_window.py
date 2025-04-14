import pywinstyles
from totp_setup_window import TOTPSetupWindow
from common import consts, interaction
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic, QtCore
import re


Form, Base = uic.loadUiType(f"{consts.UI}/registration_window.ui")

class RegistrationWindow(QDialog, Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.response = ""
        self.setupUi(self)
        pywinstyles.apply_style(self, "dark")  # Применение темного стиля окна Windows
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # Сигналы
        self.register_pushButton.clicked.connect(self.create_user)

    def create_user(self):
        """
        Функция регистрации нового пользователя.
        """
        if not ((self.password_lineEdit.text()) and (self.password_conf_lineEdit.text()) and (self.login_lineEdit.text())):
            self.error_label.setText("Заполните все поля!"); return
        elif self.password_lineEdit.text() != self.password_conf_lineEdit.text():
            self.error_label.setText("Пароли не совпадают!"); return
        elif len(self.password_lineEdit.text()) < 16:
            self.error_label.setText("Пароль должен быть не менее 16 символов!"); return
        self.response = interaction.send_to_server(f"REG:{self.login_lineEdit.text()}:{self.password_lineEdit.text()}")
        if re.search("0:.*", self.response):
            self.close()
            self.totp_setup_window = TOTPSetupWindow(self.login_lineEdit.text(), self.password_lineEdit.text())
            self.totp_setup_window.exec_()
        else:
            self.error_label.setText("Логин уже существует!")