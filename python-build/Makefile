VERSION=2.7.10
ndk_build = $(NDK_PATH)/ndk-build
# set -ex
CWD := $(shell pwd)
OUT := $(CWD)/python$(__BUILD_ARCH)
DEBUG=no

RELEASE_VERSION:=$(shell cat LATEST_VERSION)
PYTHONSRC := $(CWD)/python-src
PYTHONNET := Python-$(VERSION).tgz
PYTHONTAR := $(CWD)/Python-$(VERSION).tgz
PYTHONLIB := python$(basename $(VERSION))
PYTHONHST := $(CWD)/host
PYTHONHST_bin := $(PYTHONHST)/bin/python
TAR := tar xvfz
ZIP_BIN_arm := python_$(RELEASE_VERSION).zip
ZIP_BIN_x86 := python_$(RELEASE_VERSION)_x86.zip
ZIP_LIB := python_lib_$(RELEASE_VERSION).zip
ZIP_EXT := python_extras_$(shell cat LATEST_VERSION_EXTRA).zip
ZIP_SCR := python_scripts_$(shell cat LATEST_VERSION_SCRIPTS).zip
ZIP := $(ZIP_BIN_arm) $(ZIP_BIN_x86) $(ZIP_LIB) $(ZIP_EXT) $(ZIP_SCR)

OUT_EXT := $(OUT)/python-ext/python
OUT_INC := $(OUT)/python-lib/python/include/$(PYTHONLIB)

PYBINR := python

.PHONY: build error init cleanall \
        build_copy build_copy_lib build_bin build_zip

ifeq (x$(NDK_PATH),x)
build: error
else
build: $(ZIP)
endif

ifeq (x$(__BUILD_ARCH),x_arm)
    __BUILD_ABI := armeabi
    __BUILD_HST := arm-unknown-linux-androideabi
    __APP_ABI := 
else
ifeq (x$(__BUILD_ARCH),x_x86)
    __BUILD_ABI := x86
    __BUILD_HST := i686-pc-linux-android
    __APP_ABI := APP_ABI=x86
else
endif
endif

JNI_BIN := ./python/obj/local/$(__BUILD_ABI)

cleanall: clean
	rm -f $(PYTHONTAR)

clean:
	make -C openssl clean
	rm -f .build_*
	rm -rf $(PYTHONSRC)
	rm -rf python python_arm python_x86
	rm -rf ncurses readline libffi libcrypt sqlite3 uClibc-0.9.33.2 expat bzip2

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
	PYBINR=$(PYBINR) CWD=$(CWD) make -C openssl build
	touch .build_openssl

.build_host: $(PYTHONTAR)
	# we need to build the host python and host pgen so we can
	# generate the correct grammar and some other stuff
	echo "Decompressing Python-$(VERSION)"
	$(TAR) $(PYTHONTAR)
	mkdir -p $(PYTHONHST)
	cd Python-$(VERSION)/; ./configure --prefix=$(PYTHONHST)
	make -C Python-$(VERSION)
	make -C Python-$(VERSION) install
	cp Python-$(VERSION)/Parser/pgen $(PYTHONHST)
	rm -rf Python-$(VERSION)
	touch .build_host

$(PYTHONSRC): $(PYTHONTAR) .build_host
	$(TAR) $(PYTHONTAR)
	mv Python-$(VERSION) $(PYTHONSRC)
	cd $(PYTHONSRC); \
	for i in $(CWD)/patches/python*.patch; do patch -p1 -i $$i; done

LIBS = site-packages encodings compiler hotshot \
    email email/mime \
    json \
    sqlite3 \
    logging bsddb wsgiref \
    ctypes ctypes/macholib idlelib idlelib/Icons \
    distutils distutils/command \
    multiprocessing multiprocessing/dummy \
    plat-linux2 \
    xml xml/dom xml/etree xml/parsers xml/sax \
    curses setuptools

# libraries {{{1
TARGET_LIBS := .build_misc_sqlite3 \
               .build_misc_ncurses \
               .build_misc_readline \
               .build_misc_bzip2 \
               .build_misc_expat \
               .build_misc_libffi \
               .build_misc_libcrypt
targz = $(subst .tar.gz,,$1)

## download {{{2
sqlite3.tar.gz:
	wget -O $@ http://sqlite.org/2015/sqlite-autoconf-3080900.tar.gz
bzip2-1.0.6.tar.gz:
	wget http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz
