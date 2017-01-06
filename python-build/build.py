#!env python
#
# Copyright (C) 2015 Shimoda
# Copyright (C) 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
from __future__ import print_function, unicode_literals
import compileall
import os
import re
import subprocess
import shutil
import glob
import fnmatch
import sys
import zipfile
from logging import (critical as crit, error as eror,
                     info, debug as debg)


VERSION = {
    "": "",
    "scripts": "",
    "extra": "",
    "lib": ""
}


class cfg:
    fExtra = fLib = fScripts = fBin = False
    plat = ""
    dest = "python_arm"
    path_jni = "python/obj/local"
    path_bin = os.path.join(path_jni, "armeabi")


def options():
    import logging
    l = logging.getLogger("")
    l.setLevel(logging.DEBUG)

    for arg in sys.argv:
        if arg in ("x86", ):
            # info("arch: %s" % arg)
            cfg.plat = "_x86"
            cfg.dest = "python_x86"
            cfg.path_bin = os.path.join(cfg.path_jni, "x86")
        elif arg in ("extra", ):
            cfg.fExtra = True
        elif arg in ("lib", ):
            cfg.fLib = True
        elif arg in ("scripts", ):
            cfg.fScripts = True
        elif arg in ("bin", ):
            cfg.fBin = True
    assert cfg.fExtra or cfg.fLib or cfg.fScripts or cfg.fBin

def main():
    options()

    # get version
    for i in ("scripts", "extra", "lib"):
        if os.path.isfile("LATEST_VERSION_"+i.upper()):
            VERSION[i] = "_"+open("LATEST_VERSION_"+i.upper()).read().strip()

    if os.path.isfile("LATEST_VERSION"):
        VERSION[""] = "_"+open("LATEST_VERSION").read().strip()

    # path expansion
    pwd = os.getcwd()
    cfg.dest = os.path.abspath(os.path.join(pwd, cfg.dest))
    cfg.path_bin = os.path.abspath(os.path.join(pwd, cfg.path_bin)) + "/"

    cfg.fLib and zipup_libs(pwd)

    cfg.fExtra and zipup_extra(pwd)
    # zipup_cleanup()
    cfg.fBin and zipup_bin(pwd)
    cfg.fScripts and zipup_script(pwd)
    info('Done.')


def run(cmd, exit=True, cwd=None):
    debg(cmd)
    if subprocess.Popen(cmd.split(), cwd=cwd).wait() != 0:
        if exit:
            crit('Failed!')
            sys.exit(1)
        else:
            eror('Ignoring failure.')


def find(directory, pattern=None, exclude=None):
    class Pattern:
        def __init__(self, exp):
            self.__exp__ = exp

        def __eq__(self, b):
            ret = fnmatch.fnmatch(b, self.__exp__)
            # import pdb; ret and pdb.set_trace()
            return ret

    debg('Looking for paths in %r matching %r' % (directory, pattern))
    matches = []
    misses = []
    if exclude is None:
        exclude = []
    else:
        exclude = [Pattern(i) for i in exclude]
    directory = os.path.abspath(directory)
    for root, dirs, files in os.walk(directory):
        for basename in dirs + files:
            if basename in exclude:
                if basename in dirs:
                    dirs.remove(basename)
                continue
            path = os.path.join(root, basename)
            if pattern is None or re.search(pattern, path):
                matches.append(path)
            else:
                misses.append(path)
    debg('Found %d matches and %d misses' % (len(matches), len(misses)))
    return matches, misses


def rm(path):
    debg('Deleting %r' % path)
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except OSError:
        pass


def strip(path):
    ndkpath = os.environ["NDK_PATH"]
    toolchain = os.path.join(
        ndkpath, "toolchains/arm-linux-androideabi-4.9/prebuilt/"
                 "linux-x86_64/arm-linux-androideabi")
    if cfg.plat == "_x86":
        toolchain = os.path.join(
            ndkpath, "toolchains/x86-4.9/prebuilt/"
                     "linux-x86_64/i686-linux-android")
    run('%s/bin/strip %s' % (toolchain, path))


