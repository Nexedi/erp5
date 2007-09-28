#!/bin/bash

# Modules to get from the SVN
PRODUCTS="CMFActivity CMFCategory ERP5 ERP5Banking ERP5Catalog \
          ERP5Form ERP5OOo ERP5Security ERP5Subversion ERP5SyncML \
          ERP5Type TimerService ZMySQLDDA ZSQLCatalog MimetypesRegistry PortalTransforms"

# System user and group that own Zope product files
USER="zope"
GROUP="zope"

# Define paths
ZOPE_PRODUCTS="/var/lib/zope/Products"
EXTENSIONS_FOLDER="/var/lib/zope/Extensions"
BT5_FOLDER="/var/lib/zope/bt5"

# Update each product
for p in $PRODUCTS
  do
    echo ""
    echo "----- Updating $p -----"
    if ls $ZOPE_PRODUCTS/$p > /dev/null 2>&1 /dev/null; then
      svn update $p
    else
      svn checkout https://svn.erp5.org/repos/public/erp5/trunk/products/$p
    fi
  done

# Get latests Business Templates
echo ""
echo "----- Updating Business Templates -----"
wget -nv -N --no-host-directories -r --cut-dirs=2 --level=2 --relative \
  --no-parent --accept=bt5,bt5list http://www.erp5.org/dists/snapshot/bt5/
rm -f robots.txt

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
    echo ""
    echo "----- Symlink updated: $BASE/$SOURCE -> $DESTINATION"
  fi
}

for p in $PRODUCTS
  do
    if test $p = "ZSQLCatalog"; then
      echo `update_symlink $EXTENSIONS_FOLDER zsqlbrain.py ../Products/ZSQLCatalog/zsqlbrain.py`
    fi
    if test $p = "ERP5"; then
      echo `update_symlink $EXTENSIONS_FOLDER InventoryBrain.py ../Products/ERP5/Extensions/InventoryBrain.py`
    fi
    if test $p = "bt5"; then
      echo `update_symlink $BT5_FOLDER erp5_bt5 ../Products/bt5`
    fi
  done

exit 0
