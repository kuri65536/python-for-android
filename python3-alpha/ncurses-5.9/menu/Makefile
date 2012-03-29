# $Id: Makefile.in,v 1.54 2010/11/27 21:45:27 tom Exp $
##############################################################################
# Copyright (c) 1998-2009,2010 Free Software Foundation, Inc.                #
#                                                                            #
# Permission is hereby granted, free of charge, to any person obtaining a    #
# copy of this software and associated documentation files (the "Software"), #
# to deal in the Software without restriction, including without limitation  #
# the rights to use, copy, modify, merge, publish, distribute, distribute    #
# with modifications, sublicense, and/or sell copies of the Software, and to #
# permit persons to whom the Software is furnished to do so, subject to the  #
# following conditions:                                                      #
#                                                                            #
# The above copyright notice and this permission notice shall be included in #
# all copies or substantial portions of the Software.                        #
#                                                                            #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    #
# THE ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        #
# DEALINGS IN THE SOFTWARE.                                                  #
#                                                                            #
# Except as contained in this notice, the name(s) of the above copyright     #
# holders shall not be used in advertising or otherwise to promote the sale, #
# use or other dealings in this Software without prior written               #
# authorization.                                                             #
##############################################################################
#
# Author: Thomas E. Dickey 1996-on
#
# Makefile for menu source code.
#
# This makes the following:
#	libraries (normal/debug/profile/shared)
#
# The variable 'srcdir' refers to the source-distribution, and can be set with
# the configure script by "--srcdir=DIR".
#
# The rules are organized to produce the libraries for the configured models,

# turn off _all_ suffix rules; we'll generate our own
.SUFFIXES:

SHELL		= /bin/sh

THIS		= Makefile

x		= 
o		= .o

MODEL		= shared
DESTDIR		= 
srcdir		= .
prefix		= /home/robbie/python-for-android/python3-alpha/thirdparty
exec_prefix	= ${prefix}
bindir		= ${exec_prefix}/bin
libdir		= ${exec_prefix}/lib
includedir	= ${prefix}/include/ncurses

LIBTOOL		= 
LIBTOOL_CLEAN	= 
LIBTOOL_COMPILE	= 
LIBTOOL_LINK	= ${CC}
LIBTOOL_INSTALL	= 
LIBTOOL_UNINSTALL = 
LT_UNDEF	= 

INSTALL		= /usr/bin/install -c
INSTALL_LIB	= /usr/bin/install -c -m 644
INSTALL_PROG	= ${INSTALL}
INSTALL_DATA	= ${INSTALL} -m 644

AR		= arm-linux-androideabi-ar
ARFLAGS		= -curv
AWK		= mawk
LD		= arm-linux-androideabi-ld
LN_S		= ln -s -f

CTAGS		= 
ETAGS		= 

CC		= arm-linux-androideabi-gcc
CPP		= arm-linux-androideabi-gcc -E
CFLAGS		= -O2 --param max-inline-insns-single=1200

CPPFLAGS	= -I../ncurses -DHAVE_CONFIG_H  -DNDEBUG -I. -I../include -I${includedir}

CCFLAGS		= $(CPPFLAGS) $(CFLAGS)

CFLAGS_LIBTOOL	= $(CCFLAGS)
CFLAGS_NORMAL	= $(CCFLAGS)
CFLAGS_DEBUG	= $(CCFLAGS) -g -DTRACE
CFLAGS_PROFILE	= $(CCFLAGS) -pg
CFLAGS_SHARED	= $(CCFLAGS) -fPIC

CFLAGS_DEFAULT	= $(CFLAGS_SHARED)

LINK		= $(LIBTOOL_LINK)
LDFLAGS		=   

SHLIB_DIRS	= -L../lib
SHLIB_LIST	= $(SHLIB_DIRS) -lncurses 

MK_SHARED_LIB	= ${CC} ${CFLAGS} -shared -Wl,-soname,`basename $@ .${REL_VERSION}`.${ABI_VERSION},-stats,-lc -o $@

NCURSES_MAJOR	= 5
NCURSES_MINOR	= 9
REL_VERSION	= 5.9
ABI_VERSION	= 5

RANLIB		= arm-linux-androideabi-ranlib

