export INSTANCE_HOME=/home/$USER/zope
export SOFTWARE_HOME=/usr/lib/zope/lib/python/
export COPY_OF_INSTANCE_HOME=$INSTANCE_HOME
export COPY_OF_SOFTWARE_HOME=$SOFTWARE_HOME

dir="`dirname $0`"
if test -n "$dir"; then
  cd $dir
fi
python runalltests.py
