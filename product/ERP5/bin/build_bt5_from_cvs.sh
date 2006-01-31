#!/bin/bash

# Where we want to store the source code from cvs
CVS_PATH="/home/$USER/cvs"
REPOSIT="cvs.erp5.org"

# Retrieve the version of the source code as anonymous user to be sure we get published code only
cd $CVS_PATH && cvs -d:pserver:anonymous@$REPOSIT:/cvsroot checkout erp5_bt
mkdir $CVS_PATH/bt5

# Remove CVS extra files
find $CVS_PATH/erp5_bt/* -name "CVS" | xargs rm -rf

# Get the list of Business Template
# BT5_LIST is the list of folder found in $CVS_PATH/erp5_bt
BT5_LIST=`ls $CVS_PATH/erp5_bt`

# Create one archive for each Business Template
cd $CVS_PATH/erp5_bt
for $BT5 in $BT5_LIST
  do
    cd $CVS_PATH/erp5_bt
    tar zcvf $BT5.tgz $BT5
    mv $CVS_PATH/erp5_bt/$BT5.tgz $CVS_PATH/bt5/$BT5.bt5
  done

# Get the latest version of the genbt5list (the script that generate the index)
cd $CVS_PATH/bt5
cvs -d:pserver:anonymous@$REPOSIT:/cvsroot checkout ERP5/bin/genbt5list

# Generate the repository index
python $CVS_PATH/bt5/genbt5list
rm -f genbt5list

# Publish the repository
mv -f $CVS_PATH/bt5/* /var/www/erp5.org/bt5/

# Clean up
rm -rf $CVS_PATH/*