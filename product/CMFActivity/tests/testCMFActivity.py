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
  company_id2 = 'Coramy'

  def getTitle(self):
    return "CMFActivity"

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
    return ()

  def getCategoriesTool(self):
    return getattr(self.getPortal(), 'portal_categories', None)

  def getRuleTool(self):
    return getattr(self.getPortal(), 'portal_Rules', None)

  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

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
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def InvokeAndCancelActivity(self, activity):
    """
    Simple test where we invoke and cancel an activity
    """
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
    """
    We check that the title is changed only after that
    the activity was called
    """
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
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(len(message_list),0)

  def CallOnceWithActivity(self, activity):
    """
    With this test we can check if methods are called
    only once (sometimes it was twice !!!)
    """
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

  def TryFlushActivity(self, activity):
    """
    Check the method flush
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(self.title1)
    organisation.activate(activity=activity).setTitle(self.title2)
    organisation.flushActivity(invoke=1)
    self.assertEquals(organisation.getTitle(),self.title2)
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title2)
    # Try again with different commit order
    organisation.setTitle(self.title1)
    organisation.activate(activity=activity).setTitle(self.title2)
    get_transaction().commit()
    organisation.flushActivity(invoke=1)
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title2)
    get_transaction().commit()

  def TryActivateInsideFlush(self, activity):
    """
    Create a new activity inside a flush action
    """
    portal = self.getPortal()
    def DeferredSetTitle(self,value):
      self.activate(activity=activity).setTitle(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(self.title1)
    organisation.activate(activity=activity).DeferredSetTitle(self.title2)
    organisation.flushActivity(invoke=1)
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title2)

  def TryTwoMethods(self, activity):
    """
    Try several activities
    """
    portal = self.getPortal()
    def DeferredSetDescription(self,value):
      self.setDescription(value)
    def DeferredSetTitle(self,value):
      self.setTitle(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(None)
    organisation.setDescription(None)
    organisation.activate(activity=activity).DeferredSetTitle(self.title1)
    organisation.activate(activity=activity).DeferredSetDescription(self.title1)
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title1)
    self.assertEquals(organisation.getDescription(),self.title1)

  def TryTwoMethodsAndFlushThem(self, activity):
    """
    make sure flush works with several activities
    """
    portal = self.getPortal()
    def DeferredSetTitle(self,value):
      self.activate(activity=activity).setTitle(value)
    def DeferredSetDescription(self,value):
      self.activate(activity=activity).setDescription(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(None)
    organisation.setDescription(None)
    organisation.activate(activity=activity).DeferredSetTitle(self.title1)
    organisation.activate(activity=activity).DeferredSetDescription(self.title1)
    organisation.flushActivity(invoke=1)
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title1)
    self.assertEquals(organisation.getDescription(),self.title1)

  def TryActivateFlushActivateTic(self, activity,second=None,commit_sub=0):
    """
    try to commit sub transactions
    """
    portal = self.getPortal()
    def DeferredSetTitle(self,value,commit_sub=0):
      if commit_sub:
        get_transaction().commit(1)
      self.activate(activity=second or activity,priority=4).setTitle(value)
    def DeferredSetDescription(self,value,commit_sub=0):
      if commit_sub:
        get_transaction().commit(1)
      self.activate(activity=second or activity,priority=4).setDescription(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(None)
    organisation.setDescription(None)
    organisation.activate(activity=activity).DeferredSetTitle(self.title1,commit_sub=commit_sub)
    organisation.flushActivity(invoke=1)
    organisation.activate(activity=activity).DeferredSetDescription(self.title1,commit_sub=commit_sub)
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title1)
    self.assertEquals(organisation.getDescription(),self.title1)

  def TryMessageWithErrorOnActivity(self, activity):
    """
    Make sure that message with errors are not deleted
    """
    portal = self.getPortal()
    def crashThisActivity(self):
      self.IWillCrach()
    from Products.ERP5Type.Document.Organisation import Organisation
    organisation =  portal.organisation._getOb(self.company_id)
    Organisation.crashThisActivity = crashThisActivity
    organisation.activate(activity=activity).crashThisActivity()
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    # XXX HERE WE SHOULD USE TIME SHIFT IN ORDER TO SIMULATE MULTIPLE TICS
    # Test if there is still the message after it crashed
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageCancel(organisation.getPhysicalPath(),'crashThisActivity')
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)

  def DeferedSetTitleWithRenamedObject(self, activity):
    """
    make sure that an activity is flushed before we rename
    the object
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(self.title1)
    self.assertEquals(self.title1,organisation.getTitle())
    organisation.activate(activity=activity).setTitle(self.title2)
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    self.assertEquals(self.title1,organisation.getTitle())
    organisation.edit(id=self.company_id2)
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(self.title2,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    organisation.edit(id=self.company_id)
    get_transaction().commit()

  def TryActiveProcess(self, activity):
    """
    Try to store the result inside an active process
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(self.title1)
    active_process = portal.portal_activities.newActiveProcess()
    self.assertEquals(self.title1,organisation.getTitle())
    organisation.activate(activity=activity,active_process=active_process).getTitle()
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(self.title1,organisation.getTitle())
    result = active_process.getResultList()[0]
    self.assertEquals(result.method_id , 'getTitle')
    self.assertEquals(result.result , self.title1)
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)

  def TryActiveProcessInsideActivity(self, activity):
    """
    Try two levels with active_process, we create one first
    activity with an acitive process, then this new activity
    uses another active process
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation.setTitle(self.title1)
    def Organisation_test(self):
      active_process = self.portal_activities.newActiveProcess()
      self.activate(active_process=active_process).getTitle()
      return active_process
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.Organisation_test = Organisation_test
    active_process = portal.portal_activities.newActiveProcess()
    organisation.activate(activity=activity,active_process=active_process).Organisation_test()
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    sub_active_process = active_process.getResultList()[0].result
    LOG('TryActiveProcessInsideActivity, sub_active_process',0,sub_active_process)
    result = sub_active_process.getResultList()[0]
    self.assertEquals(result.method_id , 'getTitle')
    self.assertEquals(result.result , self.title1)
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)

  def TryMethodAfterMethod(self, activity):
    """
    Try several activities
    """
    portal = self.getPortal()
    def DeferredSetDescription(self,value):
      self.setDescription(value)
    def DeferredSetTitle(self,value):
      self.setTitle(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    default_title = 'my_test_title'
    organisation.setTitle(default_title)
    organisation.setDescription(None)
    organisation.activate(activity=activity,after_method_id='DeferredSetDescription').DeferredSetTitle(self.title1)
    organisation.activate(activity=activity).DeferredSetDescription(self.title1)
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    self.assertEquals(organisation.getTitle(), default_title) # Title should not be changed the first time
    self.assertEquals(organisation.getDescription(),self.title1)
    # Test again without waiting
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    self.assertEquals(organisation.getTitle(), default_title) # Title should not be changed the first time
    self.assertEquals(organisation.getDescription(),self.title1)    
    # Now wait some time and test again (this should be simulated by changing dates in SQL Queue)
    from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
    portal.portal_activities.timeShift(2 * VALIDATION_ERROR_DELAY)
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title1)
    self.assertEquals(organisation.getDescription(),self.title1)
 
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

  def test_13_TryMessageWithErrorOnSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Message With Error On SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryMessageWithErrorOnActivity('SQLDict')

  def test_14_TryMessageWithErrorOnSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Message With Error On SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryMessageWithErrorOnActivity('SQLQueue')

  def test_15_TryMessageWithErrorOnRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Message With Error On RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryMessageWithErrorOnActivity('RAMDict')

  def test_16_TryMessageWithErrorOnRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Message With Error On RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryMessageWithErrorOnActivity('RAMQueue')

  def test_17_TryFlushActivityWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Flush Activity With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryFlushActivity('SQLDict')

  def test_18_TryFlushActivityWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Flush Activity With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryFlushActivity('SQLQueue')

  def test_19_TryFlushActivityWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Flush Activity With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryFlushActivity('RAMDict')

  def test_20_TryFlushActivityWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Flush Activity With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryFlushActivity('RAMQueue')

  def test_21_TryActivateInsideFlushWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Inside Flush With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateInsideFlush('SQLDict')

  def test_22_TryActivateInsideFlushWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Inside Flush With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateInsideFlush('SQLQueue')

  def test_23_TryActivateInsideFlushWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Inside Flush With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateInsideFlush('RAMDict')

  def test_24_TryActivateInsideFlushWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Inside Flush With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateInsideFlush('RAMQueue')

  def test_25_TryTwoMethodsWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Two Methods With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryTwoMethods('SQLDict')

  def test_26_TryTwoMethodsWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Two Methods With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryTwoMethods('SQLQueue')

  def test_27_TryTwoMethodsWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Two Methods With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryTwoMethods('RAMDict')

  def test_28_TryTwoMethodsWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Two Methods With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryTwoMethods('RAMQueue')

  def test_29_TryTwoMethodsAndFlushThemWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Two Methods And Flush Them With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryTwoMethodsAndFlushThem('SQLDict')

  def test_30_TryTwoMethodsAndFlushThemWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Two Methods And Flush Them With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryTwoMethodsAndFlushThem('SQLQueue')

  def test_31_TryTwoMethodsAndFlushThemWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Two Methods And Flush Them With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryTwoMethodsAndFlushThem('RAMDict')

  def test_32_TryTwoMethodsAndFlushThemWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Two Methods And Flush Them With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryTwoMethodsAndFlushThem('RAMQueue')

  def test_33_TryActivateFlushActivateTicWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Flush Activate Tic With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('SQLDict')

  def test_34_TryActivateFlushActivateTicWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Flush Activate Tic With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('SQLQueue')

  def test_35_TryActivateFlushActivateTicWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Flush Activate Tic With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('RAMDict')

  def test_36_TryActivateFlushActivateTicWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Flush Activate Tic With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('RAMQueue')

  def test_37_TryActivateFlushActivateTicWithMultipleActivities(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Activate Flush Activate Tic With MultipleActivities '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('SQLQueue',second='SQLDict')
    self.TryActivateFlushActivateTic('SQLDict',second='SQLQueue')

  def test_38_TryCommitSubTransactionWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Commit Sub Transaction With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('SQLDict',commit_sub=1)

  def test_39_TryCommitSubTransactionWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Commit Sub Transaction With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('SQLQueue',commit_sub=1)

  def test_40_TryCommitSubTransactionWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Commit Sub Transaction With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('RAMDict',commit_sub=1)

  def test_41_TryCommitSubTransactionWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Commit Sub Transaction With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivateFlushActivateTic('RAMQueue',commit_sub=1)

  def test_42_TryRenameObjectWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Rename Object With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferedSetTitleWithRenamedObject('SQLDict')

  def test_43_TryRenameObjectWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Rename Object With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferedSetTitleWithRenamedObject('SQLQueue')

  def test_44_TryRenameObjectWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Rename Object With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferedSetTitleWithRenamedObject('RAMDict')

  def test_45_TryRenameObjectWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Rename Object With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferedSetTitleWithRenamedObject('RAMQueue')

  def test_46_TryActiveProcessWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Active Process With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActiveProcess('SQLDict')

  def test_47_TryActiveProcessWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Active Process With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActiveProcess('SQLQueue')

  def test_48_TryActiveProcessWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Active Process With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActiveProcess('RAMDict')

  def test_49_TryActiveProcessWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Active Process With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActiveProcess('RAMQueue')

  def test_50_TryActiveProcessInsideActivityWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Active Process Inside Activity With SQL Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActiveProcessInsideActivity('SQLDict')

  def test_51_TryActiveProcessInsideActivityWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Active Process Inside Activity With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActiveProcessInsideActivity('SQLQueue')

  def test_52_TryActiveProcessInsideActivityWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Active Process Inside Activity With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActiveProcessInsideActivity('RAMDict')

  def test_53_TryActiveProcessInsideActivityWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Active Process Inside Activity With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActiveProcessInsideActivity('RAMQueue')

  def test_54_TryAfterMethodIdWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if after_method_id can be used
    if not run: return
    if not quiet:
      message = '\nTry Active Method After Another Activate Method With SQLDict'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryMethodAfterMethod('SQLDict')
    
  def test_55_TryAfterMethodIdWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if after_method_id can be used
    if not run: return
    if not quiet:
      message = '\nTry Active Method After Another Activate Method With SQLQueue'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryMethodAfterMethod('SQLQueue')
    
  def test_56_TryCallActivityWithRightUser(self, quiet=0, run=run_all_test):
    # Test if me execute methods with the right user
    # This should be independant of the activity used
    if not run: return
    if not quiet:
      message = '\nTry Call Activity With Right User'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    # We are first logged as seb
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    # Add new user toto
    uf = self.getPortal().acl_users
    uf._doAddUser('toto', '', ['Manager'], [])
    user = uf.getUserById('toto').__of__(uf)
    newSecurityManager(None, user)
    # Execute something as toto
    organisation.activate().newContent(portal_type='Email',id='email')
    # Then execute activities as seb
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    email = organisation.get('email')
    # Check if what we did was executed as toto
    self.assertEquals(email.getOwnerInfo()['id'],'toto')


    

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCMFActivity))
        return suite

