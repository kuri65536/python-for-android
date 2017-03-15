import sys
import py4a


if __name__ == "__main__":
    py4a.patch_distutils()
    sys.argv = sys.argv[1:]     # remove py4a

    # PyCrypto
    # import setup

    # numpy
    import setup
    setup.setup_package()

# vi: ft=python:et:ts=4:nowrap:fdm=marker
