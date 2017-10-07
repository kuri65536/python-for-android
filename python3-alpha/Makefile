
.PHONY: build build_config build_bin build_install build_strip \
        error init clean_output cleanall \
        patch build_misc_sqlite3 build_misc_ncurses \
        build_misc_readline build_misc_bzip2 strip_bin

# build settings section 1 {{{1
VER_MAJ=3.6
VER_MAJ_NODOT=$(subst .,,$(VER_MAJ))
VERSION=$(VER_MAJ).3
# set -ex
CWD := $(shell pwd)
DEBUG=no

RELEASE_VERSION:=$(shell cat LATEST_VERSION)
PYTHONNET := Python-$(VERSION).tgz
PYTHONTAR := $(CWD)/Python-$(VERSION).tgz
PYTHONLIB := python$(VER_MAJ)
HOSTPYTHON := $(CWD)/host
PYTHON_FOR_BUILD := $(HOSTPYTHON)/bin/python3

ZIP_BINarm := python3_$(RELEASE_VERSION).zip
ZIP_BINx86 := $(subst .zip,_x86.zip,$(ZIP_BINarm))
ZIPEXTRA := python3_extras_$(shell cat LATEST_VERSION_EXTRA).zip
ZIPSCRIPTS := python3_scripts_$(shell cat LATEST_VERSION_SCRIPTS).zip
ZIP := $(ZIP_BINarm) $(ZIP_BINx86) \
       $(ZIPEXTRA) \
       $(ZIPSCRIPTS)

# check environment {{{1
BUILDMACHINE := $(shell uname -m)
BUILDOS := $(shell uname -s | tr A-Z a-z)
BUILDARCH := $(BUILDMACHINE)-$(BUILDOS)-gnu
ifeq (x$(host),x)
# check host variable: linux-x86_64, linux-x86 or darwin-x86
host = $(BUILDOS)-$(BUILDMACHINE)
endif

ifeq (x$(NDK_PATH),x)
build: error
else
build: .build_tools $(ZIP)
endif

error:
	@echo please set NDK_PATH to android-ndk-r10d or later::
	@echo "  $$ NDK_PATH=/path/to/android-ndk-r10d make build"

.build_tools:
	@echo "check zlib,               if failed: apt install zlib1g-dev"
	python ../tools/check_zlib.py
	@echo "check makedepend command, if failed: apt install xutils-dev"
	makedepend
	@echo "check zip command,        if failed: apt install zip"
	zip -v > /dev/null 2>&1
	touch .build_tools

# tools {{{2
ndk_depends = $(NDK_PATH)/ndk-depends
TAR := tar xfz


# build variables for cross-compile. (arm) {{{1
ifeq (x$(CROSS),xarm)
TARGET := arm-linux-androideabi
tabi := $(TARGET)-4.9
# ANDROID_API := android-4     # TODO: missing waitid
export ANDROID_API := android-9
export ANDROID_TOOLCHAIN := $(NDK_PATH)/toolchains/$(tabi)/prebuilt/$(host)/bin
export PATH := $(ANDROID_TOOLCHAIN):$(PATH)
_ANDROID_ARCH = arch-arm
_ANDROID_EABI = $(tabi)

# CXX = ${TARGET}-g++
# AR = ${TARGET}-ar
# RANLIB=${TARGET}-ranlib
MACHINE = armv7
export ARCH = arm
BLDSHARED = arm-linux-androideabi-gcc -shared
CROSS_COMPILE = arm-linux-androideabi-
CROSS_COMPILE_TARGET = arm
HOSTARCH = arm-linux-androideabi

    export PYTHONSRC := ./python-src_arm
    SFX := _arm
    ZIPMAIN := $(ZIP_BINarm)
endif

# build variables for cross-compile. (x86) {{{1
ifeq (x$(CROSS),xx86)
    TARGET := i686-linux-android
    HOSTARCH := $(TARGET)
    _ANDROID_EABI = x86-4.9

    MACHINE := i686
    export ARCH := x86

    export PYTHONSRC := ./python-src_x86
    SFX := _x86
    ZIPMAIN := $(ZIP_BINx86)
endif

export _PYTHON_PROJECT_BASE := $(abspath $(PYTHONSRC))

# build settings section 2 {{{1
ANDROID_NDK_ROOT := $(NDK_PATH)
ANDROID_SYSROOT = $(NDK_PATH)/platforms/$(ANDROID_API)/$(_ANDROID_ARCH)
export SYSROOT = $(ANDROID_SYSROOT)
NDK_SYSROOT = $(ANDROID_SYSROOT)
ANDROID_NDK_SYSROOT = $(ANDROID_SYSROOT)
ANDROID_DEV = $(ANDROID_SYSROOT)/usr

