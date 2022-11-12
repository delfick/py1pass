import glob
import http.server
import inspect
import os
import shutil
import socket
import socketserver
import sys
import threading
import time
import typing as tp
import webbrowser
from pathlib import Path

here = Path(__file__).parent


@tp.runtime_checkable
class Command(tp.Protocol):
    __is_command__: bool

    def __call__(self, bin_dir: Path, args: list[str]) -> None:
        ...


class App:
    commands: dict[str, Command]

    def __init__(self):
        self.commands = {}

        compare = inspect.signature(type("C", (Command,), {})().__call__)

        for name in dir(self):
            val = getattr(self, name)
            if getattr(val, "__is_command__", False):
                assert (
                    inspect.signature(val) == compare
                ), f"Expected '{name}' to have correct signature, have {inspect.signature(val)} instead of {compare}"
                self.commands[name] = val

    @staticmethod
    def command(func: tp.Callable) -> tp.Callable:
        tp.cast(Command, func).__is_command__ = True
        return func

    def __call__(self, args: list[str], *, venv_location: None | Path = None) -> None:
        if venv_location is None:
            venv_location = Path(sys.executable) / ".." / ".."

        import sh

        if args and args[0] in self.commands:
            os.chdir(here.parent)
            try:
                self.commands[args[0]](venv_location / "bin", args[1:])
            except sh.ErrorReturnCode as error:
                sys.exit(error.exit_code)
            return

        sys.exit(f"Unknown command:\nAvailable: {sorted(self.commands)}\nWanted: {args}")

    @command
    def format(self, bin_dir: Path, args: list[str]) -> None:
        import sh

        files = ["py1pass", "tools/venv", *glob.glob("tools/*.py"), "setup.py"]
        sh.Command(bin_dir / "black")(*files, *args, _fg=True)
        sh.Command(bin_dir / "isort")(*files, *args, _fg=True)

    @command
    def lint(self, bin_dir: Path, args: list[str]) -> None:
        import sh

        sh.Command(bin_dir / "pylama")(*args, _fg=True)

    @command
    def types(self, bin_dir: Path, args: list[str]) -> None:
        import sh

        if args and args[0] == "restart":
            args.pop(0)
            sh.Command(bin_dir / "dmypy")("stop", _fg=True)

        args = ["run", *args]
        if "--" not in args:
            args.extend(["--", "."])

        sh.Command(bin_dir / "dmypy")(*args, _fg=True)

    @command
    def tests(self, bin_dir: Path, args: list[str]) -> None:
        import sh

        sh.Command(bin_dir / "pytest")(*args, _fg=True)

    @command
    def tox(self, bin_dir: Path, args: list[str]) -> None:
        import sh

        sh.Command(bin_dir / "tox")(*args, _fg=True)

    @command
    def docs(self, bin_dir: Path, args: list[str]) -> None:
        import sh

        do_view: bool = False
        docs_path = here / ".." / "docs"
        for arg in args:
            match arg:
                case "fresh":
                    build_path = docs_path / "_build"
                    if build_path.exists():
                        shutil.rmtree(build_path)
                case "view":
                    do_view = True

        os.chdir(docs_path)
        sh.Command(bin_dir / "sphinx-build")(
            "-b", "html", ".", "_build/html", "-d", "_build/doctrees", _fg=True
        )

        if do_view:

            with socket.socket() as s:
                s.bind(("", 0))
                port = s.getsockname()[1]

            address = f"http://127.0.0.1:{port}"
            results = docs_path / "_build" / "html"

            class Handler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(results), **kwargs)

            def open_browser():
                time.sleep(0.2)
                webbrowser.open(address)

            with socketserver.TCPServer(("", port), Handler) as httpd:
                print(f"Serving docs at {address}")
                thread = threading.Thread(target=open_browser)
                thread.daemon = True
                thread.start()
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    pass


app = App()

if __name__ == "__main__":
    app(sys.argv[1:])
