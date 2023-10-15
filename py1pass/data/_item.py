import datetime
import typing as tp

import strcs
from attrs import define

from py1pass import accounts as accnts

from .. import errors
from ._base import Data, categories, data_strcs_creator

T = tp.TypeVar("T", bound=Data)

VaultID: tp.TypeAlias = str


@define
class ItemVault:
    id: VaultID
    name: str


@define
class ItemUrl:
    label: str
    primary: bool
    href: str


@define
class Item(tp.Generic[T]):
    fields: T

    id: str
    title: str
    version: int
    vault: ItemVault
    category: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    urls: list[ItemUrl]
    lasted_edited_by: None | accnts.UserUUID = None


@data_strcs_creator(Item)
def create_item(
    item: object, want: strcs.Type[Item], /, _register: strcs.CreateRegister
) -> None | dict:
    if not isinstance(item, dict):
        return None

    if "fields" in item and "category" in item and item["category"] in categories:
        item["fields"] = categories[item["category"]](_register, item["fields"])
    elif "category" not in item:
        item["fields"] = _register.create(Data, item["fields"])
    elif "fields" not in item:
        item["fields"] = _register.create(Data, {})
    else:
        raise errors.UnregisteredCategory(want=item["category"], available=sorted(categories))

    return item
