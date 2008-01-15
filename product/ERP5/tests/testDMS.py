##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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

import unittest
import os

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from zExceptions import BadRequest
from Products.ERP5Type.Tool.ClassTool import _aq_reset

class TestDMS(ERP5TypeTestCase):

  run_all_test = 1
  quiet = 1

  username = 'user_test'

  def getTitle(self):
    return "DMS"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base', 'erp5_crm', 'erp5_web',
            'erp5_dms_mysql_innodb_catalog', 
            'erp5_dms',)

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, 'user', ['Manager'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    portal_catalog = self.getCatalogTool()

  def test_01_getCreationDate(self, quiet=quiet, run=run_all_test):
    """
    Check getCreationDate on all document type, as those documents 
    are not associated to edit_workflow.
    """
    if not run: return
    portal = self.getPortalObject()
    for document_type in portal.getPortalDocumentTypeList():
      module = portal.getDefaultModule(document_type)
      obj = module.newContent(portal_type=document_type)
      self.assertNotEquals(obj.getCreationDate(),
                           module.getCreationDate())
      self.assertNotEquals(obj.getCreationDate(),
                           portal.CreationDate())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDMS))
  return suite
