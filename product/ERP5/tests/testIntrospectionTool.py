##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
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

from AccessControl.SecurityManagement import newSecurityManager

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import json


class TestIntrospectionTool(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    """  """
    return ('erp5_base',)

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.login()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def test_getSystemSignatureJSON(self):
    """
      Test
    """
    signature_json = self.portal.portal_introspections.getSystemSignatureAsJSON()
    signature_by_json = json.loads(signature_json)
    signature = self.portal.portal_introspections.getSystemSignatureDict()

    self.assertSameSet(signature_by_json.keys(), signature.keys())
    for key in signature:
      self.assertEqual(signature[key], signature_by_json[key])

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestIntrospectionTool))
  return suite
