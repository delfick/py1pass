import inspect
import types
import typing as tp
from contextvars import ContextVar
from functools import wraps
from pathlib import Path

import typer
from attrs import define

from ..config import OPConfig

P = tp.ParamSpec("P")

app = typer.Typer()


@define
class CLIConfig:
    op_config: OPConfig


config_v: ContextVar[CLIConfig] = ContextVar("config")


def with_config(func: tp.Callable[tp.Concatenate[CLIConfig, P], None]) -> tp.Callable[P, None]:
    source_spec = inspect.getfullargspec(func)
    assert (
        source_spec.args
        and source_spec.args[0] == "cfg"
        and func.__annotations__["cfg"] is CLIConfig
    )

    @wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> None:
        cfg = config_v.get()
        if cfg is None:
            raise RuntimeError("The configuration hadn't been set yet")
        return func(cfg, *args, **kwargs)

    code = [v for k, v in inspect.getmembers(func) if k == "__code__"][0]
    passer_code = code.replace(co_argcount=code.co_argcount - 1, co_varnames=code.co_varnames[1:])
    passer = types.FunctionType(passer_code, globals())

    wrapped.__wrapped__ = passer  # type:ignore
    del wrapped.__annotations__["cfg"]

    return wrapped


@app.callback(invoke_without_command=True)
def global_args(
    ctx: typer.Context,
    config_path: tp.Optional[Path] = typer.Option(None),
    op_path: None | Path = None,
):
    cfg = CLIConfig(op_config=OPConfig.create(op_path, config_path))
    config_v.set(cfg)

    if not ctx.invoked_subcommand:
        for account in cfg.op_config.accounts:
            print(account)


@app.command()
@with_config
def current_account(cfg: CLIConfig):
    print(cfg.op_config.account())
