from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QLayout
from common import consts


class FlowLayout(QLayout):
    def __init__(self, selected_tags, combobox, parent=None, margin=0, spacing=-1, max_items_per_row=4):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.combo_box = combobox
        self.selected_tags = selected_tags
        self.spacing = spacing
        self.max_items_per_row = max_items_per_row

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if index >= 0 and index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Horizontal | Qt.Vertical)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        num_in_line = 0

        effective_spacing = self.spacing if self.spacing != -1 else 10

        for item in self._item_list:
            next_x = x + item.sizeHint().width()
            if num_in_line >= self.max_items_per_row or next_x - effective_spacing > rect.right():
                x = rect.x()
                y += line_height + effective_spacing
                line_height = 0
                num_in_line = 0

            if not test_only:
                item.setGeometry(QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x += item.sizeHint().width() + effective_spacing
            line_height = max(line_height, item.sizeHint().height())
            num_in_line += 1

        return y + line_height - rect.y()

    def add_tag(self, text):
        tag = self.create_tag(text)
        self.selected_tags.append(text)
        self.addWidget(tag)

    def create_tag(self, text):
        tag_container = QtWidgets.QFrame()
        tag_container.setObjectName("tagContainer")
        layout = QtWidgets.QHBoxLayout(tag_container)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        label = QtWidgets.QLabel(str(text))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("border: none;")
        close_btn = QtWidgets.QPushButton("×")
        #close_btn.setFixedSize(16, 16)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {consts.colors["fg"]};
                border-left: 1px solid {consts.colors["main_text"]};
                color: red;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}
            QPushButton:hover {{
                color: darkred;
            }}
        """)

        close_btn.clicked.connect(lambda checked, t=tag_container: self.remove_tag(t))

        layout.addWidget(label)
        layout.addWidget(close_btn)
        layout.setSpacing(0)
        # Добавляем элементы с относительным весом
        layout.addWidget(label, stretch=4)   # 4 части
        layout.addWidget(close_btn, stretch=1)  # 1 часть

        return tag_container

    def remove_tag(self, tag_widget):
        tag = tag_widget.findChild(QtWidgets.QLabel)
        self.combo_box.addItem(tag.text())
        self.selected_tags.remove(tag.text())
        self.removeWidget(tag_widget)
        tag_widget.deleteLater()