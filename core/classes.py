import dataclasses


@dataclasses.dataclass()
class Package:
    name: str
    epoch: int
    version: str
    release: str
    arch: str
    disttag: str
    buildtime: int
    source: str
