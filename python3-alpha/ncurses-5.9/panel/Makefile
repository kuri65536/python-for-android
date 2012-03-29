# $Id: Makefile.in,v 1.58 2010/11/27 21:45:27 tom Exp $
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
# Makefile for panels source code.
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
datadir		= ${prefix}/share

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

LIBRARIES	=  ../lib/libpanel.so.${REL_VERSION} ../lib/libpanel.a ../lib/libpanel_g.a

LINT		= 
LINT_OPTS	= 
LINT_LIBS	= -lpanel -lncurses 

AUTO_SRC	= \
		../include/panel.h

################################################################################
all \
libs \
install ::	$(AUTO_SRC) $(LIBRARIES)

sources:	$(AUTO_SRC)

$(DESTDIR)$(bindir) \
$(DESTDIR)$(libdir) :
	mkdir -p $@

# make a copy to simplify include-paths while still keeping panel's include
# file in this directory.
../include/panel.h : $(srcdir)/panel.h
	-rm -f $@
	cp $(srcdir)/panel.h $@

HEADER_DEPS = \
	$(srcdir)/panel.priv.h \
	$(srcdir)/panel.h

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
#   libname:    panel
#   subsets:    ticlib+termlib+ext_tinfo+base+ext_funcs

.SUFFIXES: .c .cc .h .i .ii
.c.i :
	$(CPP) $(CPPFLAGS) $< >$@
.cc.ii :
	$(CPP) $(CPPFLAGS) $< >$@
.h.i :
	$(CPP) $(CPPFLAGS) $< >$@

C_SRC = \
	$(srcdir)/panel.c \
	$(srcdir)/p_above.c \
	$(srcdir)/p_below.c \
	$(srcdir)/p_bottom.c \
	$(srcdir)/p_delete.c \
	$(srcdir)/p_hide.c \
	$(srcdir)/p_hidden.c \
	$(srcdir)/p_move.c \
	$(srcdir)/p_new.c \
	$(srcdir)/p_replace.c \
	$(srcdir)/p_show.c \
	$(srcdir)/p_top.c \
	$(srcdir)/p_update.c \
	$(srcdir)/p_user.c \
	$(srcdir)/p_win.c

# Producing llib-lpanel is time-consuming, so there's no direct-dependency for
# it in the lintlib rule.  We'll only remove in the cleanest setup.
clean ::
	rm -f llib-lpanel.*

realclean ::
	rm -f llib-lpanel

llib-lpanel : $(C_SRC)
	cproto -a -l -DNCURSES_ENABLE_STDBOOL_H=0 -DLINT $(CPPFLAGS) $(C_SRC) >$@

lintlib :
	sh $(srcdir)/../misc/makellib panel $(CPPFLAGS)
lint :
	$(LINT) $(LINT_OPTS) $(CPPFLAGS) $(C_SRC) $(LINT_LIBS)

# generated by mk-1st.awk (subset=ticlib+termlib+ext_tinfo+base+ext_funcs)
#  name:          panel
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
#  depend:        ../include/ncurses_cfg.h ./panel.priv.h
#  host:          arm-unknown-linux-androideabi

SHARED_OBJS = \
	../obj_s/panel$o \
	../obj_s/p_above$o \
	../obj_s/p_below$o \
	../obj_s/p_bottom$o \
	../obj_s/p_delete$o \
	../obj_s/p_hide$o \
	../obj_s/p_hidden$o \
	../obj_s/p_move$o \
	../obj_s/p_new$o \
	../obj_s/p_replace$o \
	../obj_s/p_show$o \
	../obj_s/p_top$o \
	../obj_s/p_update$o \
	../obj_s/p_user$o \
	../obj_s/p_win$o

$(SHARED_OBJS) : ../include/ncurses_cfg.h ./panel.priv.h

