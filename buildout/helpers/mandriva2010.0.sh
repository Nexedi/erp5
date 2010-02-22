#!/bin/sh

USAGE="""\
Helper for buildout-base installation of ERP5 on Mandriva 2010.
 Usage:
   mandriva2010.sh [-h|-l]

   With no options, attempts to install the dependencies required
   to run the buildout.

 Options:
   -h  shows this message
   -l  lists the required dependencies\
"""
PACKAGE_LIST="""\
bison
cpio
flex
gcc
gcc-c++
libbzip2-devel
libgdbm-devel
libglib2.0-devel
libjpeg-devel
libldap-devel
libncurses-devel
libneon-devel
libopenssl-devel
libtermcap-devel
libxml2-devel
libxslt-devel
make
patch
rpm
subversion
subversion-devel
subversion-tools
x11-server-xvfb
zip
zlib1-devel\
"""
if [ x"$1" == x ]; then
  urpmi $PACKAGE_LIST
elif [ "$1" = "-l" ]; then
  echo "$PACKAGE_LIST"
elif [ "$1" = "-h" ]; then
  echo "$USAGE"
else
  echo "Unknown argument."
  echo "$USAGE"
fi
