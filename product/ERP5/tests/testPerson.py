##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
import time

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestPerson(ERP5TypeTestCase):

  run_all_test = 1
 
  def getTitle(self):
    return "Person Test"
    
  def getBusinessTemplateList(self):
    """  """
    return ('erp5_base',)
  
  def afterSetUp(self):
    self.login()
    
  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def test_01_CopyPastePersonObject(self, quiet=0, run=run_all_test):
    """ Test copy/paste a Person object. """
    if not run: 
      return
    if not quiet:
      portal = self.getPortal()
      person_module = self.getPersonModule()
      person = person_module.newContent(portal_type='Person')
      person.setReference('ivan')

      ## copy object as if using ERP5/ZMI UI
      person_copy = person_module.manage_copyObjects(ids=(person.getId(),))
      person_copy_id = person_module.manage_pasteObjects(person_copy)[0]['new_id']
      person_copy_obj = person_module[person_copy_id]
      ## because we copy/paste Person object in the same ERP5 
      ## instance its reference must be resetted
      self.assertEquals(person_copy_obj.getReference(), None)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPerson))
        return suite

