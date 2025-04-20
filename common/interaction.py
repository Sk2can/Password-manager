from common import crypt
import socket


def init_client():
    """
    Создает объект подключения к серверу для взаимодействия.

    :return: Объект подключения к серверу или код ошибки.
    :rtype: Объект класса socket или int
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("127.0.0.1", 5721))
        return client
    except ConnectionRefusedError:
        return 2

def send_to_server(string):
    """
    Отправляет данные на сервер в виде зашифрованной строки.

    :param string: Строка с названием команды и параметрами для ее обработки вида CMD:param1:param2:...
    :type string: str
    :return decrypted_message: Код возврата и сообщение от функции на сервере вида code:message
    :rtype decrypted_message: str
    """
    client = init_client()  # Создание объекта для обмена данными
    if client == 2: # Возврат ошибки создания соединения
        return f"{client}|Сервер недоступен!"
    client_private_key, server_public_key = crypt.generate_key_pair() # Генерация пары ключей
    client_public_key = client.recv(4096).decode("utf-8") # Получение ключа для шифрования сообщения серверу
    message = server_public_key.decode("utf-8") + "|" + string # Формирование сообщения для клиента
    encrypted_data = crypt.encrypt_large_data(client_public_key, message)
    client.send(encrypted_data.encode("utf-8")) # Отправка сообщения на сервер
    response = client.recv(4096).decode("utf-8") # Получение зашифрованного сообщение от сервера
    decrypted_message = crypt.decrypt_large_data(client_private_key, response) # Расшифровка полученного сообщения
    return decrypted_message


if __name__ == "__main__":
    pass