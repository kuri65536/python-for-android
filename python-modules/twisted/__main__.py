import sys
import py4a

import setuptools


if __name__ == "__main__":
    py4a.patch_distutils()
    sys.argv = sys.argv[1:]     # remove py4a

    # twisted
    _setup = {}
    with open('src/twisted/python/_setup.py') as f:
        exec(f.read(), _setup)

    try:
        setuptools.setup(**_setup["getSetupArgs"]())
    except KeyboardInterrupt:
        sys.exit(1)

# vi: ft=python:et:ts=4:nowrap:fdm=marker
