import ast
from datetime import datetime
from common import database, crypt, TOTP
from common.crypt import decrypt_string, encrypt_string
import threading
import socket
import os

from common.general import convert_string


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
                # Создание пользователя
                result = database.add_user(username, password, cursor=None)
                # Создание базовой категории
                result += database.add_entry(table="categories", user_fk=username, name="default")

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
                secret = database.search("users", "username", user,
                                         "fa_secret_encrypted").split("|")[1]
                decrypted_secret = decrypt_string(DB_PRIVATE_KEY ,secret)
                result = TOTP.totp_verify(decrypted_secret, user_input) # Закомментируй, чтобы убрать второй фактор
                result = "ok"
                if result:
                    result = "0|ok"
                else:
                    result = "1|wrong time password"
            except Exception as e:
                print(f"Error: {e}")
        elif cmd == "GET_PASSWORDS":
            try:
                user = decrypted_message[0]
                result = database.search_all("credentials", "user_fk", user)
                # Преобразуем в список списков
                mutable_data = [list(row) for row in result]
                ind = 0
                for cred in mutable_data:
                    password = decrypt_string(DB_PRIVATE_KEY ,cred[4])
                    mutable_data[ind][4] = password
                    category_name = database.search("categories", "id", mutable_data[ind][6],
                                                  "name").split("|")[1]
                    mutable_data[ind][6] = category_name
                    ind+=1
                # Обратно в кортеж кортежей
                result = tuple(tuple(row) for row in mutable_data)
                if result != "()":
                    result = f"{result}" # Конвертируем в строку для передачи
                else:
                    result = "1|"
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "GET_CATEGORIES":
            try:
                user = decrypted_message[0]
                result = database.search_all("categories", "user_fk", user)
                categories = []
                for tuple_i in result:
                    categories.append(tuple_i[2])
                if categories:
                    result = f"{categories}" # Конвертируем в строку для передачи
                else:
                    result = "1|the user has no categories"
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "ADD_CREDENTIAL":
            try:
                user_fk = decrypted_message[0]
                service = decrypted_message[1]
                login = decrypted_message[2]
                password_encrypted = decrypted_message[3]
                url = decrypted_message[4]
                category_name = decrypted_message[5]
                category_id = database.search("categories", "name", category_name,"id")
                if category_id:
                    category_id = category_id.split("|")[1]
                elif category_name:
                    database.add_entry(table="categories", user_fk=user_fk, name=category_name)
                    category_id = database.search("categories", "name", category_name,"id")
                    category_id = category_id.split("|")[1]
                notes = decrypted_message[6]
                result = database.add_credential(user_fk, service, login, password_encrypted, url, category_id, notes)
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "EDIT_CREDENTIAL":
            try:
                table = decrypted_message[0]
                where_clause = ast.literal_eval(decrypted_message[1]) # Преобразуем строку в кортеж
                where_params = ast.literal_eval(decrypted_message[2])
                updates = ast.literal_eval(decrypted_message[3]) # Преобразуем строку в словарь
                category_name = updates["category"]
                current_user = updates["user"]
                del updates["category"]
                del updates["user"]
                now = datetime.now() # Получаем текущее время
                time_format = "%Y-%m-%d %H:%M:%S"
                change_at = f"{now:{time_format}}" # Преобразуем объект времени по заданному шаблону
                updates["updated_at"] = change_at
                password_encrypted = encrypt_string(DB_PRIVATE_KEY, updates["password_encrypted"]) # Шифруем пароль
                updates["password_encrypted"] = password_encrypted
                category_id = database.search("categories", "name", category_name,"id")
                if category_id:
                    category_id = category_id.split("|")[1]
                elif category_name and not category_id:
                    database.add_entry(table="categories", user_fk=current_user, name=category_name)
                    category_id = database.search("categories", "name", category_name,"id")
                    category_id = category_id.split("|")[1]
                updates["category_id"] = category_id
                result = database.edit_credential(table, updates, where_clause, where_params)
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "ADD_ENTRY":
            try:
                new_entry = dict(item.split("=") for item in decrypted_message) # Преобразование списка в словарь
                database.add_entry(table=new_entry["table"], user_fk=new_entry["user_fk"], name=new_entry["name"])
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "EDIT_ENTRY":
            try:
                new_entry = dict(item.split("=") for item in decrypted_message) # Преобразование списка в словарь
                table = new_entry["table"]
                updates = convert_string(new_entry["updates"])
                where_clause = convert_string(new_entry["where_clause"])
                where_params = convert_string(new_entry["where_params"])
                database.edit_credential(table, updates, where_clause, where_params)
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "DELETE_ENTRY":
            try:
                table = decrypted_message[0]
                key_column = decrypted_message[1]
                key = decrypted_message[2]
                result = database.delete_entry(table, key_column, key)
            except Exception as e:
                print(f"Error| {e}")
        elif cmd == "SEARCH_ENTRY":
            try:
                search_params = dict(item.split("=") for item in decrypted_message) # Преобразование списка в словарь
                table = search_params["table"]
                searching_column = search_params["searching_column"]
                params = convert_string(search_params["params"])
                result = str(database.search_entries(table, searching_column, params))
            except Exception as e:
                print(f"Error| {e}")

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