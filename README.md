## Test task for ООО "БАЗАЛЬТ СПО" ##
## Description

>We have a public REST API for our database:  
https://rdb.altlinux.org/api/  
It has a method  
/export/branch_binary_packages/{branch}  
We can use sisyphus and p10 as a branch  
We need to make a python module and a cli linux utility (using this python module) that:  
>1) retrieves lists of binary packages of sisyphus and p10 branches  
>2) does a comparison of the obtained lists of packages and outputs JSON (structure to be invented), which will display:  
>- all packages that are in p10 but not in sisyphus  
>- all packages that are in sisyphus but not in p10  
>- all packages whose version-release is larger in sisyphus than in p10.   
>This should be done for each of the architectures supported by the branch (arch field in the answer).  
>The development process should be organized as a git repository with a history of all changes  
>from the very first stage (without rewriting commits) and uploaded, for example, on github  
>The utility must run under Linux operating system (it will be tested on ALT Linux, version 10),  
>It must have a README in English with instructions on how to run it.  
>Compare version-release according to rpm package versioning rules.
>
>The site working on the basis of this API is https://packages.altlinux.org/ru/sisyphus/.


## Programming Language
- Python
## Libraries and tools
- setuptools - library for building an application into a Python package.
- argparse - for parsing command line arguments in Python.
- asyncio - for asynchronously fetching JSON data from an external API.
- aiohttp - for creating an asynchronous HTTP client
- multiprocessing - for creating parallel processes and executing tasks in several processor cores in Python.  
In my case it is used if a large amount of data needs to be sorted. And if the hardware allows it.
- json - for working with data in JSON format: their serialization and deserialization.
- os - needed to get the user name, which is included in the final JSON response.
- re - used for convenient separation of package versions.
- sys - for outputting the response to stdout.
- dataclasses - to create a class, with which the main application logic happens.
- pathlib - for working with paths in the system.
- typing - for adding type annotations and static type checking.

## Principle of operation
### ***Parsing data***
Data parsing is done asynchronously, since it is I/O-Bound this method was chosen.  
Since we have a specific URL to send the request to, the application does not assume its replacement.  
The request goes to: https://rdb.altlinux.org/api/export/branch_binary_packages/{branch}, where {branch} is the branch name.  
After checking if the data is successfully received, the necessary packages are retrieved using the “packages” key and passed for further work with them.  
In case of an error, an error is sent to the console with the name of the branch in which it occurred and the status code of the error.  

### ***Data Processing***
The handler receives two lists of packages and determines the number of packages. If the total number of packages is greater than 1,600,000, the application  
will check the hardware parameters to try to run the calculations in multithreaded mode.  
How the check happens:
- The handler receives two lists of packages, it determines the number of packages.
  - If the total number of packages is less than 1.600.000, the sorting will be done in normal synchronous mode.  
  - If the total number of packages is more than 1,600,000, it receives information about the number of cores of the processor on which the application is running.
  - If the system has 3 or more cores, the sorting will be performed in three processes, which significantly increases the sorting execution time.
  - If the system has 2 cores, it checks that the total number of packages is more than 2,100,000, if it is less than that, the synchronous sorting method works faster.  
    synchronous sorting method, if there are more of them, then the sorting will be done in two processes.
  - Otherwise the execution will be done in normal synchronous mode.
- After selecting the sorting mode, the data is passed to the main logic.
- The function for working with data is called.
  - It creates a tuple (for quick access by hash, the package with which the comparison will be performed), based on the  
    keys by which sorting will be performed.
  - packages that will be compared, are processed to obtain the necessary keys and compare them with the 2nd package.
  - The resulting list of packages is given for further processing (as a result, we get two lists of packages with unique data).
- The first list of packages is searched for newer version-release packages.
  - Packages are processed, a dictionary is created with a key like tuple(name, arch), and values (epoch, version, release).  
    after which the dictionary is given for further processing.
  - Then sorting is performed.
    - We take a list of packages in which we need to find newer versions.
    - We loop through the list, form tuple(name, arch) and look for it in the dictionary we received earlier.
    - Then the comparison follows the following scenario
      - Compare epoch
      - Compare version
      - Compare release
      - Add the newer ones from the first list to the list.
      - give the finished list
- The finished results are passed to form the response
  - JSON is created
  - Depending on the selected options, the response is written to a file, console

### ***Setup***

1. Copy the repository:
```bash
   git clone https://github.com/likeThatDude/test-job-bazalt-spo.git
```
```bash
   git clone git@github.com:likeThatDude/test-job-bazalt-spo.git
```
2. While in the folder with [setup.py](setup.py)
```bash
   pip install .
```
3. Execute the command
```bash
   compare_packages --branch1 p10 --branch2 sisyphus
```
- Additional properties 
  - --branch1 first branch.
  - --branch2 second branch where newer versions of packages will be searched.
  - --write folder where the .json file will be saved, if the flag does not apply the file will not be written.
  - --console to output the result to the console, if the flag is not applied there will be no output to the console.

# Developer
**Gorbatenko Ivan**

**GitHub**: https://github.com/likeThatDude  

**Email**: 1995van95@gmail.com
