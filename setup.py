from setuptools import setup, find_packages

setup(
    name='test_task_bazalt_spo',
    version='0.1',
    py_modules=['main'],
    packages=find_packages(),
    install_requires=[
        "aiohappyeyeballs==2.4.0",
        "aiohttp==3.10.5",
        "aiosignal==1.3.1",
        "attrs==24.2.0",
        "certifi==2024.8.30",
        "charset-normalizer==3.3.2",
        "click==8.1.7",
        "frozenlist==1.4.1",
        "idna==3.10",
        "multidict==6.1.0",
        "mypy-extensions==1.0.0",
        "packaging==24.1",
        "pathspec==0.12.1",
        "platformdirs==4.3.6",
        "requests==2.32.3",
        "setuptools==75.1.0",
        "urllib3==2.2.3",
        "yarl==1.11.1"
    ],
    entry_points={
        'console_scripts': [
            'compare_packages=main:main',
        ],
    },
    description='A CLI tool for comparing packages',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ivan Gorbatenko',
    author_email='1995van95@gmail.com',
    url='https://github.com/likeThatDude/test-job-bazalt-spo',
    license='MIT',
)
