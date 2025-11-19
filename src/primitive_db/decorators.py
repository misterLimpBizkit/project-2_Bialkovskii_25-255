import time
from functools import wraps


def handle_db_errors(func):
    """
    Decorator for handling database-related errors.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. Возможно, база данных не" \
                " инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name):
    """
    Ask for confirmation before executing a function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if (
                input(
                    f"Вы уверены, что хотите выполнить действие '{action_name}'?"
                      "(y/n): "
            ).lower()
            == "y"
                ):
                return func(*args, **kwargs)
            else:
                print("Действие отменено.")
                return None

        return wrapper

    return decorator


def log_time(function):
    """
    Decorator to log the execution time of a function.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = function(*args, **kwargs)
        end = time.monotonic()

        function_time = end - start
        print(f"Функция {function.__name__} выполнилась за {function_time:.3f} секунд.")

        return result

    return wrapper


def create_cacher():
    """
    Factory function to create a cacher decorator.
    """
    cache = {}

    def cache_result(key, value_function):
        """
        Cache the result of a function call.

        Args:
            key (str): The key to store the result.
            value_function (function): The function to call to get the value.

        Returns:
            The cached value.
        """
        if key in cache:
            print(f"Используется кешированный результат для ключа {key}.")
            return cache[key]

        result = value_function()
        cache[key] = result
        print(f"Результат кеширован для ключа {key}.")
        return result

    return cache_result
