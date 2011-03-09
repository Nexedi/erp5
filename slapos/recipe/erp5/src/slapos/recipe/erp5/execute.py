import sys
import os
import signal
import subprocess
import time


def execute(args):
  """Portable execution with process replacement"""
  # Note: Candidate for slapos.lib.recipe
  os.execv(args[0], args)

child_pg = None


def sig_handler(signal, frame):
  print 'Received signal %r, killing children and exiting' % signal
  if child_pg is not None:
    os.killpg(child_pg, signal.SIGHUP)
    os.killpg(child_pg, signal.SIGTERM)
  sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGQUIT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)


def execute_with_signal_translation(args):
  """Run process as children and translate from SIGTERM to another signal"""
  child = subprocess.Popen(args, close_fds=True, preexec_fn=os.setsid)
  child_pg = child.pid
  try:
    while True:
      print 'Running'
      time.sleep(10)
  finally:
    os.killpg(child_pg, signal.SIGHUP)
    os.killpg(child_pg, signal.SIGTERM)
