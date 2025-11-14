import prompt
import shlex
from primitive_db.core import create_table, drop_table  
from primitive_db.utils import load_metadata, save_metadata
def run():
    '''
    Main function of the program. Cicle of interaction with the user.

    Returns:
    None.
    '''
    print("Добро пожаловать в DB-проект!")
    print("Доступные команды: 'help', 'exit', 'create_table', 'drop_table")
    root_json = 'metadata.json'
    metadata = load_metadata(root_json)
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
                            save_metadata(metadata, root_json)
                            print(f"Таблица '{table_name}' создана.")
                case 'drop_table':
                    if len(args) != 2:
                        print("Использование: drop_table <table>")
                    else:
                        table_name = args[1]
                        if table_name in metadata:
                            drop_table(metadata, table_name)
                            save_metadata(metadata, root_json)
                            print(f"Таблица '{table_name}' удалена.")
                        else:
                            print(f"Таблица '{table_name}' не существует.")
                case 'help':
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
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

            
            
        
            