import re
import pywinstyles
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QAction
from common import consts, interaction


class SettingsWindow(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.current_user = user
        self.base_style = None
        self.settings = QSettings("KVA", "Vaultary")
        self.color = self.settings.value("theme", "dark")
        self.language = self.settings.value("language", "en")
        self.load_ui("user_settings_window.ui")

    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """

        uic.loadUi(f"{consts.UI}/{ui_file}", self)
        settings = QSettings("KVA", "Vaultary")
        if settings.value("theme", "dark") == "dark": pywinstyles.apply_style(self, "dark")
        self.base_style = self.light_mode_pushButton.styleSheet()
        self.user_label.setText(self.current_user)
        # Запрос времени создания пользователя
        params = {"username": self.current_user}
        message = f"SEARCH_ENTRY|table=users|searching_column=created_at|params={params}"
        response = interaction.send_to_server(message)
        date = re.findall(r'\d+(?=[,)])', response) # Разделяем строку по запятой и скобке
        self.time_label.setText(f"{date[0]}-{date[1]}-{date[2]} {date[3]}:{date[4]}:{date[5]}")

        # Подсветка действующих режимов языка и цвета
        if self.color == "dark":
            self.add_effect(self.dark_mode_pushButton)  # Выделение действующей настройки
        else:
            self.add_effect(self.light_mode_pushButton)
        if self.language == "en":
            self.add_effect(self.eng_pushButton)
        else:
            self.add_effect(self.rus_pushButton)

        # Подключение сигналов
        if hasattr(self, "dark_mode_pushButton"):
            self.dark_mode_pushButton.clicked.connect(lambda i:self.add_effect(self.light_mode_pushButton))
        if hasattr(self, "light_mode_pushButton"):
            self.light_mode_pushButton.clicked.connect(lambda i:self.add_effect(self.dark_mode_pushButton))
        if hasattr(self, "eng_pushButton"):
            self.eng_pushButton.clicked.connect(lambda i:self.add_effect(self.rus_pushButton))
        if hasattr(self, "rus_pushButton"):
            self.rus_pushButton.clicked.connect(lambda i:self.add_effect(self.eng_pushButton))
        if hasattr(self, "confirm_pushButton"):
            self.confirm_pushButton.clicked.connect(self.send_changes)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    def add_effect(self, old_button):
        """Функция для добавления эффекта к кнопке, не заменяя текущий стиль"""
        sender = self.sender()
        if self.settings.value("theme", "dark") == "dark":
            new_effect = "border: 2px solid #EAEAEA; border-radius: 5px;"  # Новый эффект контура для темной темы
        else:
            new_effect = "border: 2px solid #EAEAEA; border-radius: 5px;"  # Новый эффект для светлой темы
        if isinstance(sender, QAction):
            if self.color == "dark":
                self.dark_mode_pushButton.setStyleSheet(self.base_style + " " + new_effect)
            else:
                self.light_mode_pushButton.setStyleSheet(self.base_style + " " + new_effect)
            if self.language == "en":
                self.eng_pushButton.setStyleSheet(self.base_style + " " + new_effect)
            else:
                self.rus_pushButton.setStyleSheet(self.base_style + " " + new_effect)
            return
        sender.setStyleSheet(sender.styleSheet() + " " + new_effect)  # Добавляем новый эффект
        old_button.setStyleSheet(self.base_style)
        if sender == self.dark_mode_pushButton:
            self.color = "dark"
        elif sender == self.light_mode_pushButton:
            self.color = "light"
        elif sender == self.eng_pushButton:
            self.language = "en"
        elif sender == self.rus_pushButton:
            self.language = "ru"

    def send_changes(self):
        if self.color == "dark":
            self.settings.setValue("theme", "dark")
        elif self.color == "light":
            self.settings.setValue("theme", "light")
        if self.language == "en":
            self.settings.setValue("language", "en")
        elif self.language == "ru":
            self.settings.setValue("language", "ru")
        self.close()