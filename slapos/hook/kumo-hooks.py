import os
import sys
import traceback
from shutil import copy
from subprocess import Popen, PIPE

CONFIGURE_PATH = os.path.join('configure')
CONFIGURE_BACKUP_PATH = CONFIGURE_PATH + '_disabled'
# Fake configure, generating a fake Makefile which will create a marker file
# instead of actually installing anything.
# This is needed (?) to fetch --prefix from configure parameters, so we know
# where to tell Makefile to put the dummy file.
FAKE_CONFIGURE = '''#!%(python)s -S
import os
import sys
print 'Configuration is disabled on this host because %%s'
print 'Original configure file available at %(backup)s'
prefix = None
next = False
for arg in sys.argv:
    if next:
        prefix = arg
        break
    if arg.startswith('--prefix'):
        if arg.startswith('--prefix='):
            _, prefix = arg.split('=', 1)
            break
        next = True
if prefix is None:
    raise '--prefix parameter not found'
# Generate Makefile with proper prefix
open('Makefile', 'w').write("""all:
\techo 'make disabled, see configure'

install:
\ttouch %%%%s""" %%%% (
  os.path.join(prefix, 'BUILD_DISABLED_BY_BUILDOUT'),
))
sys.exit(0)
''' % {
    'backup': CONFIGURE_BACKUP_PATH,
    'python': sys.executable,
}

def pre_configure_hook(options, buildout):
    gcc_executable = os.getenv('CC', 'gcc')
    try:
        gcc = Popen([gcc_executable, '-v'], stdout=PIPE, stderr=PIPE,
            close_fds=True)
    except OSError, (errno, _):
        if errno == 2:
            # No gcc installed, nothing to check
            pass
        else:
            print 'Unexpected failure trying to detect gcc version'
            traceback.print_exc()
    else:
        gcc.wait()
        # Considered innocent until proven guilty.
        error = None
        for line in '\n'.join((gcc.stdout.read(), gcc.stderr.read())).splitlines():
            if line.startswith('gcc version'):
                if '4.1.1' in line and 'prerelease' in line:
                    # There is a bug in 4.1.1 prerelease (ie, as of mandriva
                    # 2007.0) g++ preventing kumo compilation from succeeding.
                    error = 'broken GCC version: %s' % (line, )
                break
        else:
            print >>sys.stderr, 'GCC version could not be detected, ' \
                'building anyway'
        if error is not None:
            print 'Disabling build, with reason:', error
            # Copy to preserver permission
            copy(CONFIGURE_PATH, CONFIGURE_BACKUP_PATH)
            open(CONFIGURE_PATH, 'w').write(FAKE_CONFIGURE % (error, ))

