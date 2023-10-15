import json
import shutil
import typing as tp
from pathlib import Path

import strcs
from attrs import define, field
from sh import Command, RunningCommand

from py1pass.accounts import Account, AccountUUID

from ..data import Data, Item, VaultID, data_strcs_register
from ..errors import No1PasswordCLI

T = tp.TypeVar("T")
D = tp.TypeVar("D", bound=Data)

op_strcs_register = strcs.CreateRegister()
op_strcs_creator = op_strcs_register.make_decorator()


@define
class OPCLI:
    command: Path

    _sh: Command = field(init=False)
    _disabled: bool = field(init=False, default=False)

    @classmethod
    def create(cls, op: tp.Union[None, "OPCLI", Path] = None) -> "OPCLI":
        if isinstance(op, OPCLI):
            return op

        if op is None:
            found = shutil.which("op")
            if not found:
                raise No1PasswordCLI()
            op = Path(found)

        return cls(command=op)

    def __attrs_post_init__(self):
        if not self._disabled:
            self._sh = Command(self.command)

    @property
    def sh(self) -> Command:
        if self._disabled:
            raise RuntimeError("This OPCLI is disabled")
        return self._sh

    def accounts(self) -> list[Account]:
        return self._load(list[Account], self.sh.accounts.list(format="json", no_color=True))

    def get_item(self, typ: type[Item[D]], item: str, vault: VaultID, account: AccountUUID):
        return self._load(
            typ,
            self.sh.item.get(item, vault=vault, account=account, format="json", no_color=True),
            register=data_strcs_register,
        )

    def _load(
        self,
        typ: type[T],
        output: RunningCommand,
        register: strcs.CreateRegister = op_strcs_register,
    ) -> T:
        out = str(output).strip()
        if not out:
            dflt: object = {}
            if isinstance(typ, list):
                dflt = []
            return register.create(typ, dflt)
        else:
            return register.create(typ, json.loads(out))
