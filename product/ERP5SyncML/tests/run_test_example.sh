export INSTANCE_HOME=/home/$USER/zope
export SOFTWARE_HOME=/usr/lib/zope/lib/python/

dir="`dirname $0`"
if test -n "$dir"; then
  cd $dir
fi
python runalltests.py