def zipup(out_path, in_path, top, exclude=None, prefix=''):
    info("zipup: %s" % out_path)
    # Remove an existing zip file.
    rm(out_path)

    zip_file = zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED)
    for path in find(in_path, exclude=exclude)[0]:
        if os.path.islink(path):
                dest = os.readlink(path)
                attr = zipfile.ZipInfo()
                attr.filename = prefix + path[len(top):].lstrip('/')
                attr.create_system = 3
                # long type of hex say, symlink attr magic...
                attr.external_attr = 0xA1ED0000L
                zip_file.writestr(attr, dest)
        elif not os.path.isdir(path):
            arcname = prefix + path[len(top):].lstrip('/')
            debg('Adding %s to %s' % (arcname, out_path))
            zip_file.write(path, arcname)
    zip_file.close()


def install_py4a(pwd):                                      # {{{1
    class PathInfo:
        def __init__(self, file_or_dir, relSrc, relDst):
            self.file_or_dir = file_or_dir
            self.src = relSrc
            self.dst = relDst

    class PkgInfo:
        def __init__(self, seq, build, *items):
            self.path_seq = seq
            self.build = build
            self.items = items

    path_libs = cfg.dest + "/python-ext/python"
    run("mkdir -p %s" % path_libs)
    pkgs = {
        'Installing xmppy.': PkgInfo(
            ('xmpppy', 'xmpp'), False, PathInfo(False, '', 'xmpp')),
        'Installing BeautifulSoup.': PkgInfo(
            ('BeautifulSoup', ), False,
            PathInfo(True, 'BeautifulSoup.py', '')),
        'Installing gdata.': PkgInfo(
            ('gdata', ), True,
            PathInfo(False, "build/lib/gdata", "gdata"),
            PathInfo(False, "build/lib/atom", "atom")),
        # disable twitter in 2015.
        # 'Installing python-twitter.': PkgInfo(
        #     ('python-twitter', ), False,
        #     PathInfo(True, 'twitter.pyc', '')),
        # 'Installing simplejson.': PkgInfo(
        #     ('python-twitter', 'simplejson'), False,
        #     PathInfo(False, "", 'simplejson')),
        'Installing setuptools.': PkgInfo(
            ('setuptools', ), False,
            PathInfo(True, "*.pyc", 'site-packages'),
            PathInfo(False, "setuptools", 'setuptools')),
    }

    for title, v in pkgs.items():
        info(title)
        path = os.path.join(*((pwd, 'python-libs') + v.path_seq))
        if v.build:
            run('python setup.py build', cwd=path)
        debg("compile: %s" % (path, ))
        # compileall.compile_dir(path, quiet=True)      # do it after.
        for item in v.items:
            src = os.path.join(path, item.src)
            dst = os.path.join(path_libs, item.dst)
            if not item.file_or_dir:     # dir
                shutil.copytree(src, dst)
                continue
            # file to dir
            for fname in glob.glob(src):
                shutil.copy(fname, dst)


def zipup_libs(pwd):                                        # {{{1
    info('Zipping up Python Libs for deployment.')
    root = os.path.join(cfg.dest, "python-lib")
    output = os.path.join(root, "python/lib/python2.7")
    # output2 = os.path.join(root, "python/include")
    run("mkdir -p %s" % (root + "/python/bin"))
    run("mkdir -p %s" % output)

    # map(rm, find('output.temp', '\.py$',
    #              exclude=['setuptools', 'distutils'])[0])
    # map(rm, find('output.temp/usr/lib/python2.7', '.*',
    #              exclude=['setuptools', 'distutils'])[0])
    # map(rm, find('output.temp', 'python$',
    #              exclude=['setuptools', 'distutils'])[0])

    shutil.copytree("python-libs/py4a", output + "/py4a")
    # run("cp %s/setup.cfg ." % pwd, cwd="output.temp/usr")
    shutil.copy2("prepare_setuptools.sh",
                 root + "/python/bin/setup.sh")
    shutil.copy2("../sl4atools/python2.sh",
                 root + "/python/bin/python.sh")
    zipup('python_lib%s.zip' % VERSION[""],
          root, root)