LIBRARIES	=  ../lib/libmenu.so.${REL_VERSION} ../lib/libmenu.a ../lib/libmenu_g.a

LINT		= 
LINT_OPTS	= 
LINT_LIBS	= -lmenu -lncurses 

AUTO_SRC	= \
		../include/menu.h \
		../include/eti.h \
		../include/mf_common.h

################################################################################
all \
libs \
install ::	$(AUTO_SRC) $(LIBRARIES)

sources :	$(AUTO_SRC)

$(DESTDIR)$(bindir) \
$(DESTDIR)$(libdir) :
	mkdir -p $@

# make copies to simplify include-paths while still keeping menu's include
# file in this directory.
../include/menu.h : $(srcdir)/menu.h
	-rm -f $@
	cp $(srcdir)/menu.h $@
../include/eti.h : $(srcdir)/eti.h
	-rm -f $@
	cp $(srcdir)/eti.h $@
../include/mf_common.h : $(srcdir)/mf_common.h
	-rm -f $@
	cp $(srcdir)/mf_common.h $@

HEADER_DEPS = \
	$(srcdir)/menu.priv.h \
	$(AUTO_SRC) \
	../include/curses.h

tags:
	$(CTAGS) *.[ch]

#TAGS:
#	$(ETAGS) *.[ch]

mostlyclean ::
	-rm -f core tags TAGS *~ *.bak *.i *.ln *.atac trace

clean :: mostlyclean
	-rm -f $(AUTO_SRC)

distclean :: clean
	-rm -f Makefile

realclean :: distclean

###############################################################################
# The remainder of this file is automatically generated during configuration
###############################################################################

# generated by mk-0th.awk
#   libname:    menu
#   subsets:    ticlib+termlib+ext_tinfo+base+ext_funcs

.SUFFIXES: .c .cc .h .i .ii
.c.i :
	$(CPP) $(CPPFLAGS) $< >$@
.cc.ii :
	$(CPP) $(CPPFLAGS) $< >$@
.h.i :
	$(CPP) $(CPPFLAGS) $< >$@

C_SRC = \
	$(srcdir)/m_attribs.c \
	$(srcdir)/m_cursor.c \
	$(srcdir)/m_driver.c \
	$(srcdir)/m_format.c \
	$(srcdir)/m_global.c \
	$(srcdir)/m_hook.c \
	$(srcdir)/m_item_cur.c \
	$(srcdir)/m_item_nam.c \
	$(srcdir)/m_item_new.c \
	$(srcdir)/m_item_opt.c \
	$(srcdir)/m_item_top.c \
	$(srcdir)/m_item_use.c \
	$(srcdir)/m_item_val.c \
	$(srcdir)/m_item_vis.c \
	$(srcdir)/m_items.c \
	$(srcdir)/m_new.c \
	$(srcdir)/m_opts.c \
	$(srcdir)/m_pad.c \
	$(srcdir)/m_pattern.c \
	$(srcdir)/m_post.c \
	$(srcdir)/m_req_name.c \
	$(srcdir)/m_scale.c \
	$(srcdir)/m_spacing.c \
	$(srcdir)/m_sub.c \
	$(srcdir)/m_trace.c \
	$(srcdir)/m_userptr.c \
	$(srcdir)/m_win.c

# Producing llib-lmenu is time-consuming, so there's no direct-dependency for
# it in the lintlib rule.  We'll only remove in the cleanest setup.
clean ::
	rm -f llib-lmenu.*

realclean ::
	rm -f llib-lmenu

llib-lmenu : $(C_SRC)
	cproto -a -l -DNCURSES_ENABLE_STDBOOL_H=0 -DLINT $(CPPFLAGS) $(C_SRC) >$@

lintlib :
	sh $(srcdir)/../misc/makellib menu $(CPPFLAGS)
lint :
	$(LINT) $(LINT_OPTS) $(CPPFLAGS) $(C_SRC) $(LINT_LIBS)

