##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
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



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
import time

class TestCMFActivity(ERP5TypeTestCase):

  run_all_test = 1
  # Different variables used for this test
  company_id = 'Nexedi'
  title1 = 'title1'
  title2 = 'title2'
  destination_company_stock = 'site/Stock_MP/Gravelines'
  destination_company_group = 'group/Coramy'
  destination_company_id = 'Coramy'
  component_id = 'brick'
  sales_order_id = '1'
  purchase_order_id = '1'
  quantity = 10
  base_price = 0.7832

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

      the business template crm give the following things :
      modules:
        - person
        - organisation
      base categories:
        - region
        - subordination
      
      /organisation
    """
    return ('erp5_crm',)

  def getCategoriesTool(self):
    return getattr(self.getPortal(), 'portal_categories', None)

  def getRuleTool(self):
    return getattr(self.getPortal(), 'portal_Rules', None)

  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  #def populate(self, quiet=1, run=1):
  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    # Then add new components
    if not(hasattr(portal,'organisation')):
      portal.portal_types.constructContent(type_name='Organisation Module',
                                         container=portal,
                                         id='organisation')
    organisation_module = self.getOrganisationModule()
    if not(organisation_module.hasContent(self.company_id)):
      o1 = organisation_module.newContent(id=self.company_id)

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def InvokeAndCancelActivity(self, activity):
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(self.title1)
    self.assertEquals(self.title1,organisation.getTitle())
    organisation.activate(activity=activity).setTitle(self.title2)
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageCancel(organisation.getPhysicalPath(),'setTitle')
    # Needed so that the message are removed from the queue
    get_transaction().commit()
    self.assertEquals(self.title1,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    organisation.activate(activity=activity).setTitle(self.title2)
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageInvoke(organisation.getPhysicalPath(),'setTitle')
    # Needed so that the message are removed from the queue
    get_transaction().commit()
    self.assertEquals(self.title2,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)

  def DeferedSetTitleActivity(self, activity):
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(self.title1)
    self.assertEquals(self.title1,organisation.getTitle())
    organisation.activate(activity=activity).setTitle(self.title2)
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    self.assertEquals(self.title1,organisation.getTitle())
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(self.title2,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)

  def CallOnceWithActivity(self, activity):
    portal = self.getPortal()
    def setFoobar(self):
      if hasattr(self,'foobar'):
        self.foobar = self.foobar + 1
      else:
        self.foobar = 1
    def getFoobar(self):
      return (getattr(self,'foobar',0))
    from Products.ERP5Type.Document.Organisation import Organisation
    organisation =  portal.organisation._getOb(self.company_id)
    Organisation.setFoobar = setFoobar
    Organisation.getFoobar = getFoobar
    organisation.foobar = 0
    organisation.setTitle(self.title1)
    self.assertEquals(0,organisation.getFoobar())
    organisation.activate(activity=activity).setFoobar()
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(1,organisation.getFoobar())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    organisation.activate(activity=activity).setFoobar()
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageInvoke(organisation.getPhysicalPath(),'setFoobar')
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(2,organisation.getFoobar())

  def test_01_DeferedSetTitleSQLDict(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Defered Set Title SQLDict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferedSetTitleActivity('SQLDict')

  def test_02_DeferedSetTitleSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Defered Set Title SQLQueue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferedSetTitleActivity('SQLQueue')

  def test_03_DeferedSetTitleRAMDict(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Defered Set Title RAMDict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferedSetTitleActivity('RAMDict')

  def test_04_DeferedSetTitleRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Defered Set Title RAMQueue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferedSetTitleActivity('RAMQueue')

  def test_05_InvokeAndCancelSQLDict(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Invoke And Cancel SQLDict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.InvokeAndCancelActivity('SQLDict')

  def test_06_InvokeAndCancelSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Invoke And Cancel SQLQueue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.InvokeAndCancelActivity('SQLQueue')

  def test_07_InvokeAndCancelRAMDict(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Invoke And Cancel RAMDict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.InvokeAndCancelActivity('RAMDict')

  def test_08_InvokeAndCancelRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Invoke And Cancel RAMQueue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.InvokeAndCancelActivity('RAMQueue')

  def test_09_CallOnceWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nCall Once With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CallOnceWithActivity('SQLDict')

  def test_10_CallOnceWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nCall Once With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CallOnceWithActivity('SQLQueue')

  def test_11_CallOnceWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nCall Once With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CallOnceWithActivity('RAMDict')

  def test_12_CallOnceWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nCall Once With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CallOnceWithActivity('RAMQueue')









if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCMFActivity))
        return suite

