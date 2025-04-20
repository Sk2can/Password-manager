from PyQt5.QtWidgets import QMainWindow
from common import consts, interaction
from main_window import MainWindow
from registration_window import RegistrationWindow
from PyQt5 import uic


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
        # Подключение сигналов
        if hasattr(self, "auth_totp_pushButton"):
            self.auth_totp_pushButton.clicked.connect(self.verify_code)
        if hasattr(self, "auth_pushButton"):
            self.auth_pushButton.clicked.connect(self.auth)
        if hasattr(self, "registration_pushButton"):
                self.registration_pushButton.clicked.connect(self.open_registration_window)

    def auth(self):
        """
        Функция авторизации в приложении.
        """
        response = interaction.send_to_server(f"AUTH|{self.login_lineEdit.text()}|{self.password_lineEdit.text()}")
        if response.split("|")[0] == "0":
            self.current_user = f"{self.login_lineEdit.text()}"
            self.load_ui("totp_auth_window.ui")
            self.totp_lineEdit.setFocus()
        elif response.split(":")[0] == "1": # Неверный логин или пароль
            self.error_label.setText("Неправильный логин или пароль!")
        elif response.split("|")[0] == "2": # Нет доступа к серверу
            self.error_label.setText(response.split("|")[1])

    def verify_code(self):
        """
        Функция проверки второго фактора TOTP.
        """
        response = interaction.send_to_server(f"VERIFY|{self.current_user}|{self.totp_lineEdit.text()}")
        if response.split("|")[0] == "0":
            self.open_main_window()
        elif response.split("|")[0] == "1": # Неправильный код
            self.error_label.setText("Неправильный код!")
        elif response.split("|")[0] == "2": # Нет доступа к серверу
            self.error_label.setText("Сервер недоступен!")

    def open_main_window(self):
        """
        Функция инициализации главного окна приложения.
        """
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def open_registration_window(self):
        """
        Функция инициализации диалогового окна регистрации.
        """
        response = interaction.send_to_server(f"AUTH||")  # Проверка доступности сервера
        if response.split("|")[0] == "2":  # Нет доступа к серверу
            self.error_label.setText("Сервер недоступен!")
        else:
            registration_window = RegistrationWindow()
            registration_window.exec_()