# generated by mk-1st.awk (subset=ticlib+termlib+ext_tinfo+base+ext_funcs)
#  name:          menu
#  traces:        DEBUG
#  MODEL:         SHARED
#  model:         obj_s
#  prefix:        lib
#  suffix:        .so
#  subset:        ticlib+termlib+ext_tinfo+base+ext_funcs
#  ShlibVer:      rel
#  ShlibVerInfix: no
#  SymLink:       ln -s -f
#  TermlibRoot:   ncurses
#  TermlibSuffix: .so
#  ReLink:        yes
#  DoLinks:       yes
#  rmSoLocs:      no
#  ldconfig:      :
#  overwrite:     no
#  depend:        ../include/ncurses_cfg.h ./menu.priv.h
#  host:          arm-unknown-linux-androideabi

SHARED_OBJS = \
	../obj_s/m_attribs$o \
	../obj_s/m_cursor$o \
	../obj_s/m_driver$o \
	../obj_s/m_format$o \
	../obj_s/m_global$o \
	../obj_s/m_hook$o \
	../obj_s/m_item_cur$o \
	../obj_s/m_item_nam$o \
	../obj_s/m_item_new$o \
	../obj_s/m_item_opt$o \
	../obj_s/m_item_top$o \
	../obj_s/m_item_use$o \
	../obj_s/m_item_val$o \
	../obj_s/m_item_vis$o \
	../obj_s/m_items$o \
	../obj_s/m_new$o \
	../obj_s/m_opts$o \
	../obj_s/m_pad$o \
	../obj_s/m_pattern$o \
	../obj_s/m_post$o \
	../obj_s/m_req_name$o \
	../obj_s/m_scale$o \
	../obj_s/m_spacing$o \
	../obj_s/m_sub$o \
	../obj_s/m_userptr$o \
	../obj_s/m_win$o

$(SHARED_OBJS) : ../include/ncurses_cfg.h ./menu.priv.h

../lib/libmenu.so.$(REL_VERSION) : \
		../lib \
		$(SHARED_OBJS)
	@echo linking $@
	$(MK_SHARED_LIB) $(SHARED_OBJS) $(SHLIB_LIST) $(LDFLAGS)
	cd ../lib && ($(LN_S) libmenu.so.$(REL_VERSION) libmenu.so.$(ABI_VERSION); $(LN_S) libmenu.so.$(ABI_VERSION) libmenu.so; )

install \
install.libs \
install.menu :: $(DESTDIR)$(libdir)/libmenu.so.$(REL_VERSION)

$(DESTDIR)$(libdir)/libmenu.so.$(REL_VERSION) : \
		$(DESTDIR)$(libdir) \
		$(SHARED_OBJS)
	@echo linking $@
	$(MK_SHARED_LIB) $(SHARED_OBJS) $(SHLIB_LIST) $(LDFLAGS)
	cd $(DESTDIR)$(libdir) && ($(LN_S) libmenu.so.$(REL_VERSION) libmenu.so.$(ABI_VERSION); $(LN_S) libmenu.so.$(ABI_VERSION) libmenu.so; )

uninstall \
uninstall.libs \
uninstall.menu ::
	@echo uninstalling $(DESTDIR)$(libdir)/libmenu.so.$(REL_VERSION)
	-rm -f $(DESTDIR)$(libdir)/libmenu.so.$(REL_VERSION)
	-rm -f $(DESTDIR)$(libdir)/libmenu.so.$(ABI_VERSION)
	-rm -f $(DESTDIR)$(libdir)/libmenu.so

clean ::
	-rm -f ../lib/libmenu.so.$(REL_VERSION)
	-rm -f ../lib/libmenu.so.$(ABI_VERSION)
	-rm -f ../lib/libmenu.so

mostlyclean::
	-rm -f $(SHARED_OBJS)

# generated by mk-2nd.awk
#   model:      obj_s
#   MODEL:      SHARED
#   echo:       yes
#   subset:     ticlib+termlib+ext_tinfo+base+ext_funcs
#   crenames:   yes
#   cxxrenames: yes
#   traces:     DEBUG
#   srcdir:     .

../obj_s/m_attribs$o :	$(srcdir)/m_attribs.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_attribs.c -o ../obj_s/m_attribs$o

../obj_s/m_cursor$o :	$(srcdir)/m_cursor.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_cursor.c -o ../obj_s/m_cursor$o

../obj_s/m_driver$o :	$(srcdir)/m_driver.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_driver.c -o ../obj_s/m_driver$o

../obj_s/m_format$o :	$(srcdir)/m_format.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_format.c -o ../obj_s/m_format$o

