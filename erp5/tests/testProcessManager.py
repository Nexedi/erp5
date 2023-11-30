##############################################################################
#
# Copyright (c) 2023 Nexedi SA and Contributors. All Rights Reserved.
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
# as published by the Free Software Foundation; either version 3
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

import os
import shutil
import subprocess
import tempfile
import unittest
import sys
import time

from erp5.util.testnode.ProcessManager import ProcessManager


class TestProcessManagerKillAll(unittest.TestCase):
  def setUp(self):
    self.path = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.path)
    self.script = os.path.join(self.path, 'script')
    with open(self.script, 'w') as f:
      f.write('#!/bin/sh\nsleep 30')
    os.chmod(self.script, 0o700)
    self.pm = ProcessManager()
    self.start_time = time.time()

  def tearDown(self):
    self.assertLess(
      time.time() - self.start_time,
      29,
      'Process did not stop in time',
    )

  def test_killall_script_in_path(self):
    process = subprocess.Popen([self.script])
    self.pm.killall(self.path)
    process.communicate()
    self.assertTrue(process.poll())

  def test_killall_another_path(self):
    process = subprocess.Popen([self.script])
    self.pm.killall("another path")
    self.assertIsNone(process.poll())
    process.kill()
    process.communicate()
    process.wait()

  def test_killall_proctitle_cwd(self):
    with open(self.script, 'w') as f:
      f.write('''if 1:
      import setproctitle
      setproctitle.setproctitle('hidden')
      import time
      time.sleep(30)
      ''')
    process = subprocess.Popen([sys.executable, self.script], cwd=self.path)
    self.pm.killall(self.path)
    process.communicate()
    self.assertTrue(process.poll())
