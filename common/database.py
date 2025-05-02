from datetime import datetime, date
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
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            user_fk VARCHAR(32) NOT NULL,
            service VARCHAR(32),
            login VARCHAR(64) NOT NULL,
            password_encrypted VARCHAR(64) NOT NULL,
            url TEXT,
            category_id INTEGER,
            notes TEXT,
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
    """
    Декоратор для реализации подключения к БД.

    :param func: Функция для обертывания.
    :type func: function
    """

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

def convert_dates_tuple(data):
    """
    Инициализация или проверка БД.
    :param data: Кортеж с датой для преобразования формата.
    :type data: tuple
    :return: Кортеж с преобразованной датой.
    :rtype data: tuple
    """

    return tuple(
        tuple(
            value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, (datetime, date)) else value
            for value in row
        )
        for row in data
    )

@db_connect
def add_credential(user_fk, service, login, password_encrypted, url, category_id, notes, cursor=None):
    """
    Добавление нового пароля пользователя.
    :param user_fk: Внешний ключ на пользователя.
    :type user_fk: str
    :param service: Название сервиса.
    :type service: str
    :param login: Логин пользователя.
    :type login: str
    :param password_encrypted: Зашифрованный пароль.
    :type password_encrypted: str
    :param url: Ссылка на сервис.
    :type url: str
    :param category_id: Id категории, к которой принадлежит пароль.
    :type category_id: str
    :param notes: Заметки для пароля.
    :type notes: str
    :return: Код возврата.
    """

    # SQL-запрос для добавления записи
    now = datetime.now()
    time_format = "%Y-%m-%d %H:%M:%S"
    created_at = f"{now:{time_format}}"
    password_encrypted = encrypt_string(DB_PRIVATE_KEY, password_encrypted)

    query = "INSERT INTO credentials (user_fk, service, login, password_encrypted, url, category_id, notes, created_at)\
     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (user_fk, service, login, password_encrypted, url, category_id, notes, created_at)
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

@db_connect
def search_all(table, fk_key_column, fk_key_value, cursor=None):
    """
    Поиск всех полей соответствующих внешнему ключу.
    :param table: Название таблицы.
    :type table: str
    :param fk_key_column: столбец внешних ключей.
    :type fk_key_column: str
    :param fk_key_value: значение внешнего ключа.
    :type fk_key_value: str
    :return: Результирующая строка
    :rtype: str
    """

    # Составление запроса для поиска
    query = f"SELECT * FROM {table} WHERE {fk_key_column} = %s"
    cursor.execute(query, (fk_key_value,))
    result = cursor.fetchall()
    result = convert_dates_tuple(result) # Конвертирование объектов дат в строки
    if result == "0|()":
        print("Записи не найдены.")
        result = "1|no records found"
    return result

@db_connect
def delete_entry(table, key_column, key, cursor=None):
    """
    Удаление записи по ключу.
    :param table: Название таблицы.
    :type table: str
    :param key_column: Название столбца с первичными ключами.
    :type key_column: str
    :param key: Первичный ключ.
    :type key: str
    :return: Код возврата.
    :rtype: str
    """

    # Составление запроса для поиска
    query = f"DELETE FROM {table} WHERE {key_column} = %s"
    cursor.execute(query, (key,))
    result = "0|entry deleted"
    return result

@db_connect
def edit_credential(table, updates: dict, where_clause: tuple, where_params: tuple, cursor=None):
    """
    Универсальный метод обновления записи в любой таблице.

    :param table: Имя таблицы
    :param updates: Словарь с колонками и новыми значениями
    :param where_clause: Поля для условия (например: (id,))
    :param where_params: Значения для условия (например: (5,))
    """

    # Формируем часть SET column1 = %s, column2 = %s ...
    update_str = ""
    values = ()
    for column, value in updates.items():
        update_str += column + " = %s, "
        values+= (value,)
    else:
        update_str = update_str[:-2] # Удаляем последние 2 символа строки
    # Формируем часть WHERE id1 = %s, id2 = %s...
    clause_str = ""
    for column in where_clause:
        clause_str += column + " = %s AND "
    else:
        clause_str = clause_str[:-5]
    # Добавляем значения условий в кортеж для запроса
    for value in where_params:
        values += (value,)
    # SQL-запрос для изменения записи
    query = f"UPDATE {table} SET {update_str} WHERE {clause_str}"
    # Выполняем запрос
    cursor.execute(query, values)
    status = f"0|ok"
    return status

@db_connect
def add_entry(cursor=None, **kwargs):
    """
    Добавление новой записи в заданную таблицу.
    :param table: Название таблицы.
    :type table: str
    :return: Код возврата.
    :rtype : str
    """

    column_names = ""
    values = []
    for column, value in kwargs.items():
        if column != "table":
            column_names += f"{column}, "
            values.append(value)
    else:
        column_names = column_names[:-2]
    values_string = (len(values) * "%s, ")[:-2]

    # SQL-запрос для добавления записи
    query = f"INSERT INTO {kwargs['table']} ({column_names})\
     VALUES ({values_string})"
    # Выполняем запрос
    cursor.execute(query, tuple(values))
    status = f"0|ok"
    return status


if __name__ == "__main__":
    pass