../obj_s/m_global$o :	$(srcdir)/m_global.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_global.c -o ../obj_s/m_global$o

../obj_s/m_hook$o :	$(srcdir)/m_hook.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_hook.c -o ../obj_s/m_hook$o

../obj_s/m_item_cur$o :	$(srcdir)/m_item_cur.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_item_cur.c -o ../obj_s/m_item_cur$o

../obj_s/m_item_nam$o :	$(srcdir)/m_item_nam.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_item_nam.c -o ../obj_s/m_item_nam$o

../obj_s/m_item_new$o :	$(srcdir)/m_item_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_item_new.c -o ../obj_s/m_item_new$o

../obj_s/m_item_opt$o :	$(srcdir)/m_item_opt.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_item_opt.c -o ../obj_s/m_item_opt$o

../obj_s/m_item_top$o :	$(srcdir)/m_item_top.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_item_top.c -o ../obj_s/m_item_top$o

../obj_s/m_item_use$o :	$(srcdir)/m_item_use.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_item_use.c -o ../obj_s/m_item_use$o

../obj_s/m_item_val$o :	$(srcdir)/m_item_val.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_item_val.c -o ../obj_s/m_item_val$o

../obj_s/m_item_vis$o :	$(srcdir)/m_item_vis.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_item_vis.c -o ../obj_s/m_item_vis$o

../obj_s/m_items$o :	$(srcdir)/m_items.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_items.c -o ../obj_s/m_items$o

../obj_s/m_new$o :	$(srcdir)/m_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_new.c -o ../obj_s/m_new$o

../obj_s/m_opts$o :	$(srcdir)/m_opts.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_opts.c -o ../obj_s/m_opts$o

../obj_s/m_pad$o :	$(srcdir)/m_pad.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_pad.c -o ../obj_s/m_pad$o

../obj_s/m_pattern$o :	$(srcdir)/m_pattern.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_pattern.c -o ../obj_s/m_pattern$o

../obj_s/m_post$o :	$(srcdir)/m_post.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_post.c -o ../obj_s/m_post$o

../obj_s/m_req_name$o :	$(srcdir)/m_req_name.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_req_name.c -o ../obj_s/m_req_name$o

../obj_s/m_scale$o :	$(srcdir)/m_scale.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_scale.c -o ../obj_s/m_scale$o

../obj_s/m_spacing$o :	$(srcdir)/m_spacing.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_spacing.c -o ../obj_s/m_spacing$o

../obj_s/m_sub$o :	$(srcdir)/m_sub.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_sub.c -o ../obj_s/m_sub$o

../obj_s/m_userptr$o :	$(srcdir)/m_userptr.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_userptr.c -o ../obj_s/m_userptr$o

../obj_s/m_win$o :	$(srcdir)/m_win.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../menu/m_win.c -o ../obj_s/m_win$o


# generated by mk-1st.awk (subset=ticlib+termlib+ext_tinfo+base+ext_funcs)
#  name:          menu
#  traces:        DEBUG
#  MODEL:         NORMAL
#  model:         objects
#  prefix:        lib
#  suffix:        .a
#  subset:        ticlib+termlib+ext_tinfo+base+ext_funcs
#  ShlibVer:      rel
#  ShlibVerInfix: no
#  SymLink:       ln -s -f
#  TermlibRoot:   ncurses
#  TermlibSuffix: .so
#  ReLink:        yes
#  DoLinks:       yes
#  rmSoLocs:      no
#  ldconfig:      :
#  overwrite:     no
#  depend:        ../include/ncurses_cfg.h ./menu.priv.h
#  host:          arm-unknown-linux-androideabi

NORMAL_OBJS = \
	../objects/m_attribs$o \
	../objects/m_cursor$o \
	../objects/m_driver$o \
	../objects/m_format$o \
	../objects/m_global$o \
	../objects/m_hook$o \
	../objects/m_item_cur$o \
	../objects/m_item_nam$o \
	../objects/m_item_new$o \
	../objects/m_item_opt$o \
	../objects/m_item_top$o \
	../objects/m_item_use$o \
	../objects/m_item_val$o \
	../objects/m_item_vis$o \
	../objects/m_items$o \
	../objects/m_new$o \
	../objects/m_opts$o \
	../objects/m_pad$o \
	../objects/m_pattern$o \
	../objects/m_post$o \
	../objects/m_req_name$o \
	../objects/m_scale$o \
	../objects/m_spacing$o \
	../objects/m_sub$o \
	../objects/m_userptr$o \
	../objects/m_win$o

