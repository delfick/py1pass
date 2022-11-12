from attrs import define


@define
class Py1PassError(Exception):
    ...


del define
