VERSION=3.4.3
ndk_build = $(NDK_PATH)/ndk-build
# set -ex
CWD := $(shell pwd)
OUT := $(CWD)/output
DEBUG=no

RELEASE_VERSION:=$(shell cat LATEST_VERSION)
PYBINR := python3
PYBIN := $(CWD)/$(PYBINR)
PYTHONSRC := ./python-src
PYTHONNET := Python-$(VERSION).tgz
PYTHONTAR := $(CWD)/Python-$(VERSION).tgz
PYTHONLIB := python$(basename $(VERSION))
PYTHON_FOR_BUILD := $(CWD)/host/bin/python3
PYLIB := $(PYBINR)/lib/$(PYTHONLIB)
TAR := tar xfz

ZIPMAIN := python3_$(RELEASE_VERSION).zip
ZIPEXTRA := python3_extras_$(shell cat LATEST_VERSION_EXTRA).zip
ZIPSCRIPTS := python3_scripts_$(shell cat LATEST_VERSION_SCRIPTS).zip
ZIP := $(ZIPMAIN) \
       $(ZIPEXTRA) \
       $(ZIPSCRIPTS) \
       $(patsubst .zip,_x86.zip,$(ZIPMAIN))
ZIP_PIE := $(patsubst .zip,_pie.zip,$(ZIPMAIN)) \
           $(patsubst .zip,_x86_pie.zip,$(ZIPMAIN))

OUT_LIB := $(OUT)/usr/lib/$(PYTHONLIB)

.PHONY: build build_config build_bin error init clean_output cleanall \
        patch .build_misc_sqlite3_arm .build_misc_ncurses_arm \
        .build_misc_readline_arm .build_misc_bzip2_arm strip_bin

ifeq (x$(NDK_PATH),x)
build: error
else
build: $(ZIP) $(ZIP_PIE)
endif

ifeq (x$(host),x)
# check host variable: linux-x86_64, linux-x86 or darwin-x86
host = $(shell uname -s | tr A-Z a-z)-$(shell uname -m)
endif

# build variables for cross-compile.
ifeq (x$(CROSS),xarm)
TARGET := arm-linux-androideabi
tabi := $(TARGET)-4.9
# ANDROID_API := android-4     # TODO: missing waitid
ANDROID_API := android-9
ANDROID_TOOLCHAIN := $(NDK_PATH)/toolchains/$(tabi)/prebuilt/$(host)/bin
export PATH := $(ANDROID_TOOLCHAIN):$(PATH)
_ANDROID_ARCH = arch-arm
_ANDROID_EABI = $(tabi)
export CFLAGS = --sysroot=$(ANDROID_NDK_SYSROOT) \
                -I$(CWD)/sqlite3 -I$(CWD)/bzip2-1.0.6 \
                -I$(CWD) -I$(PYBIN)/include -I$(PYBIN)/include/ncurses
# -I$(CWD): for #include <readline/readline.h>
export LDFLAGS = --sysroot=$(ANDROID_NDK_SYSROOT) \
                 -L$(PYBIN)/lib
# CXX = ${TARGET}-g++
# AR = ${TARGET}-ar
# RANLIB=${TARGET}-ranlib
MACHINE = armv7
export ARCH = arm
HOSTPGEN = $(PYTHONSRC)/Parser/hostpgen
BLDSHARED = arm-linux-androideabi-gcc -shared
CROSS_COMPILE = arm-linux-androideabi-
CROSS_COMPILE_TARGET = arm
HOSTARCH = arm-linux-androideabi
BUILDARCH = x86_64-linux-gnu
endif

ANDROID_NDK_ROOT := $(NDK_PATH)
ANDROID_SYSROOT = $(NDK_PATH)/platforms/$(ANDROID_API)/$(_ANDROID_ARCH)
SYSROOT = $(ANDROID_SYSROOT)
NDK_SYSROOT = $(ANDROID_SYSROOT)
ANDROID_NDK_SYSROOT = $(ANDROID_SYSROOT)
ANDROID_DEV = $(ANDROID_SYSROOT)/usr


cleanall: clean
	rm -f $(PYTHONTAR)

clean:
	rm -rf sqlite3
	make -C readline-6.3 clean
	make -C ncurses-5.9 clean
	make -C bzip2-1.0.6 clean
	make -C openssl clean
	rm -f .build_*
	rm -rf $(PYTHONSRC)

