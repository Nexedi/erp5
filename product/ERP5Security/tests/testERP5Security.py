##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                                    Jerome Perrin <jerome@nexedi.com>
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

"""Tests ERP5 User Management.
"""
import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from Products.PluggableAuthService import PluggableAuthService

class TestERP5Security(ERP5TypeTestCase):
  """Test invoice are created from orders then packing lists. """
 
  RUN_ALL_TESTS = 1
  
  def getTitle(self):
    """Title of the test."""
    return "ERP5 Security"
  
  def getBusinessTemplateList(self):
    """List of BT to install. """
    return ('erp5_base',)
  
  def login(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)
  
  def test_Interfaces(self, run=RUN_ALL_TESTS):
    """Tests plugins respects interfaces they declare."""
    # TODO
    if not run:
      return

  def test_UserFolder(self, run=RUN_ALL_TESTS):
    """Tests user folder has correct meta type."""
    if not run:
      return
    self.failUnless(isinstance(self.getPortal().acl_users,
        PluggableAuthService.PluggableAuthService))

  def test_MultiplePersonReference(self, run=RUN_ALL_TESTS):
    """Tests that it's refused to create two Person with same reference."""
    if not run:
      return
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person',
                     reference='new_person')
    get_transaction().commit()
    self.tic()
    self.assertRaises(RuntimeError, person_module.newContent,
                    portal_type='Person', reference='new_person')

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5Security))
    return suite

