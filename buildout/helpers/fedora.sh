#!/bin/sh

USAGE="""\
Helper for buildout-base installation of ERP5 on Fedora 12.
 Usage:
   fedora.sh [-h|-l]

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
gettext
groff
SDL-devel
SDL_gfx-devel
SDL_image-devel
boost-devel
libzip-devel
gdbm-devel
glib2-devel
libgomp
libjpeg-devel
openldap-devel
ncurses-devel
neon-devel
openssl-devel
libpng-devel
readline-devel
librsync-devel
libgsasl-devel
mingw32-termcap
libtool
giflib
libxml2-devel
libcom_err-devel
libxslt-devel
make
patch
python-devel
python-setuptools
rpm
scons
subversion
subversion-devel
tesseract-devel
xorg-x11-server-devel
xorg-x11-server-Xvfb
zip
zlib-devel\
"""
if [ x"$1" == x ]; then
  yum install $PACKAGE_LIST
elif [ "$1" = "-l" ]; then
  echo "$PACKAGE_LIST"
elif [ "$1" = "-h" ]; then
  echo "$USAGE"
else
  echo "Unknown argument."
  echo "$USAGE"
fi
