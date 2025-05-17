import ast
import pywinstyles
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QCheckBox, QWidget, QLayout
from PyQt5 import uic, QtCore
from common import consts, interaction
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
        settings = QSettings("KVA", "Vaultary")
        if settings.value("theme", "dark") == "dark": pywinstyles.apply_style(self, "dark")
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
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.bits_label.setText("0 bits")
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
            self.error_label.setText(self.tr("The password field must be filled in!"))
        elif not self.category_comboBox.currentText():
            self.error_label.setText(self.tr("The category field cannot be empty!"))

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
        # Ограничим значение максимумом
        entropy = password_entropy(self.password_lineEdit.text())
        display_value = min(entropy, 128)
        # Вычисляем соотношение заполненности
        max_measure = self.get_progress_bar_color()
        max_color = max_measure["color"]
        self.progressBar.setStyleSheet(f"""
        QProgressBar {{
            color: rgb(255, 255, 255);
            border-radius: 5px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background: transparent;
            border-radius: 5px;
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgb(255, 0, 0),
                stop: 1 rgb{max_color}
            );
        }}
    """)
        if entropy > 128:
            self.bits_label.setText(">128 bits")
        else:
            self.bits_label.setText(f"{str(display_value)} bits")
        self.progressBar.setValue(display_value)

    def get_progress_bar_color(self):
        display_value = password_entropy(self.password_lineEdit.text())
        # Ограничиваем значение от 0 до 128
        value = max(0, min(display_value, 128))
        # Вычисляем соотношение заполненности
        percentage = (value / 128) * 100
        # Красный, Желтый, Зеленый в RGB
        red = (255, 0, 0)
        yellow = (255, 255, 0)
        green = (0, 255, 0)
        # Вычисляем, на каком участке градиента находится заполненность
        if percentage <= 50:
            # Интерполяция от красного к желтому
            ratio = percentage / 50  # Нормализуем на 0-1 (для первой половины)
            r = int(red[0] + (yellow[0] - red[0]) * ratio)
            g = int(red[1] + (yellow[1] - red[1]) * ratio)
            b = int(red[2] + (yellow[2] - red[2]) * ratio)
        else:
            # Интерполяция от желтого к зеленому
            ratio = (percentage - 50) / 50  # Нормализуем на 0-1 (для второй половины)
            r = int(yellow[0] + (green[0] - yellow[0]) * ratio)
            g = int(yellow[1] + (green[1] - yellow[1]) * ratio)
            b = int(yellow[2] + (green[2] - yellow[2]) * ratio)
        return {"color":(r, g, b), "percent":percentage}