import prompt
import shlex
from core import create_table, drop_table, insert, select, delete
from utils import load_metadata, save_metadata, load_table_data, save_table_data
def run():
    '''
    Main function of the program. Cicle of interaction with the user.

    Returns:
    None.
    '''
    print("Добро пожаловать в DB-проект!")
    print("Вызовите help для просмотра доступных команд.")
    metadata = load_metadata()
    while True:
        try:
            answer = prompt.string('Введите команду: ').strip().lower()
            if not answer:
                continue

            args = shlex.split(answer)
            if not args:
                print("Пустая команда.")
                continue
            command = args[0]
            match command:
                case 'exit':
                    if len(args) == 1:
                        print("До свидания!")
                        break
                    else:
                        print("Exit не требует аргументов")
                case 'create_table':
                    if len(args) < 3:
                        print("Использование: create_table <table> <col1:type> [col2:type ...]")
                    else:
                        table_name = args[1]
                        columns = args[2:]
                        if table_name in metadata:
                            print(f"Таблица '{table_name}' уже существует.")
                        else:
                            create_table(metadata, table_name, *columns)
                            save_metadata(metadata)
                case 'drop_table':
                    if len(args) != 2:
                        print("Использование: drop_table <table>")
                    else:
                        table_name = args[1]
                        if table_name in metadata:
                            drop_table(metadata, table_name)
                            save_metadata(metadata)
                            print(f"Таблица '{table_name}' удалена.")
                        else:
                            print(f"Таблица '{table_name}' не существует.")
                case 'help':
                    print_help()
                case 'list_tables':
                    if metadata:
                        list_tables = list(metadata.keys())
                        print(f"Таблицы в базе данных: {', '.join(list_tables)}")
                    else:
                        print("В базе данных нет таблиц.")
                case 'insert':
                    if len(args) < 3:
                        print("Использование: insert <table> <value1> [value2 ...]")
                    else:
                        table_name = args[1]
                        values = args[2:]
                        if table_name in metadata:
                            insert(metadata, table_name, *values)
                        else:
                            print(f"Таблица '{table_name}' не существует.")
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
