import json
import multiprocessing
import os
import re
from datetime import datetime
from itertools import zip_longest
from typing import Tuple


def split_version(version: str) -> list:
    return [int(part) if part.isdigit() else part for part in re.split(r'(\d+)', version) if part]


def compare_versions(version1: str, version2: str) -> bool:
    split1 = split_version(version1)
    split2 = split_version(version2)

    for part1, part2 in zip_longest(split1, split2, fillvalue=''):
        if isinstance(part1, int) and isinstance(part2, int):
            if part1 > part2:
                return True
            else:
                return False
        elif isinstance(part1, int) and isinstance(part2, str):
            return True
        elif isinstance(part1, str) and isinstance(part2, int):
            return False
        elif isinstance(part1, str) and isinstance(part2, str):
            if part1 > part2:
                return True
            else:
                return False
    return False


def generate_package_set(dict_list):
    package_dict = {}
    for item in dict_list:
        key = (item['name'], item['arch'])
        if key not in package_dict:
            package_dict[key] = {
                'epoch': item['epoch'],
                'version': item['version'],
                'release': item['release'],
            }
    return package_dict


def worker(func, *args):
    return func(*args)


def key_func_name(pkg):
    return (pkg.name, pkg.arch)


def check_difficult(dict_list1: list, dict_list2: list) -> Tuple[bool, int]:
    length_sum = len(dict_list1) + len(dict_list2)
    num_cores = multiprocessing.cpu_count()
    if length_sum > 1_600_000:
        if num_cores == 2:
            return (True, 2) if length_sum >= 2_100_000 else (False, 0)
        elif num_cores > 2:
            return True, 3
    return False, 0


def get_current_user():
    try:
        user = os.getenv('USER') or os.getenv('USERNAME') or os.getlogin()
        if not user:
            raise ValueError("Failed to retrieve username")
        return user
    except Exception:
        return "Unknown user"


def get_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime('%H:%M:%S %d-%m-%Y')
    return formatted_time


def create_response(data):
    result = {
        'user': get_current_user(),
        'time': get_time(),
        'result': {
            'first_package': data[0],
            'second_package': data[1],
            'newer_versions_first_package': data[2],
        }
    }
    return result