$(NORMAL_OBJS) : ../include/ncurses_cfg.h ./menu.priv.h

../lib/libmenu.a : $(NORMAL_OBJS)
	$(AR) $(ARFLAGS) $@ $?
	$(RANLIB) $@

install \
install.libs \
install.menu :: $(DESTDIR)$(libdir) ../lib/libmenu.a
	@echo installing ../lib/libmenu.a as $(DESTDIR)$(libdir)/libmenu.a
	$(INSTALL_DATA) ../lib/libmenu.a $(DESTDIR)$(libdir)/libmenu.a
	$(RANLIB) $(DESTDIR)$(libdir)/libmenu.a

uninstall \
uninstall.libs \
uninstall.menu ::
	@echo uninstalling $(DESTDIR)$(libdir)/libmenu.a
	-@rm -f $(DESTDIR)$(libdir)/libmenu.a

clean ::
	-rm -f ../lib/libmenu.a
	-rm -f ../lib/
	-rm -f ../lib/libmenu.a

mostlyclean::
	-rm -f $(NORMAL_OBJS)

# generated by mk-2nd.awk
#   model:      objects
#   MODEL:      NORMAL
#   echo:       yes
#   subset:     ticlib+termlib+ext_tinfo+base+ext_funcs
#   crenames:   yes
#   cxxrenames: yes
#   traces:     DEBUG
#   srcdir:     .

../objects/m_attribs$o :	$(srcdir)/m_attribs.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_attribs.c -o ../objects/m_attribs$o

../objects/m_cursor$o :	$(srcdir)/m_cursor.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_cursor.c -o ../objects/m_cursor$o

../objects/m_driver$o :	$(srcdir)/m_driver.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_driver.c -o ../objects/m_driver$o

../objects/m_format$o :	$(srcdir)/m_format.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_format.c -o ../objects/m_format$o

../objects/m_global$o :	$(srcdir)/m_global.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_global.c -o ../objects/m_global$o

../objects/m_hook$o :	$(srcdir)/m_hook.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_hook.c -o ../objects/m_hook$o

../objects/m_item_cur$o :	$(srcdir)/m_item_cur.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_item_cur.c -o ../objects/m_item_cur$o

../objects/m_item_nam$o :	$(srcdir)/m_item_nam.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_item_nam.c -o ../objects/m_item_nam$o

../objects/m_item_new$o :	$(srcdir)/m_item_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_item_new.c -o ../objects/m_item_new$o

../objects/m_item_opt$o :	$(srcdir)/m_item_opt.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_item_opt.c -o ../objects/m_item_opt$o

../objects/m_item_top$o :	$(srcdir)/m_item_top.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_item_top.c -o ../objects/m_item_top$o

../objects/m_item_use$o :	$(srcdir)/m_item_use.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_item_use.c -o ../objects/m_item_use$o

../objects/m_item_val$o :	$(srcdir)/m_item_val.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_item_val.c -o ../objects/m_item_val$o

../objects/m_item_vis$o :	$(srcdir)/m_item_vis.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_item_vis.c -o ../objects/m_item_vis$o

../objects/m_items$o :	$(srcdir)/m_items.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_items.c -o ../objects/m_items$o

../objects/m_new$o :	$(srcdir)/m_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_new.c -o ../objects/m_new$o

../objects/m_opts$o :	$(srcdir)/m_opts.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_opts.c -o ../objects/m_opts$o

../objects/m_pad$o :	$(srcdir)/m_pad.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_pad.c -o ../objects/m_pad$o

../objects/m_pattern$o :	$(srcdir)/m_pattern.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_pattern.c -o ../objects/m_pattern$o

../objects/m_post$o :	$(srcdir)/m_post.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_post.c -o ../objects/m_post$o

../objects/m_req_name$o :	$(srcdir)/m_req_name.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_req_name.c -o ../objects/m_req_name$o

../objects/m_scale$o :	$(srcdir)/m_scale.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_scale.c -o ../objects/m_scale$o

