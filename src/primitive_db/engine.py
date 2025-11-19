import shlex

import prompt

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.parser import (
    parse_select_delete_commands,
    parse_update_command,
    parser_insert_command,
)
from primitive_db.utils import (
    display_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def run():
    """
    Main function of the program. Cicle of interaction with the user.

    Returns:
    None.
    """
    print("Добро пожаловать в DB-проект!")
    print("Вызовите help для просмотра доступных команд.")
    metadata = load_metadata()
    while True:
        try:
            answer = prompt.string("Введите команду: ").strip().lower()
            if not answer:
                continue

            parts = shlex.split(answer)
            if not parts:
                print("Пустая команда.")
                continue
            command = parts[0]
            args = parts[1:]
            match command:
                case "exit":
                    if len(parts) == 1:
                        print("До свидания!")
                        break
                    else:
                        print("Exit не требует аргументов")

                case "create_table":
                    if len(parts) < 3:
                        print(
                            "Использование: create_table <table> <col1:type> "
                            "[col2:type ...]"
                        )
                    else:
                        table_name = parts[1]
                        columns = parts[2:]
                        if table_name in metadata:
                            print(f"Таблица '{table_name}' уже существует.")
                        else:
                            create_table(metadata, table_name, *columns)
                            save_metadata(metadata)

                case "drop_table":
                    if len(parts) != 2:
                        print("Использование: drop_table <table>")
                    else:
                        table_name = parts[1]
                        if table_name in metadata:
                            drop_table(metadata, table_name)
                            save_metadata(metadata)
                            if table_name not in metadata:
                                print(f"Таблица {table_name} удалена.")
                        else:
                            print(f"Таблица '{table_name}' не существует.")

                case "list_tables":
                    if metadata:
                        list_tables = list(metadata.keys())
                        print(f"Таблицы в базе данных: {', '.join(list_tables)}")
                    else:
                        print("В базе данных нет таблиц.")

                case "insert":
                    table_name, values = parser_insert_command(args)
                    if table_name is None:
                        continue
                    new_table_data = insert(metadata, table_name, values)
                    if not new_table_data:
                        continue
                    save_table_data(table_name, new_table_data)
                    print(f"Данные успешно добавлены в таблицу '{table_name}'")

                case "select":
                    table_name, where_clause = parse_select_delete_commands(args)
                    if table_name not in metadata:
                        print("Такой таблицы нет.")
                        continue
                    table_data = load_table_data(table_name)
                    if table_name is None:
                        continue
                    data_to_be_showed = select(table_data, where_clause)
                    if not data_to_be_showed:
                        continue
                    display_table_data(data_to_be_showed, table_name)
                    print("Данные показаны.")

                case "update":
                    table_name, set_clause, where_clause = parse_update_command(args)
                    if table_name is None:
                        continue
                    if table_name not in metadata:
                        continue
                    table_data = load_table_data(table_name)
                    updated_data = update(table_data, set_clause, where_clause)
                    if not updated_data:
                        continue
                    save_table_data(table_name, updated_data)
                    print("Данные обновлены.")

                case "delete":
                    table_name, where_clause = parse_select_delete_commands(args)
                    if not where_clause:
                        table_data = []
                    if table_name not in metadata:
                        print("Такой таблицы нет.")
                        continue
                    if table_name is None:
                        continue
                    table_data = load_table_data(table_name)
                    deleted_data = delete(table_data, where_clause)
                    save_table_data(table_name, deleted_data)

                case "help":
                    print_help()

                case _:
                    print(f"Неизвестная команда {command}. Введите 'help'")
        except KeyboardInterrupt:
            print("\nПрервано пользователем.")
            break
        except IndexError:
            print("Пустая команда.")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")


def print_help():
    """Prints the help message for the current mode."""

    print("\n*** Доступные команды ***")
    print("create_table <table> <col1:type> [col2:type ...] - создать таблицу")
    print("list_tables - показать список таблиц")
    print("drop_table <table> - удалить таблицу")
    print("select from <table> [where <conditions>] - выбрать данные")
    print("update <table> set <col=val> [where <conditions>] - обновить данные")
    print("delete from <table> [where <conditions>] - удалить данные")
    print("exit - выход")
    print("help - эта справка")
    print("\nПримеры:")
    print("  create_table users name:str age:int")
    print("  select from users where age = 25 and name = 'dasha'")
    print("  update users set name = 'ivan' where age = 25")
    print("  delete from users where id = 1")
