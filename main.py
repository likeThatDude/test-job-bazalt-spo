import asyncio
import json

from core.parse_data import async_version
from core.data_extractor import get_sorted_data


def main():
    branch1 = "p10"
    branch2 = "sisyphus"
    received_data = asyncio.run(async_version(branch1, branch2))
    result = get_sorted_data(received_data[0], received_data[1])



if __name__ == '__main__':
    main()
