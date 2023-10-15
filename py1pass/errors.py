from pathlib import Path

from attrs import define


@define
class Py1PassError(Exception):
    ...


@define
class ConfigNotFound(Exception):
    tried: Path


@define
class InvalidConfigType(Exception):
    got: str

    def __str__(self):
        return f"Configuration was not a dictionary, got instead {self.got}"


@define
class NoAccountFound(Exception):
    reason: str
    want: None | str
    available: None | list[str]

    def __str__(self) -> str:
        out: list[str] = []

        if self.available is None:
            out.append("1password is providing 1password-cli with accounts but none were found")
        elif not self.available:
            out.append("No accounts appear to be registered with 1password-cli")

        out.append(self.reason)
        if self.want:
            out.append(f"Wanted {self.want}")
        return "\n".join(out)


@define
class No1PasswordCLI(Exception):
    def __str__(self) -> str:
        return "Can't find the 1password-cli app on your command line, please install that first"


@define
class UnregisteredCategory(Exception):
    want: str
    available: list[str]

    def __str__(self) -> str:
        return f"Unknown category {self.want} requested, available: {self.available}"


del define
del Path
