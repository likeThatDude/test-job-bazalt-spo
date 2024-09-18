import dataclasses


@dataclasses.dataclass()
class Package:
    """
    A data class representing a package with various attributes.

    Attributes:
        name (str): The name of the package.
        epoch (int): The epoch version of the package (used for version comparison).
        version (str): The version string of the package.
        release (str): The release version of the package.
        arch (str): The architecture for which the package is built (e.g., 'x86_64', 'arm').
        disttag (str): The distribution tag for the package (e.g., 'stable', 'testing').
        buildtime (int): The build timestamp of the package, typically in UNIX epoch format.
        source (str): The source package from which this binary package was built.
    """

    name: str
    epoch: int
    version: str
    release: str
    arch: str
    disttag: str
    buildtime: int
    source: str
