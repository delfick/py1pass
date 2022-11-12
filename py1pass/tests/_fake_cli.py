import inspect
import json
import os
import shlex
import types
import typing as tp
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent
from unittest import mock

import pytest
from attrs import define, field
from pytest import TempPathFactory

from py1pass.op import OPCLI


@define
class DisabledOPCLI(OPCLI):
    _disabled: bool = True
    command: Path = Path("/")


@define
class FakeCLI:
    location: Path
    call_log: Path

    responses: dict[str, str] = field(init=False, factory=lambda: {})
    _op: OPCLI = field(init=False)

    @property
    def op(self) -> OPCLI:
        if not hasattr(self, "_op"):
            self._op = OPCLI.create(self.location)
        return self._op

    @classmethod
    def make_fixture(
        cls, *, name: str
    ) -> dict[str, tp.Callable[[TempPathFactory], tp.Generator["FakeCLI", None, None]]]:
        @pytest.fixture(name=name)
        def fakecli(tmp_path_factory: TempPathFactory) -> tp.Generator[FakeCLI, None, None]:
            testpath = tmp_path_factory.mktemp("testpath")
            with FakeCLI(location=testpath / "op", call_log=testpath / "call_log") as op:
                yield op

        return {name: fakecli}

    def __enter__(self) -> "FakeCLI":
        self.write()
        return self

    def __exit__(
        self,
        exc_typ: None | type[BaseException],
        exc: None | BaseException,
        tb: None | types.TracebackType,
    ) -> None:
        self.remove_from_path()

    def put_onto_path(self) -> None:
        parent = str(self.location.parent)
        os.environ["PATH"] = f"{parent}:{os.environ['PATH']}"

    def remove_from_path(self) -> None:
        parent = str(self.location.parent)
        os.environ["PATH"] = os.environ["PATH"].replace(f"{parent}:", "")

    @contextmanager
    def on_path(self) -> tp.Generator[None, None, None]:
        try:
            self.put_onto_path()
            yield
        finally:
            self.remove_from_path()

    def assert_called(self, *args: str, count: int) -> None:
        called = []
        if self.call_log.exists():
            with open(self.call_log) as cl:
                called = json.load(cl)

        if args == (mock.ANY,):
            want = tp.cast(list[str], mock.ANY)
        else:
            want = list(args)

        found = 0
        for ff in called:
            if ff == want:
                found += 1

        assert found == count, f"Expected {want} to be found {count} times, only found {found}"

    def write(self) -> None:
        def main(match: dict[str, str], call_log: Path):
            sys = __import__("sys")
            json = __import__("json")

            current = []
            if call_log.exists():
                with open(call_log) as cl:
                    current = json.load(cl)

            current.append(sys.argv[1:])
            with open(call_log, "w") as clw:
                json.dump(current, clw)

            print(match[json.dumps(sys.argv[1:])])

        with open(self.location, "w") as fle:
            print(f"#!{__import__('sys').executable}", file=fle)
            print("from pathlib import Path", file=fle)
            print(dedent(inspect.getsource(main)), file=fle)
            print(
                f"main({json.dumps(self.responses)}, Path('{shlex.quote(str(self.call_log))}'))",
                file=fle,
            )

        os.chmod(self.location, 0o755)

    def read(self) -> str:
        with open(self.location) as fle:
            return fle.read()

    def responds_to(self, args: tp.Iterable[str], response: object) -> None:
        if not isinstance(response, str):
            response = json.dumps(response)

        self.responses[json.dumps(list(args))] = dedent(response).strip()
        self.write()
