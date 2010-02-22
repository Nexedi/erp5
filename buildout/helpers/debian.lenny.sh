#!/bin/sh

PACKAGE_LIST="""\
bison
build-essential
cpio
flex
gcc
libbz2-dev
libgdbm-dev
libglib2.0-dev
libjpeg62-dev
libncurses5-dev
libneon27-dev
libssl-dev
libsvn-dev
libxml2-dev
libxslt1-dev
make
patch
rpm
subversion
subversion-tools
xvfb
zip
zlib1g-dev\
"""

apt-get install $PACKAGE_LIST
