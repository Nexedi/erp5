import os
import subprocess
import time
import sys


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
      # XXX: Follow http://dev.mysql.com/doc/refman/5.0/en/default-privileges.html
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
  sys.stdout.flush()
  sys.stderr.flush()
  os.execl(mysqld_wrapper_list[0], *mysqld_wrapper_list)


def updateMysql(args):
  conf = args[0]
  sleep = 30
  is_succeed = False
  while True:
    if not is_succeed:
      mysql_upgrade_list = [conf['mysql_upgrade_binary'], '--no-defaults', '--user=root', '--socket=%s' % conf['socket']]
      mysql_upgrade = subprocess.Popen(mysql_upgrade_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      result = mysql_upgrade.communicate()[0]
      if mysql_upgrade.returncode is None:
        mysql_upgrade.kill()
      if mysql_upgrade.returncode != 0 and not 'is already upgraded' in result:
        print "Command %r failed with result:\n%s" % (mysql_upgrade_list, result)
        print 'Sleeping for %ss and retrying' % sleep
      else:
        if mysql_upgrade.returncode == 0:
          print "MySQL database upgraded with result:\n%s" % result
        else:
          print "No need to upgrade MySQL database"
        mysql_list = [conf['mysql_binary'].strip(), '--no-defaults', '-B', '--user=root', '--socket=%s' % conf['socket']]
        mysql = subprocess.Popen(mysql_list, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = mysql.communicate(conf['mysql_script'])[0]
        if mysql.returncode is None:
          mysql.kill()
        if mysql.returncode != 0:
          print 'Command %r failed with:\n%s' % (mysql_list, result)
          print 'Sleeping for %ss and retrying' % sleep
        else:
          is_succeed = True
          print 'SlapOS initialisation script succesfully applied on database.'
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(sleep)
