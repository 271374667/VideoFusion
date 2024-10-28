from abc import ABC, abstractmethod
from enum import Enum


class PackageType(Enum):
    Pyinstaller = 0
    Nuitka = 1


class Packaged(ABC):
    @abstractmethod
    def package(self):
        pass


class PyinstallerPackaged(Packaged):
    def package(self):
        print("PyinstallerPackaged")


class NuitkaPackaged(Packaged):
    def package(self):
        print("NuitkaPackaged")


class PackagedFactory:
    @staticmethod
    def create_packaged(packaged_type: PackageType) -> Packaged:
        if packaged_type == PackageType.Pyinstaller:
            return PyinstallerPackaged()
        elif packaged_type == PackageType.Nuitka:
            return NuitkaPackaged()
        else:
            raise ValueError(f"Unknown packaged type {packaged_type}")


if __name__ == '__main__':
    pf = PackagedFactory()
    packaged = pf.create_packaged(PackageType.Pyinstaller)
    packaged.package()