../objects/m_spacing$o :	$(srcdir)/m_spacing.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_spacing.c -o ../objects/m_spacing$o

../objects/m_sub$o :	$(srcdir)/m_sub.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_sub.c -o ../objects/m_sub$o

../objects/m_userptr$o :	$(srcdir)/m_userptr.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_userptr.c -o ../objects/m_userptr$o

../objects/m_win$o :	$(srcdir)/m_win.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../menu/m_win.c -o ../objects/m_win$o


# generated by mk-1st.awk (subset=ticlib+termlib+ext_tinfo+base+ext_funcs)
#  name:          menu
#  traces:        DEBUG
#  MODEL:         DEBUG
#  model:         obj_g
#  prefix:        lib
#  suffix:        _g.a
#  subset:        ticlib+termlib+ext_tinfo+base+ext_funcs
#  ShlibVer:      rel
#  ShlibVerInfix: no
#  SymLink:       ln -s -f
#  TermlibRoot:   ncurses
#  TermlibSuffix: .so
#  ReLink:        yes
#  DoLinks:       yes
#  rmSoLocs:      no
#  ldconfig:      :
#  overwrite:     no
#  depend:        ../include/ncurses_cfg.h ./menu.priv.h
#  host:          arm-unknown-linux-androideabi

DEBUG_OBJS = \
	../obj_g/m_attribs$o \
	../obj_g/m_cursor$o \
	../obj_g/m_driver$o \
	../obj_g/m_format$o \
	../obj_g/m_global$o \
	../obj_g/m_hook$o \
	../obj_g/m_item_cur$o \
	../obj_g/m_item_nam$o \
	../obj_g/m_item_new$o \
	../obj_g/m_item_opt$o \
	../obj_g/m_item_top$o \
	../obj_g/m_item_use$o \
	../obj_g/m_item_val$o \
	../obj_g/m_item_vis$o \
	../obj_g/m_items$o \
	../obj_g/m_new$o \
	../obj_g/m_opts$o \
	../obj_g/m_pad$o \
	../obj_g/m_pattern$o \
	../obj_g/m_post$o \
	../obj_g/m_req_name$o \
	../obj_g/m_scale$o \
	../obj_g/m_spacing$o \
	../obj_g/m_sub$o \
	../obj_g/m_trace$o \
	../obj_g/m_userptr$o \
	../obj_g/m_win$o

$(DEBUG_OBJS) : ../include/ncurses_cfg.h ./menu.priv.h

../lib/libmenu_g.a : $(DEBUG_OBJS)
	$(AR) $(ARFLAGS) $@ $?
	$(RANLIB) $@

install \
install.libs \
install.menu :: $(DESTDIR)$(libdir) ../lib/libmenu_g.a
	@echo installing ../lib/libmenu_g.a as $(DESTDIR)$(libdir)/libmenu_g.a
	$(INSTALL_DATA) ../lib/libmenu_g.a $(DESTDIR)$(libdir)/libmenu_g.a
	$(RANLIB) $(DESTDIR)$(libdir)/libmenu_g.a

uninstall \
uninstall.libs \
uninstall.menu ::
	@echo uninstalling $(DESTDIR)$(libdir)/libmenu_g.a
	-@rm -f $(DESTDIR)$(libdir)/libmenu_g.a

clean ::
	-rm -f ../lib/libmenu_g.a
	-rm -f ../lib/
	-rm -f ../lib/libmenu_g.a

mostlyclean::
	-rm -f $(DEBUG_OBJS)

# generated by mk-2nd.awk
#   model:      obj_g
#   MODEL:      DEBUG
#   echo:       yes
#   subset:     ticlib+termlib+ext_tinfo+base+ext_funcs
#   crenames:   yes
#   cxxrenames: yes
#   traces:     DEBUG
#   srcdir:     .

../obj_g/m_attribs$o :	$(srcdir)/m_attribs.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_attribs.c -o ../obj_g/m_attribs$o

../obj_g/m_cursor$o :	$(srcdir)/m_cursor.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_cursor.c -o ../obj_g/m_cursor$o

../obj_g/m_driver$o :	$(srcdir)/m_driver.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_driver.c -o ../obj_g/m_driver$o

