import pywinstyles
from PyQt5.QtWidgets import QDialog, QGraphicsScene
from dotenv import load_dotenv
from common.consts import ROOT
from common.interaction import send_to_server
from common.crypt import decrypt_string
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPixmap
from PyQt5 import uic, QtCore
from common import consts
import qrcode
import pyotp
import os


# Загружаем переменные из .env
load_dotenv(f"{ROOT}/critical.env")
DB_PRIVATE_KEY = os.getenv("DB_PRIVATE_KEY")

Form, Base = uic.loadUiType(f"{consts.UI}totp_setup_window.ui")


class TOTPSetupWindow(QDialog, Form):
    def __init__(self,user, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint) # Удаление кнопки вопроса
        pywinstyles.apply_style(self, "dark")  # Применение темного стиля окна Windows
        encrypted_totp_code = send_to_server(f"TOTP|{user}").split("|")[1]
        totp_code = decrypt_string(DB_PRIVATE_KEY, encrypted_totp_code)
        # Создание URI для Google Authenticator
        self.totp_uri = pyotp.TOTP(totp_code).provisioning_uri(
            name=user,
            issuer_name="Password manager"
        )
        self.secret_key_label.setText(totp_code)
        self.display_qr_code(self.totp_uri)
        # Сигналы
        self.done_pushButton.clicked.connect(self.close)

    def display_qr_code(self, totp_uri):
        """
        Метод создания и отображения QR кода для Google authenticator.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)

        # Создаем изображение QR-кода
        img = qr.make_image(fill_color="black", back_color="white")

        # Сохраняем изображение во временный файл
        qr_path=f"{consts.TEMP}temp_qr.png".replace("/", "\\")
        img.save(qr_path)

        # Загружаем изображение в QPixmap
        pixmap = QPixmap(qr_path)

        # Создаем QGraphicsScene и добавляем изображение
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        scene.setSceneRect(QRectF(pixmap.rect()))

        # Устанавливаем сцену в QGraphicsView
        self.qr_graphicsView.setScene(scene)

        os.remove(qr_path)