import json
import typing as tp
from pathlib import Path

import pytest
from attrs import define, field


@define
class OPConfigHelper:
    location: Path
    xdg_config_home: Path

    _config: dict = field(init=False, factory=lambda: {})

    @property
    def config(self) -> dict:
        return self._config

    @config.setter
    def config(self, val: object) -> None:
        if not isinstance(val, dict):
            raise ValueError("Config must be a dictionary")
        self._config = val
        self.write()

    @classmethod
    def make_fixture(
        cls, *, name: str
    ) -> dict[str, tp.Callable[[pytest.TempPathFactory, pytest.MonkeyPatch], "OPConfigHelper"]]:
        @pytest.fixture(name=name)
        def op_config_helper(
            tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
        ) -> OPConfigHelper:
            xdg_config_home = tmp_path_factory.mktemp("xdg_config_home")
            monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config_home))
            instance = cls(
                xdg_config_home=xdg_config_home, location=xdg_config_home / ".op" / "config"
            )
            instance.write()
            return instance

        return {name: op_config_helper}

    def write(self) -> None:
        if not self.location.parent.exists():
            self.location.parent.mkdir(parents=True)

        with open(self.location, "w") as fle:
            json.dump(self.config, fle)
