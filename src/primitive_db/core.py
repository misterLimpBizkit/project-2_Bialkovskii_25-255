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
            print(f'Ошибка: Недопустимый тип данных "{data_type}". Допустимы: int, str, bool')
            return None
        
        existing_columns = [col.split(':')[0] for col in processed_columns]
        if column_name in existing_columns:
            print(f'Ошибка: Колонка "{column_name}" уже существует в таблице.')
            return None
        
        processed_columns.append(f'{column_name}:{data_type}')
    
    
    metadata[table_name] = {'columns': processed_columns}
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(processed_columns)}')
    return metadata


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
        return metadata
    else:
        print('Такой таблицы не существует.')
        return None

def insert(metadata, table_name, *values):
    '''
        Insert a new row into a table.

        Args:
                metadata (dict): The metadata dictionary.
                table_name (str): The name of the table.
                values (tuple): The values to insert.

        Returns:
                Updated metadata.
        '''
    from primitive_db.utils import load_table_data, save_table_data

    if table_name not in metadata:
        print('Такой таблицы не существует.')
        return None
    
    table_data = load_table_data(table_name)

    table_columns = metadata[table_name]['columns']
    useful_table_columns = [col for col in table_columns if not col.startswith('ID:')]
    if len(values) != len(useful_table_columns):
        print('Кол-во передаваемых значений ' \
        'не совпадает с количеством столбцов')
        print(f"Столбцы: {', '.join(useful_table_columns)}")  
        return None
    
    checked_data = validate_and_convert_types(useful_table_columns, values)
    if checked_data == None:
        print('Типы данных столбцов и внесенной информации не совпадают')
        return None
    
    new_id = id_generator(table_data)
    new_record = create_record(new_id, checked_data, useful_table_columns)
    table_data.append(new_record)
    save_table_data(table_name, table_data)
    
    print(f"Запись успешно добавлена в таблицу '{table_name}' с ID={new_id}")
    return table_data


def validate_and_convert_types(useful_table_columns, values):
    '''
    Validate and convert values to their respective types.

    Args:
            usefull_table_columns (list): List of column definitions.
            values (tuple): Values to validate and convert.

    Returns:
            list: Converted values or None on error.
    '''
    converted_values = []

    for value, column in zip(values, useful_table_columns):
        col_name, col_type = column.split(':', 1)
        col_type = col_type.strip().lower()
        
        try:
            if col_type == 'int':
                converted = int(value)
            elif col_type == 'bool':
                if value.lower() in ('true', '1', 'yes', 'да'):
                    converted = True
                elif value.lower() in ('false', '0', 'no', 'нет'):
                    converted = False
                else:
                    print(f"Ошибка: '{value}' нельзя преобразовать в bool")
                    return None
            elif col_type == 'str':
                converted = str(value)
            else:
                print(f"Неизвестный тип: {col_type}")
                return None
                
            converted_values.append(converted)
            
        except ValueError as e:
            print(f"Ошибка: не могу преобразовать '{value}' в {col_type}")
            return None
    
    return converted_values


def id_generator(table_data):
    '''
    Generate a unique ID for a new row.

    Args:
            table_data (str): The list of rows in the table.
        
    Returns:
            int: The generated ID.
    '''
    if not table_data:
        return 1
    
    return max((row['ID'] for row in table_data), default=0) + 1

def create_record(new_id, checked_values, useful_table_columns):
    '''
        Create a new record dictionary.

        Args:
                new_id (int): The ID of the new record.
                values (tuple): The values to insert.
                usefull_table_columns (list): List of column definitions.

        Returns:
                dict: The new record.
    '''
    record = {'ID': new_id}
    for value, column in zip(checked_values, useful_table_columns):
        column = column.split(':')[0]
        record[column] = value
    return record


    





            
        
        


    
    
