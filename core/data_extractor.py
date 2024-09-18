import json
from multiprocessing import Pool

from typing import Callable

from core.classes import Package
from core.utils import generate_package_set, compare_versions, check_difficult, worker, key_func_name, \
    create_response


def unic_first_list(dict_list1: dict, dict_list2: dict, key_func: Callable[['Package'], tuple]) -> list:
    package_set = {key_func(Package(**d)) for d in dict_list2}
    data = [d for d in dict_list1 if key_func(Package(**d)) not in package_set]
    return data


def unic_second_list(dict_list1: dict, dict_list2: dict, key_func: Callable[['Package'], tuple]) -> list:
    package_set = {key_func(Package(**d)) for d in dict_list1}
    data = [d for d in dict_list2 if key_func(Package(**d)) not in package_set]
    return data


def be_into_to_lists(dict_list1: dict, dict_list2: dict) -> list:
    package_set = generate_package_set(dict_list2)
    data = [
        d for d in dict_list1
        if (d['name'], d['arch']) in package_set
           and d['epoch'] >= package_set[(d['name'], d['arch'])]['epoch']
           and compare_versions(d['version'], package_set[(d['name'], d['arch'])]['version'])
    ]
    return data


def multiprocess_variant(processes_count: int, first_package, second_package):
    with Pool(processes=processes_count) as pool:
        results = pool.starmap(
            worker,
            [
                (unic_first_list, first_package, second_package, key_func_name),
                (unic_second_list, first_package, second_package, key_func_name),
                (be_into_to_lists, second_package, first_package)
            ]
        )
    return results


def sync_variant(first_package, second_package):
    results = [
        unic_first_list(first_package, second_package, lambda pkg: (pkg.name, pkg.arch)),
        unic_second_list(first_package, second_package, lambda pkg: (pkg.name, pkg.arch)),
        be_into_to_lists(second_package, first_package)
    ]
    return results


def get_sorted_data(first_package: list, second_package: list) -> json:
    execution_options = check_difficult(first_package, second_package)
    if execution_options[0]:
        sorted_data = multiprocess_variant(execution_options[1], first_package, second_package)
    else:
        sorted_data = sync_variant(first_package, second_package)

    return create_response(sorted_data)
