import re
import asyncio
import datetime
import functools
import threading
import snakecase
from zoneinfo import ZoneInfo

# Custom JSON serializer for datetime objects
def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()


def run_once(func):
    """
    This decorator wraps a function and makes sure it is executed only once for the lifetime of the process.
    Depending on whether the wrapped function is normal or async it wraps accordingly.
    It cache's the response returned by the original function and returns the cached response on subsequent calls.

    Usage:
    @run_once
    def foo():
        ...

    @run_once
    async def async_foo():
        ...
    
    """
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with wrapper.lock:
                if not wrapper.has_executed:
                    wrapper.has_executed = True
                    wrapper.response = await func(*args, **kwargs)
            return wrapper.response
        wrapper.lock = asyncio.Lock()
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with wrapper.lock:
                if not wrapper.has_executed:
                    wrapper.has_executed = True
                    wrapper.response = func(*args, **kwargs)
            return wrapper.response
                    
        wrapper.lock = threading.Lock()
    wrapper.has_executed = False
    return wrapper


def generate_unique_id(name, table_args):
    unique_constraint = f"{snake_case(name)}_{'_'.join(table_args).replace('UrdhvaPostgresBase.', '')}"
    if len(unique_constraint) > 63:
        unique_constraint = f"{snake_case(name)}_{'_'.join([args.replace('_', '')[0:5] for args in table_args]).replace('UrdhvaPostgresBase.', '')}"[0:62]
    return unique_constraint


def snake_case(s):
    """
    # Replace hyphens with spaces, then apply regular expression substitutions for title case conversion
    # and add an underscore between words, finally convert the result to lowercase
    :param s: string
    :return: converted snake case string
    Example:- snake_case("AlgoFusion")
              return:- algo_fusion
    """
    return snakecase.convert(s)


def kebab_case(text):
    """To convert text to kebab case"""
    # Replace non-alphanumeric with space
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    # Insert space before capital letters (for camelCase/PascalCase)
    text = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
    # Lowercase, strip, and join with hyphens
    return '-'.join(text.lower().split())


def get_present_time(utc=False):
    """
    Function to get present time in utc or local format
    :param utc:
    :return:
    """
    time_stamp = datetime.datetime.now(datetime.timezone.utc)
    if not utc:
        time_stamp = time_stamp.astimezone(ZoneInfo('America/New_York'))
    return time_stamp

def to_sql_tuple(values):
    return f"({', '.join(repr(v) for v in values)})" if values else ""


def parse_bool(value: str) -> bool | None:
    """
    Try to interpret a string as a boolean.

    Returns:
        True if value is a recognized true token
        False if value is a recognized false token
        None if value is not recognized
    """
    if value is None:
        return None

    val = str(value).strip().lower()

    truthy = {"true", "t", "yes", "y", "1", "on", "ok", "allow", "trye", "success"}

    if val in truthy:
        return True

    return False
