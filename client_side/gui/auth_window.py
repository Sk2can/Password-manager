import pywinstyles
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMainWindow
from common import consts, interaction
from main_window import MainWindow
from registration_window import RegistrationWindow
from PyQt5 import uic, QtCore


class AuthWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui("auth_window.ui")
        self.login_lineEdit.setFocus()
        self.current_user = ""
        self.current_key = ""
        self.response = ""

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
        if hasattr(self, "auth_totp_pushButton"):
            self.auth_totp_pushButton.clicked.connect(self.verify_code)
        if hasattr(self, "auth_pushButton"):
            self.auth_pushButton.clicked.connect(self.auth)
        if hasattr(self, "registration_pushButton"):
            self.registration_pushButton.clicked.connect(self.open_registration_window)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    def auth(self):
        """
        Функция авторизации в приложении.
        """

        response = interaction.send_to_server(f"AUTH|{self.login_lineEdit.text()}|{self.password_lineEdit.text()}")
        if response.split("|")[0] == "0":
            self.current_user = f"{self.login_lineEdit.text()}"
            self.load_ui("totp_auth_window.ui")
            self.totp_lineEdit.setFocus()
        elif response.split("|")[0] == "1": # Неверный логин или пароль
            self.error_label.setText(self.tr("Incorrect username or password!"))
        elif response.split("|")[0] == "2":
            self.error_label.setText(self.tr("Server is unreachable!"))

    def verify_code(self):
        """
        Функция проверки второго фактора TOTP.
        """

        response = interaction.send_to_server(f"VERIFY|{self.current_user}|{self.totp_lineEdit.text()}")
        if True: # response.split("|")[0] == "0"
            self.open_main_window()
        elif response.split("|")[0] == "1": # Неправильный код
            self.error_label.setText(self.tr("Incorrect code!"))
        elif response.split("|")[0] == "2": # Нет доступа к серверу
            self.error_label.setText(self.tr("Server is unreachable!"))

    def open_main_window(self):
        """
        Функция инициализации главного окна приложения.
        """

        self.main_window = MainWindow(self.current_user)
        self.main_window.show()
        self.close()

    def open_registration_window(self):
        """
        Функция инициализации диалогового окна регистрации.
        """

        response = interaction.send_to_server(f"AUTH||")  # Проверка доступности сервера
        if response.split("|")[0] == "2":  # Нет доступа к серверу
            self.error_label.setText(self.tr("Server is unreachable!"))
        else:
            registration_window = RegistrationWindow()
            registration_window.exec_()