error:
	@echo please set NDK_PATH to android-ndk-r10d or later::
	@echo "  $$ NDK_PATH=/path/to/android-ndk-r10d make build"


$(PYTHONTAR):
	@echo "Building Python VM For Android Release $(RELEASE_VERSION)"
	if [ ! -f $(CWD)/Python-$(VERSION).tar.bz2 ]; then \
	    URL="http://www.python.org/ftp/python/$(VERSION)/$(PYTHONNET)"; \
	    wget -O $(PYTHONTAR) $$URL; \
	fi

.build_openssl: $(PYTHONTAR)
	make -C openssl build
	mkdir -p $(PYBIN)/lib
	cp -dp openssl/.build_arm/lib*.so* $(PYBIN)/lib
	touch .build_openssl


#### libraries
sqlite3.tar.gz:
	wget -O $@ https://sqlite.org/2015/sqlite-autoconf-3080803.tar.gz
ncurses-5.9.tar.gz:
	wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz
readline-6.3.tar.gz:
	wget ftp://ftp.gnu.org/gnu/readline/readline-6.3.tar.gz
# zlib-1.2.8.tar.gz:
# 	wget http://zlib.net/zlib-1.2.8.tar.gz
bzip-1.0.6.tar.gz:
	wget http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz


targz = $(subst .tar.gz,,$1)

.build_misc_ncurses: ncurses-5.9.tar.gz
	tar xfz $<
	make $@_arm CROSS=arm
	touch $@
.build_misc_ncurses_arm: ncurses-5.9.tar.gz
	cd $(call targz,$<); \
	  ./configure --host=$(HOSTARCH) --target=$(HOSTARCH) --prefix=$(PYBIN) \
	  --enable-shared --without-ada --without-cxx --without-manpages \
	  --without-cxx-binding --without-progs --without-tests \
	  --with-termlib --enable-termcap --enable-widec \
	  --disable-database --disable-home-terminfo
	cd $(call targz,$<); patch -p1 < android.patch
	make -C $(call targz,$<)
	make -C $(call targz,$<) install
	@echo Fix symlinks for Python _curses and _curses_panel extensions.
	cd $(call targz,$<)
	  ln -s ncursesw/curses.h $(PYBIN)/include/curses.h
	  ln -s ncursesw/panel.h $(PYBIN)/include/panel.h

.build_misc_readline: readline-6.3.tar.gz
	tar xfz $<
	cd $(call targz,$<); patch < fix.patch
	make $@_arm CROSS=arm
	touch $@
.build_misc_readline_arm: readline-6.3.tar.gz
	cd $(call targz,$<); \
	   bash_cv_wcwidth_broken=no \
	   CFLAGS="$(CFLAGS) -I$(CWD)/ncurses-5.9/include" \
	   ./configure --host=$(HOSTARCH) --target=$(HOSTARCH) --prefix=$(PYBIN) \
	   --disable-shared --with-curses=$(CWD)/ncurses-5.9
	cd $(call targz,$<); patch < android.patch
	make -C $(call targz,$<)
	make -C $(call targz,$<) install
	# ln -sf $(call targz,$<) $(patsubst -6.3,,$(call targz,$<))
	touch $@

.build_misc_sqlite3: sqlite3.tar.gz
	tar xfz $<
	mv sqlite-autoconf-3080803 $(call targz,$<)
	make $@_arm CROSS=arm
	touch $@
.build_misc_sqlite3_arm: sqlite3.tar.gz
	cd $(call targz,$<); \
	   ./configure --host=$(HOSTARCH) --target=$(HOSTARCH) --prefix=$(PYBIN) \
	   --disable-shared
	make -C $(call targz,$<)
	make -C $(call targz,$<) install

# .build_misc_zlib: zlib-1.2.8.tar.gz
# 	tar xfz $<
# 	make $@_arm CROSS=arm
# 	touch $@
# .build_misc_zlib_arm: zlib-1.2.8.tar.gz
# 	make -C $(call targz,$<)

.build_misc_bzip2: bzip2-1.0.6.tar.gz
	tar xfz $<
	cd $(call targz,$<); patch -p1 < pre.patch
	make $@_arm CROSS=arm
	touch $@
