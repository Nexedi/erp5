##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kazuhiko <kazuhiko@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from AccessControl.SecurityManagement import newSecurityManager,\
                                             getSecurityManager
from zLOG import LOG
from DateTime import DateTime
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Form.Document.Preference import Priority
from Products.ERP5Form.Selection import Selection


class TestSelectionTool(ERP5TypeTestCase):
  quiet = 1
  run_all_tests = 1
  
  def getTitle(self):
    return "SelectionTool"

  def getBusinessTemplateList(self):
    # Use the same framework as the functional testing for convenience.
    # This adds some specific portal types and skins.
    return ('erp5_ui_test',)

  def afterSetUp(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', '', ['Manager', 'Assignor'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)
    self.portal_selections = self.getPortal().portal_selections
    self.portal_selections.setSelectionFor('test_selection', Selection())
    self.portal_selections.setSelectionParamsFor('test_selection', {'key':'value'})

  def testGetSelectionNames(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals(['test_selection'],
                      self.portal_selections.getSelectionNames())

  def testGetSelectionFor(self, quiet=quiet, run=run_all_test):
    if not run: return
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assert_(isinstance(selection, Selection))
    self.assertEquals('test_selection', selection.name)

  def testGetSelectionParamsFor(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals({'key':'value'},
                      self.portal_selections.getSelectionParamsFor('test_selection'))

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSelectionTool))
    return suite
