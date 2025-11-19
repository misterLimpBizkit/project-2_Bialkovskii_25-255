import os

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import (
    create_record,
    id_generator,
    load_table_data,
    validate_and_convert_types,
)


@handle_db_errors
def create_table(metadata, table_name, *columns):
    '''
    Create a new table in the metadata.

    Args:
        metadata (dict): The metadata dictionary.
        table_name (str): The name of the table to create.
        columns (list): A list of column definitions like ["name:str", "age:int"].

    Returns:
        dict: Updated metadata or None on error.
    '''

    if not table_name or not table_name.strip():
        print('Ошибка: Имя таблицы не может быть пустым.')
        return None
    
    table_name = table_name.strip()
    
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None
    
    if not columns:
        print('Ошибка: Таблица должна содержать хотя бы один столбец (кроме ID).')
        return None
    
    allowed_data_types = ['int', 'str', 'bool']
    processed_columns = ['ID:int']
    
    for column in columns:
        if not isinstance(column, str):
            print(f'Ошибка: Недопустимый формат колонки "{column}".')
            return None
        
        parts = column.split(':', 1)
        if len(parts) != 2:
            print(f'Ошибка: Некорректный формат "{column}". Используйте: имя:тип')
            return None
        
        column_name, data_type = parts
        column_name = column_name.strip()
        data_type = data_type.strip().lower()
        
        if not column_name:
            print('Ошибка: Имя колонки не может быть пустым.')
            return None
        
        if column_name.upper() == 'ID':
            print('Ошибка: Имя "ID" зарезервировано системой.')
            return None
        
        if data_type not in allowed_data_types:
            print(f'Ошибка: Недопустимый тип данных "{data_type}".' 
            'Допустимы: int, str, bool')
            return None
        
        existing_columns = [col.split(':')[0] for col in processed_columns]
        if column_name in existing_columns:
            print(f'Ошибка: Колонка "{column_name}" уже существует в таблице.')
            return None
        
        processed_columns.append(f'{column_name}:{data_type}')
    
    
    metadata[table_name] = {'columns': processed_columns}
    print(f'Таблица "{table_name}" успешно создана со столбцами:'
           f'{", ".join(processed_columns)}')
    return metadata


@handle_db_errors
@confirm_action('удаление таблицы')
def drop_table(metadata, table_name):
    '''
        Drop a table from the metadata file.

        Args:
                metadata (dict): The metadata dictionary.
                table_name (str): The name of the table to drop.

        Returns:
                Updated metadata.
    '''
    if table_name in metadata:
        del metadata[table_name]
        file_path = f"data/{table_name}.json"
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Файл данных '{file_path}' удален")
        except OSError as e:
            print(f"Ошибка при удалении файла '{file_path}': {e}")
        return metadata
    else:
        print('Такой таблицы не существует.')
        return None

@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    '''
        Insert a new row into a table.

        Args:
                metadata (dict): The metadata dictionary.
                table_name (str): The name of the table.
                values (tuple): The values to insert.

        Returns:
                Updated metadata.
        '''

    if table_name not in metadata:
        print('Такой таблицы не существует.')
        return None
    
    table_data = load_table_data(table_name)
    if not table_data:
        table_data = []

    table_columns = metadata[table_name]['columns']
    useful_table_columns = [col for col in table_columns if not col.startswith('ID:')]
    if len(values) != len(useful_table_columns):
        print('Кол-во передаваемых значений ' \
        'не совпадает с количеством столбцов')
        print(f"Столбцы: {', '.join(useful_table_columns)}")  
        return None
    
    checked_data = validate_and_convert_types(useful_table_columns, values)
    if checked_data is None:
        print('Типы данных столбцов и внесенной информации не совпадают')
        return None
    
    new_id = id_generator(table_data)
    new_record = create_record(new_id, checked_data, useful_table_columns)
    table_data.append(new_record)
    
    print(f"Запись успешно добавлена в таблицу '{table_name}' с ID={new_id}")
    return table_data


