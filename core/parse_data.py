import aiohttp
import asyncio
import json
from pathlib import Path


async def get_packages_async(branch: str) -> list:
    url = f"https://rdb.altlinux.org/api/export/branch_binary_packages/{branch}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['packages']
            else:
                raise Exception(f"Failed to fetch data from {branch} HTTP status {response.status}")


async def async_version(branch1, branch2):
    tasks = [
        get_packages_async(branch1),
        get_packages_async(branch2)
    ]
    results = await asyncio.gather(*tasks)
    return results
