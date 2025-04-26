from PyQt5.QtWidgets import QDialog, QCheckBox
from PyQt5 import uic, QtCore
from common import consts, interaction
import pywinstyles
from common.general import generate_password


class EditPasswordWindow(QDialog):
    def __init__(self, row_data, db_index, parent=None):
        super().__init__(parent)
        self.db_index = db_index
        self.load_ui("passwords_edit_window.ui")
        pywinstyles.apply_style(self, "dark")  # Применение темного стиля окна Windows
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # Блокировка отключения последнего чекбокса
        self.checkboxes = self.findChildren(QCheckBox)
        for cb in self.checkboxes:
            cb.toggled.connect(self.check_last_one_enabled)
        # Заполнение полей
        self.service_lineEdit.setText(row_data["Service"])
        self.login_lineEdit.setText(row_data["Login"])
        self.password_lineEdit.setText(row_data["Password"])
        self.url_lineEdit.setText(row_data["URL"])
        #self.category_lineEdit.setText(row_data["Category"])
        self.notes_plainTextEdit.setPlainText(row_data["Notes"])

    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """

        uic.loadUi(f"{consts.UI}/{ui_file}", self)
        # Подключение сигналов
        if hasattr(self, "confirm_pushButton"):
            self.confirm_pushButton.clicked.connect(self.edit_credential)
        if hasattr(self, "generate_pushButton"):
            self.generate_pushButton.clicked.connect(self.generate_password)

    def check_last_one_enabled(self):
        """
        Функция, препятствующая выключению последнего чекбокса.
        """

        checked_boxes = [cb for cb in self.checkboxes if cb.isChecked()]
        sender_cb = self.sender()
        # Если всего один включён и его пытаются выключить — отменяем
        if len(checked_boxes) == 0 and not sender_cb.isChecked():
            sender_cb.blockSignals(True)  # временно блокируем сигнал, чтобы не зациклить
            sender_cb.setChecked(True)
            sender_cb.blockSignals(False)

    def edit_credential(self):
        """
        Отправка запроса на изменение пароля в БД.
        """

        table = "credentials"
        where_clause = ("id",)
        where_params = (self.db_index,)
        updates = {"service": self.service_lineEdit.text(),
                   "login": self.login_lineEdit.text(),
                   "password_encrypted": self.password_lineEdit.text(),
                   "url": self.url_lineEdit.text(),
                   "notes": self.notes_plainTextEdit.toPlainText()}

        response = interaction.send_to_server(f"EDIT_CREDENTIAL|{table}|{where_clause}|{where_params}|{updates}")

    def generate_password(self):
        """
        Функция генерации случайного пароля.
        """

        capitals = self.capital_checkBox.isChecked()
        lowercase = self.lowercase_checkBox.isChecked()
        numbers = self.numbers_checkBox.isChecked()
        symbols = self.symbols_checkBox.isChecked()
        length = self.length_spinBox.value()
        password = generate_password(length, lowercase, numbers, capitals, symbols)
        self.password_lineEdit.setText(password)