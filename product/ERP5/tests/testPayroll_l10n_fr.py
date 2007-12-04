##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Fabien Morin <fabien.morin@gmail.com>
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
"""
  Tests paysheet creation using paysheet model.

TODO:
  this test currently just verify that this bt could be installed,
  test method must be add to verify things specific to this localised bt.
"""

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_parent

class TestPayroll_l10n_fr(ERP5TypeTestCase):

  run_all_test = 1
  quiet = 1

  def getTitle(self):
    return "Payroll_l10n_fr"

  def afterSetUp(self):
    """Prepare the test."""
    self.portal = self.getPortal()
    self.login()

  def login(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('admin', 'admin', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('admin').__of__(uf)
    newSecurityManager(None, user)

  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
        'erp5_payroll', 'erp5_payroll_l10n_fr')


  def test_01_btInstallation(self, quiet=0, run=run_all_test):
    '''
      this test must be replace with real test
      it's just here because a test method must be present to launch test
    '''
    if not run: return
    if not quiet:
      self.logMessage('BT Installation')
    pass

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPayroll_l10n_fr))
  return suite
 
