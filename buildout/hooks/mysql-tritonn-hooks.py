import errno
import os

# the comand below assumes there is only one sub-directory under the
# 'compile-directory', which is why the cd .../* would work.
CMDS = """
libtoolize -c -f
aclocal %(aclocal-options)s
autoheader
automake -c -a -f
autoconf
touch sql/sql_yacc.yy
""".strip()

def pre_configure_hook(options, buildout):
    os.system(CMDS % {
        'aclocal-options':options.get('aclocal-options', '').strip(),
    })

def post_make_hook(options, buildout):
    try:
        os.mkdir("%s/var" % options['location'])
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