.build_misc_bzip2_arm: bzip2-1.0.6.tar.gz
	PREFIX=$(PYBIN)\
	  CC=$(TARGET)-gcc RANLIB=$(TARGET)-ranlib \
	  make -C $(call targz,$<) -f Makefile-libbz2_so
	mkdir -p $(PYBIN)/lib
	cp $(call targz,$<)/*.so* $(PYBIN)/lib

.build_misc: .build_misc_sqlite3 .build_misc_ncurses \
             .build_misc_readline .build_misc_bzip2
	touch .build_misc

.build_host: HOSTPYTHON:=$(dir $(dir PYTHON_FOR_BUILD))
.build_host: $(PYTHONTAR)
	# we need to build the host python and host pgen so we can
	# generate the correct grammar and some other stuff
	echo "Decompressing Python-$(VERSION)"
	$(TAR) $(PYTHONTAR)
	mkdir -p $(HOSTPYTHON)
	cd Python-$(VERSION)/; ./configure --prefix=$(HOSTPYTHON)
	make -C Python-$(VERSION)
	make -C Python-$(VERSION) install
	cp Python-$(VERSION)/Parser/pgen $(HOSTPYTHON)
	rm -rf Python-$(VERSION)
	touch .build_host

$(CWD)/Python-$(VERSION)-android.patch:
	echo
.build_src: $(PYTHONTAR) $(CWD)/Python-$(VERSION)-android.patch
	rm -rf $(PYTHONSRC)
	$(TAR) $(PYTHONTAR)
	mv Python-$(VERSION) $(PYTHONSRC)
	cd $(PYTHONSRC); \
	  for p in $(CWD)/patches/*.patch; do patch -p1 -i $$p; done
	touch .build_src


.build_config: .build_src .build_misc
	make build_config CROSS=arm
	touch .build_config
build_config:
	# @echo PATH: "'$$PATH'"
	@echo CFLAGS: "'$$CFLAGS'"
	cd $(PYTHONSRC); CONFIG_SITE=`pwd`/config.site \
	./configure --host=$(TARGET) --build=x86_64-linux-gnu \
	            --prefix=$(PYBIN) --enable-shared --with-ensurepip=no

.build_bin: .build_config
	make build_bin CROSS=arm
	touch .build_bin
build_bin: .build_openssl .build_misc
	make -C $(PYTHONSRC)
	make -C $(PYTHONSRC) install
strip_bin:
	$(TARGET)-strip $(PYBIN)/bin/python3
	for i in $(PYBIN)/lib/*.so*; do $(TARGET)-strip $$i; done
	for i in $(PYLIB)/lib-dynload/*.so*; do $(TARGET)-strip $$i; done


$(ZIPMAIN): .build_bin
	@echo non-PIE: build the android libraries/executables
	# make strip_bin CROSS=arm
	@echo "Packing $(ZIPMAIN)"
	rm -f $(ZIPMAIN)
	zip -g $@ $(PYBINR)/bin/python3
	zip -g $@ $(PYBINR)/lib/libpython3.so
	deps=$$($(NDK_PATH)/ndk-depends $(PYBINR)/bin/python3 \
	  | grep -v ^python3$$ | grep -v -e \.so$$ ); \
	  for i in $$deps; do \
	    zip -g $@ $(PYBINR)/lib/$$i; done
	zip -gri"*.so" $@ $(PYBINR)/lib/$(PYTHONLIB)/lib-dynload
	zip -g $@ $(PYBINR)/lib/$(PYTHONLIB)/config-3.4m/Makefile \
	          $(PYBINR)/include/python3.4m/pyconfig.h

PYEXT_ := python3-extras
PYEXT := $(PYEXT_)/$(PYBINR)
$(ZIPEXTRA): $(ZIPMAIN)
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
	cp -r $(PYLIB)/* $(PYEXT)
	cp -r python-libs/* $(PYEXT)/site-packages
	# $(PYTHON_FOR_BUILD) -m compileall $(PYEXT) || echo
	
	cd $(PYEXT_); \
	zip -grx"*.so" -x"*.so.*" -x"test/*" -x"*/test/*" -x"*.pyc" \
	               -x"*.pyo" $(CWD)/$@ *
	zip -d $@ "*.pc" "*pkgconfig*" "*/libpython3.4m.a" \
	          "*/test/*" "*.exe" "*.a" "bin/*" "*.la"

$(ZIPSCRIPTS):
	echo "Packing $(ZIPSCRIPTS)"
	rm -f $(ZIPSCRIPTS)
	cd python-scripts; zip -g ../$@ *


patch:
	diff -wuprN Python-$(VERSION) $(PYTHONSRC) \
	  > Python-$(VERSION)-android.patch.new