../lib/libpanel.so.$(REL_VERSION) : \
		../lib \
		$(SHARED_OBJS)
	@echo linking $@
	$(MK_SHARED_LIB) $(SHARED_OBJS) $(SHLIB_LIST) $(LDFLAGS)
	cd ../lib && ($(LN_S) libpanel.so.$(REL_VERSION) libpanel.so.$(ABI_VERSION); $(LN_S) libpanel.so.$(ABI_VERSION) libpanel.so; )

install \
install.libs \
install.panel :: $(DESTDIR)$(libdir)/libpanel.so.$(REL_VERSION)

$(DESTDIR)$(libdir)/libpanel.so.$(REL_VERSION) : \
		$(DESTDIR)$(libdir) \
		$(SHARED_OBJS)
	@echo linking $@
	$(MK_SHARED_LIB) $(SHARED_OBJS) $(SHLIB_LIST) $(LDFLAGS)
	cd $(DESTDIR)$(libdir) && ($(LN_S) libpanel.so.$(REL_VERSION) libpanel.so.$(ABI_VERSION); $(LN_S) libpanel.so.$(ABI_VERSION) libpanel.so; )

uninstall \
uninstall.libs \
uninstall.panel ::
	@echo uninstalling $(DESTDIR)$(libdir)/libpanel.so.$(REL_VERSION)
	-rm -f $(DESTDIR)$(libdir)/libpanel.so.$(REL_VERSION)
	-rm -f $(DESTDIR)$(libdir)/libpanel.so.$(ABI_VERSION)
	-rm -f $(DESTDIR)$(libdir)/libpanel.so

clean ::
	-rm -f ../lib/libpanel.so.$(REL_VERSION)
	-rm -f ../lib/libpanel.so.$(ABI_VERSION)
	-rm -f ../lib/libpanel.so

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

../obj_s/panel$o :	$(srcdir)/panel.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/panel.c -o ../obj_s/panel$o

../obj_s/p_above$o :	$(srcdir)/p_above.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_above.c -o ../obj_s/p_above$o

../obj_s/p_below$o :	$(srcdir)/p_below.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_below.c -o ../obj_s/p_below$o

../obj_s/p_bottom$o :	$(srcdir)/p_bottom.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_bottom.c -o ../obj_s/p_bottom$o

../obj_s/p_delete$o :	$(srcdir)/p_delete.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_delete.c -o ../obj_s/p_delete$o

../obj_s/p_hide$o :	$(srcdir)/p_hide.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_hide.c -o ../obj_s/p_hide$o

../obj_s/p_hidden$o :	$(srcdir)/p_hidden.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_hidden.c -o ../obj_s/p_hidden$o

../obj_s/p_move$o :	$(srcdir)/p_move.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_move.c -o ../obj_s/p_move$o

../obj_s/p_new$o :	$(srcdir)/p_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_new.c -o ../obj_s/p_new$o

../obj_s/p_replace$o :	$(srcdir)/p_replace.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_replace.c -o ../obj_s/p_replace$o

../obj_s/p_show$o :	$(srcdir)/p_show.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_show.c -o ../obj_s/p_show$o

../obj_s/p_top$o :	$(srcdir)/p_top.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_top.c -o ../obj_s/p_top$o

../obj_s/p_update$o :	$(srcdir)/p_update.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_update.c -o ../obj_s/p_update$o

../obj_s/p_user$o :	$(srcdir)/p_user.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_user.c -o ../obj_s/p_user$o

../obj_s/p_win$o :	$(srcdir)/p_win.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_SHARED) -c ../panel/p_win.c -o ../obj_s/p_win$o


# generated by mk-1st.awk (subset=ticlib+termlib+ext_tinfo+base+ext_funcs)
#  name:          panel
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
#  depend:        ../include/ncurses_cfg.h ./panel.priv.h
#  host:          arm-unknown-linux-androideabi

