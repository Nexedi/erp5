#! /bin/bash
#
# Usage: build_bt5_from_svn.sh [-p path] [-d dir]
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
MODULES="bt5 products/ERP5/bootstrap"
# Script generating the business template repository index
GENBTLIST="products/ERP5/bin"
# Local directory to receive SVN copies
BASELOCALDIR="/tmp"
LOCALDIR="$BASELOCALDIR/$$"
# Local directory to receive butiness templates
BT5DIR="$repository"


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
  for BT5 in `ls "$LOCALDIR/$BMODULE"`; do
    if [ -d "$LOCALDIR/$BMODULE/$BT5" ]; then
      tar -zcf "$LOCALDIR/$BT5.bt5" --exclude .svn "$BT5"
    fi
  done
done

# Get the latest version of the genbt5list and generate the index
cd "$LOCALDIR"
svn co "$SVNROOT/$GENBTLIST" > /dev/null

# Publish the repository
mv -f "$LOCALDIR/"*.bt5 "$BT5DIR"

# Generate the index from repository directory, in case there are BT5 manually added there
cd "$BT5DIR"
/usr/bin/python "$LOCALDIR/`basename $GENBTLIST`/genbt5list" > /dev/null
chmod go+r bt5list

# Clean up
cleanup
