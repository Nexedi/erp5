# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Lukasz Nowak <luke@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#                    Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
""" Run this test at software built folder.

    cd software
    python path/to/assertInstance.py
"""
import signal
import pexpect, time
import os
import unittest
import subprocess
import shutil

class TimeoutException(Exception):
  pass

class SubFailed(Exception):
  pass

def callWithTimeout(command_list, timeout=60, cwd=None,
    input_list=None):

  output = []
  def timeout_handler(signum, frame):
    raise TimeoutException()

  old_handler = signal.signal(signal.SIGALRM, timeout_handler)
  signal.signal(signal.SIGALRM, timeout_handler)
  signal.alarm(timeout)
  command = None
  try:
    try:
      returncode = None
      command = pexpect.spawn(" ".join(command_list), timeout=timeout, cwd=cwd)
      isalive = True
      while isalive:
        if input_list is not None:
          for input in input_list:
            command.expect(input[0])
            command.sendline(input[1])
            time.sleep(1)
        line = command.readline()
        if line:
          line = line[:-1]
          l = line.rstrip('\n').rstrip('\r')
          print l
          output.append(l)
        isalive = command.isalive()
      for line in command.readlines():
        print line
        output.append(l)
      command.close()
      returncode = command.exitstatus
    except TimeoutException:
      returncode = 1
      command.close()
  finally:
    if command is not None:
      command.kill(signal.SIGKILL)
    signal.signal(signal.SIGALRM, old_handler)
    signal.alarm(0)
  if returncode != 0:
    raise SubFailed, "%s %s" % (returncode, command_list)
  return returncode, "\n".join(output)

class AssertDefaultERP5Instance26(unittest.TestCase):
  instance_path = os.path.join(os.getcwd(),".instance_test")
  software_path = os.getcwd()
  extends_cache = os.path.join(os.getcwd(),"extends-cache")
  instance_buildout = """[buildout]
extends-cache = %(extends_cache)s
offline = true
extends =
  %(instance_profile_url)s
  %(instance_template_file)s

parts =
  mysql-instance
  cloudooo-instance
  supervisor-instance
  runUnitTest
  development-site

[configuration]
supervisor_port = 19999
mysql_port = 19998
oood_port = 19997

[development-site]
http-address = 19996
"""
  instance_profile_url = 'https://svn.erp5.org/repos/public/erp5/trunk/buildout/profiles/development-2.12.cfg'
  binary_bootstrap_file_name = 'bootstrap2.6'

  def assertRelativePathExists(self,relative_list):
    path_list = [self.instance_path]
    path_list.extend(relative_list)
    self.assertTrue(os.path.exists(os.path.join(*path_list)))

  def test(self):
    if not os.path.exists(self.instance_path):
      mkdir = ['mkdir', self.instance_path]
      callWithTimeout(mkdir)
  
    self.assertTrue(os.path.exists(self.instance_path))

    # Create buildout profile
    instance_kw = dict(
      instance_profile_url = self.instance_profile_url,
      extends_cache = self.extends_cache,
      instance_template_file = os.path.join(self.software_path, 'instance.inc')
    )
    
    file(os.path.join(self.instance_path, 'buildout.cfg'), 'w').write(
        self.instance_buildout % instance_kw)
    
    # Bootstrap instance
    instance_bootstrap = [os.path.join(self.software_path, 'bin' , self.binary_bootstrap_file_name)]
    callWithTimeout(instance_bootstrap, cwd=self.instance_path)

    self.assertRelativePathExists(['bin', 'buildout'])

    # Run instance buildout
    callWithTimeout([os.path.join(self.instance_path, 'bin', 'buildout')], cwd=self.instance_path)

    self.assertRelativePathExists(['var'])
    self.assertRelativePathExists(['var', 'development-site'])
    self.assertRelativePathExists(['var', 'bin', 'supervisord'])
    self.assertRelativePathExists(['var', 'bin', 'mysql'])
    self.assertRelativePathExists(['var', 'bin', 'cloudoooctl'])
    # Start supervisor in foreground mode and have control over its process
    # as in the end it have to be cleanly shutdown
    supervisord_command = [os.path.join(self.instance_path, 'bin', 'supervisord'),
       '-n']
    supervisord_popen = subprocess.Popen(supervisord_command, cwd=self.instance_path)
    supervisord_popen.poll()
    # Wait 10 seconds, to give supervisord chance to start required services
    time.sleep(10)
    try:
      mysql_command = [os.path.join(self.instance_path, 'var', 'bin', 'mysql'),
              '-h', '127.0.0.1', '-u', 'root']
  
      callWithTimeout(mysql_command,
              cwd=self.instance_path, input_list=[
                ("mysql> ", "create database development_site;"),
                ("mysql> ", "grant all privileges on development_site.* to "
                  "'development_user'@'localhost' identified by "
                  "'development_password';"),
                ("mysql> ", "grant all privileges on development_site.* to "
                  "'development_user'@'127.0.0.1' identified by "
                  "'development_password';"),
                ("mysql> ", "create database test212;"),
                ("mysql> ", "grant all privileges on test212.* to "
                  "'test'@'localhost';"),
                ("mysql> ", "grant all privileges on test212.* to "
                  "'test'@'127.0.0.1';"),
                ("mysql> ", "exit")])

      # Run a test from readme
      test_run_command = [os.path.join(self.instance_path, 'bin', 'runUnitTest'),
                                         'testClassTool']
      returncode, output = callWithTimeout(test_run_command, 
                                           timeout=1200, 
                                           cwd=self.instance_path)
      self.assertEquals(output.split("\n")[-1], 'OK')

      bt5_directory = os.path.join(self.instance_path, 'bt5')
      try:
        svn = os.path.join(self.software_path, 'parts', 'subversion', 'bin', 'svn')
        if not os.path.exists(bt5_directory):
          os.mkdir(bt5_directory)
          # Get needed business template
        for bt5 in ['erp5_base', 'erp5_ingestion', 'erp5_ingestion_mysql_'
            'innodb_catalog', 'erp5_web', 'erp5_dms', 'erp5_full_text_myisam_catalog']:
          callWithTimeout([svn, 'export', '--non-interactive',
              '--trust-server-cert',
              'https://svn.erp5.org/repos/public/erp5/trunk/bt5/' + bt5,
              os.path.join(bt5_directory, bt5)], timeout=600)
        # Check that catalog is working
        for test in ['testERP5Catalog.TestERP5Catalog.'
            'test_04_SearchFolderWithDeletedObjects', 
            'testDms.TestDocument.'
            'testOOoDocument_get_size']:
          test_run_command = [os.path.join(self.instance_path, 'bin', 'runUnitTest'),
             '--bt5_path=%s/bt5' % self.instance_path, test]
          returncode, output = \
            callWithTimeout(test_run_command, timeout=1200,cwd=self.instance_path)
          self.assertEquals(output.split("\n")[-1], 'OK')
      finally:
        if os.path.exists(bt5_directory):
          shutil.rmtree(bt5_directory)
    finally:
      # Stop supervisor
      while supervisord_popen.poll() is None:
        # send SIGKILL
        supervisord_popen.terminate()
        # give some time to terminate services
        time.sleep(5)
    callWithTimeout(["rm -rf", self.instance_path])

if __name__ == '__main__':
  unittest.main()
