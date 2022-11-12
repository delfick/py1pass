import pytest

from py1pass import errors
from py1pass.config import OPConfig
from py1pass.config import accounts as accnts
from py1pass.tests import DisabledOPCLI, FakeCLI, OPConfigHelper

locals().update(
    **FakeCLI.make_fixture(name="fakecli"), **OPConfigHelper.make_fixture(name="op_config_helper")
)


class TestOPConfig:
    def test_can_be_created(self, fakecli: FakeCLI, op_config_helper: OPConfigHelper):
        fakecli.put_onto_path()
        op_config_helper.config = {"latest_signin": "one"}
        created = OPConfig.create()
        assert created.op_cli.command == fakecli.location
        assert created.location == op_config_helper.location
        assert created.latest_signin == "one"
        assert created.system_auth_latest_signin == ""

    def test_can_get_all_accounts(self, op_config_helper: OPConfigHelper):
        accounts = [
            accnts.Account(account_uuid="one", url="two", email="three@four.com", user_uuid="five"),
            accnts.Account(
                account_uuid="six", url="seven", email="eight@nine.com", user_uuid="ten"
            ),
        ]

        class CLI(DisabledOPCLI):
            def accounts(self) -> list[accnts.Account]:
                return accounts

        created = OPConfig.create(CLI())
        assert created.accounts is accounts

    def test_can_get_current_account(self, op_config_helper: OPConfigHelper):
        accounts = [
            accnts.Account(account_uuid="one", url="two", email="three@four.com", user_uuid="five"),
            accnts.Account(
                account_uuid="six", url="seven", email="eight@nine.com", user_uuid="ten"
            ),
        ]

        class CLI(DisabledOPCLI):
            def accounts(self) -> list[accnts.Account]:
                return accounts

        op_config_helper.config = {"latest_signin": "one"}
        created = OPConfig.create(CLI())
        assert created.account() is accounts[0]
        assert created.account("six") is accounts[1]
        assert created.account("five") is accounts[0]

        op_config_helper.config = {"system_auth_latest_signin": "seven"}
        created = OPConfig.create(CLI())
        assert created.account() is accounts[1]
        assert created.account("six") is accounts[1]
        assert created.account("five") is accounts[0]

    def test_fails_if_cant_find_an_account(self, op_config_helper: OPConfigHelper):
        accounts = [
            accnts.Account(account_uuid="one", url="two", email="three@four.com", user_uuid="five"),
            accnts.Account(
                account_uuid="six", url="seven", email="eight@nine.com", user_uuid="ten"
            ),
        ]

        class CLI(DisabledOPCLI):
            def accounts(self) -> list[accnts.Account]:
                return accounts

        op_config_helper.config = {}
        created = OPConfig.create(CLI())

        with pytest.raises(
            errors.NoAccountFound, match="No account passed in or latest signin information"
        ):
            created.account()

        with pytest.raises(errors.NoAccountFound, match="No such account in configuration"):
            created.account("twenty")

        op_config_helper.config = {"system_auth_latest_signin": "thirty"}
        created = OPConfig.create(CLI())
        with pytest.raises(errors.NoAccountFound, match="No such account in configuration"):
            created.account()

        op_config_helper.config = {"latest_signin": "forty"}
        created = OPConfig.create(CLI())
        with pytest.raises(errors.NoAccountFound, match="No such account in configuration"):
            created.account()
