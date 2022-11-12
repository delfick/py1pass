import json
from pathlib import Path

import pytest
from attrs import define

from py1pass import errors
from py1pass.config import ConfigMaker
from py1pass.op import OPCLI
from py1pass.tests import DisabledOPCLI


@define
class Config:
    op_cli: OPCLI
    location: None | Path
    one: int


class TestConfigMaker:
    def test_can_find_existing_filepath_in_home(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempdirFactory
    ):
        home = Path(tmp_path_factory.mktemp("home"))
        xdg_config_home = Path(tmp_path_factory.mktemp("xdg_config_home"))
        config = home / ".config" / "op" / "config"
        config.parent.mkdir(parents=True)

        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config_home))
        maker = ConfigMaker(Config)
        assert maker.find_config() is None

        with open(config, "w") as fle:
            json.dump({"one": 1}, fle)

        assert maker.find_config() == config
        assert maker.read_file() == (config, {"one": 1})

        op_cli = DisabledOPCLI()
        cfg = maker.create(op_cli)
        assert isinstance(cfg, Config)
        assert cfg.one == 1
        assert cfg.op_cli is op_cli
        assert cfg.location == config

    def test_can_find_existing_filepath_in_xdg_config_home(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempdirFactory
    ):
        home = Path(tmp_path_factory.mktemp("home"))
        xdg_config_home = Path(tmp_path_factory.mktemp("xdg_config_home"))

        config = xdg_config_home / ".op" / "config"
        config.parent.mkdir(parents=True)

        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config_home))

        maker = ConfigMaker(Config)
        assert maker.find_config() is None

        with open(config, "w") as fle:
            json.dump({"one": 2}, fle)

        assert maker.find_config() == config
        assert maker.read_file() == (config, {"one": 2})

        op_cli = DisabledOPCLI()
        cfg = maker.create(op_cli)
        assert isinstance(cfg, Config)
        assert cfg.one == 2
        assert cfg.op_cli is op_cli
        assert cfg.location == config

    def test_can_find_existing_filepath_passed_in(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempdirFactory
    ):
        home = Path(tmp_path_factory.mktemp("home"))
        for_test = Path(tmp_path_factory.mktemp("for_test"))
        xdg_config_home = Path(tmp_path_factory.mktemp("xdg_config_home"))

        configxdg = xdg_config_home / ".op" / "config"
        configxdg.parent.mkdir(parents=True)
        confighome = xdg_config_home / ".config" / "op" / "config"
        confighome.parent.mkdir(parents=True)

        configfortest = for_test / "config"

        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config_home))

        with open(confighome, "w") as fle:
            json.dump({"one": 1}, fle)

        with open(configxdg, "w") as fle:
            json.dump({"one": 2}, fle)

        maker = ConfigMaker(Config)
        with pytest.raises(errors.ConfigNotFound):
            maker.read_file(configfortest)

        with open(configfortest, "w") as fle:
            json.dump({"one": 3}, fle)

        assert maker.read_file(configfortest) == (configfortest, {"one": 3})

        op_cli = DisabledOPCLI()
        cfg = maker.create(op_cli, configfortest)
        assert isinstance(cfg, Config)
        assert cfg.one == 3
        assert cfg.op_cli is op_cli
        assert cfg.location == configfortest

    def test_complains_if_not_a_dictionary(self, tmp_path_factory: pytest.TempdirFactory):
        for_test = Path(tmp_path_factory.mktemp("for_test"))
        configfortest = for_test / "config"

        with open(configfortest, "w") as fle:
            json.dump([], fle)

        maker = ConfigMaker(Config)

        with pytest.raises(
            errors.InvalidConfigType,
            match=f"Configuration was not a dictionary, got instead {list}",
        ):
            maker.read_file(configfortest)
