import json
import sys
from multiprocessing import Pool
from typing import Callable

from core.classes import Package
from core.utils import (
    check_difficult,
    colorize_text,
    compare_versions_release,
    create_response,
    generate_package_set,
    key_func_name,
    worker,
)


def search_unic_packages(data_list1: list, data_list2: list, key_func: Callable[["Package"], tuple]) -> list:
    """
    Filters items from the first list that are not in the second list, based on the key function.

    Args:
        data_list1 (list): The first list of dictionaries representing packages.
        data_list2 (list): The second list of dictionaries representing packages.
        key_func (Callable[["Package"], tuple]): A function to extract the key from a package.

    Returns:
        list: A list of packages that are present in the first list but not present in the second list.

    Examples:
        unic_first_list(list1, list2, lambda pkg: (pkg.name, pkg.arch))
        [{'name': 'pkg1', 'arch': 'x86_64'}, {'name': 'pkg2', 'arch': 'arm'}]
    """
    package_set = {key_func(Package(**d)) for d in data_list2}
    data = [d for d in data_list1 if key_func(Package(**d)) not in package_set]
    return data


def be_into_to_lists(data_list1: list, data_list2: list) -> list:
    """
    Filters items from the first list that are also present in the second list and compares their versions.

    Args:
        data_list1 (list): The first list of dictionaries representing packages.
        data_list2 (list): The second list of dictionaries representing packages.

    Returns:
        list: A list of packages that are in both lists and meet the version comparison criteria.

    Examples:
        be_into_to_lists(list1, list2)
        [{'name': 'pkg1', 'arch': 'x86_64', 'version': '2.0'}]
    """
    package_set = generate_package_set(data_list2)
    data = [
        d
        for d in data_list1
        if (d["name"], d["arch"]) in package_set
           and d["epoch"] >= package_set[(d["name"], d["arch"])]["epoch"]
           and compare_versions_release(d["version"], package_set[(d["name"], d["arch"])]["version"])
           and compare_versions_release(d["release"], package_set[(d["name"], d["arch"])]["release"])
    ]
    return data


def multiprocess_variant(processes_count: int, first_package: list, second_package: list) -> list:
    """
    Executes comparison functions in parallel using multiple processes.

    Args:
        processes_count (int): The number of processes to use.
        first_package (list): The first list of packages.
        second_package (list): The second list of packages.

    Returns:
        list: A list of results from the parallel execution of comparison functions.

    Examples:
        multiprocess_variant(4, list1, list2)
        [[unique_in_first], [unique_in_second], [common_and_newer_versions]]
    """
    with Pool(processes=processes_count) as pool:
        results = pool.starmap(
            worker,
            [
                (
                    search_unic_packages,
                    first_package,
                    second_package,
                    key_func_name,
                ),
                (
                    search_unic_packages,
                    second_package,
                    first_package,
                    key_func_name,
                ),
                (be_into_to_lists, second_package, first_package),
            ],
        )
    return results


def sync_variant(first_package: list, second_package: list) -> list:
    """
    Executes comparison functions sequentially (synchronously).

    Args:
        first_package (list): The first list of packages.
        second_package (list): The second list of packages.

    Returns:
        list: A list of results from the synchronous execution of comparison functions.

    Examples:
        sync_variant(list1, list2)
        [[unique_in_first], [unique_in_second], [common_and_newer_versions]]
    """
    results = [
        search_unic_packages(first_package, second_package, lambda pkg: (pkg.name, pkg.arch)),
        search_unic_packages(second_package, first_package, lambda pkg: (pkg.name, pkg.arch)),
        be_into_to_lists(second_package, first_package),
    ]
    return results


def get_sorted_data(first_package: list, second_package: list) -> json:
    """
    Determines whether to use parallel or sequential processing based on data size and system resources,
    then processes package data and returns the result.

    Args:
        first_package (list): The first list of packages.
        second_package (list): The second list of packages.

    Returns:
        json: A JSON-formatted response containing the results of the comparison.

    Examples:
        get_sorted_data(list1, list2)
        {
            'user': 'john_doe',
            'time': '14:30:15 18-09-2024',
            'result': {
                'first_package': [{'name': 'pkg1', 'arch': 'x86_64', ...}],
                'second_package': [{'name': 'pkg2', 'arch': 'arm', ...}],
                'newer_versions_first_package': [{'name': 'pkg3', 'arch': 'x86_64', ...}]
            }
        }
    """
    execution_options = check_difficult(first_package, second_package)
    if execution_options[0]:
        sorted_data = multiprocess_variant(execution_options[1], first_package, second_package)
    else:
        sorted_data = sync_variant(first_package, second_package)

    sys.stdout.write(
        f"\tNumber of packets found for the first branch: "
        f"{colorize_text('red', str(len(sorted_data[0])))}"
        f"\n\tNumber of packets found for the second branch: "
        f"{colorize_text('red', str(len(sorted_data[1])))}\n "
        f"\tAll packages whose version-release is larger in the second branch: "
        f"{colorize_text('red', str(len(sorted_data[2])))}\n"
    )
    return create_response(sorted_data)
