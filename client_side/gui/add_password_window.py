import ast
from PyQt5.QtWidgets import QDialog, QCheckBox, QWidget, QLayout
from PyQt5 import uic, QtCore
from common import consts, interaction
import pywinstyles
from common.general import generate_password, password_entropy


class AddPasswordWindow(QDialog):
    def __init__(self,user, parent=None):
        super().__init__(parent)
        self.user = user
        self.load_ui("passwords_add_window.ui")

    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """

        uic.loadUi(f"{consts.UI}/{ui_file}", self)
        # Подключение сигналов
        if hasattr(self, "clear_pushButton"):
            self.clear_pushButton.clicked.connect(self.reset_interface)
        if hasattr(self, "add_pushButton"):
            self.add_pushButton.clicked.connect(self.add_credential)
        if hasattr(self, "generate_pushButton"):
            self.generate_pushButton.clicked.connect(self.generate_password)
        if hasattr(self, "password_lineEdit"):
            self.password_lineEdit.textChanged.connect(self.change_status_bar)
        self.progressBar.setMaximum(128)
        pywinstyles.apply_style(self, "dark")  # Применение темного стиля окна Windows
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # Блокировка отключения последнего чекбокса
        self.checkboxes = self.findChildren(QCheckBox)
        for cb in self.checkboxes:
            cb.toggled.connect(self.check_last_one_enabled)
        categories = ast.literal_eval(interaction.send_to_server(f"GET_CATEGORIES|{self.user}"))
        for category in categories:
            self.category_comboBox.addItem(category)

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

    def reset_interface(self):
        """
        Сброс интерфейса к изначальному состоянию из .ui файла.
        """

        # Удаляем основной макет
        if self.layout():
            old_layout = self.layout()
            QWidget().setLayout(old_layout)  # Переносим макет в пустой виджет для удаления
        # Удаляем дочерние виджеты
        for child in self.children():
            if isinstance(child, QWidget):  # Если это виджет
                child.setParent(None)
            elif isinstance(child, QLayout):  # Если это макет
                self.clear_layout(child)
        self.load_ui("passwords_add_window.ui")

    def clear_layout(self, layout):
        """
        Удаление всех элементов лейаута.
        """
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                else:
                    self.clear_layout(item.layout())

    def add_credential(self):
        """
        Отправка запроса серверу на добавление новой записи в таблицу credentials.
        """
        if self.password_lineEdit.text() and self.category_comboBox.currentText():
            interaction.send_to_server(f"ADD_CREDENTIAL|{self.user}|{self.service_lineEdit.text()}|\
{self.login_lineEdit.text()}|{self.password_lineEdit.text()}|{self.URL_lineEdit.text()}|\
{self.category_comboBox.currentText()}|{self.notes_plainTextEdit.toPlainText()}")
            self.close()
        elif not self.password_lineEdit.text():
            self.error_label.setText("The password field must be filled in!")
        elif not self.category_comboBox.currentText():
            self.error_label.setText("The category field cannot be empty!")

    def generate_password(self):
        """
        Функция генерации случайного пароля исходя из параметров пользователя.
        """
        capitals = self.capital_checkBox.isChecked()
        lowercase = self.lowercase_checkBox.isChecked()
        numbers = self.numbers_checkBox.isChecked()
        symbols = self.special_checkBox.isChecked()
        length = self.length_spinBox.value()
        password = generate_password(length, lowercase, numbers, capitals, symbols)
        self.password_lineEdit.setText(password)

    def change_status_bar(self):
        bits = password_entropy(self.password_lineEdit.text())
        display_value = min(bits, 128)
        self.progressBar.setValue(display_value)

        # Вычисляем цвет от красного к зелёному
        ratio = min(display_value / 128, 1.0)
        red = int(255 * (1 - ratio))
        green = int(255 * ratio)
        color = f'rgb({red}, {green}, 0)'

        self.progressBar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #999;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)