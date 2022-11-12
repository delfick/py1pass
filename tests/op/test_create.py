import shutil

from attrs import define

from py1pass.op import OPCLI
from py1pass.tests import FakeCLI

locals().update(FakeCLI.make_fixture(name="fakecli"))


class TestOPCLI:
    def test_it_can_be_created_getting_from_system_path(self, fakecli: FakeCLI) -> None:
        @define
        class Info:
            one: int

        fakecli.responds_to(["hello", "there"], '{"one": 1}')

        with fakecli.on_path():
            assert shutil.which("op") == str(fakecli.location)
            op = OPCLI.create()
            assert str(op.sh.hello.there()).strip() == '{"one": 1}'
            assert op._load(Info, op.sh.hello.there()) == Info(one=1)

        fakecli.assert_called("hello", "there", count=2)

    def test_it_can_be_created_getting_from_location(self, fakecli: FakeCLI) -> None:
        @define
        class Info:
            one: int

        fakecli.responds_to(["hello", "there"], '{"one": 1}')

        assert shutil.which("op") != str(fakecli.location)
        op = OPCLI.create(fakecli.location)
        assert str(op.sh.hello.there()).strip() == '{"one": 1}'
        assert op._load(Info, op.sh.hello.there()) == Info(one=1)
        fakecli.assert_called("hello", "there", count=2)

    def test_it_passes_through_existing_instances(self, fakecli: FakeCLI) -> None:
        op = OPCLI.create(fakecli.location)
        assert OPCLI.create(op) is op
