# Introduction #

I've decided to annotate my experiences in porting Python3 to Android.

# Details #

Install the android toolchain: Toolchain\_Installation

Make sure the bin directory of whereever you installed the toolchain is in you path.

ie:
```
export PATH=$PATH:~/android-toolchain/bin
```

NB: Platform-9 supports widechar a bit, Platform-8 doesn't. Be aware.

It's probably a good idea to make sure the android platform tools are also in your path:

```
export PATH=$PATH:~/android-sdk-linux_86/platform-tools
```

Get the source code of the version of Python you need to port.

The following the instructions here:
http://randomsplat.com/id5-cross-compiling-python-for-embedded-linux.html

The target for Android is **arm-linux-androideabi**

Now, Android does NOT support Locale properly, and the wcs/mbs routines are completely broken.
Therefore you need to remove any reference to them.
I manually modify pyconfig.h as follows:

```
#define ANDROID 1  /* Useful for specific code changes.*/

#define HAVE_BROKEN_MBSTOWCS 1
#undef HAVE_DEV_PTMX
#undef HAVE_GETHOSTBYNAME_R
#undef HAVE_MBRTOWC
#define HAVE_NCURSES_H 1  /* This only if you've cross compiled curses */
#undef HAVE_SETLOCALE
#undef HAVE_WCSCOLL
#undef HAVE_WCSFTIME
#undef HAVE_WCSXFRM
```

Here is my sample configure parameters:
```
pushd ../thirdparty
export THIRD_PARTY_DIR=`pwd`
popd
export TARGET=arm-linux-androideabi

CC=${TARGET}-gcc CXX=${TARGET}-g++ AR=${TARGET}-ar RANLIB=${TARGET}-ranlib ./configure --host=${TARGET} --build=x86_64-linux-gnu --prefix=/python --enable-shared
```

Note that this refers to a bunch of third party libraries I cross-compiled.
I've put these here in case you don't want to do them yourself:
http://code.google.com/p/python-for-android/downloads/detail?name=thirdparty.tar.gz

## Setup Changes ##

setup.py will probably need to be modified. The major changes have to do with making sure setup looks for include files and libraries in your cross-compiled libraries, and not your system defaults.
Mostly this has involved changes in `build_extension(self, ext)` and modifying `inc_dirs` and `lib_dirs`. Look in [setup.py](http://code.google.com/p/python-for-android/source/browse/python3-alpha/python3-src/setup.py), and look for `cross_compile`.

Note: It's possible a lot of these changes to setup.py may have been rendered needless by correct use of LDFLAGS and CFLAGS (see readline example below).

## Code Changes ##
Not all references to locale or mbs/wcs are handled with the configuration changes. Some of these have to be handled in code.
For example, Python3 assumes the existance of a working mbstowcs regardless. These not only don't work under Android, they _catastrophically_ don't work.

I got around the problem thus:
In [pythonrun.c](http://code.google.com/p/python-for-android/source/browse/python3-alpha/python3-src/Python/pythonrun.c) I defined my own versions:

```
#ifdef ANDROID
size_t android_mbstowcs(wchar_t *dest, char * in, int maxlen) 
{
    wchar_t *out = dest;
    int size = 0;
    if (in) 
    {
      while(*in && size<maxlen) {
          if(*in < 128)
              *out++ = *in++;
          else
              *out++ = 0xdc00 + *in++;
         size += 1;     
      }
    }  
    *out = 0;
    return size;
}  

size_t android_wcstombs(char * dest, wchar_t *source, int maxlen)
{
  wchar_t c;
  int i;
  for (i=0; i<maxlen && source[i]; i++) 
  {
    c=source[i];
    if (c >= 0xdc80 && c <= 0xdcff) 
    {
      /* UTF-8b surrogate */
      c-=0xdc00;
    }
    if (dest) dest[i]=c;  
  }
  return i;  
}
  
#endif

```

This is a rough and ready conversion taken from elsewhere in the python 3 code base. Then, in any file where mbstowcs or wcstombs were referenced, I added this header:

```
#ifdef ANDROID
size_t android_wcstombs(char * dest, wchar_t *source, int maxlen);
size_t android_mbstowcs(wchar_t * dest, char *source, int maxlen);
#define wcstombs android_wcstombs
#define mbstowcs android_wcstombs
#endif
```

Note that this is not the only, or even best way to achieve the results, just the ones I used.

The first time you compile, you will probably see references to things not being in the lconv structure.

For the most part, the code will be to obtain structs like the decimal point,thousands seperator and grouping.

The easiest way to get around these errors is to hardcode in some sensible default values, and to remove references to localeconv and lconv altogether.
```
//      struct lconv *locale_data = localeconv();
        locale_info->decimal_point = ".";
        locale_info->thousands_sep = ",";
        locale_info->grouping = "3";
```

This should get you off the ground and pointing in the right directions.

### Unsupported calls ###
These are calls that will compile, but are not actually provided on the android platfrom, so they will throw errors when to you try to load. The trick is to make sure that references to these functions are not compiled in. See `_termios.c` as an example (look for `#ifdef ANDROID`)
  * tcdrain
  * getgrp and setgrp
    * times and chmod do NOT work under fuse file systems (and are almost irrelevant in any case) but the errors they throw will screw up most installation programs. posixmodule.c has been modified to silently fail instead, which allows pip and distribute to behave nicely.

## Third Party Components ##
http://www.crosscompile.org contains a lot of useful hints and tips.
A lot of configure scripts fail to recognize **arm-linux-androideabi** as a host. This can be solved by replacing config.sub and config.guess from here:
http://git.savannah.gnu.org/gitweb/?p=config.git;a=tree

or, indeed, here:

http://code.google.com/p/python-for-android/source/browse/#hg%2Fpython3-alpha%2Fsqlite3


Note: different configurations have sub and guess in different folders... you'll need to work out where.

As my readline configure command is:
```
export  TARGET=arm-linux-androideabi
pushd ../thirdparty
TARGET_DIR=`pwd`
popd

LDFLAGS=-L${TARGET_DIR}/lib CFLAGS="-I${TARGET_DIR}/include -I${TARGET_DIR}/include/ncurses" ./configure --host=$TARGET --target=$TARGET --prefix=$TARGET_DIR --enable-shared  --with-curses 
```

This is a pretty good starting point for most libraries. **readline** is one of the ones that require a little patching to work. The patch file is:

```
--- config.h	2012-03-27 15:10:24.000000000 +1100
+++ /home/robbie/readline-6.2/config.h	2012-03-27 10:49:38.000000000 +1100
@@ -15,6 +15,7 @@
 
 #define VOID_SIGHANDLER 1
 
+#define ANDROID 1
 /* Characteristics of the compiler. */
 /* #undef sig_atomic_t */
```

You will probably have to make these minor changes. Most of the time it will be commenting out references to unsupported library calls.

## Changes to Python modules ##
  * subprocess.py has a hardcoded call to `/bin/sh`, which breaks os.popen. This has been changed to `/system/bin/sh` for android.
  * locale.py - changed preferred encoding to utf-8