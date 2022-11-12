import json
import os
import typing as tp
from itertools import chain
from pathlib import Path

from attrs import define

from ..errors import ConfigNotFound, InvalidConfigType, NoAccountFound
from ..op import OPCLI
from . import accounts as accnts
from ._register import config_strcs_register


class TConfig(tp.Protocol):
    op_cli: OPCLI
    location: None | Path


T = tp.TypeVar("T", bound=TConfig)


class ConfigMaker(tp.Generic[T]):
    def __init__(self, config_cls: type[T]):
        self.config_cls = config_cls

    def paths(self, base: Path) -> tp.Iterator[Path]:
        yield base / ".config" / "op" / "config"
        yield base / ".op" / "config"

    def find_config(self) -> None | Path:
        bases = [Path.home()]
        if "XDG_CONFIG_HOME" in os.environ:
            bases.append(Path(os.environ["XDG_CONFIG_HOME"]))

        for path in chain.from_iterable([self.paths(base) for base in bases]):
            if path.exists():
                return path

        return None

    def read_file(self, filepath: None | Path = None) -> tuple[None | Path, dict]:
        if filepath is None:
            filepath = self.find_config()

            if filepath is None:
                return None, {}

        if not filepath.exists():
            raise ConfigNotFound(tried=filepath)

        with open(filepath) as fle:
            ret = json.load(fle)
        if not isinstance(ret, dict):
            raise InvalidConfigType(got=repr(type(ret)))

        return filepath, ret

    def create(self, op: OPCLI, filepath: None | Path = None) -> T:
        location, content = self.read_file(filepath)
        content["op_cli"] = op
        content["location"] = location
        return config_strcs_register.create(self.config_cls, content)


@define
class OPConfig:
    @classmethod
    def create(
        cls, op: tp.Union[None, OPCLI, Path] = None, filepath: None | Path = None
    ) -> "OPConfig":
        from ..op import OPCLI

        op = OPCLI.create(op)
        return ConfigMaker(cls).create(op, filepath)

    op_cli: OPCLI
    location: None | Path

    latest_signin: accnts.UserUUID = ""
    system_auth_latest_signin: accnts.UserUUID = ""

    @property
    def accounts(self) -> list[accnts.Account]:
        return self.op_cli.accounts()

    def account(self, identifier: None | str = None) -> accnts.Account:
        accounts = self.accounts
        choices = [identifier, self.system_auth_latest_signin, self.latest_signin]

        if not any(choices):
            raise NoAccountFound(
                reason="No account passed in or latest signin information",
                want=" OR ".join([c for c in choices if c]),
                available=sorted([a.shorthand or a.user_uuid for a in accounts]),
            )

        for choice in choices:
            for account in accounts:
                if choice and account.matches(choice):
                    return account

        raise NoAccountFound(
            reason="No such account in configuration",
            want=" OR ".join([c for c in choices if c]),
            available=sorted([a.shorthand or a.user_uuid for a in accounts]),
        )


__all__ = ["OPConfig", "ConfigMaker"]
