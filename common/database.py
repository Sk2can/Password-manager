from common.crypt import encrypt_string
from common import TOTP
import pymysql
import bcrypt


def get_db_connection(database):
    """
    Создание объекта соединения между клиентом и сервером.

    :param database: Название БД.
    :type database: str
    :return: Объект соединения.
    """

    try:
        if database:
            return pymysql.connect(
                host="localhost",
                user="root",
                password="1qaz!QAZ",
                database=database)
        else:
            return pymysql.connect(
            host="localhost",
            user="root",
            password="1qaz!QAZ")
    except RuntimeError:
        raise BaseException("Unable to connect to the database server")

def initialize_database():
    """
    Инициализация или проверка БД.
    """

    try:
        conn = get_db_connection(False)
    except BaseException as e:
        exit(e)
    cursor = conn.cursor()
    try:
        # Создаем базу данных, если она не существует
        cursor.execute("CREATE DATABASE IF NOT EXISTS password_manager\
         CHARACTER SET utf8mb4\
         COLLATE utf8mb4_unicode_ci;")
        print("База данных 'password_manager' создана или уже существует.")

        # Используем базу данных
        cursor.execute("USE password_manager")

        # Создаем таблицу users, если она не существует
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(64) UNIQUE NOT NULL PRIMARY KEY,
            password_hash VARCHAR(64) NOT NULL,
            fa_secret VARCHAR(64) NOT NULL
        )
        """)
        print("Таблица 'users' создана или уже существует.")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")

    finally:
        cursor.close()
        conn.close()

def add_user(username, password):
    """
    Добавление нового пользователя в БД.

    :param username: Имя пользователя.
    :type username: str
    :param password: Пароль пользователя.
    :type password: str
    :return: Код возврата.
    """

    conn = get_db_connection("password_manager")
    cursor = conn.cursor()
    status = ""

    try:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        secret_key = TOTP.generate_secret_key()
        secret_key_crypt = encrypt_string(password, secret_key)
        # SQL-запрос для добавления записи
        query = "INSERT INTO users (username, password_hash, fa_secret) VALUES (%s, %s, %s)"
        values = (username, password_hash, secret_key_crypt)

        # Выполняем запрос
        cursor.execute(query, values)

        # Фиксируем изменения
        conn.commit()
        status = f"0:{secret_key}"

    except pymysql.connect.Error as err:
        error = str(err).split(", ")
        status = error[0][1:] + ":" + error[1][1:-2]

        conn.rollback()  # Откатываем изменения в случае ошибки

    finally:
        cursor.close()
        conn.close()
        return status

def auth_user(username, password):
    """
    Проверка введенных пользовательских данных для авторизации.

    :param username: Имя пользователя.
    :type username: str
    :param password: Пароль пользователя.
    :type password: str
    :return: Код возврата.
    """

    conn = get_db_connection("password_manager")
    cursor = conn.cursor()

    try:
        # Ищем пользователя по логину
        query = "SELECT password_hash FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result is None:
            return "1:User not found"

        # Извлекаем хэш пароля из базы данных
        stored_password_hash = result[0]

        # Проверяем пароль
        if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash.encode("utf-8")):
            return "0:ok"
        else:
            return "2:wrong password"

    except pymysql.connect.Error as err:
        print(f"Ошибка: {err}")
        error = str(err).split(", ")
        return error[0][1:] + ":" + error[1][1:-2]

    finally:
        cursor.close()
        conn.close()

def search(table, key_column, key_value, field):
    """
    Поиск определенного поля в таблице по ключевому полю.

    :param table: Название таблицы.
    :type table: str
    :param key_column:  Название ключевого поля.
    :type key_column:str
    :param key_value: Значение ключевого поля.
    :type key_value: str
    :param field: Название поля для поиска.
    :type field: str
    :return: Результирующая строка
    :rtype: str
    """

    # Подключаемся к базе данных
    conn = get_db_connection("password_manager")
    cursor = conn.cursor()
    result = ""
    try:
        # Составление запроса для поиска
        query = f"SELECT {field} FROM {table} WHERE {key_column} = %s"
        cursor.execute(query, (key_value,))
        result = f"0:{cursor.fetchone()[0]}"

        if result is None:
            print("Пользователь не найден.")
            result = "1:user not found"

    except pymysql.connect.Error as err:
        print(f"Ошибка: {err}")
        error = str(err).split(", ")
        result = error[0][1:] + ":" + error[1][1:-2]

    finally:
        cursor.close()
        conn.close()
        return result

if __name__ == "__main__":
    pass