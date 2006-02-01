#!/bin/bash

# TODO: BT5 version support (stable/unstable)

# Lock file name
LOCKFILE="/tmp/$0.lock"
# CVS root
CVSROOT=":pserver:anonymous@cvs.erp5.org:/cvsroot"
# Module containing business template
MODULE="erp5_bt5"
# Script generating the business template repository index (in $REPOSITORY)
GENBTLIST="ERP5/bin/genbt5list" # XXX: relative to the same repository
# Local directory to receive CVS copy
BASELOCALDIR="/tmp"
# Local directory to receive butiness templates
BT5DIR="/var/lib/zope/static/reposit/erp5/upload_module"

function cleanup () {
  rm -f $LOCKFILE
  exit 1
}

if [ -e "$LOCKFILE" ]; then
  echo "Lock file '$LOCKFILE' exists, exiting..."
  exit 1
fi

touch "$LOCKFILE" || exit 1
LOCALDIR="$BASELOCALDIR/$$"
mkdir "$LOCALDIR" || cleanup

# Checkout the source code from cvs
cd "$LOCALDIR" || cleanup
cvs -Qz3 "-d$CVSROOT" checkout "$MODULE" || cleanup

# Create one archive for each Business Template
for BT5 in `ls "$LOCALDIR/$MODULE"`; do
  if [ "$BT5" != "CVS" -a -d "$LOCALDIR/$MODULE/$BT5" ]; then
    echo "Building $BT5..."
    cd "$LOCALDIR/$MODULE/$BT5" || cleanup
    tar -zcf "$LOCALDIR/$BT5.bt5" --exclude CVS --exclude .cvsignore . || cleanup
  else
    echo "Skipping $BT5"
  fi
done

# Get the latest version of the genbt5list and generate the index
cd "$LOCALDIR" || cleanup
cvs -Qz3 "-d$CVSROOT" checkout "$GENBTLIST" || cleanup
python "$GENBTLIST" || cleanup

# Publish the repository
mv -f bt5list "$LOCALDIR/"*.bt5 "$BT5DIR"

# Clean up
rm -rf $LOCALDIR
rm -f $LOCKFILE
