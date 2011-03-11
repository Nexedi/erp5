import os
import subprocess
import sys
import time


def runMysql(args):
  sleep = 60
  conf = args[0]
  mysqld_wrapper_list = [conf['mysqld_binary'], '--defaults-file=%s' %
      conf['configuration_file']]
  # we trust mysql_install that if mysql directory is available mysql was
  # correctly initalised
  if not os.path.isdir(os.path.join(conf['data_directory'], 'mysql')):
    while True:
      # XXX: Protect with proper root password
      popen = subprocess.Popen([conf['mysql_install_binary'],
        '--skip-name-resolve', '--no-defaults', '--datadir=%s' %
        conf['data_directory']],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      result = popen.communicate()[0]
      if popen.returncode is None or popen.returncode != 0:
        print "Failed to initialise server.\nThe error was: %s" % result
        print "Waiting for %ss and retrying" % sleep
        time.sleep(sleep)
      else:
        print "Mysql properly initialised"
        break
  else:
    print "MySQL already initialised"
  print "Starting %r" % mysqld_wrapper_list[0]
  os.execl(mysqld_wrapper_list[0], *mysqld_wrapper_list)


def updateMysql(args):
  mysql_command_list = args[0]
  mysql_script = args[1]
  sleep = 30
  is_succeed = False
  while True:
    if not is_succeed:
      mysql = subprocess.Popen(mysql_command_list, stdin=subprocess.PIPE,
          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      result = mysql.communicate(mysql_script)[0]
      if mysql.returncode is None:
        mysql.kill()
      if mysql.returncode != 0:
        print 'Script failed with: %s' % result
        print 'Sleeping for %ss and retrying' % sleep
      else:
        is_succeed = True
        print 'Script succesfully run on database, exiting'
    time.sleep(sleep)
