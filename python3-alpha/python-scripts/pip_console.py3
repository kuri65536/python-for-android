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

    # try to propagate the PYTHONUSERBASE to sysconfig and site.
    os.environ["PYTHONUSERBASE"] = dname
    import importlib
    import sysconfig
    import site

    importlib.reload(sysconfig)
    mods = [i for i in sys.modules.items()
            if getattr(i[1], "__cached__", 1) is None]
    for k, v in mods:
        del sys.modules[k]
    importlib.reload(site)
    for k, v in mods:
        sys.modules[k] = v
    return dname


def dummy_utime(path, times=None, ns=None, dir_fd=None, follow_symlinks=True):
    pass


def dummy_chmod(path, mode):
    pass


def pip_rooting(dname):
    fRoot = False
    if os.getuid() != 0 and fRoot:
        # pip need os.utime and os.chmod, need root permission.
        # ver.1: call python3.sh
        # dname = os.path.dirname(dname)
        # cmd = "sh %s/python3.sh" % dname       # need setup script.

        # ver.2: setup like the python3.sh
        bin = "/data/data/com.googlecode.python3forandroid/files/python3"
        ext = os.path.join(os.path.dirname(dname), "extras", "python3")
        dyn = os.path.join(
                bin, "lib",
                "python%d.%d" % sys.version_info[0:2], "lib-dynload")
        cmd = "sh -c '"
        cmd += " LD_LIBRARY_PATH=%s/lib" % bin
        cmd += " TEMP=%s/tmp" % ext
        cmd += " EXTERNAL_STORAGE=" + \
            os.environ.get("EXTERNAL_STORAGE", "/sdcard")
        cmd += " PYTHONPATH=%s:%s" % (ext, dyn)
        cmd += " PYTHON_EGG_CACHE=%s/tmp" % ext
        cmd += " PYTHONHOME=%s:%s" % (ext, bin)
        cmd += " %s" % sys.executable
        cmd = "su 0 %s %s'" % (cmd, sys.argv[0])

        print("launch script by super user: %s" % cmd)
        os.system(cmd)
        print("restart %s script" % os.path.basename(__file__))
        return 1
    elif os.getuid() != 0:
        os.utime = dummy_utime
        os.chmod = dummy_chmod
    return 0


def bootstrap():
    print("launch ensurepip.")
    dname = setup_dir()    # set up site.USER_BASE
    if pip_rooting(dname):
        return 0

    import ensurepip
    ret = ensurepip._main(["--user"])
    print("restart %s script" % os.path.basename(__file__))
    return ret


if sys.version_info[0] == 3 and sys.version_info[1] >= 6:
    ImportErrors = (ModuleNotFoundError, )
else:
    ImportErrors = (ImportError, )
try:
    setup_dir()
    import pip
except ImportErrors:
    bootstrap()
    sys.exit(0)


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
    if os.path.basename(__file__) in args[0]:
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
        if not args:
            continue
        if args[0] == "pip":
            args = args[1:]
        run(args)


if __name__ == "__main__":
    readline
    dname = setup_dir()
    pip_monkeypatch(dname)
    if pip_rooting(dname):
        sys.exit(0)
    main(list(sys.argv))
# vi: ft=python
