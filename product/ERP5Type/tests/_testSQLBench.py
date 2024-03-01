##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import os
import subprocess
import unittest

class TestSQLBench(unittest.TestCase):
  """Tests to get sqlbench values
  """
  def test_sqlbench(self):
    """
    launch sql bench test to check speed of hardware. There is quite dirty
    launch of bench depending on many environ variables. However this allows
    to get a quick solution
    """
    home = os.environ['REAL_INSTANCE_HOME']
    sql_connection_string = os.environ['erp5_sql_connection_string']
    database_and_server, user, password = sql_connection_string.split(' ')
    database, host = database_and_server.split('@')
    sqlbench_path = os.environ.get('SQLBENCH_PATH')
    if not sqlbench_path:
      software_home = os.environ['OPENSSL_BINARY'].replace(
           "/bin/openssl", "/software_release/")
      sqlbench_path = software_home + '/parts/mariadb/sql-bench'
      perl_command = software_home + "/parts/perl/bin/perl"
    else:
      perl_command = 'perl'
    command_list = [perl_command,
       sqlbench_path + '/test-alter-table',
      '--database', database,
      '--host', host, '--user', user, '--password', password]
    print(command_list)
    process = subprocess.Popen(command_list,
      cwd = sqlbench_path,
      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    self.assertEqual(0, len(error), error)
    print(output)
    self.assertTrue(output.find("Total time: ")>=0)
