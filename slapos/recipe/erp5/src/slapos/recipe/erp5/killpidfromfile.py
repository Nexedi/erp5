import sys
import os
import signal
def killpidfromfile():
  file = sys.argv[1]
  sig = getattr(signal, sys.argv[2], None)
  if sig is None:
    raise ValueError('Unknwon signal name %s' % sys.argv[2])
  if os.path.exists(file):
    pid = int(open(file).read())
    print 'Killing pid %s with signal %s' % (pid, sys.argv[2])
    os.kill(pid, sig)
