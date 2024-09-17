import aiohttp
import asyncio
import json
from pathlib import Path


async def get_packages_async(branch: str, file_path: Path):
    url = f"https://rdb.altlinux.org/api/export/branch_binary_packages/{branch}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                # Записываю файлы в файл для того чтобы не делать постоянно запросы на апи при разработке,
                # Позже этого не будет
                with open(file_path, 'w') as file:
                    json.dump(data, file, indent=4)

                print(f"Data for branch '{branch}' saved to {file_path}")
            else:
                raise Exception(f"Failed to fetch data from {branch}")


async def async_version():
    branch1 = "p10"
    branch2 = "sisyphus"

    output_dir = Path('../data')
    output_dir.mkdir(exist_ok=True)

    file_path1 = output_dir / f"{branch1}_packages.json"
    file_path2 = output_dir / f"{branch2}_packages.json"

    tasks = [
        get_packages_async(branch1, file_path1),
        get_packages_async(branch2, file_path2)
    ]

    # Параллельное выполнение асинхронных задач
    await asyncio.gather(*tasks)
