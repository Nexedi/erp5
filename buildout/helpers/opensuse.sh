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
groff
libzip-devel
gdbm-devel
glib2-devel
libjpeg-devel
libldapcpp-devel
ncurses-devel
libneon-devel
libopenssl-devel
readline-devel
libgsasl-devel
termcap
libxml2-devel
libtool
libcom_err-devel
libxslt-devel
make
patch
python-devel
python-setuptools
rpm
subversion
subversion-devel
subversion-tools
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
