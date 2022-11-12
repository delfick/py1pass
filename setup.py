import runpy

from setuptools import setup

VERSION = runpy.run_path("py1pass/version.py")["VERSION"]

setup(
    name="py1pass",
    version=VERSION,
    # Make sure you change VERSION value when you change install_requires
    install_requires=["strcs==0.2.0", "typer==0.7.0"],
    extras_require={
        "tests": ["noseOfYeti==2.3.1", "pytest==7.1.2"],
    },
    entry_points={
        "console_scripts": [
            "py1pass = py1pass.executor:app",
        ],
    },
)
