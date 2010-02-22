import sys, os
def invokepython():
  os.environ['PYTHONPATH'] = ':'.join(sys.path)
  os.execl(sys.executable, *sys.argv)
