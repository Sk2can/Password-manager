import ast
import pywinstyles
from PyQt5.QtCore import Qt, QPoint, QTimer, QEvent
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMenu, QAction, QMessageBox, QApplication, QHeaderView
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
        self.restarting_to_login = False
        self.lsts = () # Инициализация кортежа для полученных паролей
        self.response = "" # Инициализация строки ответа от сервера
        self.update_table()
        self.update_tree()

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
            self.tableWidget.cellClicked.connect(self.on_table_item_clicked)
            self.tableWidget.customContextMenuRequested.connect(self.open_context_menu)
            self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tableWidget.setColumnHidden(6, True)
            self.tableWidget.setColumnHidden(7, True)

        # Таймер бездействия
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setSingleShot(False)
        self.inactivity_timer.timeout.connect(self.restart_to_login)
        self.reset_inactivity_timer()
        QApplication.instance().installEventFilter(self)

    def add_row_to_table(self, data):
        """
        Добавление записи в таблицу окна.

        :param data: Кортеж с информацией о записи.
        :type data: tuple
        """

        exclude_indices = {0, 1, 4}  # индексы, которые нужно исключить (id из БД и название категории)
        row_position = self.tableWidget.rowCount()  # получаем индекс новой строки
        self.tableWidget.insertRow(row_position)  # вставляем новую строку

        column = 0
        for i, value in enumerate(data):
            if i not in exclude_indices:
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, data[0])
                self.tableWidget.setItem(row_position, column, item)
                column+=1
            elif i == 4:
                stars = "*" * len(value)
                item = QTableWidgetItem(str(stars))
                item.setData(Qt.UserRole + 1, value)  # Сохраняем оригинальный текст в скрытых данных
                self.tableWidget.setItem(row_position, column, item)
                column += 1

    def update_table(self):
        """
        Обновление таблицы окна.
        """

        response = interaction.send_to_server(f"GET_PASSWORDS|{self.user}")
        self.lsts = ast.literal_eval(response)
        for credential in self.lsts:
            self.add_row_to_table(credential)
        self.tableWidget.resizeColumnsToContents()

    def update_tree(self):
        """
        Обновление списка категорий.
        """

        response = interaction.send_to_server(f"GET_CATEGORIES|{self.user}")
        self.add_tree_item(ast.literal_eval(response))

    def add_tree_item(self, children):
        """
        Добавление элемента в дерево категорий.

        :param children: Список элементов.
        :type children: list
        """

        # Создаём корневой элемент
        parent_item = QStandardItem('Data base')
        model = QStandardItemModel()
        # Добавляем дочерние элементы
        for child_text in children:
            child_item = QStandardItem(child_text)
            parent_item.appendRow(child_item)
        model.appendRow(parent_item)
        model.setHeaderData(0, QtCore.Qt.Horizontal, 'Categories')
        self.treeView.setModel(model)
        self.treeView.expandAll()

    def on_tree_item_clicked(self, index):
        model = self.treeView.model()
        item = model.itemFromIndex(index)
        if not item.parent():  # Если у элемента нет родителя — значит это корень
            for row in range(self.tableWidget.rowCount()):
                self.tableWidget.showRow(row)
        else:
            text = index.data()
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 4)
                if item is not None and text.lower() in item.text().lower():
                    self.tableWidget.setRowHidden(row, False)
                else:
                    self.tableWidget.setRowHidden(row, True)

    def open_add_password_window(self):
        """
        Функция инициализации диалогового окна добавления пароля.
        """

        add_password_window = AddPasswordWindow(self.user)
        add_password_window.exec_()

    def update_window(self):
        reset_interface(self,"main_window.ui")
        self.update_table()
        self.update_tree()

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
            action_copy = QAction("Copy password", self)
            action_edit = QAction("Edit", self)
            action_delete = QAction("Delete", self)
            action_copy.triggered.connect(lambda: self.copy_password(row))
            action_edit.triggered.connect(lambda: self.edit_row(row))
            action_delete.triggered.connect(lambda: self.delete_row(row))
            menu.addAction(action_copy)
            menu.addAction(action_edit)
            menu.addAction(action_delete)
            menu.exec_(self.tableWidget.viewport().mapToGlobal(pos))

    def copy_password(self, row):
        """
        Функция копирования пароля из таблицы.

        :param row: Индекс записи в таблице окна.
        :type row: int
        """

        item = self.tableWidget.item(row, 2)

        if item:
            password = item.data(Qt.UserRole + 1)
            clipboard = QApplication.clipboard()
            clipboard.setText(password)

    def edit_row(self, row_index):
        """
        Инициализация окна редактирования записи.

        :param row_index: Индекс записи в таблице окна.
        :type row_index: int
        """

        row_data = general.get_row_as_dict(self.tableWidget, row_index)
        db_index = self.tableWidget.item(row_index, 0).data(Qt.UserRole)
        item = self.tableWidget.item(row_index, 2)
        edit_password_window = EditPasswordWindow(self.user, row_data, item.data(Qt.UserRole + 1), db_index)
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

    def on_table_item_clicked(self, row):
        row_data = {}
        self.textBrowser.clear()
        notes = ""
        for col in range(self.tableWidget.columnCount()):
            header_item = self.tableWidget.horizontalHeaderItem(col)
            header = header_item.text() if header_item else f"Column {col}"
            item = self.tableWidget.item(row, col)
            value = item.text() if item else ''
            row_data[header] = value
        for column, value in row_data.items():
            if value:
                if column == "URL":
                    self.textBrowser.insertHtml(f"<b>{column}</b>: <a href={value}>{value}</a>. ")
                elif column == "Notes":
                    notes = f"<br><br><b>{column}</b>:<br>{value}"
                else:
                    self.textBrowser.insertHtml(f"<b>{column}</b>: {value}. ")
        if notes:
            self.textBrowser.insertHtml(notes)

    def restart_to_login(self):
        from client_side.gui.auth_window import AuthWindow
        if self.restarting_to_login:
            return  # Уже перезапускаемся, ничего не делаем

        self.restarting_to_login = True  # Устанавливаем флаг

        self.login_window = AuthWindow()
        self.login_window.setObjectName("auth")
        self.login_window.show()

        for widget in QApplication.topLevelWidgets():
            if widget.objectName() != "auth":
                widget.close()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseMove, QEvent.KeyPress, QEvent.MouseButtonPress):
            self.reset_inactivity_timer()
        return super().eventFilter(obj, event)

    def reset_inactivity_timer(self):
        """Сброс таймера бездействия."""
        self.inactivity_timer.stop()
        self.inactivity_timer.start(5 * 60 * 1000)  # 5 минут = 300000 мс