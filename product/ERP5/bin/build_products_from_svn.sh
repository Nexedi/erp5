#! /bin/bash
#
# Usage: build_products_from_svn.sh [-p path] [-d dir]
#
# The path is the last part of the svn root, for example, tag/5.0 or trunk.
# By default, the path is "trunk".
#
# The dir is the destination directory where the repository is made.
# By default, the dir is the current directory.

set -e

path=trunk
repository=$(pwd)

while getopts "p:d:" opt; do
  case $opt in
    p) path="$OPTARG" ;;
    d) repository="$OPTARG" ;;
  esac
done

# Lock file name
LOCKFILE="/tmp/$(basename $0).lock"
# SVN paths
SVNROOT="https://svn.erp5.org/repos/public/erp5/$path"
# Relative svn paths to fetch
MODULES="products"
# Local directory to receive SVN copies
BASELOCALDIR="/tmp"
LOCALDIR="$BASELOCALDIR/$$"
# Local directory to receive products
PRODUCTSDIR="$repository"


function cleanup {
  rm -f "$LOCKFILE"
  rm -rf "$LOCALDIR"
}

if [ -e "$LOCKFILE" ]; then
  echo "Lock file '$LOCKFILE' exists, exiting..."
  exit 1
fi

trap "cleanup" ERR

touch "$LOCKFILE"
mkdir "$LOCALDIR"

for MODULE in $MODULES; do
  # Checkout the source code from svn
  cd "$LOCALDIR"
  svn co "$SVNROOT/$MODULE" > /dev/null
  BMODULE=`basename "$MODULE"`

  # Create one archive for each Business Template
  cd "$LOCALDIR/$BMODULE"
  for PRODUCT in `ls "$LOCALDIR/$BMODULE"`; do
    if [ -d "$LOCALDIR/$BMODULE/$PRODUCT" ]; then
      tar -zcf "$LOCALDIR/$PRODUCT.tgz" --exclude .svn "$PRODUCT"
    fi
  done
done

# Publish the repository
mv -f "$LOCALDIR/"*.tgz "$PRODUCTSDIR"

# Clean up
cleanup
