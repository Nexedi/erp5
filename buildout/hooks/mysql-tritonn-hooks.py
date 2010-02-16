import errno
import os

# the comand below assumes there is only one sub-directory under the
# 'compile-directory', which is why the cd .../* would work.
CMDS = """
cd %s/*
libtoolize -c -f
aclocal-1.9
autoheader
automake-1.9 -c -a -i
autoconf
touch sql/sql_yacc.yy
""".strip()

def pre_configure_hook(options, buildout):
    os.system(CMDS % options['compile-directory'])

def post_make_hook(options, buildout):
    try:
    	os.mkdir("%s/var" % options['location'])
    except OSError, e:
	if e.errno != errno.EEXIST:
	    raise
