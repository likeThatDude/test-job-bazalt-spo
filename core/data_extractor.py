import json
import re
from pathlib import Path
import dataclasses
import time as t
from multiprocessing import Pool

p10_data = Path(__file__).parent.parent / 'data/p10_packages.json'
sisyphus_data = Path(__file__).parent.parent / 'data/sisyphus_packages.json'


def create_variables(path: Path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


# p10_json = create_variables(p10_data)
# sisyphus_json = create_variables(sisyphus_data)
p10_json = create_variables(p10_data)['packages'] * 10
sisyphus_json = create_variables(sisyphus_data)['packages'] * 10


# print(len(p10_json), len(sisyphus_json))


@dataclasses.dataclass(frozen=True)
class Package:
    name: str
    epoch: int
    version: str
    release: str
    arch: str
    disttag: str
    buildtime: int
    source: str


def unic_first_list(dict_list1, dict_list2):
    package_set = {Package(**d) for d in dict_list2}
    data = [d for d in dict_list1 if Package(**d) not in package_set]
    print(f'Данные в compare_lists: {len(data)}')
    return data


def unic_second_list(dict_list1, dict_list2):
    package_set = {Package(**d) for d in dict_list1}
    data = [d for d in dict_list2 if Package(**d) not in package_set]
    print(f'Данные в compare_lists: {len(data)}')
    return data


def worker(func, *args):
    return func(*args)


def main():
    start_time = t.time()
    unic_first_list(p10_json, sisyphus_json)
    # compare_lists(p10_json['packages'], sisyphus_json['packages'])
    end_time = t.time()
    execution_time = end_time - start_time
    print(f"Время выполнения функции unic_first_list: {execution_time:.4f} секунд")

    start_time = t.time()
    unic_second_list(p10_json, sisyphus_json)
    # compare_lists(p10_json['packages'], sisyphus_json['packages'])
    end_time = t.time()
    execution_time = end_time - start_time
    print(f"Время выполнения функции unic_second_list: {execution_time:.4f} секунд")

    start_time = t.time()
    with Pool(processes=2) as pool:
        results = pool.starmap(
            worker,
            [
                (unic_first_list, p10_json, sisyphus_json),
                (unic_second_list, p10_json, sisyphus_json)
            ]
        )
    end_time = t.time()
    execution_time = end_time - start_time
    print(f"Время выполнения всех процессов: {execution_time:.4f} секунд")


if __name__ == '__main__':
    main()
