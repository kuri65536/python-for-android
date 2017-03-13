# -*- coding: utf-8 -*-
from __future__ import print_function
import sysconfig
from distutils import sysconfig as dstconfig
import os


cross_compiling = "_PYTHON_HOST_PLATFORM" in os.environ


if cross_compiling:
    def _cross_cfg():
        ret = os.path.join(os.environ["PYTHONSRC"], "pyconfig.h")
        ret = os.path.abspath(ret)
        return ret

    sysconfig.get_config_h_filename = _cross_cfg

    for override in (
                     # ('CC', ),
                     # ('HOST_GNU_TYPE', ),
                     ('EXT_SUFFIX', ),
                     # ('SO', os.environ["EXT_SUFFIX"]),
                     ('srcdir',
                      os.path.dirname(sysconfig.get_config_h_filename())),
                     ):
        if len(override) == 1:
            v = override[0]
            v = os.environ[v]
        else:
            v = override[1]
        sysconfig.get_config_vars()[override[0]] = v

    for override in (
                     ('EXT_SUFFIX', ),
                     ('SOABI', ),
                     ):
        if len(override) == 1:
            v = override[0]
            v = os.environ[v]
        else:
            v = override[1]
        dstconfig.get_config_vars()[override[0]] = v


def customize_compiler36(compiler):
    sysroot = " --sysroot=%s" % os.environ["ANDROID_SYSROOT"]
    cflags = ("-I%s" % os.environ["PY4A_INC"] +
              " -MMD -MP -MF -fpic -ffunction-sections -funwind-tables"
              " -fstack-protector"
              " -D__ARM_ARCH_5__ -D__ARM_ARCH_5T__ -D__ARM_ARCH_5E__"
              " -D__ARM_ARCH_5TE__"
              " -Wno-psabi -march=armv5te -mtune=xscale -msoft-float"
              " -mthumb -Os"
              " -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64"
              " -DANDROID  -Wa,--noexecstack -O2 -DNDEBUG -g" +
              sysroot)
    cc = "arm-linux-androideabi-gcc"
    os.environ["CC"] = cc
    cxx = "arm-linux-androideabi-g++"
    cpp = "arm-linux-androideabi-cpp"
    ldshared = "%s -shared" % cxx
    ldshared += sysroot
    # removed -lsupc++
    ldshared += (" -lc -lstdc++ -lm -lpython3.6m"
                 " -Wl,--no-undefined -Wl,-z,noexecstack")
    ldshared += " -L%s " % os.environ["PY4A_LIB"]
    # sample: _multibytecodec.cpython-36m-arm-linux-androideabi.so
    ccshared = sysconfig.get_config_vars("CCSHARED")
    so_ext = "so"

    if 'LDFLAGS' in os.environ:
        ldshared += os.environ['LDFLAGS']
    if 'CFLAGS' in os.environ:
        cflags += os.environ['CFLAGS']
        ldshared += os.environ['CFLAGS']
    if 'CPPFLAGS' in os.environ:
        cpp += os.environ['CPPFLAGS']
        cflags += os.environ['CPPFLAGS']
        ldshared += os.environ['CPPFLAGS']

    cc_cmd = cc + ' ' + cflags
    compiler.set_executables(
        preprocessor=cpp,
        compiler=cc_cmd,
        compiler_so=cc_cmd + ' ' + ' '.join(ccshared),
        compiler_cxx=cxx,
        linker_so=ldshared,
        linker_exe=cc + ' ' + sysroot)

    compiler.shared_lib_extension = so_ext


def customize_compiler2(compiler):
    sysroot = " --sysroot=%s" % os.environ["ANDROID_SYSROOT"]


def patch_distutils():
    import os
    from distutils import sysconfig
    from distutils.sysconfig import get_python_inc as du_get_python_inc

    def get_python_inc(plat_specific=0, *args, **kwargs):
        if plat_specific == 0:
            out = os.environ["PY4A_INC"]
        else:
            out = du_get_python_inc(plat_specific=plat_specific, *args, **kwargs)
        return out
    setattr(sysconfig, 'get_python_inc', get_python_inc)

    def customize_compiler(compiler):
        cflags = "-I%s/python2.7" % os.environ["PY4A_INC"]
        cflags+=" -MMD -MP -MF -fpic -ffunction-sections -funwind-tables -fstack-protector"
        cflags+=" -D__ARM_ARCH_5__ -D__ARM_ARCH_5T__ -D__ARM_ARCH_5E__ -D__ARM_ARCH_5TE__"
        cflags+=" -Wno-psabi -march=armv5te -mtune=xscale -msoft-float -mthumb -Os"
        cflags+=" -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64"
        cflags+=" -DANDROID  -Wa,--noexecstack -O2 -DNDEBUG -g"
        cflags += sysroot
        cc = "arm-linux-androideabi-gcc"
        os.environ["CC"] = cc
        cxx = "arm-linux-androideabi-g++"
        cpp = "arm-linux-androideabi-cpp"
        ldshared= "%s -shared" % cxx
        ldshared += sysroot
        # removed -lsupc++
        ldshared += (" -lc -lstdc++ -lm -lpython2.7"
                     " -Wl,--no-undefined -Wl,-z,noexecstack")
        ldshared+=" -L%s " % os.environ["PY4A_LIB"]
        ccshared = sysconfig.get_config_vars("CCSHARED")
        so_ext = "so"

        if 'LDFLAGS' in os.environ:
            ldshared += os.environ['LDFLAGS']
        if 'CFLAGS' in os.environ:
            cflags += os.environ['CFLAGS']
            ldshared += os.environ['CFLAGS']
        if 'CPPFLAGS' in os.environ:
            cpp += os.environ['CPPFLAGS']
            cflags += os.environ['CPPFLAGS']
            ldshared += os.environ['CPPFLAGS']

        cc_cmd = cc + ' ' + cflags
        compiler.set_executables(
            preprocessor=cpp,
            compiler=cc_cmd,
            compiler_so=cc_cmd + ' ' + ' '.join(ccshared),
            compiler_cxx=cxx,
            linker_so=ldshared,
            linker_exe=cc + ' ' + sysroot)

        compiler.shared_lib_extension = so_ext

    if os.environ["PY"] == "2":
        pass
    else:
        customize_compiler = customize_compiler36
    setattr(sysconfig, 'customize_compiler', customize_compiler)

    def get_config_h_filename():
        inc_dir = os.environ["PY4A_INC"]
        # inc_dir = os.path.join(os.environ["PY4A_INC"], "python2.7")
        config_h = 'pyconfig.h'
        return os.path.join(inc_dir, config_h)
    setattr(sysconfig, 'get_config_h_filename', get_config_h_filename)


if __name__ == "__main__":
    print("for use: (python or python3) -m py4a setup.py ")
# vi: ft=python:nowrap:et:ts=4
