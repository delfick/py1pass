import typer

from py1pass.data import Data, Item

from ._base import CLIConfig, app, with_config


@app.command()
@with_config
def current_account(cfg: CLIConfig):
    print(cfg.op_config.account())


@app.command()
@with_config
def get_item(
    cfg: CLIConfig,
    vault: str = typer.Argument(None),
    item: str = typer.Argument(None),
):
    acnt = cfg.op_config.account()
    print(cfg.op_config.op_cli.get_item(Item[Data], item, vault=vault, account=acnt.account_uuid))
