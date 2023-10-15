import shutil
import typing as tp
from unittest import mock

import pytest
import typer

from py1pass import accounts as accnts
from py1pass.tests import FakeCLI, OPConfigHelper

locals().update(FakeCLI.make_fixture(name="other_fakecli"))


class TestNoArgs:
    def test_prints_accounts(
        self,
        capsys: pytest.CaptureFixture,
        entrypoint: tp.Callable[[int], tp.ContextManager[typer.Typer]],
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
        with entrypoint(0) as ep:
            ep([])

        captured = capsys.readouterr()
        assert captured.out.strip() == "{0}\n{1}".format(
            repr(
                accnts.Account(
                    url="one", email="two@three.com", user_uuid="four", account_uuid="five"
                )
            ),
            repr(
                accnts.Account(
                    url="six", email="seven@eight.com", user_uuid="nine", account_uuid="ten"
                )
            ),
        )

    def test_with_different_op_path(
        self,
        capsys: pytest.CaptureFixture,
        entrypoint: tp.Callable[[int], tp.ContextManager[typer.Typer]],
        op_config_helper: OPConfigHelper,
        fakecli: FakeCLI,
        other_fakecli: FakeCLI,
    ):
        op_config_helper.config = {"latest_signin": "one"}
        other_fakecli.responds_to(
            ["accounts", "list", "--format=json", "--no-color"],
            [
                {
                    "url": "twenty",
                    "email": "two@three.com",
                    "user_uuid": "four",
                    "account_uuid": "five",
                },
                {
                    "url": "thirty",
                    "email": "seven@eight.com",
                    "user_uuid": "nine",
                    "account_uuid": "ten",
                },
            ],
        )
        with entrypoint(0) as ep:
            assert shutil.which("op") == str(fakecli.location)
            ep(["--op-path", str(other_fakecli.location)])

        captured = capsys.readouterr()
        assert captured.out.strip() == "{0}\n{1}".format(
            repr(
                accnts.Account(
                    url="twenty", email="two@three.com", user_uuid="four", account_uuid="five"
                )
            ),
            repr(
                accnts.Account(
                    url="thirty", email="seven@eight.com", user_uuid="nine", account_uuid="ten"
                )
            ),
        )

        fakecli.assert_called(mock.ANY, count=0)
        other_fakecli.assert_called(mock.ANY, count=1)
