##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors.
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
#          Fabien MORIN <fabien@nexedi.com>
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
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.backportUnittest import expectedFailure


class TestERP5Discussion(ERP5TypeTestCase):
  """Test for erp5_discussion business template.
  """

  manager_username = 'manager'
  manager_password = 'pwd'

  def getTitle(self):
    return "Test ERP5 Discussion"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_core',
            'erp5_base',
            'erp5_xhtml_style',
            'erp5_ingestion',
            'erp5_web',
            'erp5_dms',
            'erp5_knowledge_pad',
            'erp5_rss_style',
            'erp5_jquery',
            'erp5_discussion', )

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    self.portal_id = self.portal.getId()
    self.auth = '%s:%s' % (self.manager_username, self.manager_password)

  def beforeTearDown(self):
    transaction.abort()
    for module in (self.portal.discussion_thread_module,):
      module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  def stepCreateThread(self):

    module =  self.portal.getDefaultModule("Discussion Thread")
    return module.newContent(portal_type="Discussion Thread")

  def stepCreatePost(self,thread):
    return thread.newContent(portal_type="Discussion Post")

  def test_01_createDiscussionThread(self):
    """Create a new discussion thread"""

    self.stepCreateThread();
    self.stepTic()

  def test_02_createDiscussionPost(self):
    """Create a disucssion post inside a discussion thread"""

    thread = self.stepCreateThread();
    post = self.stepCreatePost(thread);
    self.stepTic()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Discussion))
  return suite
