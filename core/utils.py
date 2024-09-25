import multiprocessing
import os
import re
from datetime import datetime
from itertools import zip_longest
from typing import Tuple


def split_version_release(version_release: str) -> list:
    """
    Splits a version string into a list of integers and strings.

    Args:
        version_release (str): The version string to be split.

    Returns:
        list: A list where version numbers are represented as integers and non-numeric parts as strings.

    Examples:
        split_version("1.2.3")
        [1, '.', 2, '.', 3]
        split_version("1.2a3")
        [1, '.', 2, 'a', 3]
    """
    result = [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", version_release) if part]
    return result


def data_preparation(version1: str, version2: str) -> tuple:
    """
    Prepares data from version strings by splitting them into components.

    Args:
        version1 (str): The first version as a string.
        version2 (str): The second version as a string.

    Returns:
        tuple: A tuple containing two lists:
            - A list of split components of the first version.
            - A list of split components of the second version.

    Examples:
        data_preparation("alt1.qa2", "alt1.p10.1")
        ([['alt', 1], ['qa', 2]], [['alt', 1], ['p', 10], [1]])
    """
    data1 = re.split(r'[^a-zA-Z0-9]+', version1)
    data2 = re.split(r'[^a-zA-Z0-9]+', version2)

    fixed_data = [split_version_release(i) for i in data1]
    fixed_data2 = [split_version_release(i) for i in data2]
    return fixed_data, fixed_data2


def create_zip_data(fixed_data: tuple) -> list:
    """
    Creates a list where pairs of elements from two lists are combined into tuples.

    Args:
        fixed_data (tuple): A tuple containing two lists to be zipped together.

    Returns:
        list: A list where each element is a list of tuples,
              combining elements from both lists.
              If one list is shorter, None will be substituted.

    Examples:
        create_zip_data(([['alt', 1], ['qa', 2]], [['alt', 1], [15]]))
        [[('alt', 'alt'), (1, None)], [('qa', None), (2, None)]]
    """
    zip_data = [
        list(zip_longest(r1 or [], r2 or [], fillvalue=None))
        for r1, r2 in zip_longest(fixed_data[0], fixed_data[1], fillvalue=None)
    ]
    return zip_data


def compare_versions_release(version1: str, version2: str, release: bool = False) -> bool:
    """
    Compares two strings of versions or releases to determine if the first is larger than the second.

    Args:
        version1 (str): The first version string.
        version2 (str): The second version string.
        release (bool): The parameter is used to define what is being compared,
            if it is a release and the releases are the same in the two packages then False is returned,
            if versions are being compared and they are the same then True is returned to further compare versions.
    Returns:
        bool: True if version1 is greater than version2, False otherwise.

    Examples:
        compare_versions("1.2.3", "1.2.2")
        True
        compare_versions("1.2.3", "1.2.4")
        False
    """
    fixed_data = data_preparation(version1, version2)

    zip_data = create_zip_data(fixed_data)

    this_start = True

    for block in zip_data:
        for data in block:

            if None in data:
                if not this_start:
                    return data[0] is None and isinstance(data[1], str)
                else:
                    return data[1] is None

            if isinstance(data[0], int) and isinstance(data[1], int):
                if data[0] == data[1]:
                    this_start = False
                    continue
                return data[0] > data[1]

            elif isinstance(data[0], str) and isinstance(data[1], str):
                if data[0] == data[1]:
                    this_start = False
                    continue
                return data[0] > data[1]

            elif isinstance(data[0], int) and isinstance(data[1], str):
                return True
            elif isinstance(data[0], str) and isinstance(data[1], int):
                return False

        this_start = True
    return False if release else True


def generate_package_set(dict_list: list) -> dict:
    """
    Generates a dictionary of package information from a list of dictionaries.

    Args:
        dict_list (list): A list of dictionaries where each dictionary contains package details.

    Returns:
        dict: A dictionary with package names and architectures as keys, and their respective details as values.

    Examples:
        generate_package_set([
             {"name": "pkg1", "arch": "x86_64", "epoch": 1, "version": "1.0", "release": "1"},
             {"name": "pkg2", "arch": "arm", "epoch": 2, "version": "2.0", "release": "2"}
         ])
        {('pkg1', 'x86_64'): {'epoch': 1, 'version': '1.0', 'release': '1'},
         ('pkg2', 'arm'): {'epoch': 2, 'version': '2.0', 'release': '2'}}
    """
    package_dict = {}
    for item in dict_list:
        key = (item["name"], item["arch"])
        if key not in package_dict:
            package_dict[key] = {
                "epoch": item["epoch"],
                "version": item["version"],
                "release": item["release"],
            }
    return package_dict


def worker(func, *args):
    """
    Executes a function with provided arguments.

    Args:
        func (callable): The function to be executed.
        *args: The arguments to be passed to the function.

    Returns:
        The result of the function call.

    Examples:
        worker(sum, 1, 2, 3)
        6
    """
    return func(*args)


def key_func_name(pkg) -> tuple:
    """
    Returns a tuple of package name and architecture.

    Args:
        pkg (object): A package object with attributes `name` and `arch`.

    Returns:
        tuple: A tuple containing the package's name and architecture.

    Examples:
        class Package:
             def __init__(self, name, arch):
                 self.name = name
                 self.arch = arch

        pkg = Package("pkg1", "x86_64")
        key_func_name(pkg)
        ('pkg1', 'x86_64')
    """
    return (pkg.name, pkg.arch)


def check_difficult(dict_list1: list, dict_list2: list) -> Tuple[bool, int]:
    """
    Checks the complexity of processing two lists of dictionaries based on their total length.

    Args:
        dict_list1 (list): The first list of dictionaries.
        dict_list2 (list): The second list of dictionaries.

    Returns:
        Tuple[bool, int]: A tuple where the first element is True if processing is considered difficult,
        and the second element is a numerical code indicating the level of difficulty.

    Examples:
        check_difficult([{}], [{}])
        (False, 0)
    """
    length_sum = len(dict_list1) + len(dict_list2)
    num_cores = multiprocessing.cpu_count()
    if length_sum > 1_600_000:
        if num_cores == 2:
            return (True, 2) if length_sum >= 2_100_000 else (False, 0)
        elif num_cores > 2:
            return True, 3
    return False, 0


def get_current_user() -> str:
    """
    Retrieves the current username.

    Returns:
        str: The username of the current user. Returns "Unknown user" if unable to retrieve the username.

    Examples:
        get_current_user()
        'john_doe'
    """
    try:
        user = os.getenv("USER") or os.getenv("USERNAME") or os.getlogin()
        if not user:
            raise ValueError("Failed to retrieve username")
        return user
    except Exception:
        return "Unknown user"


def get_time() -> str:
    """
    Gets the current time formatted as HH:MM:SS DD-MM-YYYY.

    Returns:
        str: The current time formatted as HH:MM:SS DD-MM-YYYY.

    Examples:
        get_time()
        '14:30:15 18-09-2024'
    """
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S %d-%m-%Y")
    return formatted_time


def create_response(data: list) -> dict:
    """
    Creates a response dictionary with user information, current time, and provided data.

    Args:
        data (list): A list containing information about two packages and newer versions.

    Returns:
        dict: A dictionary with user, time, and result information.

    Examples:
        create_response([
             {"name": "pkg1", "arch": "x86_64"},
             {"name": "pkg2", "arch": "arm"},
             {"pkg1": "1.0", "pkg2": "2.0"}
         ])
        {'user': 'john_doe',
         'time': '14:30:15 18-09-2024',
         'result': {'first_package': {'name': 'pkg1', 'arch': 'x86_64'},
                    'second_package': {'name': 'pkg2', 'arch': 'arm'},
                    'newer_versions_first_package': {'pkg1': '1.0', 'pkg2': '2.0'}}}
    """
    result = {
        "user": get_current_user(),
        "time": get_time(),
        "result": {
            "first_package": data[0],
            "second_package": data[1],
            "newer_versions_first_package": data[2],
        },
    }
    return result


def colorize_text(color: str, text: str) -> str:
    colors = {"green": "\033[92m", "red": "\033[91m", "purple": "\033[95m"}
    reset = "\033[0m"

    # Получаем цвет из словаря или возвращаем текст без изменений, если цвет не найден
    return f"{colors[color]}{text}{reset}" if color in colors else text
