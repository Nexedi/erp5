import os
import sys
import time


def runApache(args):
  sleep = 60
  conf = args[0]
  while True:
    ready = True
    for f in conf.get('required_path_list', []):
      if not os.path.exists(f):
        print 'File %r does not exists, sleeping for %s' % (f, sleep)
        ready = False
    if ready:
      break
    time.sleep(sleep)
  apache_wrapper_list = [conf['binary'], '-f', conf['config'], '-DFOREGROUND']
  apache_wrapper_list.extend(sys.argv[1:])
  sys.stdout.flush()
  sys.stderr.flush()
  os.execl(apache_wrapper_list[0], *apache_wrapper_list)
