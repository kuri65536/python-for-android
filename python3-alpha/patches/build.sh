pushd src >/dev/null

rm -rf "Python-${VERSION}"
tar -xf "Python-${VERSION}.tar.xz" || exit 1
pushd "Python-${VERSION}" >/dev/null

# Build host components.
AR=ar AS=as CC=gcc CFLAGS= CPP=cpp CPPFLAGS= CXX=g++ CXXFLAGS= LD=ld LDFLAGS= RANLIB=ranlib ./configure || exit 1
AR=ar AS=as CC=gcc CFLAGS= CPP=cpp CPPFLAGS= CXX=g++ CXXFLAGS= LD=ld LDFLAGS= RANLIB=ranlib make BUILDPYTHON=hostpython hostpython PGEN=Parser/hostpgen Parser/hostpgen || exit 1
make distclean || exit 1

# Apply patches and build target Python.
cat > config.site <<-SITE
	ac_cv_file__dev_ptmx=no
	ac_cv_file__dev_ptc=no
SITE
ln -sf "${TOOL_PREFIX}/sysroot/usr/include/"{linux,sys}"/soundcard.h"
patch -p1  < "${FILESDIR}/${PACKAGE}-cross-compile.patch" || exit 1
patch -p1  < "${FILESDIR}/${PACKAGE}-python-misc.patch" || exit 1
patch -p1  < "${FILESDIR}/${PACKAGE}-android-locale.patch" || exit 1
patch -Ep1 < "${FILESDIR}/${PACKAGE}-android-libmpdec.patch" || exit 1
[[ "${NDK_REV}" != 10* ]] && (patch -p1 < "${FILESDIR}/${PACKAGE}-android-missing-getdents64-definition.patch" || exit 1)
patch -p1  < "${FILESDIR}/${PACKAGE}-android-misc.patch" || exit 1

./configure CROSS_COMPILE_TARGET=yes HOSTPYTHON="$(pwd)/hostpython" CONFIG_SITE=config.site --prefix="${PREFIX}" --host="${TARGET}" --build="${HOST}" --disable-ipv6 --enable-shared --without-ensurepip || exit 1
make CROSS_COMPILE_TARGET=yes HOSTPYTHON="$(pwd)/hostpython" HOSTPGEN="$(pwd)/Parser/hostpgen" || exit 1
make CROSS_COMPILE_TARGET=yes HOSTPYTHON="$(pwd)/hostpython" HOSTPGEN="$(pwd)/Parser/hostpgen" install || exit 1

popd >/dev/null
popd >/dev/null
