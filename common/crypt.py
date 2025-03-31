from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os


def generate_key_pair():
    """
    Генерирует пару ключей для ассиметричного шифрования.

    :return: Возвращает приватный и публичный ключи в байтовом формате
    :rtype: bytes
    """

    # Генерация приватного ключа
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,  # Размер ключа (рекомендуется 2048 или больше)
        backend=default_backend()
    )
    # Получение публичного ключа из приватного
    public_key = private_key.public_key()
    # Сериализация ключей для сохранения или передачи
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()  # Без пароля
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_pem, public_pem

def split_into_blocks(data, block_size):
    """
    Разбивает переданные данные на блоки допустимого размера
    для последующего шифрования.

    :param data: Строка для разбиения на блоки.
    :type data: str
    :param block_size: Итоговый размер блоков.
    :type block_size: int
    :return: Возвращает список строк заданной длины.
    """
    return [data[i:i+block_size] for i in range(0, len(data), block_size)]

def encrypt_large_data(public_key_pem, data):
    """
    Поблочное шифрование переданных данные с разделением на блоки.

    :param data: Строка для шифрования.
    :type data: str
    :param public_key_pem: Публичный ключ для шифрования.
    :type public_key_pem: str
    :return: Возвращает зашифрованную строку.
    """

    public_key_pem = public_key_pem.encode("utf-8")
    block_size = 100
    # Загрузка публичного ключа
    public_key = serialization.load_pem_public_key(
        public_key_pem,
        backend=default_backend()
    )
    blocks = split_into_blocks(data, block_size)
    encrypted_blocks = [
        public_key.encrypt(
            block.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        for block in blocks
    ]
    # Кодируем каждый блок в Base64 и объединяем через разделитель
    encoded_blocks = [base64.b64encode(block).decode('utf-8') for block in encrypted_blocks]
    return "|".join(encoded_blocks)  # Разделитель между блоками

def decrypt_large_data(private_key_pem, encrypted_data):
    """
    Поблочная расшифровка полученных данных.

    :param encrypted_data: Зашифрованная строка с разделителями блоков.
    :type encrypted_data: str
    :param private_key_pem: Приватный ключ для расшифровки.
    :type private_key_pem: str
    :return: Расшифрованная строка.
    """

    # Загрузка приватного ключа
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,  # Без пароля
        backend=default_backend()
    )
    # Разделяем строку на блоки по разделителю
    encoded_blocks = encrypted_data.split("|")
    encrypted_blocks = [base64.b64decode(block) for block in encoded_blocks]

    decrypted_blocks = [
        private_key.decrypt(
            block,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode("utf-8")
        for block in encrypted_blocks
    ]
    return "".join(decrypted_blocks)

def derive_key_from_string(key_string):
    """
    Генерация ключа симметричного шифрования из переданной строки.

    :param key_string: Строка для создания ключа (до 32 символов).
    :type key_string: str
    :return: Ключ шифрования.
    :rtype: bytes
    """

    # Используем первые 32 байта строки (для AES-256)
    key_bytes = key_string.encode('utf-8')[:32]
    # Если строка короче 32 байт, дополняем нулями
    return key_bytes.ljust(32, b'\0')

def encrypt_string(key_string, plaintext):
    """
    Симметричное шифрование строки секретным ключом.

    :param key_string: Строка для создания ключа (до 32 символов).
    :type key_string: str
    :param plaintext: Текст для шифрования.
    :type plaintext: str
    :return: Зашифрованная строка.
    """

    # Преобразуем строку-ключ в байты
    key = derive_key_from_string(key_string)

    # Генерация случайного IV (16 байт для AES-CBC)
    iv = os.urandom(16)

    # Создаем объект шифрования
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Добавляем паддинг к данным
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    # Шифруем данные
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Объединяем IV и зашифрованные данные
    encrypted_data = iv + ciphertext

    # Кодируем в Base64 для хранения в виде строки UTF-8
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_string(key_string, encrypted_data_base64):
    """
    Дешифрование симметрично зашифрованной строки.

    :param key_string: Строка для создания ключа (до 32 символов).
    :type key_string: str
    :param encrypted_data_base64: Текст для дешифрования в кодировке base64.
    :return: Расшифрованная строка.
    """

    # Преобразуем строку-ключ в байты
    key = derive_key_from_string(key_string)

    # Декодируем из Base64 обратно в байты
    encrypted_data = base64.b64decode(encrypted_data_base64)

    # Извлекаем IV из первых 16 байт
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # Создаем объект дешифрования
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Расшифровываем данные
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Удаляем паддинг
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    # Возвращаем расшифрованную строку
    return plaintext.decode()


# Пример использования
if __name__ == "__main__":
    key_string = "mysecretkey12345"  # Строка-ключ
    plaintext = "Привет, это секретное сообщение!"

    # Шифрование
    encrypted_data_base64 = encrypt_string(key_string, plaintext)
    print(f"Зашифрованные данные (Base64): {encrypted_data_base64}")

    # Дешифрование
    decrypted_text = decrypt_string(key_string, encrypted_data_base64)
    print(f"Расшифрованные данные: {decrypted_text}")