py1pass
=======

A Python3.10+ library that wraps the 1password cli tool.

Install from pypi::

    > python -m pip install py1pass

Documentation at https://py1pass.readthedocs.io/

Development
-----------

To get a virtualenv with everything in it::

    > source ./run.sh activate

To run linting, formatting and tests::

    > ./format
    > ./lint
    > ./types
    > ./test.sh

And to build the sphinx docs::

    > ./run.sh docs
    OR to delete the cache first
    > ./run.sh docs fresh
    AND to view them
    > ./run.sh docs view

All other uses of ``run.sh`` will call the ``py1pass`` console script installed
by py1pass.
