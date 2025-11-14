
def create_table(metadata, table_name, *columns):
    '''
        Create a new table in the metadata file.

        Args:
                metadata (dict): The metadata dictionary.
                table_name (str): The name of the table to create.
                columns (list): A list of column names for the table.

        Returns:
                New table metadata.
    '''
    if not table_name.strip():
        print('Имя таблицы не может быть пустым.')
        return None
    
    if table_name in metadata:
        print('Такая таблица уже существует.')
        return None
    elif columns:

        allowed_data_types = ['int', 'str', 'bool']

        for column in columns:
            if not isinstance(column, str):
                print('Недопустимый формат колонок.')
                return None
            
            parts = column.split(':', 1)

            if len(parts) != 2:
                print('Недопустимый формат колонок.')
                return None
            
            column_name, data_type = parts
            if not column_name.strip():
                print('Недопустимое имя колонки.')
                return None
            
            if data_type.strip().lower() not in allowed_data_types:
                print('Недопустимый тип данных.')
                return None
            
            if 'ID:int' not in columns:
                processed_columns = ['ID:int']
            else:
                processed_columns = []
                
            processed_columns.append(f'{column_name.strip()}:{data_type.lower().strip()}')
        
        metadata[table_name] = {'columns': processed_columns}
        return metadata
    else:
        print('Недопустимый формат колонок.')


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

