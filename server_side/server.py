from common import database, TOTP, crypt
from common.crypt import decrypt_string
import threading
import socket
import os


def handle_client(client_socket):
    try:
        DB_PRIVATE_KEY = os.getenv("DB_PRIVATE_KEY")
        server_private_key, client_public_key = crypt.generate_key_pair()
        client_socket.sendall(client_public_key) # Отправка публичного ключа клиенту

        received = client_socket.recv(4096) # Прием зашифрованного сообщения от клиента
        decrypted_message = crypt.decrypt_large_data(bytes(server_private_key), received.decode("utf-8")).split("|")

        result="|"
        server_public_key = decrypted_message[0] # Публичный ключ для шифрования, полученный от клиента
        cmd = decrypted_message[1] # Тэг команды для обработки
        del decrypted_message[:2] # Оставшиеся элементы - параметры для функций

        if cmd == "AUTH":
            try:
                username, password = decrypted_message[0], decrypted_message[1]
                result = database.auth_user(username, password)
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "REG":
            try:
                username, password = decrypted_message[0], decrypted_message[1]
                result = database.add_user(username, password, cursor=None)
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "TOTP":
            try:
                user = decrypted_message[0]
                result = database.search("users", "username", user, "fa_secret_encrypted")
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "VERIFY":
            try:
                user = decrypted_message[0]
                user_input = decrypted_message[1]
                secret = database.search("users", "username", user, "fa_secret_encrypted").split("|")[1]
                decrypted_secret = decrypt_string(DB_PRIVATE_KEY ,secret)
                result = TOTP.totp_verify(decrypted_secret, user_input)
                if result:
                    result = "0|ok"
                else:
                    result = "1|wrong time password"
            except Exception as e:
                print(f"Error: {e}")

        encrypted_data = (crypt.encrypt_large_data(server_public_key, result)) # Шифрование данных для отправки клиенту
        client_socket.sendall(encrypted_data.encode("utf-8")) # Отправка данных клиенту

    except Exception as e:
        print(f"Error| {e}")
    finally:
        client_socket.close()

def start_server():
    database.initialize_database()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5721))
    server.listen(5)
    print("Server started on port 5721")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    start_server()