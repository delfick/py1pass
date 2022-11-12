from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def do_not_look_at_users_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempdirFactory
):
    home = Path(tmp_path_factory.mktemp("home"))
    xdg_config_home = Path(tmp_path_factory.mktemp("xdg_config_home"))

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_config_home))