expat-2.1.0.tar.gz:
	wget http://downloads.sourceforge.net/project/expat/expat/2.1.0/expat-2.1.0.tar.gz
libffi-3.2.1.tar.gz:
	wget ftp://sourceware.org/pub/libffi/libffi-3.2.1.tar.gz
uClibc-0.9.33.2.tar.bz2:
	wget http://www.uclibc.org/downloads/uClibc-0.9.33.2.tar.bz2
ncurses-5.9.tar.gz:
	wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz
readline-6.3.tar.gz:
	wget ftp://ftp.gnu.org/gnu/readline/readline-6.3.tar.gz

# sqlite3 {{{1
.build_misc_sqlite3: sqlite3.tar.gz
	rm -rf $(call targz,$<)
	tar xfz $<
	mv sqlite-autoconf-3080900 $(call targz,$<)
	cp sqlite3.mk $(call targz,$<)/Android.mk
	touch $@
# bzip2 {{{1
.build_misc_bzip2: bzip2-1.0.6.tar.gz
	rm -rf bzip2
	tar xfz $<
	cd $(call targz,$<); patch -p1 < $(CWD)/../python3-alpha/patches/bzip2-1.0.6-pre.patch
	mv $(call targz,$<) bzip2
	cp bzip2.mk bzip2/Android.mk
	touch $@
# expat {{{1
.build_misc_expat: expat-2.1.0.tar.gz
	rm -rf expat
	tar xfz $<
	mv expat-2.1.0 expat
	cp expat.mk expat/Android.mk
	cd expat; ./configure --build=arm-linux-androideabi
	touch $@
# ffi {{{1
.build_misc_libffi: libffi-3.2.1.tar.gz
	rm -rf libffi
	tar xfz $<
	mv libffi-3.2.1 libffi
	cp libffi.mk libffi/Android.mk
	make -C libffi -f ../libffi.mk build_sep_arm
	make -C libffi -f ../libffi.mk build_sep_x86
	touch $@
# ncurses {{{1
.build_misc_ncurses: ncurses-5.9.tar.gz
	rm -rf ncurses
	tar xfz $<
	mv $(call targz,$<) ncurses
	cp ncurses.mk ncurses/Android.mk
	cd ncurses; for i in ../patches/ncurses*; do patch -p1 -i $$i; done
	make -C ncurses -f Android.mk build_arm TARGET_ARCH_ABI=armeabi \
	                                        NCURSES_PATH=$(CWD)/ncurses
	make -C ncurses -f Android.mk build_x86 TARGET_ARCH_ABI=x86 \
	                                        NCURSES_PATH=$(CWD)/ncurses
	touch $@
# readline {{{1
.build_misc_readline: readline-6.3.tar.gz .build_misc_ncurses 
	rm -rf readline
	tar xfz $<
	mv $(call targz,$<) readline
	cp readline.mk readline/Android.mk
	cd readline; patch -p1 < ../patches/readline-6.3-pre.patch
	make -C readline -f Android.mk build_arm TARGET_ARCH_ABI=armeabi \
	             NCURSES_PATH=$(CWD)/ncurses READLINE_PATH=$(CWD)/readline
	make -C readline -f Android.mk build_x86 TARGET_ARCH_ABI=x86 \
	             NCURSES_PATH=$(CWD)/ncurses READLINE_PATH=$(CWD)/readline
	touch $@
# libcrypt {{{1
.build_misc_libcrypt: uClibc-0.9.33.2.tar.bz2
	rm -rf $(subst .tar.bz2,,$<)
	rm -rf libcrypt
	tar xfj $<
	mv $(subst .tar.bz2,,$<)/libcrypt .
	cp $(subst .tar.bz2,,$<)/include/crypt.h libcrypt
	cp libcrypt.mk libcrypt/Android.mk
	
	# rm -rf pwd_grp
	# mv $(subst .tar.bz2,,$<)/libc/pwd_grp .
	# cp pwd_grp.mk pwd_grp/Android.mk
	
	touch $@

