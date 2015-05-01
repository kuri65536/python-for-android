
.PHONY: build build_config build_bin build_install build_strip \
        error init clean_output cleanall \
        patch build_misc_sqlite3 build_misc_ncurses \
        build_misc_readline build_misc_bzip2 strip_bin

# build settings section 1 {{{1
VERSION=3.4.3
# set -ex
CWD := $(shell pwd)
DEBUG=no

RELEASE_VERSION:=$(shell cat LATEST_VERSION)
PYTHONNET := Python-$(VERSION).tgz
PYTHONTAR := $(CWD)/Python-$(VERSION).tgz
PYTHONLIB := python$(basename $(VERSION))
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
build: $(ZIP)
endif

error:
	@echo please set NDK_PATH to android-ndk-r10d or later::
	@echo "  $$ NDK_PATH=/path/to/android-ndk-r10d make build"

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

    PYTHONSRC := ./python-src_arm
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

    PYTHONSRC := ./python-src_x86
    SFX := _x86
    ZIPMAIN := $(ZIP_BINx86)
endif

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

    export HOSTPGEN = $(HOSTPYTHON)/bin/hostpgen

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
	make clean_work CROSS=arm PIE=yes
	make clean_work CROSS=x86 PIE=yes
	rm -rf python3_extras
	rm -f .build_*
