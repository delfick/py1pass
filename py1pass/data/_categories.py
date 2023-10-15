from attrs import define

from . import op_type
from ._base import Data, categories


@categories.register("LOGIN")
@define
class Login(Data):
    username: op_type.Username
    password: op_type.Password
    notesPlain: op_type.Notes
