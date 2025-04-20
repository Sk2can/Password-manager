from datetime import datetime
from common.crypt import encrypt_string
from common.consts import ROOT
from dotenv import load_dotenv
from common import TOTP
import pymysql
import bcrypt
import os

# Загружаем переменные из .env
load_dotenv(f"{ROOT}/critical.env")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PRIVATE_KEY = os.getenv("DB_PRIVATE_KEY")

def get_db_connection(database):
    """
    Создание объекта соединения между клиентом и сервером.

    :param database: Название БД.
    :type database: str
    :return: Объект соединения.
    """

    try:
        if database != "":
            return pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=database)
        else:
            return pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD)
    except RuntimeError:
        raise BaseException("Unable to connect to the database server")

def initialize_database():
    """
    Инициализация или проверка БД.
    """

    try:
        conn = get_db_connection("")
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
        CREATE TABLE IF NOT EXISTS Users (
            username VARCHAR(32) UNIQUE NOT NULL PRIMARY KEY,
            password_hash VARCHAR(64) NOT NULL,
            fa_secret_encrypted VARCHAR(64) NOT NULL,
            created_at DATETIME NOT NULL,
            last_login DATETIME
        )
        """)

        # Создаем таблицу categories, если она не существует
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTO_INCREMENT ,
            user_fk VARCHAR(32) NOT NULL,
            name VARCHAR(32),
            FOREIGN KEY (user_fk) REFERENCES Users(username) ON DELETE CASCADE
        )
        """)

        # Создаем таблицу Credentials, если она не существует
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Credentials (
            id INTEGER PRIMARY KEY AUTO_INCREMENT ,
            user_fk VARCHAR(32) NOT NULL,
            service VARCHAR(32),
            login VARCHAR(64) NOT NULL,
            password_encrypted VARCHAR(64) NOT NULL,
            url TEXT,
            notes TEXT,
            category_id INTEGER,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (user_fk) REFERENCES Users(username) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES Categories(id) ON DELETE CASCADE
        )
        """)

        # Создаем таблицу tags, если она не существует
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tags (
            id INTEGER PRIMARY KEY AUTO_INCREMENT ,
            user_fk VARCHAR(32) NOT NULL,
            name VARCHAR(32),
            FOREIGN KEY (user_fk) REFERENCES Users(username) ON DELETE CASCADE
        )
        """)

        # Создаем таблицу Credential_tag, если она не существует
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Credential_tag (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            credential_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            FOREIGN KEY (credential_id) REFERENCES Credentials(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES Tags(id) ON DELETE CASCADE
        )
        """)

    except Exception as e:
        print(f"Ошибка при инициализации базы данных| {e}")

    finally:
        cursor.close()
        conn.close()

def db_connect(func):
    def wrapper(*args, **kwargs):
        # Подключаемся к базе данных
        conn = get_db_connection("password_manager")
        cursor = conn.cursor()
        kwargs["cursor"] = cursor
        result = ""
        try:
            result = func(*args, **kwargs)
            conn.commit()
        except pymysql.connect.Error as err:
            print(f"Ошибка| {err}")
            error = str(err).split(", ")
            result = error[0][1:] + "|" + error[1][1:-2]
        finally:
            cursor.close()
            conn.close()
            return result
    return wrapper

@db_connect
def add_password(username, password, title, url, notes, cursor=None):
    """
    Добавление нового пароля пользователя.
    """

    # SQL-запрос для добавления записи
    query = "INSERT INTO passwords (username, password, title, url, notes) VALUES (%s, %s, %s, %s, %s)"
    values = (username, password, title, url, notes)
    # Выполняем запрос
    cursor.execute(query, values)
    status = f"0|ok"
    return status

@db_connect
def add_user(username, password, cursor=None):
    """
    Добавление нового пользователя в БД.

    :param username: Имя пользователя.
    :type username: str
    :param password: Пароль пользователя.
    :type password: str
    :return: Код возврата.
    """
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    secret_key = TOTP.generate_secret_key()
    secret_key_crypt = encrypt_string(DB_PRIVATE_KEY, secret_key)

    # SQL-запрос для добавления записи
    now = datetime.now()
    time_format = "%Y-%m-%d %H:%M:%S"
    current_time = f"{now:{time_format}}"
    query = "INSERT INTO users (username, password_hash, fa_secret_encrypted, created_at) VALUES (%s, %s, %s, %s)"
    values = (username, password_hash, secret_key_crypt, current_time)

    # Выполняем запрос
    cursor.execute(query, values)
    status = f"0|{secret_key}"
    return status

@db_connect
def auth_user(username, password, cursor=None):
    """
    Проверка введенных пользовательских данных для авторизации.

    :param username: Имя пользователя.
    :type username: str
    :param password: Пароль пользователя.
    :type password: str
    :return: Код возврата.
    """

    # Ищем пользователя по логину
    query = "SELECT password_hash FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result is None:
        return "1|User not found"

    # Извлекаем хэш пароля из базы данных
    stored_password_hash = result[0]

    # Проверяем пароль
    if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash.encode("utf-8")):
        return "0|ok"
    else:
        return "2|wrong password"

@db_connect
def search(table, key_column, key_value, field, cursor=None):
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

    # Составление запроса для поиска
    query = f"SELECT {field} FROM {table} WHERE {key_column} = %s"
    cursor.execute(query, (key_value,))
    result = f"0|{cursor.fetchone()[0]}"

    if result is None:
        print("Пользователь не найден.")
        result = "1|user not found"
    return result

if __name__ == "__main__":
    pass