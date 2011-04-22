import os
import sys
import time
def catdatefile(args):
  directory = args[0]
  try:
    suffix = args[1]
  except IndexError:
    suffix = '.log'
  f = open(os.path.join(directory,
    time.strftime('%Y-%m-%d.%H:%M.%s') + suffix), 'aw')
  for line in sys.stdin.read():
    f.write(line)
  f.close()
