from pathlib import Path

import strcs

config_strcs_register = strcs.CreateRegister()
config_strcs_creator = config_strcs_register.make_decorator()


@config_strcs_creator(Path)
def convert_path(item: object, /) -> None | Path:
    if isinstance(item, (str, Path)):
        return Path(item)

    return None


__all__ = ["config_strcs_register", "config_strcs_creator"]
