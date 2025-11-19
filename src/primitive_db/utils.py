import json
import os

from prettytable import PrettyTable

from primitive_db.constants import DATA_DIR, DEFAULT_FILE_PATH


def load_metadata(file_path=DEFAULT_FILE_PATH):
    """
        Load metadata from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Metadata as dictionary. Returns empty dict on error.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Ошибка, файл {file_path} не найден")
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка, некорректный формат в '{file_path}'.")
        return {}
    except PermissionError:
        print(f"Нет прав на чтение файла: {file_path}")
        return {}


def save_metadata(metadata):
    """
       Save metadata to a JSON file.

    Args:
        file_path (str): Path to save the JSON file.
        data (dict): Data to save.

    Returns:
        None.
    """
    file_path = DEFAULT_FILE_PATH
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)
    except PermissionError:
        print(f"Нет прав на запись в файл: {file_path}")


def get_table_data_path(table_name):
    """
    Get the path to the data file for a specific table.
    """
    if not table_name:
        return None
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """
    Load data from a JSON file.

    Args:
            table_name (str): Name of the table.

    Returns:
            dict: Data as dictionary. Returns empty dict on error.
    """
    file_path = get_table_data_path(table_name)
    if not file_path:
        return None

    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        else:
            return []
    except FileNotFoundError:
        print(f"Ошибка, файл {file_path} не найден")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка, некорректный формат в '{file_path}'.")
        return []
    except PermissionError:
        print(f"Нет прав на чтение файла: {file_path}")
        return []
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return []


def save_table_data(table_name, data):
    """
    Save data to a JSON file.

    Args:
            table_name (str): Name of the table.
            data (dict): Data to save.

    Returns:
            None.
    """
    file_path = get_table_data_path(table_name)
    if not file_path:
        return None
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False, sort_keys=True)
    except PermissionError:
        print(f"Нет прав на запись в файл: {file_path}")


def validate_and_convert_types(useful_table_columns, values):
    """
    Validate and convert values to their respective types.

    Args:
            usefull_table_columns (list): List of column definitions.
            values (tuple): Values to validate and convert.

    Returns:
            list: Converted values or None on error.
    """
    converted_values = []

    for value, column in zip(values, useful_table_columns):
        col_name, col_type = column.split(":", 1)
        col_type = col_type.strip().lower()

        try:
            if col_type == "int":
                converted = int(value)
            elif col_type == "bool":
                if value.lower() in ("true", "1", "yes", "да"):
                    converted = True
                elif value.lower() in ("false", "0", "no", "нет"):
                    converted = False
                else:
                    print(f"Ошибка: '{value}' нельзя преобразовать в bool")
                    return None
            elif col_type == "str":
                converted = str(value)
            else:
                print(f"Неизвестный тип: {col_type}")
                return None

            converted_values.append(converted)

        except ValueError:
            print(f"Ошибка: не могу преобразовать '{value}' в {col_type}")
            return None

    return converted_values


def id_generator(table_data):
    """
    Generate a unique ID for a new row.

    Args:
            table_data (str): The list of rows in the table.

    Returns:
            int: The generated ID.
    """
    if not table_data:
        return 1

    return max((row["ID"] for row in table_data), default=0) + 1  # +1 не забываем


def create_record(new_id, checked_values, useful_table_columns):
    """
    Create a new record dictionary.

    Args:
            new_id (int): The ID of the new record.
            values (tuple): The values to insert.
            usefull_table_columns (list): List of column definitions.

    Returns:
            dict: The new record.
    """
    record = {"ID": new_id}
    for value, column in zip(checked_values, useful_table_columns):
        column = column.split(":")[0]
        record[column] = value
    return record


def display_table_data(table_data, table_name="Данные"):
    """Display table data in a formatted table using PrettyTable.

    Args:
        table_data (list): List of dictionaries representing table rows.
                          Each dictionary should have the same keys.
        table_name (str): Name of the table for the title.

    Returns:
        None: Prints the formatted table to console.
    """
    if not table_data:
        return

    table = PrettyTable()

    table.field_names = list(table_data[0].keys())

    for row in table_data:
        table.add_row([row[field] for field in table.field_names])

    table.align = "l"
    table.horizontal_char = "─"
    table.vertical_char = "│"
    table.junction_char = "┼"

    table.title = f"{table_name}"

    print(table)
