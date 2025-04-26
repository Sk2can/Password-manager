import ast
import pywinstyles
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMenu, QAction, QMessageBox
from client_side.gui.add_password_window import AddPasswordWindow
from client_side.gui.edit_password_window import EditPasswordWindow
from common import consts, interaction, general
from PyQt5 import uic, QtCore
from common.general import reset_interface


class MainWindow(QMainWindow):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        pywinstyles.apply_style(self, "dark")  # Применение темного стиля окна Windows
        self.load_ui("main_window.ui")
        self.user = user # Сохранение логина текущего пользователя
        self.lsts = () # Инициализация кортежа для полученных паролей
        self.response = "" # Инициализация строки ответа от сервера
        self.update_table()
        self.add_tree_item(["Child 1.1", "Child 2", "Child 3"])

    def load_ui(self, ui_file):
        """
        Загружает интерфейс для текущего окна из .ui файла.

        :param ui_file: Путь к ui файлу.
        :type ui_file: str
        """
        uic.loadUi(f"{consts.UI}/{ui_file}", self)
        # Подключение сигналов
        if hasattr(self, "treeView"):
            self.treeView.clicked.connect(self.on_tree_item_clicked)
        if hasattr(self, "actionAdd_password_2"):
            self.actionAdd_password_2.triggered.connect(self.open_add_password_window)
        if hasattr(self, "update_pushButton"):
            self.update_pushButton.clicked.connect(self.update_window)
        if hasattr(self, "tableWidget"):
            self.tableWidget.customContextMenuRequested.connect(self.open_context_menu)
            self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)

    def add_row_to_table(self, data):
        """
        Добавление записи в таблицу окна.

        :param data: Кортеж с информацией о записи.
        :type data: tuple
        """
        exclude_indices = {0, 1}  # индексы, которые нужно исключить (id из БД и название категории)
        row_position = self.tableWidget.rowCount()  # получаем индекс новой строки
        self.tableWidget.insertRow(row_position)  # вставляем новую строку

        column = 0
        for i, value in enumerate(data):
            if i not in exclude_indices:
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, data[0])
                self.tableWidget.setItem(row_position, column, item)
                column+=1

    def update_table(self):
        """
        Обновление таблицы окна.
        """
        response = interaction.send_to_server(f"GET_PASSWORDS|{self.user}")
        self.lsts = ast.literal_eval(response)
        for credential in self.lsts:
            self.add_row_to_table(credential)

    def add_tree_item(self, children):
        """
        Добавление элемента в дерево категорий.

        :param children: Список элементов.
        :type children: list
        """
        # Создаём корневой элемент
        model = QStandardItemModel()
        # Добавляем дочерние элементы
        for child_text in children:
            child_item = QStandardItem(child_text)
            model.appendRow(child_item)
        model.setHeaderData(0, QtCore.Qt.Horizontal, 'Categories')
        self.treeView.setModel(model)
        self.treeView.expandAll()

    def on_tree_item_clicked(self):
        print("Кликнули на категорию")

    def open_add_password_window(self):
        """
        Функция инициализации диалогового окна добавления пароля.
        """

        add_password_window = AddPasswordWindow(self.user)
        add_password_window.exec_()

    def update_window(self):
        reset_interface(self,"main_window.ui")
        self.update_table()

    def open_context_menu(self, pos: QPoint):
        """
        Отображение контекстного меню при нажатии на кнопку действия.

        :param pos: Координаты нажатия (передаются сами).
        :type pos: QPoint
        """
        item = self.tableWidget.itemAt(pos)
        if item:
            row = item.row()
            menu = QMenu(self)
            action_edit = QAction("Редактировать", self)
            action_delete = QAction("Удалить", self)
            action_edit.triggered.connect(lambda: self.edit_row(row))
            action_delete.triggered.connect(lambda: self.delete_row(row))
            menu.addAction(action_edit)
            menu.addAction(action_delete)
            menu.exec_(self.tableWidget.viewport().mapToGlobal(pos))

    def edit_row(self, row_index):
        """
        Инициализация окна редактирования записи.

        :param row_index: Индекс записи в таблице окна.
        :type row_index: int
        """

        row_data = general.get_row_as_dict(self.tableWidget, row_index)
        db_index = self.tableWidget.item(row_index, 0).data(Qt.UserRole)
        edit_password_window = EditPasswordWindow(row_data, db_index)
        edit_password_window.exec_()

    def delete_row(self, row):
        """
        Инициализация окна удаления записи.

        :param row: Индекс записи в таблице окна.
        :type row: int
        """

        index = self.tableWidget.item(row, 0).data(Qt.UserRole)
        dialog = None  # Инициализация переменной для диалога
        # Если диалог ещё не создан — создаём его
        if dialog is None:
            dialog = QMessageBox()
            dialog.setWindowTitle("Confirm")
            dialog.setText("Are you sure you want to delete the entry?")
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        pywinstyles.apply_style(dialog, "dark")
        # Показываем окно
        reply = dialog.exec_()
        if reply == QMessageBox.Yes:
            # здесь код удаления
            response = interaction.send_to_server(f"DELETE_ENTRY|credentials|id|{index}")