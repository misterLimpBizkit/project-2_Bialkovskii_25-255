def parser_insert_command(insert_args):
    """
    Parse the insert command arguments.

    Args:
        insert_args (list): The arguments of the insert command.

    Returns:
        list: The table name and the values to insert.
    """
    if insert_args[0].lower() != "into":
        print('Ожидается ключевое слово "into".')
        return None, None

    if len(insert_args) < 4:
        print("Использование: insert into <table> values (<value1>, <value2>, ...)")
        return None, None

    table_name = insert_args[1]

    if insert_args[2].lower() != "values":
        print('Ожидается ключевое слово "values".')
        return None, None

    values = []
    for arg in insert_args[3:]:
        cleaned_arg = arg.strip("() ")
        if cleaned_arg:
            values.append(cleaned_arg)

    return table_name, values


def parse_value(value_str):
    """
    Converts a string value to the correct Python type.

    Args:
        value_str (str): String value

    Returns:
        Any type: int, bool, str or None in case of error
    """
    if not value_str:
        return None

    value_str = value_str.strip()

    if value_str.isdigit():
        return int(value_str)

    if value_str.lower() in ("true", "false"):
        return value_str.lower() == "true"

    return str(value_str)


def parse_where_clause(where_args):
    """
    Parse the where command arguments.

    Args:
        where_args (list): The arguments of the insert command.

    Returns:
        dict: The dictionary of where arguments.
    """
    if not where_args:
        return None

    where_clause = {}
    i = 0

    while i < len(where_args):
        if i + 2 >= len(where_args):
            print("Некорректное условие where: недостаточно аргументов.")
            return None

        column = where_args[i]
        operator = where_args[i + 1]
        value_str = where_args[i + 2]

        if operator != "=":
            print(f'Оператор {operator} не поддерживается. Используйте "=".')
            return None

        value = parse_value(value_str)
        if value is None:
            return None

        where_clause[column] = value

        i += 3

        if i < len(where_args):
            if where_args[i].lower() == "and":
                i += 1
                continue
            else:
                print(f"Ожидается 'and', получено {where_args[i]}.")
                return None

    return where_clause


def parse_select_delete_commands(select_args):
    """
    Parse the SELECT command arguments.

    Args:
        select_args (list): The arguments of the Select command.

    Returns:
        list: list of commands or None
    """
    if len(select_args) < 2:
        print("Использование: select from <table> [where <condition>]")
        return None, None

    if select_args[0].lower() != "from":
        print('Ожидается ключевое слово "from"')
        return None, None

    table_name = select_args[1]
    where_clause = None

    if len(select_args) > 2 and select_args[2].lower() == "where":
        where_clause = parse_where_clause(select_args[3:])
        if where_clause is None:
            print("Нет условия.")
            return None, None

    return table_name, where_clause


def parse_update_command(update_args):
    """
    Parse UPDATE command in format: update <table> set <column> = \
        <value> where <column> = <value>

    Args:
        update_args (list): The arguments after 'update' command

    Returns:
        tuple: (table_name, set_clause, where_clause) or (None, None, None) on error
    """
    if len(update_args) < 8:
        print(
            "Использование: update <table> set <column> = <value> " \
            "where <column> = <value>"
        )
        return None, None, None

    try:
        table_name = update_args[0]

        if update_args[1].lower() != "set":
            print('Ожидается "set" после имени таблицы')
            return None, None, None

        if update_args[5].lower() != "where":
            print('Ожидается "where" после значения SET')
            return None, None, None

        set_column = update_args[2]
        if update_args[3] != "=":
            print('Ожидается "=" в SET условии')
            return None, None, None

        set_value = parse_value(update_args[4])
        if set_value is None:
            return None, None, None

        set_clause = {set_column: set_value}

        where_column = update_args[6]
        if update_args[7] != "=":
            print('Ожидается "=" в WHERE условии')
            return None, None, None

        where_value = parse_value(update_args[8] if len(update_args) > 8 else "")
        if where_value is None:
            return None, None, None

        where_clause = {where_column: where_value}

        return table_name, set_clause, where_clause

    except Exception as e:
        print(f"Ошибка парсинга UPDATE: {e}")
        return None, None, None
