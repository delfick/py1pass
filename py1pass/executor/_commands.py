from ._base import CLIConfig, app, with_config


@app.command()
@with_config
def current_account(cfg: CLIConfig):
    print(cfg.op_config.account())
