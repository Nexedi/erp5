# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi KK, Nexedi SA and Contributors. All Rights Reserved.
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
import unittest
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.CMFCore.exceptions import AccessControl_Unauthorized


class TestPDMWithSecurity(ERP5TypeTestCase):
  """
  Test PDM with Security
  """

  def getTitle(self):
    return 'Test PDM with Security'

  def getBusinessTemplateList(self):

    return ('erp5_base',
            'erp5_pdm',
            )

  def afterSetUp(self):
    if getattr(self.portal, '_run_after_setup', None) is not None:
      return


    self.portal._run_after_setup = True
    transaction.commit()
    self.tic()

  def login(self, quiet=0):
    ERP5TypeTestCase.login(self, quiet)
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser('author', '', ['Auditor', 'Author'], [])
    user_folder._doAddUser('assignor', '', ['Auditor', 'Author', 'Assignor'], [])
    user_folder._doAddUser('assignee', '', ['Auditor', 'Author', 'Assignee'], [])

  def changeUser(self, name):
    user_folder = self.getPortal().acl_users
    user = user_folder.getUserById(name).__of__(user_folder)
    newSecurityManager(None, user)

  def testValidatedProductCanContainMeasure(self):
    """
    Make sure that validated product can contain measure.
    """
    self.changeUser('author')
    product = self.portal.product_module.newContent(portal_type='Product',
                                                    title='Chair')

    transaction.commit()
    self.tic()

    # Author try to add a measure to validated product and succeed.
    product.newContent(portal_type='Measure')

    transaction.commit()
    self.tic()

    self.assertEqual(len(product.contentValues(portal_type='Measure')), 1)

    self.changeUser('assignor')
    self.portal.portal_workflow.doActionFor(product, 'validate_action')

    transaction.commit()
    self.tic()

    self.assertEqual(product.getValidationState(), 'validated')

    # Change to author and try to add a measure to validated product and fail.
    self.changeUser('author')
    self.assertRaises(AccessControl_Unauthorized,
                      product.newContent, portal_type='Measure')

    # Change to assignee and try to add a measure to validated product and succeed.
    self.changeUser('assignee')
    product.newContent(portal_type='Measure')

    transaction.commit()
    self.tic()

    self.assertEqual(len(product.contentValues(portal_type='Measure')),
                     2)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPDMWithSecurity))
  return suite
