import typing as tp
from contextlib import contextmanager
from importlib.metadata import entry_points

import pytest
import typer

from py1pass.tests import FakeCLI, OPConfigHelper

locals().update(
    **FakeCLI.make_fixture(name="fakecli"), **OPConfigHelper.make_fixture(name="op_config_helper")
)


@pytest.fixture
def entrypoint(
    fakecli: FakeCLI, op_config_helper: OPConfigHelper
) -> tp.Callable[[int], tp.ContextManager[typer.Typer]]:
    fakecli.put_onto_path()

    @contextmanager
    def entrypoint(exit_code: int) -> tp.Generator[typer.Typer, None, None]:
        with pytest.raises(SystemExit) as error:
            yield tuple(entry_points(group="console_scripts", name="py1pass"))[0].load()

        assert error.value.code == exit_code

    return entrypoint
