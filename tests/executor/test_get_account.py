import json
import typing as tp

import pytest
import typer

from py1pass import accounts as accnts
from py1pass.tests import FakeCLI, OPConfigHelper


class TestGetAccount:
    def test_without_arguments_prints_accounts(
        self,
        capsys: pytest.CaptureFixture,
        entrypoint: tp.Callable[[int], tp.ContextManager[typer.Typer]],
        op_config_helper: OPConfigHelper,
        fakecli: FakeCLI,
    ):
        op_config_helper.config = {"latest_signin": "one"}
        fakecli.responds_to(
            ["accounts", "list", "--format=json", "--no-color"],
            [{"url": "one", "email": "two@three.com", "user_uuid": "four", "account_uuid": "five"}],
        )
        with entrypoint(0) as ep:
            ep(["current-account"])

        captured = capsys.readouterr()
        assert captured.out.strip() == repr(
            accnts.Account(url="one", email="two@three.com", user_uuid="four", account_uuid="five")
        )

    def test_with_different_config(
        self,
        capsys: pytest.CaptureFixture,
        entrypoint: tp.Callable[[int], tp.ContextManager[typer.Typer]],
        tmp_path_factory: pytest.TempPathFactory,
        op_config_helper: OPConfigHelper,
        fakecli: FakeCLI,
    ):
        op_config_helper.config = {"latest_signin": "one"}
        fakecli.responds_to(
            ["accounts", "list", "--format=json", "--no-color"],
            [
                {
                    "url": "one",
                    "email": "two@three.com",
                    "user_uuid": "four",
                    "account_uuid": "five",
                },
                {
                    "url": "six",
                    "email": "seven@eight.com",
                    "user_uuid": "nine",
                    "account_uuid": "ten",
                },
            ],
        )

        config = tmp_path_factory.mktemp("configs") / "config"
        with open(config, "w") as fle:
            json.dump({"latest_signin": "nine"}, fle)

        with entrypoint(0) as ep:
            ep(["--config-path", str(config), "current-account"])

        captured = capsys.readouterr()
        assert captured.out.strip() == repr(
            accnts.Account(url="six", email="seven@eight.com", user_uuid="nine", account_uuid="ten")
        )
