import importlib

from ._base import app

importlib.import_module("._commands", package=__package__)

__all__ = ["app"]
