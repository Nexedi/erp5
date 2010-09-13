#!/bin/sh

USAGE="""\
Helper for buildout-base installation of ERP5 on OpenSUSE 11.2
 Usage:
   opensuse.sh [-h|-l]

   With no options, attempts to install the dependencies required
   to run the buildout.

 Options:
   -h  shows this message
   -l  lists the required dependencies\
"""
PACKAGE_LIST="""\
automake
bison
boost-devel
cpio
flex
gc-devel
gcc
gcc-c++
gdbm-devel
gettext-runtime
giflib-devel
git
glib2-devel
groff
libSDL-devel
libSDL_gfx-devel
libSDL_image-devel
libSDLmm-devel
libbz2-devel
libcom_err-devel
libgsasl-devel
libjpeg-devel
libldapcpp-devel
libneon-devel
libopenssl-devel
libpng-devel
librsync
libtiff-devel
libtool
libxml2-devel
libxslt-devel
libzip-devel
make
ncurses-devel
patch
pcre-devel
python-devel
python-setuptools
python-xml
readline-devel
rpm
sqlite3-devel
subversion
subversion-devel
subversion-tools
termcap
xorg-x11-server
xorg-x11-server-extra
zip
zlib-devel\
"""
if [ x"$1" == x ]; then
  zypper install $PACKAGE_LIST
elif [ "$1" = "-l" ]; then
  echo "$PACKAGE_LIST"
elif [ "$1" = "-h" ]; then
  echo "$USAGE"
else
  echo "Unknown argument."
  echo "$USAGE"
fi
