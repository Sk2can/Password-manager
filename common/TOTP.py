import base64
import pyotp
import time
import os


def generate_secret_key():
    """
    Создает секретный ключ, на основе которого в дальнейшем генерируется TOTP-код.

    :return: Секретный ключ для генерации TOTP-кодов.
    :rtype: str
    """
    # Генерация 10 байт случайных данных (16 символов в Base32)
    random_bytes = os.urandom(10)
    # Кодирование в Base32
    secret_key = base64.b32encode(random_bytes).decode("utf-8").rstrip("=")
    return secret_key

def totp_verify(secret_key, user_input):
    """
    Сравнивает введенный TOTP-код с правильным.

    :param secret_key: Секретный ключ для генерации TOTP.
    :type secret_key: str
    :param user_input: Введенный пользователем TOTP-код.
    :type user_input: str
    :return: True если код верный, иначе False.
    :rtype: bool
    """
    #  Получение текущего одноразового пароля
    totp = pyotp.TOTP(secret_key.encode("utf-8"))
    if totp.verify(user_input):
        return True
    else:
        return False


if __name__ == "__main__":
    sk = generate_secret_key()
    print(f"Текущий код: {pyotp.TOTP(sk).now()}, осталось {30 - (int(time.time()) % 30)} сек.")
    code = input("Введите TOTP код: ")
    status = totp_verify(sk, code)
    print(f"Код верен: {status}")