from py1pass.config import accounts as accnts


class TestAccount:
    def test_match_against_an_account(self):
        account = accnts.Account(
            account_uuid="one", url="two", email="three@four.com", user_uuid="five", shorthand="six"
        )
        assert account.matches("one")
        assert account.matches("two")
        assert account.matches("three@four.com")
        assert account.matches("five")
        assert account.matches("six")
        assert not account.matches(None)
        assert not account.matches("three")
        assert not account.matches("four")
        assert not account.matches("si")

        account = accnts.Account(
            account_uuid="one", url="two", email="three@four.com", user_uuid="five"
        )
        assert account.matches("one")
        assert account.matches("two")
        assert account.matches("three@four.com")
        assert account.matches("five")
        assert not account.matches("six")
        assert not account.matches(None)
        assert not account.matches("three")
        assert not account.matches("four")
        assert not account.matches("si")
