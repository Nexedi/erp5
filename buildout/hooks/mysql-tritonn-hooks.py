import errno
import os

# the comand below assumes there is only one sub-directory under the
# 'compile-directory', which is why the cd .../* would work.
CMDS = """
cd %s/*
libtoolize -c -f
which aclocal-1.9 >/dev/null 2>/dev/null && aclocal-1.9 || aclocal
autoheader
which automake-1.9 >/dev/null 2>/dev/null && automake-1.9 -c -a -i || automake -c -a -i
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
