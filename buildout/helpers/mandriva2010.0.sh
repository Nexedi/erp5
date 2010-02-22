#!/bin/sh

PACKAGE_LIST="""
  bison
  cpio
  flex
  gcc
  gcc-c++
  libbzip2-devel
  libgdbm-devel
  libglib2.0-devel
  libjpeg-devel
  libncurses-devel
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
  zlib1-devel
"""
urpmi $PACKAGE_LIST
