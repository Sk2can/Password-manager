import re


def is_valid_windows_filename(filename):
    """
    Проверяет, является ли имя файла допустимым в Windows.

    :param filename: Имя файла для проверки.
    :type filename: str
    :return: True если имя допустимо, иначе False.
    :rtype: bool
    """
    # Проверка длины имени файла
    if len(filename) > 255:
        return False

    # Проверка на наличие запрещенных символов
    invalid_chars = r'[\\/:*?"<>|]'
    if re.search(invalid_chars, filename):
        return False

    # Проверка на совпадение с зарезервированными именами устройств
    reserved_names = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    }
    name, _, ext = filename.partition('.')
    if name.upper() in reserved_names:
        return False

    # Проверка на завершение пробелом или точкой
    if filename.endswith(' ') or filename.endswith('.'):
        return False

    return True


# Пример использования
if __name__ == "__main__":
    pass