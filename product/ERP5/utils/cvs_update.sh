#!/bin/bash

# Modules to get from the CVS
MODULES="CMFActivity CMFCategory ERP5 ERP5Catalog ERP5Form \
         ERP5OOo ERP5Security ERP5SyncML ERP5Type ZSQLCatalog \
         erp5_banking erp5_bt5"

# CVS Users name
CVS_USER="anonymous" #CVS_USER="seb"
ANON_CVS="anonymous"

# System user and group that own Zope product files
USER="zope"
GROUP="zope"

# Define paths
ZOPE_PRODUCTS="/var/lib/zope/Products"
EXTENSIONS_FOLDER="/var/lib/zope/Extensions"
BT5_FOLDER="/var/lib/zope/bt5"



LOGGED=0
ZERO=0
export CVS_RSH=ssh



# Update each module
for f in $MODULES
  do
    echo ""
    echo "----- Updating $f -----"
    if ls $ZOPE_PRODUCTS/$f > /dev/null 2>&1 /dev/null; then
      cd $ZOPE_PRODUCTS/$f && \
        cvs update -RdPA && cd $ZOPE_PRODUCTS/
    else
      if [ $CVS_USER == $ANON_CVS ] ; then
        if [ $LOGGED == $ZERO ] ; then
          cvs -d:pserver:anonymous@cvs.erp5.org:/cvsroot login
          cvs -z3 -d:pserver:anonymous@cvs.erp5.org:/cvsroot co -A $f
          LOGGED=1
        else
          cvs -z3 -d:pserver:anonymous@cvs.erp5.org:/cvsroot co -A $f
        fi
      else
        cvs -z3 -d $CVS_USER@cvs.erp5.org:/cvsroot co -A $f
      fi
    fi
  done



# Restore good right
chown -R $USER.$GROUP .



# Replace symlinks installed by the default ERP5 installation by the new ones

update_symlink() {
  BASE=$1
  SOURCE=$2
  DESTINATION=$3
  # If a previous symlink exist delete it
  cd $BASE
  if test -h $SOURCE; then
    rm -f $SOURCE
  fi
  # If there is no $SOURCE file, create a symlink
  if [ ! -e $SOURCE ]; then
    ln -s $DESTINATION
    echo "----- Symlink updated: $BASE/$SOURCE -> $DESTINATION"
  fi
}

for f in $MODULES
  do
    if test $f = "ZSQLCatalog"; then
      echo `update_symlink $EXTENSIONS_FOLDER zsqlbrain.py ../Products/ZSQLCatalog/zsqlbrain.py`
    fi
    if test $f = "ERP5"; then
      echo `update_symlink $EXTENSIONS_FOLDER InventoryBrain.py ../Products/ERP5/Extensions/InventoryBrain.py`
    fi
    if test $f = "erp5_bt5"; then
      echo `update_symlink $BT5_FOLDER erp5_bt5 ../Products/erp5_bt5`
    fi
    if test $f = "erp5_banking"; then
      echo `update_symlink $BT5_FOLDER erp5_banking ../Products/erp5_banking`
    fi
  done


exit 0
