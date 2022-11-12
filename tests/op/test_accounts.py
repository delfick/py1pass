from py1pass.config import accounts as accnts
from py1pass.tests import FakeCLI

locals().update(FakeCLI.make_fixture(name="fakecli"))


class TestOPCLIAccounts:
    def test_it_can_intepret_empty_accounts_list(self, fakecli: FakeCLI) -> None:
        fakecli.responds_to(["accounts", "list", "--format=json", "--no-color"], "")
        assert fakecli.op.accounts() == []

    def test_it_can_intepret_accounts_list(self, fakecli: FakeCLI) -> None:
        fakecli.responds_to(
            ["accounts", "list", "--format=json", "--no-color"],
            [
                {
                    "url": "my.1password.com",
                    "email": "me@me.com",
                    "user_uuid": "UKZKOXVOA6AIZFOA4743W6P9S4",
                    "account_uuid": "ZTT2HHSSS5AAPDIINFJ9394RPM",
                },
                {
                    "url": "mycompany.1password.com",
                    "email": "tim@mycompany.com",
                    "user_uuid": "VJ7IYNPQQFB53G4N9M9ZYYYYKY",
                    "account_uuid": "ATN2IRU7YJIEAK9J9H9S9B9O9Q",
                },
            ],
        )
        assert fakecli.op.accounts() == [
            accnts.Account(
                url="my.1password.com",
                email="me@me.com",
                user_uuid="UKZKOXVOA6AIZFOA4743W6P9S4",
                account_uuid="ZTT2HHSSS5AAPDIINFJ9394RPM",
            ),
            accnts.Account(
                url="mycompany.1password.com",
                email="tim@mycompany.com",
                user_uuid="VJ7IYNPQQFB53G4N9M9ZYYYYKY",
                account_uuid="ATN2IRU7YJIEAK9J9H9S9B9O9Q",
            ),
        ]
