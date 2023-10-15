from attrs import define


@define
class Username:
    id: str
    type: str
    purpose: str
    label: str
    value: str
    reference: str


@define
class PasswordDetails:
    strength: str
    entropy: float | None = None
    generated: bool | None = None


@define
class Password:
    id: str
    type: str
    purpose: str
    label: str
    value: str
    reference: str
    password_details: PasswordDetails
    entropy: float | None = None


@define
class Notes:
    id: str
    type: str
    purpose: str
    label: str
    reference: str
