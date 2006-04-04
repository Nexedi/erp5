#!/bin/bash

# TODO: BT5 version support (stable/unstable)

# Lock file name
LOCKFILE="/tmp/`basename $0`.lock"
# SVN paths
SVNROOT="https://svn.erp5.org/repos/public/erp5/trunk/"
# Relative svn paths to fetch
MODULES="bt5 products/ERP5/bootstrap"
# Script generating the business template repository index
GENBTLIST="products/ERP5/bin"
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
  svn co "$SVNROOT$MODULE" > /dev/null || cleanup
  BMODULE=`basename "$MODULE"`

  # Create one archive for each Business Template
  cd "$LOCALDIR/$BMODULE"
  for BT5 in `ls "$LOCALDIR/$BMODULE"`; do
    if [ -d "$LOCALDIR/$BMODULE/$BT5" ]; then
      tar -zcf "$LOCALDIR/$BT5.bt5" --exclude .svn "$BT5" || cleanup
    fi
  done
done

# Get the latest version of the genbt5list and generate the index
cd "$LOCALDIR" || cleanup
svn co "$SVNROOT$GENBTLIST" > /dev/null || cleanup

# Publish the repository
mv -f "$LOCALDIR/"*.bt5 "$BT5DIR"

# Generate the index from repository directory, in case there are BT5 manually added there
cd "$BT5DIR" || cleanup
/usr/bin/python "$LOCALDIR/`basename $GENBTLIST`/genbt5list" > /dev/null
chmod go+r bt5list

# Clean up
rm -rf $LOCALDIR
rm -f $LOCKFILE
