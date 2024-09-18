import json
import multiprocessing
import os
import re
import time
from multiprocessing import Pool
from pathlib import Path
import dataclasses
from typing import Callable, Tuple
from itertools import zip_longest

p10_data = Path(__file__).parent.parent / 'data/p10_packages.json'
sisyphus_data = Path(__file__).parent.parent / 'data/sisyphus_packages.json'


def create_variables(path: Path) -> dict:
    with open(path, 'r') as f:
        data = json.load(f)
    return data


p10_json = create_variables(p10_data)['packages']
sisyphus_json = create_variables(sisyphus_data)['packages']
print(len(p10_json) + len(sisyphus_json))


@dataclasses.dataclass()
class Package:
    name: str
    epoch: int
    version: str
    release: str
    arch: str
    disttag: str
    buildtime: int
    source: str


def unic_first_list(dict_list1: dict, dict_list2: dict, key_func: Callable[['Package'], tuple]) -> list:
    package_set = {key_func(Package(**d)) for d in dict_list2}
    data = [d for d in dict_list1 if key_func(Package(**d)) not in package_set]
    return data


def unic_second_list(dict_list1: dict, dict_list2: dict, key_func: Callable[['Package'], tuple]) -> list:
    package_set = {key_func(Package(**d)) for d in dict_list1}
    data = [d for d in dict_list2 if key_func(Package(**d)) not in package_set]
    return data


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
        else:
            'ВНИМАНИЕ ПОВТОР !'
    return package_dict


def be_into_to_lists(dict_list1: dict, dict_list2: dict) -> list:
    package_set = generate_package_set(dict_list2)
    data = [
        d for d in dict_list1
        if (d['name'], d['arch']) in package_set
           and d['epoch'] >= package_set[(d['name'], d['arch'])]['epoch']
           and compare_versions(d['version'], package_set[(d['name'], d['arch'])]['version'])
    ]
    return data


def worker(func, *args):
    return func(*args)


def key_func_name(pkg):
    return (pkg.name, pkg.arch)


def check_difficult(dict_list1: dict, dict_list2: dict) -> Tuple[bool, int]:
    length_sum = len(dict_list1) + len(dict_list2)
    num_cores = multiprocessing.cpu_count()
    if length_sum > 1_600_000:
        if num_cores == 2:
            return (True, 2) if length_sum >= 2_100_000 else (False, 0)
        elif num_cores > 2:
            return True, 3
    return False, 0


def main():
    execution_options = check_difficult(p10_json, sisyphus_json)

    if execution_options[0]:
        with Pool(processes=execution_options[1]) as pool:
            results = pool.starmap(
                worker,
                [
                    (unic_first_list, p10_json, sisyphus_json, key_func_name),
                    (unic_second_list, p10_json, sisyphus_json, key_func_name),
                    (be_into_to_lists, sisyphus_json, p10_json)
                ]
            )
        return results
    else:
        return [
            unic_first_list(p10_json, sisyphus_json, lambda pkg: (pkg.name, pkg.arch)),
            unic_second_list(p10_json, sisyphus_json, lambda pkg: (pkg.name, pkg.arch)),
            be_into_to_lists(sisyphus_json, p10_json)
        ]


if __name__ == '__main__':
    main()
