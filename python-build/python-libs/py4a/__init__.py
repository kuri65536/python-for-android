# -*- coding: utf-8 -*-
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
	cflags = "-I%s/python2.6" % os.environ["PY4A_INC"]
	cflags+=" -MMD -MP -MF -fpic -ffunction-sections -funwind-tables -fstack-protector"
	cflags+=" -D__ARM_ARCH_5__ -D__ARM_ARCH_5T__ -D__ARM_ARCH_5E__ -D__ARM_ARCH_5TE__"
	cflags+=" -Wno-psabi -march=armv5te -mtune=xscale -msoft-float -mthumb -Os"
	cflags+=" -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64"
	cflags+=" -DANDROID  -Wa,--noexecstack -O2 -DNDEBUG -g"
	cc = "arm-linux-androideabi-gcc"
	cxx = "arm-linux-androideabi-g++"
	cpp = "arm-linux-androideabi-cpp"
	ldshared= "%s -shared" % cxx
	ldshared+=" -lc -lstdc++ -lm -Wl,--no-undefined -Wl,-z,noexecstack -lsupc++ -lpython2.6"
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
            linker_exe=cc)

        compiler.shared_lib_extension = so_ext
    setattr(sysconfig, 'customize_compiler', customize_compiler)

    def get_config_h_filename():
	inc_dir = os.path.join(os.environ["PY4A_INC"], "python2.6")
	config_h = 'pyconfig.h'
	return os.path.join(inc_dir, config_h)
    setattr(sysconfig, 'get_config_h_filename', get_config_h_filename)