NORMAL_OBJS = \
	../objects/panel$o \
	../objects/p_above$o \
	../objects/p_below$o \
	../objects/p_bottom$o \
	../objects/p_delete$o \
	../objects/p_hide$o \
	../objects/p_hidden$o \
	../objects/p_move$o \
	../objects/p_new$o \
	../objects/p_replace$o \
	../objects/p_show$o \
	../objects/p_top$o \
	../objects/p_update$o \
	../objects/p_user$o \
	../objects/p_win$o

$(NORMAL_OBJS) : ../include/ncurses_cfg.h ./panel.priv.h

../lib/libpanel.a : $(NORMAL_OBJS)
	$(AR) $(ARFLAGS) $@ $?
	$(RANLIB) $@

install \
install.libs \
install.panel :: $(DESTDIR)$(libdir) ../lib/libpanel.a
	@echo installing ../lib/libpanel.a as $(DESTDIR)$(libdir)/libpanel.a
	$(INSTALL_DATA) ../lib/libpanel.a $(DESTDIR)$(libdir)/libpanel.a
	$(RANLIB) $(DESTDIR)$(libdir)/libpanel.a

uninstall \
uninstall.libs \
uninstall.panel ::
	@echo uninstalling $(DESTDIR)$(libdir)/libpanel.a
	-@rm -f $(DESTDIR)$(libdir)/libpanel.a

clean ::
	-rm -f ../lib/libpanel.a
	-rm -f ../lib/
	-rm -f ../lib/libpanel.a

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

../objects/panel$o :	$(srcdir)/panel.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/panel.c -o ../objects/panel$o

../objects/p_above$o :	$(srcdir)/p_above.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_above.c -o ../objects/p_above$o

../objects/p_below$o :	$(srcdir)/p_below.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_below.c -o ../objects/p_below$o

../objects/p_bottom$o :	$(srcdir)/p_bottom.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_bottom.c -o ../objects/p_bottom$o

../objects/p_delete$o :	$(srcdir)/p_delete.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_delete.c -o ../objects/p_delete$o

../objects/p_hide$o :	$(srcdir)/p_hide.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_hide.c -o ../objects/p_hide$o

../objects/p_hidden$o :	$(srcdir)/p_hidden.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_hidden.c -o ../objects/p_hidden$o

../objects/p_move$o :	$(srcdir)/p_move.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_move.c -o ../objects/p_move$o

../objects/p_new$o :	$(srcdir)/p_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_new.c -o ../objects/p_new$o

../objects/p_replace$o :	$(srcdir)/p_replace.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_replace.c -o ../objects/p_replace$o

../objects/p_show$o :	$(srcdir)/p_show.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_show.c -o ../objects/p_show$o

../objects/p_top$o :	$(srcdir)/p_top.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_top.c -o ../objects/p_top$o

../objects/p_update$o :	$(srcdir)/p_update.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_update.c -o ../objects/p_update$o

../objects/p_user$o :	$(srcdir)/p_user.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_user.c -o ../objects/p_user$o

../objects/p_win$o :	$(srcdir)/p_win.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_NORMAL) -c ../panel/p_win.c -o ../objects/p_win$o


# generated by mk-1st.awk (subset=ticlib+termlib+ext_tinfo+base+ext_funcs)
#  name:          panel
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
#  depend:        ../include/ncurses_cfg.h ./panel.priv.h
#  host:          arm-unknown-linux-androideabi

DEBUG_OBJS = \
	../obj_g/panel$o \
	../obj_g/p_above$o \
	../obj_g/p_below$o \
	../obj_g/p_bottom$o \
	../obj_g/p_delete$o \
	../obj_g/p_hide$o \
	../obj_g/p_hidden$o \
	../obj_g/p_move$o \
	../obj_g/p_new$o \
	../obj_g/p_replace$o \
	../obj_g/p_show$o \
	../obj_g/p_top$o \
	../obj_g/p_update$o \
	../obj_g/p_user$o \
	../obj_g/p_win$o

