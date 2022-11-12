import typing as tp

from attrs import define

AccountShorthand: tp.TypeAlias = str
AccountUUID: tp.TypeAlias = str
AccountURL: tp.TypeAlias = str
AccountEmail: tp.TypeAlias = str
UserUUID: tp.TypeAlias = str


@define
class Account:
    account_uuid: AccountUUID
    url: AccountURL
    email: AccountEmail
    user_uuid: UserUUID
    shorthand: None | AccountShorthand = None

    def matches(self, identifier: str) -> bool:
        return bool(identifier) and identifier in (
            self.shorthand,
            self.url,
            self.email,
            self.account_uuid,
            self.user_uuid,
        )
