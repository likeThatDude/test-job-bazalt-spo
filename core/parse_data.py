import asyncio

import aiohttp


async def get_packages_async(branch: str) -> list:
    """
    Asynchronously fetches package data from a specified branch of the ALT Linux repository.

    Args:
        branch (str): The branch name to fetch package data from.

    Returns:
        list: A list of packages from the specified branch.

    Raises:
        Exception: If the HTTP request fails or the response status is not 200.

    Examples:
        asyncio.run(get_packages_async('branch_name'))
        [{'name': 'package1', 'version': '1.0'}, {'name': 'package2', 'version': '2.0'}]
    """
    url = f"https://rdb.altlinux.org/api/export/branch_binary_packages/{branch}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["packages"]
            else:
                raise Exception(f"Failed to fetch data from -> {branch} <- branch. HTTP status {response.status}")


async def async_version(branch1: str, branch2: str) -> list:
    """
    Asynchronously fetches package data from two specified branches and returns the results.

    Args:
        branch1 (str): The first branch name.
        branch2 (str): The second branch name.

    Returns:
        list: A list containing the package data from both branches. The first element is the data from `branch1`,
              and the second element is the data from `branch2`.

    Examples:
        asyncio.run(async_version('branch1_name', 'branch2_name'))
        [
            [{'name': 'package1', 'version': '1.0'}, {'name': 'package2', 'version': '2.0'}],
            [{'name': 'package3', 'version': '1.5'}, {'name': 'package4', 'version': '2.5'}]
        ]
    """
    tasks = [get_packages_async(branch1), get_packages_async(branch2)]
    results = await asyncio.gather(*tasks)
    return results
