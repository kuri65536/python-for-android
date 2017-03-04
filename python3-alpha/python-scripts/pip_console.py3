#! python3.sh
from __future__ import print_function
import os
import os.path
import sys
import tempfile

try:
    import readline
except:
    pass


def setup_dir():
    dname = os.environ.get("PYTHONUSERBASE", None)
    if dname is not None:
        return dname

    dname = os.__file__
    for i in range(3):
        _dname = os.path.dirname(dname)
        if "forandroid" not in _dname:
            break
        dname = _dname
    dname = os.path.join(dname, "local")

    # failed: may be not effective in this moment.
    os.environ["PYTHONUSERBASE"] = dname
    import importlib
    import sysconfig
    import site

    # failure code: overriding by simple code
    # site.USER_BASE = dname
    # site.USER_SITE = os.path.join(dname, "lib", "python3.6", "site-packges")
    # sysconfig.get_config_vars()["userbase"] = dname

    # try to propagate the PYTHONUSERBASE to sysconfig and site.
    importlib.reload(sysconfig)
    mods = [i for i in sys.modules.items()
            if getattr(i[1], "__cached__", 1) is None]
    for k, v in mods:
        del sys.modules[k]
    importlib.reload(site)
    for k, v in mods:
        sys.modules[k] = v
    return dname


def bootstrap():
    setup_dir()    # set up site.USER_BASE

    import ensurepip
    ret = ensurepip._main(["--user"])
    return ret


if sys.version_info[0] == 3 and sys.version_info[1] >= 6:
    ImportErrors = (ModuleNotFoundError, )
else:
    ImportErrors = (ImportError, )
try:
    setup_dir()
    import pip
except ImportErrors:
    if bootstrap():
        sys.exit(1)
    print("now pip is ready. restart %s script" % os.path.basename(__file__))
    sys.exit(0)
    # FIXME: reload new pip (ensurepip load a tempolary pip, try to new file)
    del sys.modules["pip"]
    import importlib
    pip = importlib.reload("pip")


def pip_monkeypatch(dname):
    fd, fname = tempfile.mkstemp(dir=dname)
    sk = os.fdopen(fd, "w")
    sk.close()

    fPatch = False
    try:
        os.link(fname, fname + "2")
    except OSError as ex:
        # 1: Operation not permmited (in Windows ReFS?)
        # 38: Function not implemented (in android FAT)
        if ex.errno in (1, 38):
            fPatch = True
    finally:
        try:
            os.remove(fname)
        except:
            pass    # don't mind

    # patch to lockfile.py problem
    if not fPatch:
        return
    import pip._vendor.lockfile.mkdirlockfile as _mlf
    pip._vendor.lockfile.LockFile = _mlf
    pip._vendor.lockfile.FileLock = _mlf


def run(args):
    if args[0] == "install" and "--user" not in args:
        args = list(args)
        args.insert(1, "--user")
    try:
        pip.main(args)
    except Exception as ex:
        print(ex.message)


def main(args):
    if args[0] == os.path.basename(__file__):
        args = args[1:]
    if args:    # launch from command line with args.
        return run(args)

    print("Input pip commands, ie: pip install {module}")
    cmds = cmds_for_quit = ("quit", "cancel", "exit")
    print("  for quit, type: %s or %s" % (', '.join(cmds[:-1]), cmds[-1]))

    while(True):
        cmd = input("--> ")
        if cmd.strip().rstrip("()") in cmds_for_quit:
            break

        # BUG: need to parse args with quote and space.
        args = cmd.split(" ")
        args = [i for i in args if i]
        if args[0] == "pip":
            args = args[1:]
        run(args)


if __name__ == "__main__":
    readline
    dname = setup_dir()
    pip_monkeypatch(dname)
    main(sys.argv)
# vi: ft=python
