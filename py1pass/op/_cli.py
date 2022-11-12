import json
import shutil
import typing as tp
from pathlib import Path

import strcs
from attrs import define, field
from sh import Command, RunningCommand

from ..errors import No1PasswordCLI

if tp.TYPE_CHECKING:
    from py1pass.config.accounts import Account

T = tp.TypeVar("T")

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

    def accounts(self) -> list["Account"]:
        from py1pass.config.accounts import Account

        return self._load(list[Account], self.sh.accounts.list(format="json", no_color=True))

    def _load(self, typ: type[T], output: RunningCommand) -> T:
        out = str(output).strip()
        if not out:
            dflt: object = {}
            if isinstance(typ, list):
                dflt = []
            return op_strcs_register.create(typ, dflt)
        else:
            return op_strcs_register.create(typ, json.loads(out))
