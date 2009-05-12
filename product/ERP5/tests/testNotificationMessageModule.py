##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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

import transaction
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import DummyMailHost
from DateTime import DateTime

class TestNotificationMessageModule(ERP5TypeTestCase):
  """
  Test notification tool
  """
  run_all_test = 1
  quiet = 1

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def getTitle(self):
    return 'Notification Message Module'

  def getNotificationMessageModule(self):
    return self.getPortal().notification_message_module

  def createUser(self, name, role_list):
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(name, 'password', role_list, [])

  def changeUser(self, name):
    self.old_user = getSecurityManager().getUser()
    user_folder = self.getPortal().acl_users
    user = user_folder.getUserById(name).__of__(user_folder)
    newSecurityManager(None, user)

  def changeToPreviousUser(self):
    newSecurityManager(None, self.old_user)

  def afterSetUp(self):
    self.createUser('erp5user', ['Auditor', 'Author'])
    self.createUser('manager', ['Manager'])
    portal = self.getPortal()
    if 'MailHost' in portal.objectIds():
      portal.manage_delObjects(['MailHost'])
    portal._setObject('MailHost', DummyMailHost('MailHost'))
    portal.email_from_address = 'site@example.invalid'
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    self.tic()
    self.changeUser('erp5user')

  def beforeTearDown(self):
    transaction.abort()
    # clear modules if necessary
    module_list = (self.getNotificationMessageModule(),)
    for module in module_list:
      module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  def test_01_get_document(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test type base Method'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    module = self.getNotificationMessageModule()
    tool = self.getPortal().portal_notifications
    #Test Document A in english
    n_m_en = module.newContent(portal_type='Notification Message',
                               reference='A',
                               language='en',
                               version='01')
    n_m_en.validate()
    transaction.commit()
    self.tic()
    result = tool.getDocumentValue(reference='A')
    self.assertEqual(result.getRelativeUrl(), n_m_en.getRelativeUrl())
    #Same Document A in French
    n_m_fr = module.newContent(portal_type='Notification Message',
                               reference='A',
                               language='fr',
                               version='01')
    n_m_fr.validate()
    transaction.commit()
    self.tic()
    result = tool.getDocumentValue(reference='A', language='fr')
    self.assertEqual(result.getRelativeUrl(), n_m_fr.getRelativeUrl())
    #Duplicate Document A French with upgraded version
    n_m_fr_02 = module.newContent(portal_type='Notification Message',
                                  reference='A',
                                  language='fr',
                                  version='02')
    n_m_fr_02.validate()
    transaction.commit()
    self.tic()
    result = tool.getDocumentValue(reference='A', language='fr')
    self.assertEqual(result.getRelativeUrl(), n_m_fr_02.getRelativeUrl())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNotificationMessageModule))
  return suite
