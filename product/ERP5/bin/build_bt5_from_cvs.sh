#!/bin/bash

# TODO: BT5 version support (stable/unstable)

# Lock file name
LOCKFILE="/tmp/$0.lock"
# CVS root
CVSROOT=":pserver:anonymous@cvs.erp5.org:/cvsroot"
# Module containing business template
MODULES="erp5_bt5 erp5_banking ERP5/bootstrap"
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

  for MODULE in $MODULES; do
  # Checkout the source code from cvs
  cd "$LOCALDIR" || cleanup
  cvs -Qz3 "-d$CVSROOT" checkout "$MODULE" || cleanup

  # Create one archive for each Business Template
  cd "$LOCALDIR/$MODULE"
  for BT5 in `ls "$LOCALDIR/$MODULE"`; do
  if [ "$BT5" != "CVS" -a -d "$LOCALDIR/$MODULE/$BT5" ]; then
    tar -zcf "$LOCALDIR/$BT5.bt5" --exclude CVS --exclude .cvsignore "$BT5" || cleanup
  fi
  done
done

# Get the latest version of the genbt5list and generate the index
cd "$LOCALDIR" || cleanup
cvs -Qz3 "-d$CVSROOT" checkout "$GENBTLIST" || cleanup

# Publish the repository
mv -f "$LOCALDIR/"*.bt5 "$BT5DIR"

# Generate the index from repository directory, in case there are BT5 manually added there
cd "$BT5DIR" || cleanup
/usr/bin/python "$LOCALDIR/$GENBTLIST" > /dev/null
chmod go+r bt5list

# Clean up
rm -rf $LOCALDIR
rm -f $LOCKFILE