PYTHON_OPTIONAL_MODULES="bz2 lzma ssl"


# build settings section 3 {{{1
PYBINR := python3

ifneq (x$(CROSS),x)
    export PYBIN := $(CWD)/$(PYBINR)$(SFX)/$(PYBINR)
    PYDYNR := $(PYBINR)/lib/$(PYTHONLIB)/lib-dynload
    PYDYN := $(CWD)/$(PYBINR)$(SFX)/$(PYDYNR)

    export ANDROID_TOOLCHAIN := $(NDK_PATH)/toolchains/$(_ANDROID_EABI)/prebuilt/$(host)/bin
    export PATH := $(ANDROID_TOOLCHAIN):$(PATH)
    # ANDROID_API := android-4     # TODO: missing waitid
    export ANDROID_API := android-9
    _ANDROID_ARCH = arch-$(ARCH)

    export CFLAGS = --sysroot=$(ANDROID_NDK_SYSROOT) \
                    -I$(PYBIN)/include -fvisibility=default -fPIE
    export CPPFLAGS = $(CFLAGS)
    export CXXFLAGS = $(CFLAGS)
    export CCSHARED = -fvisibility=default -fPIE
    export LDFLAGS := --sysroot=$(ANDROID_NDK_SYSROOT) -L$(PYBIN)/lib
    export LINKFORSHARED := -rdynamic -fPIE -pie \
                            -Xlinker -export-dynamic

    export PYTHON_FOR_BUILD = $(HOSTPYTHON)/bin/python3
    export PGEN_FOR_BUILD = $(HOSTPYTHON)/bin/hostpgen
    # export HOSTPGEN = $(HOSTPYTHON)/bin/hostpgen
    export HOSTFILIB = $(HOSTPYTHON)/bin/host_freeze_importlib

    CROSS_COMPILE := $(HOSTARCH)-
    CROSS_COMPILE_TARGET := $(ARCH)
    BLDSHARED := $(CROSS_COMPILE)gcc -shared
    HOSTARCH := $(TARGET)
endif


# cleaning {{{1
cleanall: clean
	rm -f $(PYTHONTAR)

clean:
	make -C openssl clean
	rm -rf host-src host
	rm -rf ncurses-5.9
	rm -rf readline-6.3
	rm -rf sqlite3
	make clean_work CROSS=arm PIE=yes
	make clean_work CROSS=x86 PIE=yes
	rm -rf python3_extras
	rm -f .build_*
clean_work:
	rm -rf bzip2-1.0.6$(SFX)
	rm -rf $(PYTHONSRC)
	rm -rf $(dir $(PYBIN))


# libraries {{{1
.build_misc: .build_misc_sqlite3 .build_misc_ncurses \
             .build_misc_readline .build_misc_bzip2
	touch .build_misc

## download {{{2
sqlite3.tar.gz:
	wget -O $@ https://sqlite.org/2015/sqlite-autoconf-3080803.tar.gz
ncurses-5.9.tar.gz:
	wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz
readline-6.3.tar.gz:
	wget ftp://ftp.gnu.org/gnu/readline/readline-6.3.tar.gz
# zlib-1.2.8.tar.gz:
# 	wget http://zlib.net/zlib-1.2.8.tar.gz
bzip2-1.0.6.tar.gz:
	wget http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz


targz = $(subst .tar.gz,,$1)

## openssl {{{2
.build_openssl: $(PYTHONTAR)
	PYBINR=$(PYBINR) CWD=$(CWD) make -C openssl build
	# install_sw is contained in build.
	touch .build_openssl

## ncurses {{{2
.build_misc_ncurses: ncurses-5.9.tar.gz
	make $(subst .,,$@) CROSS=arm PIE=yes
	make $(subst .,,$@) CROSS=x86 PIE=yes
	touch $@
