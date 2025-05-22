import ast
import pywinstyles
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog
from common import consts, interaction
from common.general import compare_lists, convert_string
from common.tag_widget import FlowLayout


class TagAssignmentWindow(QDialog):
    def __init__(self, user, row_data, password, db_index, parent=None):
        super().__init__(parent)
        self.row_data = row_data
        self.password = password
        self.db_index = db_index
        self.user = user
        self.user_tags = [] # Названия тегов пользователя
        self.credential_tags_ids = [] # Id тегов присущих выбранной записи
        self.credential_tags_names = []  # Названия тегов, прикрепленных к этой записи
        self.selected_tags = [] # Имена выбранных тегов
        self.load_ui("tag_assignment_window.ui")

        # Добавление названий тегов пользователя в комбобокс
        params = {"user_fk": self.user}
        self.user_tags = ast.literal_eval(
            interaction.send_to_server(f"SEARCH_ENTRY|table=tags|searching_column=name|params={params}"))
        if self.user_tags:
            for tag in self.user_tags:
                self.tag_comboBox.addItem(tag)
        else:
            self.tag_comboBox.setEnabled(False)
            self.confirmButton.setEnabled(False)
            self.error_label.setText(self.tr("There are no available tags!"))
        # Получение названий тегов присущих выбранной записи
        params = {"credential_id": self.db_index}
        self.credential_tags_ids = ast.literal_eval(
            interaction.send_to_server(f"SEARCH_ENTRY|table=credential_tag|searching_column=tag_id|params={params}"))
        for tag_id in self.credential_tags_ids:
            params = {"user_fk": self.user, "id": tag_id}
            name = ast.literal_eval(interaction.send_to_server(f"SEARCH_ENTRY|table=tags|searching_column=name|params={params}"))
            if name:
                self.credential_tags_names.append(name[0])

        # Создаем FlowLayout с 4 элементами в строке
        self.flow_layout = FlowLayout(self.selected_tags, self.tag_comboBox, max_items_per_row=4)
        self.flow_container = QtWidgets.QWidget()
        self.flow_container.setLayout(self.flow_layout)
        self.verticalLayout_6.addWidget(self.flow_container)

        # Инициализация тегов в окне присущих записи
        for tag in self.credential_tags_names:
            self.flow_layout.add_tag(tag)
            index = self.tag_comboBox.findText(str(tag))
            if index >= 0:
                self.tag_comboBox.removeItem(index)

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
        if hasattr(self, "confirmButton"):
            self.confirmButton.clicked.connect(self.edit_tags)
        if hasattr(self, "tag_comboBox"):
            self.tag_comboBox.textActivated.connect(self.on_combo_changed)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    def edit_tags(self):
        selected_tags_ids = [] # Названия выбранных тегов
        for name in self.selected_tags:
            params = {"user_fk": self.user, "name": name}
            selected_tags_ids.append(ast.literal_eval(
                interaction.send_to_server(f"SEARCH_ENTRY|table=tags|searching_column=id|params={params}"))[0])
        for tag_to_add in compare_lists(self.credential_tags_ids, selected_tags_ids)["added"]:
            self.add_entry_local(int(tag_to_add))
        for tag_to_delete in compare_lists(self.credential_tags_ids, selected_tags_ids)["removed"]:
            self.delete_entry_local(int(tag_to_delete))
        self.close()

    def on_combo_changed(self):
        text = self.tag_comboBox.currentText().strip()
        if text:
            index = self.tag_comboBox.currentIndex()
            self.tag_comboBox.removeItem(index)
            self.flow_layout.add_tag(text)
            self.tag_comboBox.setCurrentIndex(0)

    def add_entry_local(self, tag_id):
        self.add_tag(table="credential_tag", credential_id=self.db_index, tag_id=tag_id)

    def add_tag(self, **kwargs):
        data = "|".join(f"{key}={value}" for key, value in kwargs.items())
        message = f"UNIVERSAL_ADD_ENTRY|{data}"
        interaction.send_to_server(message)

    def delete_entry_local(self, tag_id):
        table = "credential_tag"
        searching_column = "id"
        params = {"credential_id": self.db_index, "tag_id": tag_id}
        message = f"SEARCH_ENTRY|table={table}|searching_column={searching_column}|params={params}"
        field_id = convert_string(interaction.send_to_server(message))[0]
        message = f"DELETE_ENTRY|{table}|{searching_column}|{field_id}"
        interaction.send_to_server(message)