$(DEBUG_OBJS) : ../include/ncurses_cfg.h ./panel.priv.h

../lib/libpanel_g.a : $(DEBUG_OBJS)
	$(AR) $(ARFLAGS) $@ $?
	$(RANLIB) $@

install \
install.libs \
install.panel :: $(DESTDIR)$(libdir) ../lib/libpanel_g.a
	@echo installing ../lib/libpanel_g.a as $(DESTDIR)$(libdir)/libpanel_g.a
	$(INSTALL_DATA) ../lib/libpanel_g.a $(DESTDIR)$(libdir)/libpanel_g.a
	$(RANLIB) $(DESTDIR)$(libdir)/libpanel_g.a

uninstall \
uninstall.libs \
uninstall.panel ::
	@echo uninstalling $(DESTDIR)$(libdir)/libpanel_g.a
	-@rm -f $(DESTDIR)$(libdir)/libpanel_g.a

clean ::
	-rm -f ../lib/libpanel_g.a
	-rm -f ../lib/
	-rm -f ../lib/libpanel_g.a

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

../obj_g/panel$o :	$(srcdir)/panel.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/panel.c -o ../obj_g/panel$o

../obj_g/p_above$o :	$(srcdir)/p_above.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_above.c -o ../obj_g/p_above$o

../obj_g/p_below$o :	$(srcdir)/p_below.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_below.c -o ../obj_g/p_below$o

../obj_g/p_bottom$o :	$(srcdir)/p_bottom.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_bottom.c -o ../obj_g/p_bottom$o

../obj_g/p_delete$o :	$(srcdir)/p_delete.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_delete.c -o ../obj_g/p_delete$o

../obj_g/p_hide$o :	$(srcdir)/p_hide.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_hide.c -o ../obj_g/p_hide$o

../obj_g/p_hidden$o :	$(srcdir)/p_hidden.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_hidden.c -o ../obj_g/p_hidden$o

../obj_g/p_move$o :	$(srcdir)/p_move.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_move.c -o ../obj_g/p_move$o

../obj_g/p_new$o :	$(srcdir)/p_new.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_new.c -o ../obj_g/p_new$o

../obj_g/p_replace$o :	$(srcdir)/p_replace.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_replace.c -o ../obj_g/p_replace$o

../obj_g/p_show$o :	$(srcdir)/p_show.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_show.c -o ../obj_g/p_show$o

../obj_g/p_top$o :	$(srcdir)/p_top.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_top.c -o ../obj_g/p_top$o

../obj_g/p_update$o :	$(srcdir)/p_update.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_update.c -o ../obj_g/p_update$o

../obj_g/p_user$o :	$(srcdir)/p_user.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_user.c -o ../obj_g/p_user$o

../obj_g/p_win$o :	$(srcdir)/p_win.c \
			$(HEADER_DEPS)
	$(LIBTOOL_COMPILE) $(CC) $(CFLAGS_DEBUG) -c ../panel/p_win.c -o ../obj_g/p_win$o


# generated by mk-hdr.awk
#  subset:     ticlib+termlib+ext_tinfo+base+ext_funcs
#  compat:     yes

${DESTDIR}${includedir} :
	mkdir -p $@

install \
install.libs \
install.includes :: ${AUTO_SRC} ${DESTDIR}${includedir} \
		$(srcdir)/panel.h
	@ (cd ${DESTDIR}${includedir} && rm -f panel.h) ; ../headers.sh ${INSTALL_DATA} ${DESTDIR}${includedir} ${srcdir} $(srcdir)/panel.h

uninstall \
uninstall.libs \
uninstall.includes ::
	-@ (cd ${DESTDIR}${includedir} && rm -f panel.h)
depend : ${AUTO_SRC}
	makedepend -- ${CPPFLAGS} -- ${C_SRC}

# DO NOT DELETE THIS LINE -- make depend depends on it.