build_misc_ncurses: ncurses-5.9.tar.gz
	if ! [ -d $(call targz,$<) ]; then \
	    tar xfz $< ; \
	    cd $(call targz,$<); \
	    patch -p1 < $(CWD)/patches/$(call targz,$<).patch; fi
	mkdir -p $(call targz,$<)/build$(SFX)
	cd $(call targz,$<)/build$(SFX); \
	  ../configure --host=$(HOSTARCH) --build=$(BUILDARCH) \
	  --prefix=$(PYBIN) \
	    --with-shared --without-normal \
	    --disable-rpath \
	  --without-ada --without-cxx --without-manpages \
	  --without-progs --without-tests \
	  --with-termlib --enable-termcap --enable-widec \
	    --disable-home-terminfo \
	    --with-default-terminfo-dir=$(PYBIN)/share/terminfo \
	    --with-terminfo-dirs=$(PYBIN)/share/terminfo
	#  --disable-database
	#    --with-install-prefix=$(PYBIN) \
	make -C $(call targz,$<)/build$(SFX)
	make -C $(call targz,$<)/build$(SFX) install
	@echo Fix symlinks for Python _curses and _curses_panel extensions.
	cd $(PYBIN)/include; cp ncursesw/*.h .

## readline {{{2
.build_misc_readline: readline-6.3.tar.gz .build_misc_ncurses
	make $(subst .,,$@) CROSS=arm PIE=yes
	make $(subst .,,$@) CROSS=x86 PIE=yes
	touch $@
build_misc_readline: readline-6.3.tar.gz
	if ! [ -d $(call targz,$<) ]; then \
	    tar xfz $< ; \
	    cd $(call targz,$<) ; \
	    autoreconf -i ; \
	    patch < $(CWD)/patches/readline-6.3-pre.patch ; fi
	mkdir -p $(call targz,$<)/build$(SFX)
	cd $(call targz,$<)/build$(SFX); \
	   bash_cv_wcwidth_broken=no \
	   CFLAGS="$(CFLAGS) -DANDROID" \
	    ../configure --host=$(HOSTARCH) --build=$(BUILDARCH) \
	   --prefix=$(PYBIN) \
	    --with-curses=$(CWD)/ncurses-5.9/build$(SFX) \
	    --enable-shared --disable-static \
	    --enable-multibyte
	make -C $(call targz,$<)/build$(SFX)
	make -C $(call targz,$<)/build$(SFX) install

## sqlite3 {{{2
.build_misc_sqlite3: sqlite3.tar.gz
	make $(subst .,,$@) CROSS=arm PIE=yes
	make $(subst .,,$@) CROSS=x86 PIE=yes
	touch $@
build_misc_sqlite3: sqlite3.tar.gz
	if ! [ -d $(call targz,$<) ]; then \
	    tar xfz $<; \
	    mv sqlite-autoconf-3080803 $(call targz,$<); fi
	mkdir -p $(call targz,$<)/build$(SFX)
	cd $(call targz,$<)/build$(SFX); \
	   ../configure --host=$(HOSTARCH) --build=$(BUILDARCH) --prefix=$(PYBIN) \
	   --disable-shared
	make -C $(call targz,$<)/build$(SFX)
	make -C $(call targz,$<)/build$(SFX) install

## zlib => use bionic library {{{2
# .build_misc_zlib: zlib-1.2.8.tar.gz
# 	tar xfz $<
# 	make $@_arm CROSS=arm
# 	touch $@
# .build_misc_zlib_arm: zlib-1.2.8.tar.gz
# 	make -C $(call targz,$<)

## bzip2 {{{2
.build_misc_bzip2: bzip2-1.0.6.tar.gz
	make $(subst .,,$@) CROSS=arm PIE=yes
	make $(subst .,,$@) CROSS=x86 PIE=yes
	touch $@
build_misc_bzip2: BZIPPATH = $(call targz,$<)$(SFX)
build_misc_bzip2: bzip2-1.0.6.tar.gz
	rm -rf $(BZIPPATH)
	tar xfz $<
	cd $(call targz,$<); patch -p1 < $(CWD)/patches/bzip2-1.0.6-pre.patch
	mv $(call targz,$<) $(BZIPPATH)
	PREFIX=$(PYBIN)\
	  CC=$(TARGET)-gcc RANLIB=$(TARGET)-ranlib AR=$(TARGET)-ar \
	  CFLAGS="$(CFLAGS) -O3 -DUSE_MMAP" \
	  make -C $(BZIPPATH)
	PREFIX=$(PYBIN)\
	  CC=$(TARGET)-gcc RANLIB=$(TARGET)-ranlib \
	  CFLAGS="$(CFLAGS) -O3 -DUSE_MMAP" \
	  make -C $(BZIPPATH) -f Makefile-libbz2_so
	PREFIX=$(PYBIN)\
	  make -C $(BZIPPATH) install

# python3: download and build for current host  {{{1
$(PYTHONTAR):
	@echo "Building Python VM For Android Release $(RELEASE_VERSION)"
	URL="http://www.python.org/ftp/python/$(VERSION)/$(PYTHONNET)"; \
	    wget -O $(PYTHONTAR) $$URL; \

.build_host: $(PYTHONTAR)
	# we need to build the host python and host pgen so we can
	# generate the correct grammar and some other stuff
	echo "Decompressing Python-$(VERSION)"
	$(TAR) $(PYTHONTAR)
	mv Python-$(VERSION) host-src
	mkdir -p $(HOSTPYTHON)
	cd host-src/; ./configure --prefix=$(HOSTPYTHON)
	make -C host-src
	make -C host-src Parser/pgen
	make -C host-src install
	cp host-src/Parser/pgen $(HOSTPYTHON)/bin/hostpgen
	# cp host-src/Programs/_freeze_importlib \
	#     $(HOSTPYTHON)/bin/host_freeze_importlib
	touch .build_host

# python3: patching-configure-build {{{1
$(CWD)/patches/python-*.patch:
	echo
.build_src: .build_host $(PYTHONTAR) $(CWD)/patches/python-*.patch
	make $(subst .,,$@) CROSS=arm PIE=yes
	make $(subst .,,$@) CROSS=x86 PIE=yes
	touch .build_src
build_src: $(PYTHONTAR) $(CWD)/patches/python-*.patch
	rm -rf $(PYTHONSRC)
	$(TAR) $(PYTHONTAR)
	mv Python-$(VERSION) $(PYTHONSRC)
	cd $(PYTHONSRC); \
	  for p in $(CWD)/patches/python-*.patch; do \
	    echo "patching: $$p..."; patch -p1 -i $$p; done

.build_config: .build_src .build_misc .build_openssl
	make build_config CROSS=arm PIE=yes
	make build_config CROSS=x86 PIE=yes
	touch .build_config
build_config:
	# @echo PATH: "'$$PATH'"
	# @echo CROSS: "$(CROSS)"
	# @echo CFLAGS: "$$CFLAGS"
	# @echo LINKFORSHARED: "$(LINKFORSHARED)"
	ln -sf $(NDK_SYSROOT)/usr/include/linux/soundcard.h \
	       $(NDK_SYSROOT)/usr/include/sys/soundcard.h
	cd $(PYTHONSRC); CONFIG_SITE=`pwd`/config.site \
	./configure CROSS_COMPILE_TARGET=yes \
	            --host=$(TARGET) --build=$(BUILDARCH) --disable-ipv6 \
	            --prefix=$(PYBIN) --enable-shared --with-ensurepip=yes

.build_bin: .build_config
	make build_bin CROSS=arm PIE=yes
	make build_bin CROSS=x86 PIE=yes
	touch .build_bin
build_bin: .build_openssl .build_misc
	CFLAGS="$(CFLAGS)" CROSS_COMPILE_TARGET=yes make -C $(PYTHONSRC) sharedmods # build

.build_install: .build_bin
	make build_install CROSS=arm PIE=yes
	make build_install CROSS=x86 PIE=yes
	touch .build_install
build_install: .build_bin
	CROSS_COMPILE_TARGET=yes make -C $(PYTHONSRC) install

.build_strip: .build_install
	make build_strip CROSS=arm PIE=yes
	make build_strip CROSS=x86 PIE=yes
	touch .build_strip
build_strip: .build_install
	$(TARGET)-strip $(PYBIN)/bin/python3
	for i in $(PYBIN)/lib/*.so* $(PYDYN)/*.so*; do \
	    if [ -L $$i ]; then continue; fi; \
	    chmod 600 $$i; $(TARGET)-strip $$i; chmod 555 $$i; done

# python3: packaging {{{1
$(ZIP_BINarm): .build_install
	make CROSS=arm PIE=yes build_zip
$(ZIP_BINx86): .build_install
	make CROSS=x86 PIE=yes build_zip

build_zip: deps_so := $(deps_so) libssl.so.1.0.0 libcrypto.so.1.0.0
build_zip: deps_so := $(deps_so) libbz2.so.1.0.6 libbz2.so.1.0
build_zip: deps_so := $(deps_so) libreadline.so.6.3 libreadline.so.6
build_zip: deps_so := $(deps_so) libhistory.so.6.3 libhistory.so.6
build_zip: deps_so := $(deps_so) libncursesw.so.5.9 libncursesw.so.5
build_zip: deps_so := $(deps_so) libformw.so.5.9 libformw.so.5
build_zip: deps_so := $(deps_so) libmenuw.so.5.9 libmenuw.so.5
build_zip: deps_so := $(deps_so) libpanelw.so.5.9 libpanelw.so.5
build_zip: deps_so := $(deps_so) libtinfow.so.5.9 libtinfow.so.5
build_zip: tinfo := a/ansi u/unknown v/vt100 v/vt320 x/xterm
build_zip: .build_strip
	@echo non-PIE: build the android libraries/executables
	# make strip_bin CROSS=arm
	@echo "Packing $(ZIPMAIN)"
	rm -f $(ZIPMAIN)
	cd $(PYBIN)/..; zip -g ../$(ZIPMAIN) $(PYBINR)/bin/python3; \
	    zip -g ../$(ZIPMAIN) $(PYBINR)/lib/libpython3.so; \
	    zip -g ../$(ZIPMAIN) $(PYBINR)/lib/libpython$(VER_MAJ)m.so.1.0
	cd $(PYBIN)/..; echo $(ndk_depends) $(PYBINR)/bin/python3
	cd $(PYBIN)/..; deps="$(deps_so)"; \
	  for i in $$deps; do \
	    zip -g ../$(ZIPMAIN) $(PYBINR)/lib/$$i; done
	cd $(PYBIN)/..; \
	  for i in $(tinfo); do \
	    zip -gur ../$(ZIPMAIN) $(PYBINR)/share/terminfo/$$i; done
	cd $(PYBIN)/..; zip -gri"*.so" ../$(ZIPMAIN) $(PYDYNR)
	cd $(PYBIN)/..; \
	  zip -g ../$(ZIPMAIN) \
	    $(PYBINR)/lib/$(PYTHONLIB)/config-$(VER_MAJ)m/Makefile \
	    $(PYBINR)/include/python$(VER_MAJ)m/pyconfig.h

PYEXT_ := python3-extras
PYEXT := $(PYEXT_)/$(PYBINR)
$(ZIPEXTRA): $(ZIPMAIN) .build_host
	echo "Packing $(ZIPEXTRA)"
	rm -f $(ZIPEXTRA)
	rm -rf $(PYEXT_)
	mkdir -p $(PYEXT)/site-packages
	# mkdir -p $(PYEXT)/share/x
	# mkdir -p $(PYEXT)/share/a
	# mkdir -p $(PYEXT)/share/v
	# cp $(PYBINR)/share/terminfo/x/xterm $(PYEXT)/share/x
	# cp $(PYBINR)/share/terminfo/a/ansi $(PYEXT)/share/a
	# cp $(PYBINR)/share/terminfo/v/vt320 $(PYEXT)/share/v
	
	cp python-libs/ase/android.py $(PYEXT)
	cp -r $(CWD)/$(PYBINR)_arm/$(PYBINR)/lib/$(PYTHONLIB)/* $(PYEXT)
	cp -r python-libs/* $(PYEXT)/site-packages
	rm -rf $(PYEXT)/site-packages/ase           # ignore ase
	$(PYTHON_FOR_BUILD) -OO -m compileall -qfb -r 10 -x'/tests*/' $(PYEXT)
	
	cd $(PYEXT_); \
	zip -Dqgr -x "*.so" -x "*.exe" -x "*.a" -x "*/test/*" -x"*/tests/*" \
	                 -x "*/test.pyc" -x "*/tests.pyc" \
	                 -x"*/turtledemo/*" -x"*/tkinter/*" -x"*/idlelib/*" \
	                 -x"*.pyo" -x"*.py" -x"*/__pycache__/*" \
	                 $(CWD)/$@ *

$(ZIPSCRIPTS):
	echo "Packing $(ZIPSCRIPTS)"
	rm -f $(ZIPSCRIPTS)
	cd python-scripts; zip -g ../$@ *

# misc {{{1
patch:
	diff -wuprN Python-$(VERSION) $(PYTHONSRC) \
	  > Python-$(VERSION)-android.patch.new

# python3forandroid uninstall removed all file in andpath directory.
localinstall: andpath := /storage/sdcard0/com.googlecode.python3forandroid
localinstall:
	adb shell rm $(andpath)
	adb shell mkdir $(andpath)
	adb push $(ZIP_BINarm) $(andpath)
	adb push $(ZIPEXTRA) $(andpath)
	adb push $(ZIPSCRIPTS) $(andpath)

src_featured_java = ../android/Common/src/com/googlecode/android_scripting/FeaturedInterpreters.java
update_links:
	sed -i 's/Python .*"/Python 3.6.2"/' $(src_featured_java)
	sed -i 's/\([\/_]\)r[0-9]+/\1r33/' $(src_featured_java)

# vi: ft=Makefile:fdm=marker
# DO NOT DELETE
