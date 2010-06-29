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
cpio
flex
gcc
gcc-c++
gdbm-devel
glib2-devel
groff
libSDL-devel
libSDL_gfx-devel
libSDL_image-devel
libSDLmm-devel
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
python-devel
python-setuptools
readline-devel
rpm
scons
subversion
subversion-devel
subversion-tools
termcap
xorg-x11-server
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
