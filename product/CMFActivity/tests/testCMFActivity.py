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


import unittest

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.CMFActivity.ActiveObject import INVOKE_ERROR_STATE,\
                                              VALIDATE_ERROR_STATE
from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
from Products.CMFActivity.Errors import ActivityPendingError, ActivityFlushError
from Products.ERP5Type.Document.Organisation import Organisation
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from ZODB.POSException import ConflictError

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestCMFActivity(ERP5TypeTestCase):

  run_all_test = 1
  # Different variables used for this test
  company_id = 'Nexedi'
  title1 = 'title1'
  title2 = 'title2'
  company_id2 = 'Coramy'
  company_id3 = 'toto'

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
    return ('erp5_base',)

  def getCategoriesTool(self):
    return getattr(self.getPortal(), 'portal_categories', None)

  def getRuleTool(self):
    return getattr(self.getPortal(), 'portal_Rules', None)

  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    # remove all message in the message_table because
    # the previous test might have failed
    message_list = portal.portal_activities.getMessageList()
    for message in message_list:
      portal.portal_activities.manageCancel(message.object_path,message.method_id)

    # Then add new components
    if not(hasattr(portal,'organisation')):
      portal.portal_types.constructContent(type_name='Organisation Module',
                                         container=portal,
                                         id='organisation')
    organisation_module = self.getOrganisationModule()
    if not(organisation_module.hasContent(self.company_id)):
      o1 = organisation_module.newContent(id=self.company_id)
    get_transaction().commit()
    self.tic()


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
    organisation._setTitle(self.title1)
    self.assertEquals(self.title1,organisation.getTitle())
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageCancel(organisation.getPhysicalPath(),'_setTitle')
    # Needed so that the message are removed from the queue
    get_transaction().commit()
    self.assertEquals(self.title1,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageInvoke(organisation.getPhysicalPath(),'_setTitle')
    # Needed so that the message are removed from the queue
    get_transaction().commit()
    self.assertEquals(self.title2,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)

  def DeferredSetTitleActivity(self, activity):
    """
    We check that the title is changed only after that
    the activity was called
    """
    portal = self.getPortal()
    organisation = portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
    self.assertEquals(self.title1,organisation.getTitle())
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    self.assertEquals(self.title1,organisation.getTitle())
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(self.title2,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
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
    organisation =  portal.organisation._getOb(self.company_id)
    Organisation.setFoobar = setFoobar
    Organisation.getFoobar = getFoobar
    organisation.foobar = 0
    organisation._setTitle(self.title1)
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
    organisation._setTitle(self.title1)
    organisation.activate(activity=activity)._setTitle(self.title2)
    organisation.flushActivity(invoke=1)
    self.assertEquals(organisation.getTitle(),self.title2)
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title2)
    # Try again with different commit order
    organisation._setTitle(self.title1)
    organisation.activate(activity=activity)._setTitle(self.title2)
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
      self.activate(activity=activity)._setTitle(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
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
      self._setTitle(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(None)
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
      self.activate(activity=activity)._setTitle(value)
    def DeferredSetDescription(self,value):
      self.activate(activity=activity).setDescription(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(None)
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
      self.activate(activity=second or activity,priority=4)._setTitle(value)
    def DeferredSetDescription(self,value,commit_sub=0):
      if commit_sub:
        get_transaction().commit(1)
      self.activate(activity=second or activity,priority=4).setDescription(value)
    from Products.ERP5Type.Document.Organisation import Organisation
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(None)
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
    LOG('Before MessageWithErrorOnActivityFails, message_list',0,[x.__dict__ for x in message_list])
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

  def DeferredSetTitleWithRenamedObject(self, activity):
    """
    make sure that it is impossible to rename an object
    if some activities are still waiting for this object
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
    self.assertEquals(self.title1,organisation.getTitle())
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    get_transaction().commit()
    self.assertEquals(self.title1,organisation.getTitle())
    self.assertRaises(ActivityPendingError,organisation.edit,id=self.company_id2)
    portal.portal_activities.distribute()
    portal.portal_activities.tic()

  def TryActiveProcess(self, activity):
    """
    Try to store the result inside an active process
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
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
    organisation._setTitle(self.title1)
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
      Ensure the order of an execution by a method id
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = portal.organisation._getOb(self.company_id)

    o.setTitle('a')
    self.assertEquals(o.getTitle(), 'a')
    get_transaction().commit()
    self.tic()

    def toto(self, value):
      self.setTitle(self.getTitle() + value)
    o.__class__.toto = toto

    def titi(self, value):
      self.setTitle(self.getTitle() + value)
    o.__class__.titi = titi

    o.activate(after_method_id = 'titi', activity = activity).toto('b')
    o.activate(activity = activity).titi('c')
    get_transaction().commit()
    self.tic()
    self.assertEquals(o.getTitle(), 'acb')

  def ExpandedMethodWithDeletedSubObject(self, activity):
    """
    Do recursiveReindexObject, then delete a
    subobject an see if there is only one activity
    in the queue
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not(organisation_module.hasContent(self.company_id2)):
      o2 = organisation_module.newContent(id=self.company_id2)
    o1 =  portal.organisation._getOb(self.company_id)
    o2 =  portal.organisation._getOb(self.company_id2)
    for o in (o1,o2):
      if not(o.hasContent('1')):
        o.newContent(portal_type='Email',id='1')
      if not(o.hasContent('2')):
        o.newContent(portal_type='Email',id='2')
    o1.recursiveReindexObject()
    o2.recursiveReindexObject()
    o1._delOb('2')
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)

  def ExpandedMethodWithDeletedObject(self, activity):
    """
    Do recursiveReindexObject, then delete a
    subobject an see if there is only one activity
    in the queue
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not(organisation_module.hasContent(self.company_id2)):
      o2 = organisation_module.newContent(id=self.company_id2)
    o1 =  portal.organisation._getOb(self.company_id)
    o2 =  portal.organisation._getOb(self.company_id2)
    for o in (o1,o2):
      if not(o.hasContent('1')):
        o.newContent(portal_type='Email',id='1')
      if not(o.hasContent('2')):
        o.newContent(portal_type='Email',id='2')
    o1.recursiveReindexObject()
    o2.recursiveReindexObject()
    organisation_module._delOb(self.company_id2)
    get_transaction().commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)

  def TryAfterTag(self, activity):
    """
      Ensure the order of an execution by a tag
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = portal.organisation._getOb(self.company_id)

    o.setTitle('?')
    self.assertEquals(o.getTitle(), '?')
    get_transaction().commit()
    self.tic()

    o.activate(after_tag = 'toto', activity = activity).setTitle('b')
    o.activate(tag = 'toto', activity = activity).setTitle('a')
    get_transaction().commit()
    self.tic()
    self.assertEquals(o.getTitle(), 'b')

    o.setDefaultActivateParameters(tag = 'toto')
    def titi(self):
      self.setCorporateName(self.getTitle() + 'd')
    o.__class__.titi = titi
    o.activate(after_tag_and_method_id=('toto', 'setTitle'), activity = activity).titi()
    o.activate(activity = activity).setTitle('c')
    get_transaction().commit()
    self.tic()
    self.assertEquals(o.getCorporateName(), 'cd')

  def TryFlushActivityWithAfterTag(self, activity):
    """
      Ensure the order of an execution by a tag
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = portal.organisation._getOb(self.company_id)

    o.setTitle('?')
    o.setDescription('?')
    self.assertEquals(o.getTitle(), '?')
    self.assertEquals(o.getDescription(), '?')
    get_transaction().commit()
    self.tic()

    o.activate(after_tag = 'toto', activity = activity).setDescription('b')
    o.activate(tag = 'toto', activity = activity).setTitle('a')
    get_transaction().commit()
    tool = self.getActivityTool()
    self.assertRaises(ActivityFlushError,tool.manageInvoke,o.getPath(),'setDescription')
    tool.manageInvoke(o.getPath(),'setTitle')
    get_transaction().commit()
    self.assertEquals(o.getTitle(), 'a')
    self.assertEquals(o.getDescription(), '?')
    self.tic()
    self.assertEquals(len(tool.getMessageList()),0)
    self.assertEquals(o.getTitle(), 'a')
    self.assertEquals(o.getDescription(), 'b')

  def CheckScheduling(self, activity):
    """
      Check if active objects with different after parameters are executed in a correct order
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = portal.organisation._getOb(self.company_id)

    o.setTitle('?')
    self.assertEquals(o.getTitle(), '?')
    get_transaction().commit()
    self.tic()

    def toto(self, s):
      self.setTitle(self.getTitle() + s)
    o.__class__.toto = toto

    o.activate(tag = 'toto', activity = activity).toto('a')
    get_transaction().commit()
    o.activate(after_tag = 'titi', activity = activity).toto('b')
    get_transaction().commit()
    o.activate(tag = 'titi', after_tag = 'toto', activity = activity).setTitle('c')
    get_transaction().commit()
    self.tic()
    self.assertEquals(o.getTitle(), 'cb')

  def CheckClearActivities(self, activity):
    """
      Check if active objects are held even after clearing the tables.
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    get_transaction().commit()
    self.tic()

    def check(o):
      message_list = portal.portal_activities.getMessageList()
      self.assertEquals(len(message_list), 1)
      m = message_list[0]
      self.assertEquals(m.object_path, o.getPhysicalPath())
      self.assertEquals(m.method_id, '_setTitle')

    o = portal.organisation._getOb(self.company_id)
    o.activate(activity=activity)._setTitle('foo')
    get_transaction().commit()
    check(o)

    portal.portal_activities.manageClearActivities()
    get_transaction().commit()
    check(o)

    get_transaction().commit()
    self.tic()

    self.assertEquals(o.getTitle(), 'foo')

  def CheckCountMessageWithTag(self, activity):
    """
      Check countMessageWithTag function.
    """
    portal = self.getPortal()
    portal_activities = portal.portal_activities
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = portal.organisation._getOb(self.company_id)
    o.setTitle('?')
    get_transaction().commit()
    self.tic()

    o.activate(tag = 'toto', activity = activity).setTitle('a')
    get_transaction().commit()
    self.assertEquals(o.getTitle(), '?')
    self.assertEquals(portal_activities.countMessageWithTag('toto'), 1)
    self.tic()
    self.assertEquals(o.getTitle(), 'a')
    self.assertEquals(portal_activities.countMessageWithTag('toto'), 0)

  def TryConflictErrorsWhileProcessing(self, activity):
    """Try to execute active objects which may throw conflict errors
    while processing, and check if they are still executed."""
    # Make sure that no active object is installed.
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities(keep=0)

    # Need an object.
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = organisation_module._getOb(self.company_id)
    get_transaction().commit()
    self.flushAllActivities(silent = 1, loop_size = 10)
    self.assertEquals(len(activity_tool.getMessageList()), 0)

    # Monkey patch Organisation to induce conflict errors artificially.
    def induceConflictErrors(self, limit):
      if self.__class__.current_num_conflict_errors < limit:
        self.__class__.current_num_conflict_errors += 1
        raise ConflictError
    Organisation.induceConflictErrors = induceConflictErrors

    # Test some range of conflict error occurences.
    for i in xrange(10):
      Organisation.current_num_conflict_errors = 0
      o.activate(activity = activity).induceConflictErrors(i)
      get_transaction().commit()
      self.flushAllActivities(silent = 1, loop_size = i + 10)
      self.assertEquals(len(activity_tool.getMessageList()), 0)

  def TryConflictErrorsWhileValidating(self, activity):
    """Try to execute active objects which may throw conflict errors
    while validating, and check if they are still executed."""
    # Make sure that no active object is installed.
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities(keep=0)

    # Need an object.
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = organisation_module._getOb(self.company_id)
    get_transaction().commit()
    self.flushAllActivities(silent = 1, loop_size = 10)
    self.assertEquals(len(activity_tool.getMessageList()), 0)

    # Monkey patch Queue to induce conflict errors artificially.
    def validate(self, *args, **kwargs):
      from Products.CMFActivity.Activity.Queue import Queue
      if Queue.current_num_conflict_errors < Queue.conflict_errors_limit:
        Queue.current_num_conflict_errors += 1
        # LOG('TryConflictErrorsWhileValidating', 0, 'causing a conflict error artificially')
        raise ConflictError
      return self.original_validate(*args, **kwargs)
    from Products.CMFActivity.Activity.Queue import Queue
    Queue.original_validate = Queue.validate
    Queue.validate = validate

    try:
      # Test some range of conflict error occurences.
      for i in xrange(10):
        Queue.current_num_conflict_errors = 0
        Queue.conflict_errors_limit = i
        o.activate(activity = activity).getId()
        get_transaction().commit()
        self.flushAllActivities(silent = 1, loop_size = i + 10)
        self.assertEquals(len(activity_tool.getMessageList()), 0)
    finally:
      Queue.validate = Queue.original_validate
      del Queue.original_validate
      del Queue.current_num_conflict_errors
      del Queue.conflict_errors_limit

  def TryErrorsWhileFinishingCommitDB(self, activity):
    """Try to execute active objects which may throw conflict errors
    while validating, and check if they are still executed."""
    # Make sure that no active object is installed.
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities(keep=0)

    # Need an object.
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = organisation_module._getOb(self.company_id)
    get_transaction().commit()
    self.flushAllActivities(silent = 1, loop_size = 10)
    self.assertEquals(len(activity_tool.getMessageList()), 0)

    from _mysql_exceptions import OperationalError

    # Monkey patch Queue to induce conflict errors artificially.
    def query(self, query_string,*args, **kw):
      # No so nice, this is specific to zsql method
      if query_string.find("REPLACE INTO")>=0:
        raise OperationalError
      else:
        return self.original_query(query_string,*args, **kw)
    from Products.ZMySQLDA.db import DB
    portal = self.getPortal()

    try:
      # Test some range of conflict error occurences.
      organisation_module.recursiveReindexObject()
      get_transaction().commit()
      self.assertEquals(len(activity_tool.getMessageList()), 1)
      DB.original_query = DB.query
      DB.query = query
      portal.portal_activities.distribute()
      portal.portal_activities.tic()
      get_transaction().commit()
      DB.query = DB.original_query
      message_list = portal.portal_activities.getMessageList()
      self.assertEquals(len(message_list),1)
    finally:
      DB.query = DB.original_query
      del DB.original_query

  def checkIsMessageRegisteredMethod(self, activity):
    activity_tool = self.getPortal().portal_activities
    object_a = self.getOrganisationModule()
    if not object_a.hasContent(self.company_id):
      object_a.newContent(id=self.company_id)
    object_b = object_a._getOb(self.company_id)
    activity_tool.manageClearActivities(keep=0)
    get_transaction().commit()
    # First case: creating the same activity twice must only register one.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_a.activate(activity=activity).getId()
    get_transaction().commit()
    self.assertEquals(len(activity_tool.getMessageList()), 1)
    activity_tool.manageClearActivities(keep=0)
    get_transaction().commit()
    # Second case: creating activity with same tag must only register one.
    # This behaviour is actually the same as the no-tag behaviour.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity, tag='foo').getId()
    object_a.activate(activity=activity, tag='foo').getId()
    get_transaction().commit()
    self.assertEquals(len(activity_tool.getMessageList()), 1)
    activity_tool.manageClearActivities(keep=0)
    get_transaction().commit()
    # Third case: creating activities with different tags must register both.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity, tag='foo').getId()
    object_a.activate(activity=activity, tag='bar').getId()
    get_transaction().commit()
    self.assertEquals(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities(keep=0)
    get_transaction().commit()
    # Fourth case: creating activities on different objects must register
    # both.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_b.activate(activity=activity).getId()
    get_transaction().commit()
    self.assertEquals(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities(keep=0)
    get_transaction().commit()
    # Fifth case: creating activities with different method must register
    # both.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_a.activate(activity=activity).getTitle()
    get_transaction().commit()
    self.assertEquals(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities(keep=0)
    get_transaction().commit()

  def test_01_DeferredSetTitleSQLDict(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Deferred Set Title SQLDict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferredSetTitleActivity('SQLDict')

  def test_02_DeferredSetTitleSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Deferred Set Title SQLQueue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferredSetTitleActivity('SQLQueue')

  def test_03_DeferredSetTitleRAMDict(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Deferred Set Title RAMDict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferredSetTitleActivity('RAMDict')

  def test_04_DeferredSetTitleRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      message = '\nTest Deferred Set Title RAMQueue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferredSetTitleActivity('RAMQueue')

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
    self.DeferredSetTitleWithRenamedObject('SQLDict')

  def test_43_TryRenameObjectWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Rename Object With SQL Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferredSetTitleWithRenamedObject('SQLQueue')

  def test_44_TryRenameObjectWithRAMDict(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Rename Object With RAM Dict '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferredSetTitleWithRenamedObject('RAMDict')

  def test_45_TryRenameObjectWithRAMQueue(self, quiet=0, run=run_all_test):
    # Test if we call methods only once
    if not run: return
    if not quiet:
      message = '\nTry Rename Object With RAM Queue '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.DeferredSetTitleWithRenamedObject('RAMQueue')

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

  def test_57_ExpandedMethodWithDeletedSubObject(self, quiet=0, run=run_all_test):
    # Test if after_method_id can be used
    if not run: return
    if not quiet:
      message = '\nTry Expanded Method With Deleted Sub Object'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.ExpandedMethodWithDeletedSubObject('SQLDict')

  def test_58_ExpandedMethodWithDeletedObject(self, quiet=0, run=run_all_test):
    # Test if after_method_id can be used
    if not run: return
    if not quiet:
      message = '\nTry Expanded Method With Deleted Object'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.ExpandedMethodWithDeletedObject('SQLDict')

  def test_59_TryAfterTagWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if after_tag can be used
    if not run: return
    if not quiet:
      message = '\nTry After Tag With SQL Dict'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryAfterTag('SQLDict')

  def test_60_TryAfterTagWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if after_tag can be used
    if not run: return
    if not quiet:
      message = '\nTry After Tag With SQL Queue'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryAfterTag('SQLQueue')

  def test_61_CheckSchedulingWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if scheduling is correct with SQLDict
    if not run: return
    if not quiet:
      message = '\nCheck Scheduling With SQL Dict'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckScheduling('SQLDict')

  def test_62_CheckSchedulingWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if scheduling is correct with SQLQueue
    if not run: return
    if not quiet:
      message = '\nCheck Scheduling With SQL Queue'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckScheduling('SQLQueue')

  def test_63_CheckClearActivitiesWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if clearing tables does not remove active objects with SQLDict
    if not run: return
    if not quiet:
      message = '\nCheck Clearing Activities With SQL Dict'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckClearActivities('SQLDict')

  def test_64_CheckClearActivitiesWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if clearing tables does not remove active objects with SQLQueue
    if not run: return
    if not quiet:
      message = '\nCheck Clearing Activities With SQL Queue'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckClearActivities('SQLQueue')

  def flushAllActivities(self, silent=0, loop_size=1000):
    """Executes all messages until the queue only contains failed
    messages.
    """
    activity_tool = self.getPortal().portal_activities
    loop_count=0
    # flush activities
    while 1:
      loop_count += 1
      if loop_count >= loop_size:
        if silent:
          return
        self.fail('flushAllActivities maximum loop count reached')

      activity_tool.distribute(node_count=1)
      activity_tool.tic(processing_node=1)

      finished = 1
      for message in activity_tool.getMessageList():
        if message.processing_node not in (INVOKE_ERROR_STATE,
                                           VALIDATE_ERROR_STATE):
          finished = 0

      activity_tool.timeShift(3 * VALIDATION_ERROR_DELAY)
      get_transaction().commit()
      if finished:
        return

  def test_65_TestMessageValidationAndFailedActivities(self,
                                              quiet=0, run=run_all_test):
    """after_method_id and failed activities.

    Tests that if we have an active method scheduled by
    after_method_id and a failed activity with this method id, the
    method is NOT executed.

    Note: earlier version of this test checked exactly the contrary, but it
    was eventually agreed that this was a bug. If an activity fails, all the
    activities that depend on it should be block until the first one is
    resolved."""
    if not run: return
    if not quiet:
      message = '\nafter_method_id and failed activities'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    activity_tool = self.getPortal().portal_activities
    original_title = 'something'
    obj = self.getPortal().organisation_module.newContent(
                    portal_type='Organisation',
                    title=original_title)

    # Monkey patch Organisation to add a failing method
    def failingMethod(self):
      raise ValueError, 'This method always fail'
    Organisation.failingMethod = failingMethod

    # Monkey patch Message not to send failure notification emails
    from Products.CMFActivity.ActivityTool import Message
    originalNotifyUser = Message.notifyUser
    def notifyUserSilent(self, activity_tool, message=''):
      pass
    Message.notifyUser = notifyUserSilent

    activity_list = ['SQLQueue', 'SQLDict', ]
    for activity in activity_list:
      # reset
      activity_tool.manageClearActivities(keep=0)
      obj.setTitle(original_title)
      get_transaction().commit()

      # activate failing message and flush
      for fail_activity in activity_list:
        obj.activate(activity = fail_activity).failingMethod()
      get_transaction().commit()
      self.flushAllActivities(silent=1, loop_size=100)
      full_message_list = activity_tool.getMessageList()
      remaining_messages = [a for a in full_message_list if a.method_id !=
          'failingMethod']
      if len(full_message_list) != 2:
        self.fail('failingMethod should not have been flushed')
      if len(remaining_messages) != 0:
        self.fail('Activity tool should have no other remaining messages')

      # activate our message
      new_title = 'nothing'
      obj.activate(after_method_id = ['failingMethod'],
                   activity = activity ).setTitle(new_title)
      get_transaction().commit()
      self.flushAllActivities(silent=1, loop_size=100)
      full_message_list = activity_tool.getMessageList()
      remaining_messages = [a for a in full_message_list if a.method_id !=
          'failingMethod']
      if len(full_message_list) != 3:
        self.fail('failingMethod should not have been flushed')
      if len(remaining_messages) != 1:
        self.fail('Activity tool should have one blocked setTitle activity')
      self.assertEquals(remaining_messages[0].activity_kw['after_method_id'],
          ['failingMethod'])
      self.assertEquals(obj.getTitle(), original_title)

    # restore notification and flush failed and blocked activities
    Message.notifyUser = originalNotifyUser
    activity_tool.manageClearActivities(keep=0)

  def test_66_TestCountMessageWithTagWithSQLDict(self, quiet=0, run=run_all_test):
    """
      Test new countMessageWithTag function with SQLDict.
    """
    if not run: return
    if not quiet:
      message = '\nCheck countMessageWithTag'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    self.CheckCountMessageWithTag('SQLDict')

  def test_67_TestCancelFailedActiveObject(self, quiet=0, run=run_all_test):
    """Cancel an active object to make sure that it does not refer to
    a persistent object."""
    if not run: return
    if not quiet:
      message = '\nTest if it is possible to safely cancel an active object'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities(keep=0)

    original_title = 'something'
    obj = self.getPortal().organisation_module.newContent(
                    portal_type='Organisation',
                    title=original_title)

    # Monkey patch Organisation to add a failing method
    def failingMethod(self):
      raise ValueError, 'This method always fail'
    Organisation.failingMethod = failingMethod

    # Monkey patch Message not to send failure notification emails
    from Products.CMFActivity.ActivityTool import Message
    originalNotifyUser = Message.notifyUser
    def notifyUserSilent(self, activity_tool, message=''):
      pass
    Message.notifyUser = notifyUserSilent

    # First, index the object.
    get_transaction().commit()
    self.flushAllActivities(silent=1, loop_size=100)
    self.assertEquals(len(activity_tool.getMessageList()), 0)

    # Insert a failing active object.
    obj.activate().failingMethod()
    get_transaction().commit()
    self.assertEquals(len(activity_tool.getMessageList()), 1)

    # Just wait for the active object to be abandoned.
    self.flushAllActivities(silent=1, loop_size=10)
    self.assertEquals(len(activity_tool.getMessageList()), 1)
    self.assertEquals(activity_tool.getMessageList()[0].processing_node, 
                      INVOKE_ERROR_STATE)

    # Make sure that persistent objects are not present in the connection
    # cache to emulate a restart of Zope. So all volatile attributes will
    # be flushed, and persistent objects will be reloaded.
    activity_tool._p_jar._resetCache()

    # Cancel it via the management interface.
    message = activity_tool.getMessageList()[0]
    activity_tool.manageCancel(message.object_path, message.method_id)
    get_transaction().commit()
    self.assertEquals(len(activity_tool.getMessageList()), 0)

  def test_68_TestConflictErrorsWhileProcessingWithSQLDict(self, quiet=0, run=run_all_test):
    """
      Test if conflict errors spoil out active objects with SQLDict.
    """
    if not run: return
    if not quiet:
      message = '\nTest Conflict Errors While Processing With SQLDict'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    self.TryConflictErrorsWhileProcessing('SQLDict')

  def test_69_TestConflictErrorsWhileProcessingWithSQLQueue(self, quiet=0, run=run_all_test):
    """
      Test if conflict errors spoil out active objects with SQLQueue.
    """
    if not run: return
    if not quiet:
      message = '\nTest Conflict Errors While Processing With SQLQueue'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    self.TryConflictErrorsWhileProcessing('SQLQueue')

  def test_70_TestConflictErrorsWhileValidatingWithSQLDict(self, quiet=0, run=run_all_test):
    """
      Test if conflict errors spoil out active objects with SQLDict.
    """
    if not run: return
    if not quiet:
      message = '\nTest Conflict Errors While Validating With SQLDict'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    self.TryConflictErrorsWhileValidating('SQLDict')

  def test_71_TestConflictErrorsWhileValidatingWithSQLQueue(self, quiet=0, run=run_all_test):
    """
      Test if conflict errors spoil out active objects with SQLQueue.
    """
    if not run: return
    if not quiet:
      message = '\nTest Conflict Errors While Validating With SQLQueue'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    self.TryConflictErrorsWhileValidating('SQLQueue')

  def test_72_TestErrorsWhileFinishingCommitDBWithSQLDict(self, quiet=0, run=run_all_test):
    """
    """
    if not run: return
    if not quiet:
      message = '\nTest Errors While Finishing Commit DB With SQLDict'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    self.TryErrorsWhileFinishingCommitDB('SQLDict')

  def test_73_TestErrorsWhileFinishingCommitDBWithSQLQueue(self, quiet=0, run=run_all_test):
    """
    """
    if not run: return
    if not quiet:
      message = '\nTest Errors While Finishing Commit DB With SQLQueue'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    self.TryErrorsWhileFinishingCommitDB('SQLQueue')

  def test_74_TryFlushActivityWithAfterTagSQLDict(self, quiet=0, run=run_all_test):
    # Test if after_tag can be used
    if not run: return
    if not quiet:
      message = '\nTry Flus Activity With After Tag With SQL Dict'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryFlushActivityWithAfterTag('SQLDict')

  def test_75_TryFlushActivityWithAfterTagWithSQLQueue(self, quiet=0, run=run_all_test):
    # Test if after_tag can be used
    if not run: return
    if not quiet:
      message = '\nTry Flush Activity With After Tag With SQL Queue'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryFlushActivityWithAfterTag('SQLQueue')

  def test_76_ActivateKwForNewContent(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck reindex message uses activate_kw passed to newContent'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)

    o1 = self.getOrganisationModule().newContent(
                                  activate_kw=dict(tag='The Tag'))
    get_transaction().commit()
    messages_for_o1 = [m for m in self.getActivityTool().getMessageList()
                       if m.object_path == o1.getPhysicalPath()]
    self.assertNotEquals(0, len(messages_for_o1))
    for m in messages_for_o1:
      self.assertEquals(m.activity_kw.get('tag'), 'The Tag')


  def test_77_FlushAfterMultipleActivate(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck all message are flushed in SQLDict'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    orga_module = self.getOrganisationModule()
    p = orga_module.newContent(portal_type='Organisation')
    get_transaction().commit()
    self.tic()
    self.assertEqual(p.getDescription(), "")
    activity_tool = self.getPortal().portal_activities

    def updateDesc(self):
      d =self.getDescription()
      self.setDescription(d+'a')
    Organisation.updateDesc = updateDesc

    self.assertEqual(len(activity_tool.getMessageList()), 0)
    # First check dequeue read same message only once
    for i in xrange(10):
      p.activate(activity="SQLDict").updateDesc()
      get_transaction().commit()

    self.assertEqual(len(activity_tool.getMessageList()), 10)
    self.tic()
    self.assertEqual(p.getDescription(), "a")

    # Check if there is pending activity after deleting an object
    for i in xrange(10):
      p.activate(activity="SQLDict").updateDesc()
      get_transaction().commit()

    self.assertEqual(len(activity_tool.getMessageList()), 10)
    activity_tool.flush(p, invoke=0)
    get_transaction().commit()
    self.assertEqual(len(activity_tool.getMessageList()), 0)

  def test_78_IsMessageRegisteredSQLDict(self, quiet=0, run=run_all_test):
    """
      This test tests behaviour of IsMessageRegistered method.
    """
    if not run: return
    if not quiet:
      message = '\nTest IsMessageRegistered behaviour with SQLDict'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.checkIsMessageRegisteredMethod('SQLDict')

  def test_79_AbortTransactionSynchronously(self, quiet=0, run=run_all_test):
    """
      This test tests if abortTransactionSynchronously really aborts
      a transaction synchronously.
    """
    if not run: return
    if not quiet:
      message = '\nTest Aborting Transaction Synchronously'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)

    # Make a new persistent object, and commit it so that an oid gets
    # assigned.
    module = self.getOrganisationModule()
    organisation = module.newContent(portal_type = 'Organisation')
    organisation_id = organisation.getId()
    get_transaction().commit()
    organisation = module[organisation_id]

    # Now fake a read conflict.
    from ZODB.POSException import ReadConflictError
    tid = organisation._p_serial
    oid = organisation._p_oid
    conn = organisation._p_jar
    if getattr(conn, '_mvcc', 0):
      conn._mvcc = 0 # XXX disable MVCC forcibly
    try:
      conn.db().invalidate({oid: tid})
    except TypeError:
      conn.db().invalidate(tid, {oid: tid})
    conn._cache.invalidate(oid)

    # Usual abort should not remove a read conflict error.
    organisation = module[organisation_id]
    self.assertRaises(ReadConflictError, getattr, organisation, 'uid')
    get_transaction().abort()
    self.assertRaises(ReadConflictError, getattr, organisation, 'uid')

    # Synchronous abort.
    from Products.CMFActivity.Activity.Queue import abortTransactionSynchronously
    abortTransactionSynchronously()
    getattr(organisation, 'uid')


  def test_80_CallWithGroupIdParamater(self, quiet=0, run=run_all_test):
    """
    Test that group_id parameter is used to separate execution of the same method
    """
    if not run: return
    if not quiet:
      message = '\nTest Activity with group_id parameter'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)

    portal = self.getPortal()    
    organisation =  portal.organisation._getOb(self.company_id)
    # Defined a group method
    def setFoobar(self, object_list, number=1):
      for obj in object_list:
        if getattr(obj,'foobar', None) is not None:
          obj.foobar = obj.foobar + number
        else:
          obj.foobar = number
      object_list[:] = []
    from Products.ERP5Type.Document.Folder import Folder
    Folder.setFoobar = setFoobar    

    def getFoobar(self):
      return (getattr(self,'foobar',0))
    Organisation.getFoobar = getFoobar

    organisation.foobar = 0
    self.assertEquals(0,organisation.getFoobar())

    # Test group_method_id is working without group_id
    for x in xrange(5):
      organisation.activate(activity='SQLDict', group_method_id="organisation_module/setFoobar").reindexObject(number=1)
      get_transaction().commit()      

    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),5)
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(1, organisation.getFoobar())


    # Test group_method_id is working with one group_id defined
    for x in xrange(5):
      organisation.activate(activity='SQLDict', group_method_id="organisation_module/setFoobar", group_id="1").reindexObject(number=1)
      get_transaction().commit()      

    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),5)
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(2, organisation.getFoobar())

    # Test group_method_id is working with many group_id defined
    for x in xrange(5):
      organisation.activate(activity='SQLDict', group_method_id="organisation_module/setFoobar", group_id="1").reindexObject(number=1)
      get_transaction().commit()      
      organisation.activate(activity='SQLDict', group_method_id="organisation_module/setFoobar", group_id="2").reindexObject(number=3)
      get_transaction().commit()
      organisation.activate(activity='SQLDict', group_method_id="organisation_module/setFoobar", group_id="1").reindexObject(number=1)
      get_transaction().commit()
      organisation.activate(activity='SQLDict', group_method_id="organisation_module/setFoobar", group_id="3").reindexObject(number=5)
      get_transaction().commit()

    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),20)
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(11, organisation.getFoobar())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list), 0)
    

  def test_81_ActivateKwForWorkflowTransition(self, quiet=0, run=run_all_test):
    """
    Test call of a workflow transition with activate_kw parameter propagate them
    """
    if not run: return
    if not quiet:
      message = '\nCheck reindex message uses activate_kw passed to workflow transition'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    o1 = self.getOrganisationModule().newContent()
    get_transaction().commit()
    self.tic()
    o1.validate(activate_kw=dict(tag='The Tag'))
    get_transaction().commit()
    messages_for_o1 = [m for m in self.getActivityTool().getMessageList()
                       if m.object_path == o1.getPhysicalPath()]
    self.assertNotEquals(0, len(messages_for_o1))
    for m in messages_for_o1:
      self.assertEquals(m.activity_kw.get('tag'), 'The Tag')
  
  def test_82_LossOfVolatileAttribute(self, quiet=0, run=run_all_test):
    """
    Test that the loss of volatile attribute doesn't loose activities
    """
    if not run: return
    if not quiet:
      message = '\nCheck loss of volatile attribute doesn\'t cause message to be lost'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    get_transaction().commit()
    self.tic()
    activity_tool = self.getActivityTool()
    message_list = activity_tool.getMessageList()
    self.assertEquals(len(message_list), 0)
    def delete_volatiles():
      for property_id in activity_tool.__dict__.keys():
        if property_id.startswith('_v_'):
          delattr(activity_tool, property_id)
    organisation_module = self.getOrganisationModule()
    active_organisation_module = organisation_module.activate()
    delete_volatiles()
    # Cause a message to be created
    # If the buffer cannot be created, this will raise
    active_organisation_module.getTitle()
    delete_volatiles()
    # Another activity to check that first one did not get lost even if volatile disapears
    active_organisation_module.getId()
    get_transaction().commit()
    message_list = activity_tool.getMessageList()
    self.assertEquals(len(message_list), 2)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCMFActivity))
  return suite