../obj_g/m_format$o :	$(srcdir)/m_format.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_format.c -o ../obj_g/m_format$o

../obj_g/m_global$o :	$(srcdir)/m_global.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_global.c -o ../obj_g/m_global$o

../obj_g/m_hook$o :	$(srcdir)/m_hook.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_hook.c -o ../obj_g/m_hook$o

../obj_g/m_item_cur$o :	$(srcdir)/m_item_cur.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_item_cur.c -o ../obj_g/m_item_cur$o

../obj_g/m_item_nam$o :	$(srcdir)/m_item_nam.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_item_nam.c -o ../obj_g/m_item_nam$o

../obj_g/m_item_new$o :	$(srcdir)/m_item_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_item_new.c -o ../obj_g/m_item_new$o

../obj_g/m_item_opt$o :	$(srcdir)/m_item_opt.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_item_opt.c -o ../obj_g/m_item_opt$o

../obj_g/m_item_top$o :	$(srcdir)/m_item_top.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_item_top.c -o ../obj_g/m_item_top$o

../obj_g/m_item_use$o :	$(srcdir)/m_item_use.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_item_use.c -o ../obj_g/m_item_use$o

../obj_g/m_item_val$o :	$(srcdir)/m_item_val.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_item_val.c -o ../obj_g/m_item_val$o

../obj_g/m_item_vis$o :	$(srcdir)/m_item_vis.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_item_vis.c -o ../obj_g/m_item_vis$o

../obj_g/m_items$o :	$(srcdir)/m_items.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_items.c -o ../obj_g/m_items$o

../obj_g/m_new$o :	$(srcdir)/m_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_new.c -o ../obj_g/m_new$o

../obj_g/m_opts$o :	$(srcdir)/m_opts.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_opts.c -o ../obj_g/m_opts$o

../obj_g/m_pad$o :	$(srcdir)/m_pad.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_pad.c -o ../obj_g/m_pad$o

../obj_g/m_pattern$o :	$(srcdir)/m_pattern.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_pattern.c -o ../obj_g/m_pattern$o

../obj_g/m_post$o :	$(srcdir)/m_post.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_post.c -o ../obj_g/m_post$o

../obj_g/m_req_name$o :	$(srcdir)/m_req_name.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_req_name.c -o ../obj_g/m_req_name$o

../obj_g/m_scale$o :	$(srcdir)/m_scale.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_scale.c -o ../obj_g/m_scale$o

../obj_g/m_spacing$o :	$(srcdir)/m_spacing.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_spacing.c -o ../obj_g/m_spacing$o

../obj_g/m_sub$o :	$(srcdir)/m_sub.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_sub.c -o ../obj_g/m_sub$o

../obj_g/m_trace$o :	$(srcdir)/m_trace.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_trace.c -o ../obj_g/m_trace$o

../obj_g/m_userptr$o :	$(srcdir)/m_userptr.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_userptr.c -o ../obj_g/m_userptr$o

../obj_g/m_win$o :	$(srcdir)/m_win.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../menu/m_win.c -o ../obj_g/m_win$o


# generated by mk-hdr.awk
#  subset:     ticlib+termlib+ext_tinfo+base+ext_funcs
#  compat:     yes

${DESTDIR}${includedir} :
	mkdir -p $@

install \
install.libs \
install.includes :: ${AUTO_SRC} ${DESTDIR}${includedir} \
		$(srcdir)/eti.h \
		$(srcdir)/menu.h
	@ (cd ${DESTDIR}${includedir} && rm -f eti.h) ; ../headers.sh ${INSTALL_DATA} ${DESTDIR}${includedir} ${srcdir} $(srcdir)/eti.h
	@ (cd ${DESTDIR}${includedir} && rm -f menu.h) ; ../headers.sh ${INSTALL_DATA} ${DESTDIR}${includedir} ${srcdir} $(srcdir)/menu.h

uninstall \
uninstall.libs \
uninstall.includes ::
	-@ (cd ${DESTDIR}${includedir} && rm -f eti.h)
	-@ (cd ${DESTDIR}${includedir} && rm -f menu.h)
depend : ${AUTO_SRC}
	makedepend -- ${CPPFLAGS} -- ${C_SRC}

# DO NOT DELETE THIS LINE -- make depend depends on it.