# copy standard scripts and include {{{1
build_copy:
	[ x$(__BUILD_ARCH) != x ]       # stop at arch is not set.
	rm -rf $(OUT)/python-ext
	
	cd python-libs; ./setuptools.sh
	
	for lib in $(LIBS); do \
	    if [ -n "$$(find $(PYTHONSRC)/Lib/$$lib -maxdepth 1 -type f)" ]; then \
	        mkdir -p $(OUT_EXT)/$$lib; \
	        cp $$(find $(PYTHONSRC)/Lib/$$lib -maxdepth 1 -type f) \
	           $(OUT_EXT)/$$lib; \
	    fi; \
	done
	
	cd $(PYTHONSRC); $(PYTHONHST_bin) Lib/sysconfig.py --generate-posix-vars
	cp $(PYTHONSRC)/build/lib*/_sysconfigdata.py $(OUT_EXT)/
	cp $$(find $(PYTHONSRC)/Lib/ -maxdepth 1 -type f) $(OUT_EXT)/
	# Copy in ASE's Android module. (this code was moved from build.py)
	cp python-libs/ase/android.py $(OUT_EXT)

build_copy_lib:
	[ x$(__BUILD_ARCH) != x ]       # stop at arch is not set.
	rm -rf $(OUT)/python-lib
	mkdir -p $(OUT_INC)
	cp -r $(PYTHONSRC)/Include/* $(OUT_INC)/
	cp $(PYTHONSRC)/pyconfig.h $(OUT_INC)/


# build python {{{1
build_bin:
	mkdir -p $(JNI_BIN)
	
	cd $(CWD)/python; \
	$(CWD)/host/pgen $(CWD)/python-src/Grammar/Grammar \
	    $(CWD)/python-src/Include/graminit.h \
	    $(CWD)/python-src/Python/graminit.c
	cd $(CWD)/python; NDK_MODULE_PATH=$(shell pwd) $(ndk_build) $(__APP_ABI)
	
	for i in libssl.so libssl.1.0 libcrypto.so libcrypto.so.1.0 \
	         libncurses.so libpanel.so libtinfo.so \
	         libreadline.so libhistory.so \
	         libffi.so.6.0.0 libffi.so; do \
	    rm -f $(JNI_BIN)/$$i; done
	cp openssl/.build_$(__BUILD_ABI)/libssl.so.1.0.0 $(JNI_BIN)
	cp openssl/.build_$(__BUILD_ABI)/libcrypto.so.1.0.0 $(JNI_BIN)
	cp libffi/$(__BUILD_HST)/.libs/libffi.so.6 $(JNI_BIN)
	cp ncurses/lib-$(__BUILD_ABI)/python/lib/libncurses.so.5 $(JNI_BIN)
	cp ncurses/lib-$(__BUILD_ABI)/python/lib/libtinfo.so.5 $(JNI_BIN)
	cp ncurses/lib-$(__BUILD_ABI)/python/lib/libpanel.so.5 $(JNI_BIN)
	cp readline/lib-$(__BUILD_ABI)/lib/libreadline.so.6 $(JNI_BIN)
	cp readline/lib-$(__BUILD_ABI)/lib/libhistory.so.6 $(JNI_BIN)
	touch .build_bin$(__BUILD_ARCH)

.build_bin_arm: $(PYTHONSRC) .build_openssl $(TARGET_LIBS)
	@echo PIE: build the android libraries/executables
	make build_bin __ENABLE_PIE=yes __BUILD_ARCH=_arm
	
.build_bin_x86: $(PYTHONSRC) .build_openssl $(TARGET_LIBS)
	@echo PIE: build the android libraries/executables
	make build_bin __ENABLE_PIE=yes __BUILD_ARCH=_x86

# packaging {{{1
# zipup: binary: copy out all the needed files
$(ZIP_BIN_arm): .build_bin_arm
	rm -rf $(OUT)_arm/python-bin
	$(PYTHONHST_bin) build.py pie bin

$(ZIP_BIN_x86): .build_bin_x86
	rm -rf $(OUT)_x86/python-bin
	$(PYTHONHST_bin) build.py pie bin x86

# zipup: scripts or another
$(ZIP_LIB): $(ZIP_BIN_arm)
	__BUILD_ARCH=_arm make build_copy_lib
	$(PYTHONHST_bin) build.py pie lib

$(ZIP_EXT): $(PYTHONSRC)
	# optimize the python code for the light size of zip.
	__BUILD_ARCH=_arm make build_copy
	$(PYTHONHST_bin) -OO build.py pie extra

$(ZIP_SCR): python-scripts/*.py
	$(PYTHONHST_bin) build.py pie scripts

# end of file {{{1
# vi: ft=make:fdm=marker:et:ts=4:nowrap