cacher = create_cacher()
@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    '''
        Select rows from a table based on a where clause.

        Args:
                table_data (list): The list of rows in the table.
                where_clause (str, optional): The where clause to filter rows.

        Returns:
                list: Filtered rows.
        '''
    
    if not table_data:
        print('Таблица пуста.')
        return None
        
    if where_clause is None:
        return table_data
        
    if not isinstance(where_clause, dict) or len(where_clause) == 0:
        print("Ошибка: where_clause должен быть словарем")
        return None
        
    first_row = table_data[0]
    for column in where_clause.keys():
        if column not in first_row:
            print(f'Ошибка: Колонка "{column}" не существует в таблице.')
            print(f'Доступные колонки: {", ".join(first_row.keys())}')
            return None
        
    cache_key = f"select_{str(where_clause)}"

    def execute_query(): 
        '''
        Function to execute the query and cache the result.
        '''  
        filtered_data = []
        for row in table_data:
                if all(row.get(column) == value for column, 
                       value in where_clause.items()):
                    filtered_data.append(row)
        return filtered_data

    return cacher(cache_key, execute_query)


def where_clause_check(table_data, where_clause):
    '''
        Check if the where clause is valid.

        Args:
                table_data (list): The list of rows in the table.
                where_clause (dict): The where clause to filter rows.

        Returns:
                bool: True if the where clause is valid, False otherwise.
    '''
    if not where_clause:
        print('Отсутствует where_clause.')
        return False

    if not isinstance(where_clause, dict):
        print('where_clause должен быть словарем')
        return False
    
    first_row = table_data[0]
    for column in where_clause.keys():
        if column not in first_row:
            print(f'Ошибка: Колонка "{column}" не существует в таблице.')
            print(f'Доступные колонки: {", ".join(first_row.keys())}')
            return False
        
    return True


@handle_db_errors
def update(table_data, set_clause, where_clause):
    '''
        Update rows in a table based on a where clause.

        Args:
                table_data (list): The list of rows in the table.
                set_clause (dict): The set clause to update rows.
                where_clause (dict): The where clause to filter rows.

        Returns:
                list: Updated rows.
    '''
    if not table_data:
        print('Таблица пуста.')
        return None
    
    if not set_clause:
        print('Отсутствует set_clause.')
        return None
    
    if not where_clause_check(table_data, where_clause):
        return None
    
    if not isinstance(set_clause, dict):
        print("set_clause должны быть словарями")
        return None
    
    try: 
        first_row = table_data[0]
        for column in set_clause.keys():
            if column not in first_row:
                print(f'Ошибка: Колонка "{column}" не существует в таблице.')
                print(f'Доступные колонки: {", ".join(first_row.keys())}')
                return None
            
        updated_count = 0
        for row in table_data:
            if all(row.get(key) == value for key, value in where_clause.items()):
                for key, value in set_clause.items():
                    row[key] = value
                    updated_count += 1

        if updated_count == 0:
            print('Нет строк, удовлетворяющих условиям where_clause.')
        else:
            print(f'Обновлено {updated_count} строк.')

        return table_data
    
    except Exception as e:
        print(f'Ошибка при обновлении: {e}')
        return None


@handle_db_errors
@confirm_action('удаления строки')
def delete(table_data, where_clause):
    '''
    Delete rows from a table based on a where clause.

    Args:
        table_data (list): The list of rows in the table.
        where_clause (dict): The where clause to filter rows.

    Returns:
        list: Updated rows.
    '''
    if not table_data:
        print('Таблица пуста.')
        return None

    if not where_clause_check(table_data, where_clause):
        return []

    try:
        updated_count = 0
        for row in table_data:
            if all(row.get(key) == value for key, value in where_clause.items()):
                updated_count += 1
                table_data.remove(row)

        if updated_count == 0:
            print('Нет строк, удовлетворяющих условиям where_clause.')
        else:
            print(f'Удалено {updated_count} строк.')

        return table_data
    
    except Exception as e:
        print(f'Ошибка при удалении: {e}')
        return None
    