def zipup_extra(pwd):                                       # {{{1
    info('Zipping up standard library.')
    install_py4a(pwd)

    root = os.path.join(cfg.dest, "python-ext")

    # copy files done in Makefile's build_copy section.
    def rename_pyo_pyc(fname):
        # import pdb; pdb.set_trace()
        fdest = os.path.splitext(fname)[0] + ".pyc"
        if os.path.isfile(fdest):
            os.remove(fdest)
        shutil.copy2(fname, fdest)

    compileall.compile_dir(root, quiet=True)
    map(rename_pyo_pyc, find(root, ".pyo")[0])

    zipup('python_extras%s.zip' % VERSION["extra"],
          root, root,
          exclude=["*.exe", "*.py", "*.pyo"])


def zipup_cleanup(pwd):                                     # {{{1
    # TODO: remove this method, no longer needed.
    map(rm, find('output', '\.py$')[0])
    map(rm, find('output', '\.pyc$')[0])
    map(rm, find('output', '\.doc$')[0])
    map(rm, find('output', '\.egg-info$')[0])

    def clean_library(lib):
        rm(os.path.join(pwd, 'output', 'usr', 'lib', 'python2.7', lib))

    map(clean_library,
        ['ctypes', 'distutils', 'idlelib', 'plat-linux2', 'site-packages'])


def zipup_bin(pwd):                                         # {{{1
    info('Zipping up Python interpreter for deployment.')
    root = os.path.join(cfg.dest, "python-bin")
    outlib = os.path.join(root, "python/lib")
    outtic = os.path.join(root, "python/share/terminfo")
    output = os.path.join(outlib, "python2.7/lib-dynload")
    run("mkdir -p %s" % (root + "/python/bin"))
    run("mkdir -p %s" % outtic + "/a")
    run("mkdir -p %s" % outtic + "/u")
    run("mkdir -p %s" % outtic + "/v")
    run("mkdir -p %s" % outtic + "/x")
    run("mkdir -p %s" % output)

    def pickup(src, dst, later=False):
        _dst = os.path.join(dst, os.path.basename(src))
        if os.path.islink(src):     # keep soft-link
            if later:
                return src
            linkto = os.readlink(src)
            os.symlink(linkto, _dst)
            return
        debg("pickup: %s" % src)
        shutil.copy2(src, _dst)

    def copyre(path, pat, dst):
        remains = []
        for fname in os.listdir(path):
            if not re.match(pat, fname):
                continue
            fname = os.path.join(path, fname)
            ret = pickup(fname, dst, later=True)
            ret and remains.append(ret)
        for fname in remains:
            pickup(fname, dst)   # ignore symlink errors, so put file 1st.

    info('Picking up binaries from JNI dir.')
    info('python => %s' % (cfg.path_bin + "python"))
    shutil.copy2(cfg.path_bin + "python", root + "/python/bin/python")

    ticpath = ("ncurses/lib-armeabi/data/data/"
               "com.googlecode.pythonforandroid/files/python/share/terminfo")
    copyre(ticpath + "/a", "^ansi$", outtic + "/a")
    copyre(ticpath + "/u", "^unknown$", outtic + "/u")
    copyre(ticpath + "/v", "^vt100$|^vt320$", outtic + "/v")
    copyre(ticpath + "/x", "^xterm$", outtic + "/x")
    copyre(cfg.path_bin, "^lib.*\.so.*$", outlib)
    copyre(cfg.path_bin, "^(?!lib).*\.so*$", output)

    info('Strip them...')
    map(strip, find(root, '\.so$')[0])      # make 8M => 3M
    strip(root + '/python/bin/python')

    info('Removing unecessary files and directories from installation.')
    # Locale not supported on Android.
    map(rm, find(output, '_locale.so$')[0])

    zipup('python%s%s.zip' % (VERSION[""], cfg.plat),
          root, root)
    # exclude=['*.pyc',  '*.py'], prefix="python/")


def zipup_script(pwd):                                      # {{{1
    root = os.path.join(pwd, 'python-scripts')
    info('Zipping up Python scripts.')
    zipup(os.path.join(pwd, 'python_scripts%s.zip' % VERSION["scripts"]),
          root, root)


if __name__ == "__main__":                                  # {{{1
    main()
# vi: ft=python:et:ts=4:nowrap:fdm=marker
