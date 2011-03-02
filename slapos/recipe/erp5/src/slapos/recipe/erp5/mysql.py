import os
import subprocess
import sys
import time

def runMysql(args):
  sleep = 60
  initialise_command_list = args[0]
  mysql_conf = args[1]
  mysql_wrapper_list = [mysql_conf['mysqld_binary'],
      '--defaults-file=%s'%mysql_conf['configuration_file']]
  while True:
    # XXX: Protect with proper root password
    popen = subprocess.Popen(initialise_command_list,
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = popen.communicate()[0]
    if popen.returncode is None or popen.returncode != 0:
      print "Failed to initialise server.\nThe error was: %s" % result
      print "Waiting for %ss and retrying" % sleep
      time.sleep(sleep)
    else:
      print "Mysql properly initialised"
      break
  sys.stdout.flush()
  sys.stderr.flush()
  os.execl(mysql_wrapper_list[0], *mysql_wrapper_list)

def updateMysql(args):
  mysql_command_list = args[0]
  mysql_script = args[1]
  sleep = 30
  while True:
    mysql = subprocess.Popen(mysql_command_list, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = mysql.communicate(mysql_script)[0]
    if mysql.returncode is None:
      mysql.kill()
    if mysql.returncode != 0:
      print 'Script failed with: %s' % result
      print 'Sleeping for %ss and retrying' % sleep
    else:
      print 'Script succesfully run on database, exiting'
    time.sleep(sleep)
