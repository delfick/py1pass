import datetime
import typing as tp

import strcs
from attrs import define, field

D = tp.TypeVar("D", bound="Data")
Register: tp.TypeAlias = tp.Callable[[strcs.CreateRegister, object], D]

data_strcs_register = strcs.CreateRegister()
data_strcs_creator = data_strcs_register.make_decorator()


@data_strcs_creator(datetime.datetime)
def create_datetime(item: object, /) -> None | datetime.datetime:
    if isinstance(item, datetime.datetime):
        return item
    elif isinstance(item, str):
        return datetime.datetime.now()
        return datetime.datetime.fromisoformat(item)
    return None


@define
class Data:
    pass


@define
class Categories:
    categories: dict[str, Register] = field(init=False, factory=lambda: {})

    def register(self, category: str) -> tp.Callable[[type[D]], type[D]]:
        def decorator(kls: type[D]) -> type[D]:
            def transform(register: strcs.CreateRegister, item: object) -> D:
                return register.create(kls, item)

            self.categories[category] = transform
            return kls

        return decorator

    def __contains__(self, key: str | object) -> bool:
        return key in self.categories

    def __iter__(self) -> tp.Iterator[str]:
        return iter(self.categories)

    def __getitem__(self, key: str) -> Register:
        return self.categories[key]


@data_strcs_creator(Data)
def create_data(item: object, want: strcs.Type[Data], /) -> None | dict:
    if isinstance(item, list):
        if not all(isinstance(i, dict) and "id" in i for i in item):
            return None

        item = {i["id"]: i for i in item}

    if not isinstance(item, dict):
        return None

    return item


categories = Categories()
__all__ = ["categories", "Data", "data_strcs_register", "data_strcs_creator"]