clean_work:
	rm -rf ncurses-5.9$(SFX)
	rm -rf bzip2-1.0.6$(SFX)
	rm -rf readline-6.3$(SFX)
	rm -rf sqlite3$(SFX)
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
	tar xfz $<
	mv $(call targz,$<) $(call targz,$<)$(SFX)
	cd $(call targz,$<)$(SFX); \
	  ./configure --host=$(HOSTARCH) --build=$(BUILDARCH) \
	  --prefix=$(PYBIN) \
	  --without-ada --without-cxx --without-manpages \
	  --without-progs --without-tests \
	  --with-termlib --enable-termcap --enable-widec \
	  --disable-database --disable-home-terminfo
	cd $(call targz,$<)$(SFX); patch -p1 < $(CWD)/patches/$(call targz,$<).patch
	make -C $(call targz,$<)$(SFX)
	make -C $(call targz,$<)$(SFX) install
	@echo Fix symlinks for Python _curses and _curses_panel extensions.
	cd $(PYBIN)/include; cp ncursesw/*.h .

## readline {{{2
.build_misc_readline: readline-6.3.tar.gz
	make $(subst .,,$@) CROSS=arm PIE=yes
	make $(subst .,,$@) CROSS=x86 PIE=yes
	touch $@
build_misc_readline: readline-6.3.tar.gz
	tar xfz $<
	cd $(call targz,$<); patch < $(CWD)/patches/readline-6.3-pre.patch
	mv $(call targz,$<) $(call targz,$<)$(SFX)
	cd $(call targz,$<)$(SFX); \
	   autoreconf -i; \
	   bash_cv_wcwidth_broken=no \
	   CFLAGS="$(CFLAGS) -DANDROID" \
	   ./configure --host=$(HOSTARCH) --build=$(BUILDARCH) \
	   --prefix=$(PYBIN) \
	   --disable-shared --with-curses=$(CWD)/ncurses-5.9$(SFX)
	make -C $(call targz,$<)$(SFX)
	make -C $(call targz,$<)$(SFX) install

## sqlite3 {{{2
.build_misc_sqlite3: sqlite3.tar.gz
	make $(subst .,,$@) CROSS=arm PIE=yes
	make $(subst .,,$@) CROSS=x86 PIE=yes
	touch $@
build_misc_sqlite3: sqlite3.tar.gz
	tar xfz $<
	mv sqlite-autoconf-3080803 $(call targz,$<)$(SFX)
	cd $(call targz,$<)$(SFX); \
	   ./configure --host=$(HOSTARCH) --build=$(BUILDARCH) --prefix=$(PYBIN) \
	   --disable-shared
	make -C $(call targz,$<)$(SFX)
	make -C $(call targz,$<)$(SFX) install

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
build_misc_bzip2: bzip2-1.0.6.tar.gz
	tar xfz $<
	cd $(call targz,$<); patch -p1 < $(CWD)/patches/bzip2-1.0.6-pre.patch
	mv $(call targz,$<) $(call targz,$<)$(SFX)
	PREFIX=$(PYBIN)\
	  CC=$(TARGET)-gcc RANLIB=$(TARGET)-ranlib \
	  make -C $(call targz,$<)$(SFX) -f Makefile-libbz2_so
	mkdir -p $(PYBIN)/lib
	cp $(call targz,$<)$(SFX)/*.so* $(PYBIN)/lib

# python3: download and build for current host  {{{1
$(PYTHONTAR):
	@echo "Building Python VM For Android Release $(RELEASE_VERSION)"
	if [ ! -f $(CWD)/Python-$(VERSION).tar.bz2 ]; then \
	    URL="http://www.python.org/ftp/python/$(VERSION)/$(PYTHONNET)"; \
	    wget -O $(PYTHONTAR) $$URL; \
	fi

.build_host: $(PYTHONTAR)
	# we need to build the host python and host pgen so we can
	# generate the correct grammar and some other stuff
	echo "Decompressing Python-$(VERSION)"
	$(TAR) $(PYTHONTAR)
	mkdir -p $(HOSTPYTHON)
	cd Python-$(VERSION)/; ./configure --prefix=$(HOSTPYTHON)
	make -C Python-$(VERSION)
	make -C Python-$(VERSION) Parser/pgen
	make -C Python-$(VERSION) install
	cp Python-$(VERSION)/Parser/pgen $(HOSTPYTHON)/bin/hostpgen
	rm -rf Python-$(VERSION)
	touch .build_host

# python3: patching-configure-build {{{1
$(CWD)/patches/python-*.patch:
	echo
.build_src: $(PYTHONTAR) $(CWD)/patches/python-*.patch
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
	            --prefix=$(PYBIN) --enable-shared --with-ensurepip=no

.build_bin: .build_config
	make build_bin CROSS=arm PIE=yes
	make build_bin CROSS=x86 PIE=yes
	touch .build_bin
build_bin: .build_openssl .build_misc
	CROSS_COMPILE_TARGET=yes make -C $(PYTHONSRC)

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

build_zip: .build_strip
	@echo non-PIE: build the android libraries/executables
	# make strip_bin CROSS=arm
	@echo "Packing $(ZIPMAIN)"
	rm -f $(ZIPMAIN)
	cd $(PYBIN)/..; zip -g ../$(ZIPMAIN) $(PYBINR)/bin/python3; \
	    zip -g ../$(ZIPMAIN) $(PYBINR)/lib/libpython3.so; \
	    zip -g ../$(ZIPMAIN) $(PYBINR)/lib/libpython3.4m.so
	cd $(PYBIN)/..; echo $(ndk_depends) $(PYBINR)/bin/python3
	cd $(PYBIN)/..; deps="libssl.so.1.0.0 libcrypto.so.1.0.0"; \
	  for i in $$deps; do \
	    zip -g ../$(ZIPMAIN) $(PYBINR)/lib/$$i; done
	cd $(PYBIN)/..; zip -gri"*.so" ../$(ZIPMAIN) $(PYDYNR)
	cd $(PYBIN)/..; zip -g ../$(ZIPMAIN) $(PYBINR)/lib/$(PYTHONLIB)/config-3.4m/Makefile \
	          $(PYBINR)/include/python3.4m/pyconfig.h

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
	$(PYTHON_FOR_BUILD) -OO -m compileall -qf -x'tests*/.*' $(PYEXT) || echo
	# FIXME: complex shell script: change __cache__/.pyo to .pyc
	find $(PYEXT) -name *.pyo -exec sh -c \
	    'cp $$0 $$(echo $$0 | sed "s/\/__pycache__//" | sed s/.cpython-34.pyo/.pyc/)' {} \;
	
	cd $(PYEXT_); \
	zip -Dqgrx"*.so" -x"test/*" -x"*/test/*" -x"*/tests/*" \
	                 -x"*/turtledemo/*" -x"*/tkinter/*" -x"*/idlelib/*" \
	                 -x"*/ensurepip/*" \
	                 -x"*.pyo" -x"*.py" -x"*/__pycache__/*" \
	                 -x"*.so*" -x"*.exe" -x"*.a" $(CWD)/$@ *
	# zip -d $@ "*.pc" "*pkgconfig*" "*/libpython3.4m.a" \
	#           "*.a" "bin/*" "*.la"

$(ZIPSCRIPTS):
	echo "Packing $(ZIPSCRIPTS)"
	rm -f $(ZIPSCRIPTS)
	cd python-scripts; zip -g ../$@ *

# misc {{{1
patch:
	diff -wuprN Python-$(VERSION) $(PYTHONSRC) \
	  > Python-$(VERSION)-android.patch.new

# vi: ft=Makefile:fdm=marker
