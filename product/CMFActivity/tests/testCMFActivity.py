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

from Products.ERP5Type.tests.utils import LogInterceptor
from Products.ERP5Type.tests.backportUnittest import skip
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyMailHost
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.Base import Base
from Products.CMFActivity.ActiveObject import INVOKE_ERROR_STATE,\
                                              VALIDATE_ERROR_STATE
from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
from Products.CMFActivity.Activity.SQLDict import SQLDict
import Products.CMFActivity.ActivityTool
from Products.CMFActivity.Errors import ActivityPendingError, ActivityFlushError
from erp5.portal_type import Organisation
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from ZODB.POSException import ConflictError
from DateTime import DateTime
import cPickle as pickle
from Products.CMFActivity.ActivityTool import Message
import gc
import random
import threading
import sys
import weakref
import transaction

class CommitFailed(Exception):
  pass

def registerFailingTransactionManager(*args, **kw):
  from Shared.DC.ZRDB.TM import TM
  class dummy_tm(TM):
    def tpc_vote(self, *ignored):
      raise CommitFailed
    def _finish(self):
      pass
    def _abort(self):
      pass
  dummy_tm()._register()

class TestCMFActivity(ERP5TypeTestCase, LogInterceptor):

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
    super(TestCMFActivity, self).afterSetUp()
    from Products.CMFActivity.ActivityRuntimeEnvironment import BaseMessage
    # Set 'max_retry' to a known value so that we can test the feature
    BaseMessage.max_retry = property(lambda self:
      self.activity_kw.get('max_retry', 5))
    self.login()
    portal = self.portal
    # trap outgoing e-mails
    self.oldMailHost = getattr(self.portal, 'MailHost', None)
    if self.oldMailHost is not None:
      self.portal.manage_delObjects(['MailHost'])
      self.portal._setObject('MailHost', DummyMailHost('MailHost'))
    
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
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageCancel(organisation.getPhysicalPath(),'_setTitle')
    # Needed so that the message are removed from the queue
    self.commit()
    self.assertEquals(self.title1,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageInvoke(organisation.getPhysicalPath(),'_setTitle')
    # Needed so that the message are removed from the queue
    self.commit()
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
    self.commit()
    self.assertEquals(self.title1,organisation.getTitle())
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
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.tic()
    self.assertEquals(1,organisation.getFoobar())
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    organisation.activate(activity=activity).setFoobar()
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageInvoke(organisation.getPhysicalPath(),'setFoobar')
    # Needed so that the message are commited into the queue
    self.commit()
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
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title2)
    # Try again with different commit order
    organisation._setTitle(self.title1)
    organisation.activate(activity=activity)._setTitle(self.title2)
    self.commit()
    organisation.flushActivity(invoke=1)
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title2)
    self.commit()

  def TryActivateInsideFlush(self, activity):
    """
    Create a new activity inside a flush action
    """
    portal = self.getPortal()
    def DeferredSetTitle(self,value):
      self.activate(activity=activity)._setTitle(value)
    Organisation.DeferredSetTitle = DeferredSetTitle
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
    organisation.activate(activity=activity).DeferredSetTitle(self.title2)
    organisation.flushActivity(invoke=1)
    self.commit()
    portal.portal_activities.tic()
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),0)
    self.assertEquals(organisation.getTitle(),self.title2)

  def TryTwoMethods(self, activity):
    """
    Try several activities
    """
    portal = self.getPortal()
    def DeferredSetDescription(self,value):
      self._setDescription(value)
    def DeferredSetTitle(self,value):
      self._setTitle(value)
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(None)
    organisation.setDescription(None)
    organisation.activate(activity=activity).DeferredSetTitle(self.title1)
    organisation.activate(activity=activity).DeferredSetDescription(self.title1)
    self.commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.commit()
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
      self.activate(activity=activity)._setDescription(value)
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(None)
    organisation.setDescription(None)
    organisation.activate(activity=activity).DeferredSetTitle(self.title1)
    organisation.activate(activity=activity).DeferredSetDescription(self.title1)
    organisation.flushActivity(invoke=1)
    self.commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.commit()
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
        transaction.savepoint(optimistic=True)
      self.activate(activity=second or activity,priority=4)._setTitle(value)
    def DeferredSetDescription(self,value,commit_sub=0):
      if commit_sub:
        transaction.savepoint(optimistic=True)
      self.activate(activity=second or activity,priority=4)._setDescription(value)
    Organisation.DeferredSetTitle = DeferredSetTitle
    Organisation.DeferredSetDescription = DeferredSetDescription
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(None)
    organisation.setDescription(None)
    organisation.activate(activity=activity).DeferredSetTitle(self.title1,commit_sub=commit_sub)
    organisation.flushActivity(invoke=1)
    organisation.activate(activity=activity).DeferredSetDescription(self.title1,commit_sub=commit_sub)
    self.commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.commit()
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
      self.IWillCrash()
    organisation =  portal.organisation._getOb(self.company_id)
    Organisation.crashThisActivity = crashThisActivity
    organisation.activate(activity=activity).crashThisActivity()
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    LOG('Before MessageWithErrorOnActivityFails, message_list',0,[x.__dict__ for x in message_list])
    self.assertEquals(len(message_list),1)
    portal.portal_activities.tic()
    # XXX HERE WE SHOULD USE TIME SHIFT IN ORDER TO SIMULATE MULTIPLE TICS
    # Test if there is still the message after it crashed
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),1)
    portal.portal_activities.manageCancel(organisation.getPhysicalPath(),'crashThisActivity')
    # Needed so that the message are commited into the queue
    self.commit()
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
    self.commit()
    self.assertEquals(self.title1,organisation.getTitle())
    self.assertRaises(ActivityPendingError,organisation.edit,id=self.company_id2)
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
    self.commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEquals(self.title1,organisation.getTitle())
    result = active_process.getResultList()[0]
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
    self.tic()

    def toto(self, value):
      self.setTitle(self.getTitle() + value)
    o.__class__.toto = toto

    def titi(self, value):
      self.setTitle(self.getTitle() + value)
    o.__class__.titi = titi

    o.activate(after_method_id = 'titi', activity = activity).toto('b')
    o.activate(activity = activity).titi('c')
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
    self.commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.commit()
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
    self.commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.commit()
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
    self.tic()

    o.activate(after_tag = 'toto', activity = activity).setTitle('b')
    o.activate(tag = 'toto', activity = activity).setTitle('a')
    self.tic()
    self.assertEquals(o.getTitle(), 'b')

    o.setDefaultActivateParameterDict({'tag': 'toto'})
    def titi(self):
      self.setCorporateName(self.getTitle() + 'd')
    o.__class__.titi = titi
    o.activate(after_tag_and_method_id=('toto', 'setTitle'), activity = activity).titi()
    o.activate(activity = activity).setTitle('c')
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
    self.tic()

    o.activate(after_tag = 'toto', activity = activity).setDescription('b')
    o.activate(tag = 'toto', activity = activity).setTitle('a')
    self.commit()
    tool = self.getActivityTool()
    self.assertRaises(ActivityFlushError,tool.manageInvoke,o.getPath(),'setDescription')
    tool.manageInvoke(o.getPath(),'setTitle')
    self.commit()
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
    self.tic()

    def toto(self, s):
      self.setTitle(self.getTitle() + s)
    o.__class__.toto = toto

    o.activate(tag = 'toto', activity = activity).toto('a')
    self.commit()
    o.activate(after_tag = 'titi', activity = activity).toto('b')
    self.commit()
    o.activate(tag = 'titi', after_tag = 'toto', activity = activity).setTitle('c')
    self.tic()
    self.assertEquals(o.getTitle(), 'cb')

  def CheckSchedulingAfterTagList(self, activity):
    """
      Check if active objects with different after parameters are executed in a
      correct order, when after_tag is passed as a list
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = portal.organisation._getOb(self.company_id)

    o.setTitle('')
    self.tic()

    def toto(self, s):
      self.setTitle(self.getTitle() + s)
    o.__class__.toto = toto

    o.activate(tag='A', activity=activity).toto('a')
    self.commit()
    o.activate(tag='B', activity=activity).toto('b')
    self.commit()
    o.activate(after_tag=('A', 'B'), activity=activity).setTitle('last')
    self.tic()
    self.assertEquals(o.getTitle(), 'last')

  def CheckClearActivities(self, activity, activity_count=1):
    """
      Check if active objects are held even after clearing the tables.
    """
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    self.tic()

    def check(o):
      message_list = portal.portal_activities.getMessageList()
      self.assertEquals(len(message_list), activity_count)
      m = message_list[0]
      self.assertEquals(m.object_path, o.getPhysicalPath())
      self.assertEquals(m.method_id, '_setTitle')

    o = portal.organisation._getOb(self.company_id)
    for i in range(activity_count):
      o.activate(activity=activity)._setTitle('foo')
    self.commit()
    check(o)

    portal.portal_activities.manageClearActivities()
    self.commit()
    check(o)

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
    self.tic()

    o.activate(tag = 'toto', activity = activity).setTitle('a')
    self.commit()
    self.assertEquals(o.getTitle(), '?')
    self.assertEquals(portal_activities.countMessageWithTag('toto'), 1)
    self.tic()
    self.assertEquals(o.getTitle(), 'a')
    self.assertEquals(portal_activities.countMessageWithTag('toto'), 0)

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
    self.commit()
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
        self.commit()
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
    self.commit()
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
      self.commit()
      self.assertEquals(len(activity_tool.getMessageList()), 1)
      DB.original_query = DB.query
      DB.query = query
      portal.portal_activities.distribute()
      portal.portal_activities.tic()
      self.commit()
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
    self.commit()
    # First case: creating the same activity twice must only register one.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_a.activate(activity=activity).getId()
    self.commit()
    self.assertEquals(len(activity_tool.getMessageList()), 1)
    activity_tool.manageClearActivities(keep=0)
    self.commit()
    # Second case: creating activity with same tag must only register one.
    # This behaviour is actually the same as the no-tag behaviour.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity, tag='foo').getId()
    object_a.activate(activity=activity, tag='foo').getId()
    self.commit()
    self.assertEquals(len(activity_tool.getMessageList()), 1)
    activity_tool.manageClearActivities(keep=0)
    self.commit()
    # Third case: creating activities with different tags must register both.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity, tag='foo').getId()
    object_a.activate(activity=activity, tag='bar').getId()
    self.commit()
    self.assertEquals(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities(keep=0)
    self.commit()
    # Fourth case: creating activities on different objects must register
    # both.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_b.activate(activity=activity).getId()
    self.commit()
    self.assertEquals(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities(keep=0)
    self.commit()
    # Fifth case: creating activities with different method must register
    # both.
    self.assertEquals(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_a.activate(activity=activity).getTitle()
    self.commit()
    self.assertEquals(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities(keep=0)
    self.commit()

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
    self.commit()
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

  def test_61_CheckSchedulingAfterTagListWithSQLDict(self, quiet=0, run=run_all_test):
    # Test if scheduling is correct with SQLDict
    if not run: return
    if not quiet:
      message = '\nCheck Scheduling After Tag List With SQL Dict'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckSchedulingAfterTagList('SQLDict')

  def test_62_CheckSchedulingWithAfterTagListSQLQueue(self, quiet=0, run=run_all_test):
    # Test if scheduling is correct with SQLQueue
    if not run: return
    if not quiet:
      message = '\nCheck Scheduling After Tag List With SQL Queue'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckSchedulingAfterTagList('SQLQueue')

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
    self.CheckClearActivities('SQLQueue', activity_count=2)

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
      self.commit()
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
    def notifyUserSilent(self, *args, **kw):
      pass
    Message.notifyUser = notifyUserSilent

    activity_list = ['SQLQueue', 'SQLDict', ]
    for activity in activity_list:
      # reset
      activity_tool.manageClearActivities(keep=0)
      obj.setTitle(original_title)
      self.commit()

      # activate failing message and flush
      for fail_activity in activity_list:
        obj.activate(activity = fail_activity).failingMethod()
      self.commit()
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
      self.commit()
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
    a persistent object.

    XXX: this test fails if run first
    """
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
    def notifyUserSilent(self, *args, **kw):
      pass
    Message.notifyUser = notifyUserSilent

    # First, index the object.
    self.commit()
    self.flushAllActivities(silent=1, loop_size=100)
    self.assertEquals(len(activity_tool.getMessageList()), 0)

    # Insert a failing active object.
    obj.activate().failingMethod()
    self.commit()
    self.assertEquals(len(activity_tool.getMessageList()), 1)

    # Just wait for the active object to be abandoned.
    self.flushAllActivities(silent=1, loop_size=100)
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
    self.commit()
    self.assertEquals(len(activity_tool.getMessageList()), 0)

  def test_68_RetryMessageExecution(self, quiet=0):
    if not quiet:
      message = '\nCheck number of executions of failing activities'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    activity_tool = self.portal.portal_activities
    self.assertFalse(activity_tool.getMessageList())
    exec_count = [0]
    # priority does not matter anymore
    priority = random.Random().randint
    def doSomething(self, retry_list):
      i = exec_count[0]
      exec_count[0] = i + 1
      conflict, edit_kw = retry_list[i]
      if edit_kw:
        self.getActivityRuntimeEnvironment().edit(**edit_kw)
      if conflict is not None:
        raise ConflictError if conflict else Exception
    def check(retry_list, **activate_kw):
      fail = retry_list[-1][0] is not None and 1 or 0
      for activity in 'SQLDict', 'SQLQueue':
        exec_count[0] = 0
        activity_tool.activate(activity=activity, priority=priority(1,6),
                               **activate_kw).doSomething(retry_list)
        self.commit()
        self.flushAllActivities(silent=1)
        self.assertEqual(len(retry_list), exec_count[0])
        self.assertEqual(fail, len(activity_tool.getMessageList()))
        self.portal.portal_activities.manageCancel(
          activity_tool.getPhysicalPath(), 'doSomething')
    activity_tool.__class__.doSomething = doSomething
    try:
      ## Default behaviour
      # Usual successful case: activity is run only once
      check([(None, None)])
      # Usual error case: activity is run 6 times before being frozen
      check([(False, None)] * 6)
      # On ConflictError, activity is reexecuted without increasing retry count
      check([(True, None)] * 10 + [(None, None)])
      check([(True, None), (False, None)] * 6)
      ## Customized behaviour
      # Do not retry
      check([(False, {'max_retry': 0})])
      # ... even in case of ConflictError
      check([(True, {'max_retry': 0}),
             (True, {'max_retry': 0, 'conflict_retry': 0})])
      check([(True, None)] * 6, conflict_retry=False)
      # Customized number of retries
      for n in 3, 9:
        check([(False, {'max_retry': n})] * n + [(None, None)])
        check([(False, {'max_retry': n})] * (n + 1))
      # Infinite retry
      for n in 3, 9:
        check([(False, {'max_retry': None})] * n + [(None, None)])
        check([(False, {'max_retry': None})] * n + [(False, {'max_retry': 0})])
      check([(False, {'max_retry': None})] * 9 + [(False, None)])

    finally:
      del activity_tool.__class__.doSomething
    self.assertFalse(activity_tool.getMessageList())

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
    self.commit()
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
      self.commit()

    self.assertEqual(len(activity_tool.getMessageList()), 10)
    self.tic()
    self.assertEqual(p.getDescription(), "a")

    # Check if there is pending activity after deleting an object
    for i in xrange(10):
      p.activate(activity="SQLDict").updateDesc()
      self.commit()

    self.assertEqual(len(activity_tool.getMessageList()), 10)
    activity_tool.flush(p, invoke=0)
    self.commit()
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
      This test checks if transaction.abort() synchronizes connections. It
      didn't do so back in Zope 2.7
    """
    if not run: return
    if not quiet:
      message = '\nTest Aborting Transaction Synchronizes'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)

    # Make a new persistent object, and commit it so that an oid gets
    # assigned.
    module = self.getOrganisationModule()
    organisation = module.newContent(portal_type = 'Organisation')
    organisation_id = organisation.getId()
    self.commit()
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

    # Access to invalidated object in non-MVCC connections should raise a
    # conflict error
    organisation = module[organisation_id]
    self.assertRaises(ReadConflictError, getattr, organisation, 'uid')

    # In Zope 2.7, abort does not sync automatically, so even after abort,
    # ReadConflictError would be raised. But in Zope 2.8, this is automatic.

    self.abort()
    getattr(organisation, 'uid')


  def callWithGroupIdParamater(self, activity, quiet, run):
    if not run: return
    if not quiet:
      message = '\nTest Activity with group_id parameter (%s)' % activity
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)

    portal = self.getPortal()    
    organisation =  portal.organisation._getOb(self.company_id)
    # Defined a group method
    foobar_list = []
    def setFoobar(self, object_list):
      foobar_list.append(len(object_list))
      for obj, args, kw, _ in object_list:
        obj.foobar = getattr(obj.aq_base, 'foobar', 0) + kw.get('number', 1)
    from Products.ERP5Type.Core.Folder import Folder
    Folder.setFoobar = setFoobar    

    def getFoobar(self):
      return (getattr(self,'foobar',0))
    Organisation.getFoobar = getFoobar

    organisation.foobar = 0
    self.assertEquals(0,organisation.getFoobar())

    # Test group_method_id is working without group_id
    for x in xrange(5):
      organisation.activate(activity=activity, group_method_id="organisation_module/setFoobar").reindexObject(number=1)
      self.commit()

    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),5)
    portal.portal_activities.tic()
    expected = dict(SQLDict=1, SQLQueue=5)[activity]
    self.assertEquals(expected, organisation.getFoobar())


    # Test group_method_id is working with one group_id defined
    for x in xrange(5):
      organisation.activate(activity=activity, group_method_id="organisation_module/setFoobar", group_id="1").reindexObject(number=1)
      self.commit()

    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),5)
    portal.portal_activities.tic()
    self.assertEquals(expected * 2, organisation.getFoobar())

    self.assertEquals([expected, expected], foobar_list)
    del foobar_list[:]

    # Test group_method_id is working with many group_id defined
    for x in xrange(5):
      organisation.activate(activity=activity, group_method_id="organisation_module/setFoobar", group_id="1").reindexObject(number=1)
      self.commit()
      organisation.activate(activity=activity, group_method_id="organisation_module/setFoobar", group_id="2").reindexObject(number=3)
      self.commit()
      organisation.activate(activity=activity, group_method_id="organisation_module/setFoobar", group_id="1").reindexObject(number=1)
      self.commit()
      organisation.activate(activity=activity, group_method_id="organisation_module/setFoobar", group_id="3").reindexObject(number=5)
      self.commit()

    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list),20)
    portal.portal_activities.tic()
    self.assertEquals(dict(SQLDict=11, SQLQueue=60)[activity],
                      organisation.getFoobar())
    self.assertEquals(dict(SQLDict=[1, 1, 1], SQLQueue=[5, 5, 10])[activity],
                      sorted(foobar_list))
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list), 0)

  def test_80a_CallWithGroupIdParamaterSQLDict(self, quiet=0, run=run_all_test):
    """
    Test that group_id parameter is used to separate execution of the same method
    """
    self.callWithGroupIdParamater('SQLDict', quiet=quiet, run=run)

  def test_80b_CallWithGroupIdParamaterSQLQueue(self, quiet=0,
                                                run=run_all_test):
    """
    Test that group_id parameter is used to separate execution of the same method
    """
    self.callWithGroupIdParamater('SQLQueue', quiet=quiet, run=run)

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
    self.tic()
    o1.validate(activate_kw=dict(tag='The Tag'))
    self.commit()
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
    self.commit()
    message_list = activity_tool.getMessageList()
    self.assertEquals(len(message_list), 2)

  def test_83_ActivityModificationsViaCMFActivityConnectionRolledBackOnErrorSQLDict(self, quiet=0, run=run_all_test):
    """
      When an activity modifies tables through CMFActivity SQL connection and
      raises, check that its changes are correctly rolled back.
    """
    if not run: return
    if not quiet:
      message = '\nCheck activity modifications via CMFActivity connection are rolled back on error (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.tic()
    activity_tool = self.getActivityTool()
    def modifySQLAndFail(self, object_list):
      # Only create the dummy activity if none is present: we would just
      # generate missleading errors (duplicate uid).
      if activity_tool.countMessage(method_id='dummy_activity') == 0:
        # Add a dumy activity which will not be executed
        # Modified table does not matter
        method_id = 'dummy_activity'
        path = '/'.join(self.getPhysicalPath())
        message = Message(self, None, {}, method_id, (), {})
        pickled_message = pickle.dumps(message)
        self.SQLDict_writeMessageList(
          uid_list=[0], # This uid is never automaticaly assigned (starts at 1)
          date_list=[DateTime().Date()],
          path_list=[path],
          active_process_uid=[None],
          method_id_list=[method_id],
          message_list=[pickled_message],
          priority_list=[1],
          processing_node_list=[-2],
          group_method_id_list=['\0'],
          tag_list=[''],
          order_validation_text_list=[''],
          serialization_tag_list=[''],
          )
      # Mark first entry as failed
      del object_list[0][3]
    def dummy(self):
      pass
    try:
      Organisation.modifySQLAndFail = modifySQLAndFail
      Organisation.dummy = dummy
      obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      group_method_id = '%s/modifySQLAndFail' % (obj.getPath(), )
      obj.activate(activity='SQLDict', group_method_id=group_method_id).dummy()
      obj2 = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      obj2.activate(activity='SQLDict', group_method_id=group_method_id).dummy()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEquals(activity_tool.countMessage(method_id='dummy_activity'), 0)
    finally:
      delattr(Organisation, 'modifySQLAndFail')
      delattr(Organisation, 'dummy')

  def test_84_ActivityModificationsViaCMFActivityConnectionRolledBackOnErrorSQLQueue(self, quiet=0, run=run_all_test):
    """
      When an activity modifies tables through CMFActivity SQL connection and
      raises, check that its changes are correctly rolled back.
    """
    if not run: return
    if not quiet:
      message = '\nCheck activity modifications via CMFActivity connection are rolled back on error (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.tic()
    activity_tool = self.getActivityTool()
    def modifySQLAndFail(self):
      # Only create the dummy activity if none is present: we would just
      # generate missleading errors (duplicate uid).
      if activity_tool.countMessage(method_id='dummy_activity') == 0:
        # Add a dumy activity which will not be executed
        # Modified table does not matter
        method_id = 'dummy_activity'
        path = '/'.join(self.getPhysicalPath())
        message = Message(self, None, {}, method_id, (), {})
        pickled_message = pickle.dumps(message)
        self.SQLDict_writeMessageList(
          uid_list=[0], # This uid is never automaticaly assigned (starts at 1)
          date_list=[DateTime().Date()],
          path_list=[path],
          method_id_list=[method_id],
          message_list=[pickled_message],
          priority_list=[1],
          processing_node_list=[-2],
          group_method_id_list=['\0'],
          tag_list=[''],
          order_validation_text_list=[''],
          serialization_tag_list=['']
          )
      # Fail
      raise ValueError, 'This method always fail'
    try:
      Organisation.modifySQLAndFail = modifySQLAndFail
      obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      obj.activate(activity='SQLQueue').modifySQLAndFail()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEquals(activity_tool.countMessage(method_id='dummy_activity'), 0)
    finally:
      delattr(Organisation, 'modifySQLAndFail')

  def test_85_MessagePathMustBeATuple(self, quiet=0, run=run_all_test):
    """
      Message property 'object_path' must be a tuple, whatever it is generated from.
      Possible path sources are:
       - bare string
       - object
    """
    if not run: return
    if not quiet:
      message = '\nCheck that message property \'object_path\' is a tuple, whatever it is generated from.'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    def check(value):
      message = Message(value, None, {}, 'dummy', (), {})
      self.assertTrue(isinstance(message.object_path, tuple))
    # Bare string
    check('/foo/bar')
    # Object
    check(self.getPortalObject().person_module)

  def test_86_ActivityToolInvokeGroupFailureDoesNotCommitCMFActivitySQLConnectionSQLDict(self, quiet=0, run=run_all_test):
    """
      Check that CMFActivity SQL connection is rollback if activity_tool.invokeGroup raises.
    """
    if not run: return
    if not quiet:
      message = '\nCheck that activity modifications via CMFActivity connection are rolled back on ActivityTool error (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.tic()
    activity_tool = self.getActivityTool()
    def modifySQLAndFail(self, *arg, **kw):
      # Only create the dummy activity if none is present: we would just
      # generate missleading errors (duplicate uid).
      if activity_tool.countMessage(method_id='dummy_activity') == 0:
        # Add a dumy activity which will not be executed
        # Modified table does not matter
        method_id = 'dummy_activity'
        path = '/'.join(self.getPhysicalPath())
        message = Message(self, None, {}, method_id, (), {})
        pickled_message = pickle.dumps(message)
        self.SQLDict_writeMessageList(
          uid_list=[0], # This uid is never automaticaly assigned (starts at 1)
          date_list=[DateTime().Date()],
          path_list=[path],
          method_id_list=[method_id],
          message_list=[pickled_message],
          priority_list=[1],
          processing_node_list=[-2],
          group_method_id_list=['\0'],
          tag_list=[''],
          order_validation_text_list=[''],
          serialization_tag_list=[''],
          )
      # Fail
      raise ValueError, 'This method always fail'
    def dummy(self):
      pass
    invoke = activity_tool.__class__.invoke
    invokeGroup = activity_tool.__class__.invokeGroup
    try: 
      activity_tool.__class__.invoke = modifySQLAndFail
      activity_tool.__class__.invokeGroup = modifySQLAndFail
      Organisation.dummy = dummy
      obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      group_method_id = '%s/dummy' % (obj.getPath(), )
      obj.activate(activity='SQLDict', group_method_id=group_method_id).dummy()
      obj2 = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      obj2.activate(activity='SQLDict', group_method_id=group_method_id).dummy()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEquals(activity_tool.countMessage(method_id='dummy_activity'), 0)
    finally:
      delattr(Organisation, 'dummy')
      activity_tool.__class__.invoke = invoke
      activity_tool.__class__.invokeGroup = invokeGroup
  
  def test_87_ActivityToolInvokeFailureDoesNotCommitCMFActivitySQLConnectionSQLQueue(self, quiet=0, run=run_all_test):
    """
      Check that CMFActivity SQL connection is rollback if activity_tool.invoke raises.
    """
    if not run: return
    if not quiet:
      message = '\nCheck that activity modifications via CMFActivity connection are rolled back on ActivityTool error (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.tic()
    activity_tool = self.getActivityTool()
    def modifySQLAndFail(self, *args, **kw):
      # Only create the dummy activity if none is present: we would just
      # generate missleading errors (duplicate uid).
      if activity_tool.countMessage(method_id='dummy_activity') == 0:
        # Add a dumy activity which will not be executed
        # Modified table does not matter
        method_id = 'dummy_activity'
        path = '/'.join(self.getPhysicalPath())
        message = Message(self, None, {}, method_id, (), {})
        pickled_message = pickle.dumps(message)
        self.SQLDict_writeMessageList(
          uid_list=[0], # This uid is never automaticaly assigned (starts at 1)
          date_list=[DateTime().Date()],
          path_list=[path],
          method_id_list=[method_id],
          message_list=[pickled_message],
          priority_list=[1],
          processing_node_list=[-2],
          group_method_id_list=['\0'],
          tag_list=[''],
          order_validation_text_list=[''],
          serialization_tag_list=[''],
          )
      # Fail
      raise ValueError, 'This method always fail'
    def dummy(self):
      pass
    invoke = activity_tool.__class__.invoke
    invokeGroup = activity_tool.__class__.invokeGroup
    try:
      activity_tool.__class__.invoke = modifySQLAndFail
      activity_tool.__class__.invokeGroup = modifySQLAndFail
      Organisation.dummy = dummy
      obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      obj.activate(activity='SQLQueue').dummy()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEquals(activity_tool.countMessage(method_id='dummy_activity'), 0)
    finally:
      delattr(Organisation, 'dummy')
      activity_tool.__class__.invoke = invoke
      activity_tool.__class__.invokeGroup = invokeGroup

  def test_88_ProcessingMultipleMessagesMustRevertIndividualMessagesOnError(self, quiet=0, run=run_all_test):
    """
      Check that, on queues which support it, processing a batch of multiple
      messages doesn't cause failed ones to becommited along with succesful
      ones.

      Queues supporting message batch processing:
       - SQLQueue
    """
    if not run: return
    if not quiet:
      message = '\nCheck processing a batch of messages with failures'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.tic()
    activity_tool = self.getActivityTool()
    obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    active_obj = obj.activate(activity='SQLQueue')
    def appendToTitle(self, to_append, fail=False):
      self.setTitle(self.getTitle() + to_append)
      if fail:
        raise ValueError, 'This method always fail'
    try:
      Organisation.appendToTitle = appendToTitle
      obj.setTitle('a')
      active_obj.appendToTitle('b')
      active_obj.appendToTitle('c', fail=True)
      active_obj.appendToTitle('d')
      object_id = obj.getId()
      self.commit()
      self.assertEqual(obj.getTitle(), 'a')
      self.assertEqual(activity_tool.countMessage(method_id='appendToTitle'), 3)
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEqual(activity_tool.countMessage(method_id='appendToTitle'), 1)
      self.assertEqual(sorted(obj.getTitle()), ['a', 'b', 'd'])
    finally:
      delattr(Organisation, 'appendToTitle')

  def test_89_RequestIsolationInsideSameTic(self, quiet=0, run=run_all_test):
    """
      Check that request information do not leak from one activity to another
      inside the same TIC invocation.
      This only apply to queues supporting batch processing:
        - SQLQueue
    """
    if not run: return
    if not quiet:
      message = '\nCheck request isolation between messages of the same batch'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.tic()
    obj = self.getPortal().organisation_module.newContent(portal_type='Organisation', title='Pending')
    marker_id = 'marker_%i' % (random.randint(1, 10), )
    def putMarkerValue(self, marker_id):
      self.REQUEST.set(marker_id, 1)
    def checkMarkerValue(self, marker_id):
      if self.REQUEST.get(marker_id) is not None:
        self.setTitle('Failed')
      else:
        self.setTitle('Success')
    try:
      Organisation.putMarkerValue = putMarkerValue
      Organisation.checkMarkerValue = checkMarkerValue
      obj.activate(activity='SQLQueue', tag='set_first').putMarkerValue(marker_id=marker_id)
      obj.activate(activity='SQLQueue', after_tag='set_first').checkMarkerValue(marker_id=marker_id)
      self.assertEqual(obj.getTitle(), 'Pending')
      self.tic()
      self.assertEqual(obj.getTitle(), 'Success')
    finally:
      delattr(Organisation, 'putMarkerValue')
      delattr(Organisation, 'checkMarkerValue')

  def TryUserNotificationOnActivityFailure(self, activity):
    self.tic()
    obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    self.tic()
    # Use a mutable variable to be able to modify the same instance from
    # monkeypatch method.
    notification_done = []
    from Products.CMFActivity.ActivityTool import Message
    def fake_notifyUser(self, *args, **kw):
      notification_done.append(True)
    original_notifyUser = Message.notifyUser
    def failingMethod(self):
      raise ValueError, 'This method always fail'
    Message.notifyUser = fake_notifyUser
    Organisation.failingMethod = failingMethod
    try:
      # MESSAGE_NOT_EXECUTED
      obj.activate(activity=activity).failingMethod()
      self.commit()
      self.assertEqual(len(notification_done), 0)
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEqual(len(notification_done), 1)
      # MESSAGE_NOT_EXECUTABLE
      obj.getParentValue()._delObject(obj.getId())
      obj.activate(activity=activity).getId()
      self.commit()
      self.assertEqual(len(notification_done), 1)
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEqual(len(notification_done), 2)
    finally:
      Message.notifyUser = original_notifyUser
      delattr(Organisation, 'failingMethod')


  def test_90_userNotificationOnActivityFailureWithSQLDict(self, quiet=0, run=run_all_test):
    """
      Check that a user notification method is called on message when activity
      fails and will not be tried again.
    """
    if not run: return
    if not quiet:
      message = '\nCheck user notification sent on activity final error (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryUserNotificationOnActivityFailure('SQLDict')

  def test_91_userNotificationOnActivityFailureWithSQLQueue(self, quiet=0, run=run_all_test):
    """
      Check that a user notification method is called on message when activity
      fails and will not be tried again.
    """
    if not run: return
    if not quiet:
      message = '\nCheck user notification sent on activity final error (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryUserNotificationOnActivityFailure('SQLQueue')

  def TryUserNotificationRaise(self, activity):
    self.tic()
    obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    self.tic()
    from Products.CMFActivity.ActivityTool import Message
    original_notifyUser = Message.notifyUser
    def failingMethod(self, *args, **kw):
      raise ValueError, 'This method always fail'
    Message.notifyUser = failingMethod
    Organisation.failingMethod = failingMethod
    getMessageList = self.getPortalObject().portal_activities.getMessageList
    try:
      obj.activate(activity=activity, priority=6).failingMethod()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      message, = getMessageList(activity=activity, method_id='failingMethod')
      self.assertEqual(message.processing, 0)
    finally:
      Message.notifyUser = original_notifyUser
      delattr(Organisation, 'failingMethod')

  def test_92_userNotificationRaiseWithSQLDict(self, quiet=0, run=run_all_test):
    """
      Check that activities are not left with processing=1 when notifyUser raises.
    """
    if not run: return
    if not quiet:
      message = '\nCheck that activities are not left with processing=1 when notifyUser raises (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryUserNotificationRaise('SQLDict')

  def test_93_userNotificationRaiseWithSQLQueue(self, quiet=0, run=run_all_test):
    """
      Check that activities are not left with processing=1 when notifyUser raises.
    """
    if not run: return
    if not quiet:
      message = '\nCheck that activities are not left with processing=1 when notifyUser raises (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryUserNotificationRaise('SQLQueue')
    
  def test_94_ActivityToolCommitFailureDoesNotCommitCMFActivitySQLConnectionSQLDict(self, quiet=0, run=run_all_test):
    """
      Check that CMFActivity SQL connection is rollback if transaction commit raises.
    """
    if not run: return
    if not quiet:
      message = '\nCheck that activity modifications via CMFActivity connection are rolled back on commit error (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.tic()
    activity_tool = self.getActivityTool()
    def modifySQL(self, object_list):
      # Only create the dummy activity if none is present: we would just
      # generate missleading errors (duplicate uid).
      if activity_tool.countMessage(method_id='dummy_activity') == 0:
        # Add a dumy activity which will not be executed
        # Modified table does not matter
        method_id = 'dummy_activity'
        path = '/'.join(self.getPhysicalPath())
        message = Message(self, None, {}, method_id, (), {})
        pickled_message = pickle.dumps(message)
        self.SQLDict_writeMessageList(
          uid_list=[0], # This uid is never automaticaly assigned (starts at 1)
          date_list=[DateTime().Date()],
          path_list=[path],
          method_id_list=[method_id],
          message_list=[pickled_message],
          priority_list=[1],
          processing_node_list=[-2],
          group_method_id_list=['\0'],
          tag_list=[''],
          order_validation_text_list=[''],
          )
      transaction.get().__class__.commit = fake_commit
    commit = transaction.get().__class__.commit
    def fake_commit(*args, **kw):
      transaction.get().__class__.commit = commit
      raise KeyError, 'always fail'
    try: 
      Organisation.modifySQL = modifySQL
      obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      group_method_id = '%s/modifySQL' % (obj.getPath(), )
      obj2 = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      self.tic()
      obj.activate(activity='SQLDict', group_method_id=group_method_id).modifySQL()
      obj2.activate(activity='SQLDict', group_method_id=group_method_id).modifySQL()
      self.commit()
      try:
        self.flushAllActivities(silent=1, loop_size=100)
      finally:
        transaction.get().__class__.commit = commit
      self.assertEquals(activity_tool.countMessage(method_id='dummy_activity'), 0)
    finally:
      delattr(Organisation, 'modifySQL')
  
  def test_95_ActivityToolCommitFailureDoesNotCommitCMFActivitySQLConnectionSQLQueue(self, quiet=0, run=run_all_test):
    """
      Check that CMFActivity SQL connection is rollback if activity_tool.invoke raises.
    """
    if not run: return
    if not quiet:
      message = '\nCheck that activity modifications via CMFActivity connection are rolled back on commit error (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.tic()
    activity_tool = self.getActivityTool()
    def modifySQL(self, *args, **kw):
      # Only create the dummy activity if none is present: we would just
      # generate missleading errors (duplicate uid).
      if activity_tool.countMessage(method_id='dummy_activity') == 0:
        # Add a dumy activity which will not be executed
        # Modified table does not matter
        method_id = 'dummy_activity'
        path = '/'.join(self.getPhysicalPath())
        message = Message(self, None, {}, method_id, (), {})
        pickled_message = pickle.dumps(message)
        self.SQLDict_writeMessageList(
          uid_list=[0], # This uid is never automaticaly assigned (starts at 1)
          date_list=[DateTime().Date()],
          path_list=[path],
          method_id_list=[method_id],
          message_list=[pickled_message],
          priority_list=[1],
          processing_node_list=[-2],
          group_method_id_list=['\0'],
          tag_list=[''],
          order_validation_text_list=[''],
         )
      transaction.get().__class__.commit = fake_commit
    commit = transaction.get().__class__.commit
    def fake_commit(self, *args, **kw):
      transaction.get().__class__.commit = commit
      raise KeyError, 'always fail'
    try:
      Organisation.modifySQL = modifySQL
      obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      self.tic()
      obj.activate(activity='SQLQueue').modifySQL()
      self.commit()
      try:
        self.flushAllActivities(silent=1, loop_size=100)
      finally:
        transaction.get().__class__.commit = commit
      self.assertEquals(activity_tool.countMessage(method_id='dummy_activity'), 0)
    finally:
      delattr(Organisation, 'modifySQL')

  def TryActivityRaiseInCommitDoesNotStallActivityConection(self, activity):
    """
      Check that an activity which commit raises (as would a regular conflict
      error be raised in tpc_vote) does not cause activity connection to
      stall.
    """
    self.tic()
    activity_tool = self.getActivityTool()
    from Shared.DC.ZRDB.TM import TM
    try:
      Organisation.registerFailingTransactionManager = registerFailingTransactionManager
      obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      self.tic()
      now = DateTime()
      obj.activate(activity=activity).registerFailingTransactionManager()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      self.commit()
      # Check that cmf_activity SQL connection still works
      connection_da_pool = self.getPortalObject().cmf_activity_sql_connection()
      import thread
      connection_da = connection_da_pool._db_pool[thread.get_ident()]
      self.assertFalse(connection_da._registered)
      connection_da_pool.query('select 1')
      self.assertTrue(connection_da._registered)
      self.commit()
      self.assertFalse(connection_da._registered)
    finally:
      delattr(Organisation, 'registerFailingTransactionManager')

  def test_96_ActivityRaiseInCommitDoesNotStallActivityConectionSQLDict(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that raising in commit does not stall cmf activity SQL connection (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivityRaiseInCommitDoesNotStallActivityConection('SQLDict')

  def test_97_ActivityRaiseInCommitDoesNotStallActivityConectionSQLQueue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that raising in commit does not stall cmf activity SQL connection (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivityRaiseInCommitDoesNotStallActivityConection('SQLQueue')

  def TryActivityRaiseInCommitDoesNotLooseMessages(self, activity):
    """
    """
    self.tic()
    activity_tool = self.getActivityTool()
    try:
      Organisation.registerFailingTransactionManager = registerFailingTransactionManager
      obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      self.tic()
      now = DateTime()
      obj.activate(activity=activity).registerFailingTransactionManager()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      self.commit()
      self.assertEquals(activity_tool.countMessage(method_id='registerFailingTransactionManager'), 1)
    finally:
      delattr(Organisation, 'registerFailingTransactionManager')

  def test_98_ActivityRaiseInCommitDoesNotLooseMessagesSQLDict(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that raising in commit does not loose messages (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivityRaiseInCommitDoesNotLooseMessages('SQLDict')

  def test_99_ActivityRaiseInCommitDoesNotLooseMessagesSQLQueue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that raising in commit does not loose messages (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryActivityRaiseInCommitDoesNotLooseMessages('SQLQueue')

  def TryChangeSkinInActivity(self, activity):
    self.tic()
    activity_tool = self.getActivityTool()
    def changeSkinToNone(self):
      self.getPortalObject().changeSkin(None)
    Organisation.changeSkinToNone = changeSkinToNone
    try:
      organisation = self.getPortal().organisation_module.newContent(portal_type='Organisation')
      self.tic()
      organisation.activate(activity=activity).changeSkinToNone()
      self.commit()
      self.assertEquals(len(activity_tool.getMessageList()), 1)
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEquals(len(activity_tool.getMessageList()), 0)
    finally:
      delattr(Organisation, 'changeSkinToNone')

  def test_100_TryChangeSkinInActivitySQLDict(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTry Change Skin In Activity (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryChangeSkinInActivity('SQLDict')

  def test_101_TryChangeSkinInActivitySQLQueue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTry ChangeSkin In Activity (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryChangeSkinInActivity('SQLQueue')

  def test_102_1_CheckSQLDictDoesNotDeleteSimilaritiesBeforeExecution(self, quiet=0, run=run_all_test):
    """
      Test that SQLDict does not delete similar messages which have the same
      method_id and path but a different tag before execution.
    """
    if not run: return
    if not quiet:
      message = '\nCheck similarities are not deleted before execution of original message (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    activity_tool = self.getActivityTool()
    marker = []
    def doSomething(self, other_tag):
      marker.append(self.countMessage(tag=other_tag))
    activity_tool.__class__.doSomething = doSomething
    try:
      # Adds two similar but not the same activities.
      activity_tool.activate(activity='SQLDict', after_tag='foo',
        tag='a').doSomething(other_tag='b')
      activity_tool.activate(activity='SQLDict', after_tag='bar',
        tag='b').doSomething(other_tag='a')
      self.commit()
      activity_tool.tic() # make sure distribution phase was not skipped
      activity_tool.distribute()
      # after distribute, similarities are still there.
      self.assertEqual(len(activity_tool.getMessageList()), 2)
      activity_tool.tic()
      self.assertEqual(len(activity_tool.getMessageList()), 0)
      self.assertEqual(marker, [1])
    finally:
      del activity_tool.__class__.doSomething

  def test_102_2_CheckSQLDictDeleteDuplicatesBeforeExecution(self, quiet=0, run=run_all_test):
    """
      Test that SQLDict delete the same messages before execution if messages
      has the same method_id and path and tag.
    """
    if not run: return
    if not quiet:
      message = '\nCheck duplicates are deleted before execution of original message (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    activity_tool = self.getActivityTool()
    marker = []
    def doSomething(self, other_tag):
      marker.append(self.countMessage(tag=other_tag))
    activity_tool.__class__.doSomething = doSomething
    try:
      # Adds two same activities.
      activity_tool.activate(activity='SQLDict', after_tag='foo', priority=2,
        tag='a').doSomething(other_tag='a')
      self.commit()
      uid1, = [x.uid for x in activity_tool.getMessageList()]
      activity_tool.activate(activity='SQLDict', after_tag='bar', priority=1,
        tag='a').doSomething(other_tag='a')
      self.commit()
      self.assertEqual(len(activity_tool.getMessageList()), 2)
      activity_tool.distribute()
      # After distribute, duplicate is deleted.
      uid2, = [x.uid for x in activity_tool.getMessageList()]
      self.assertNotEqual(uid1, uid2)
      activity_tool.tic()
      self.assertEqual(len(activity_tool.getMessageList()), 0)
      self.assertEqual(marker, [1])
    finally:
      del activity_tool.__class__.doSomething

  def test_102_3_CheckSQLDictDistributeWithSerializationTagAndGroupMethodId(
      self, quiet=0):
    """
      Distribuation was at some point buggy with this scenario when there was
      activate with the same serialization_tag and one time with a group_method
      id and one without group_method_id :
        foo.activate(serialization_tag='a', group_method_id='x').getTitle()
        foo.activate(serialization_tag='a').getId()
    """
    organisation = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    self.tic()
    activity_tool = self.getActivityTool()
    organisation.activate(serialization_tag='a').getId()
    self.commit()
    organisation.activate(serialization_tag='a',
              group_method_id='portal_catalog/catalogObjectList').getTitle()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    activity_tool.distribute()
    # After distribute, there is no deletion because it is different method
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    self.tic()
    self.assertEqual(len(activity_tool.getMessageList()), 0)

  def test_103_interQueuePriorities(self, quiet=0, run=run_all_test):
    """
      Important note: there is no way to really reliably check that this
      feature is correctly implemented, as activity execution order is
      non-deterministic.
      The best which can be done is to check that under certain circumstances
      the activity exeicution order match expectations.
    """
    if not run: return
    if not quiet:
      message = '\nCheck inter-queue priorities'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    organisation = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    self.tic()
    activity_tool = self.getActivityTool()
    check_result_dict = {}
    def runAndCheck():
      check_result_dict.clear()
      self.commit()
      self.assertEqual(len(check_result_dict), 0)
      self.tic()
      self.assertEqual(len(check_result_dict), 2)
      self.assertTrue(check_result_dict['before_ran'])
      self.assertTrue(check_result_dict['after_ran'])
    def mustRunBefore(self):
      check_result_dict['before_ran'] = 'after_ran' not in check_result_dict
    def mustRunAfter(self):
      check_result_dict['after_ran'] = 'before_ran' in check_result_dict
    Organisation.mustRunBefore = mustRunBefore
    Organisation.mustRunAfter = mustRunAfter
    try:
      # Check that ordering looks good (SQLQueue first)
      organisation.activate(activity='SQLQueue', priority=1).mustRunBefore()
      organisation.activate(activity='SQLDict',  priority=2).mustRunAfter()
      runAndCheck()
      # Check that ordering looks good (SQLDict first)
      organisation.activate(activity='SQLDict',  priority=1).mustRunBefore()
      organisation.activate(activity='SQLQueue', priority=2).mustRunAfter()
      runAndCheck()
      # Check that tag takes precedence over priority (SQLQueue first by priority)
      organisation.activate(activity='SQLQueue', priority=1, after_tag='a').mustRunAfter()
      organisation.activate(activity='SQLDict',  priority=2, tag='a').mustRunBefore()
      runAndCheck()
      # Check that tag takes precedence over priority (SQLDict first by priority)
      organisation.activate(activity='SQLDict',  priority=1, after_tag='a').mustRunAfter()
      organisation.activate(activity='SQLQueue', priority=2, tag='a').mustRunBefore()
      runAndCheck()
    finally:
      delattr(Organisation, 'mustRunBefore')
      delattr(Organisation, 'mustRunAfter')

  def CheckActivityRuntimeEnvironment(self, activity):
    document = self.portal.organisation_module
    activity_result = []
    def extractActivityRuntimeEnvironment(self):
      activity_result.append(self.getActivityRuntimeEnvironment())
    document.__class__.doSomething = extractActivityRuntimeEnvironment
    try:
      document.activate(activity=activity).doSomething()
      self.commit()
      # Check that getActivityRuntimeEnvironment raises outside of activities
      self.assertRaises(KeyError, document.getActivityRuntimeEnvironment)
      # Check Runtime isolation
      self.tic()
      # Check that it still raises outside of activities
      self.assertRaises(KeyError, document.getActivityRuntimeEnvironment)
      # Check activity runtime environment instance
      env = activity_result.pop()
      self.assertFalse(activity_result)
      message = env._message
      self.assertEqual(message.line.priority, 1)
      self.assertEqual(message.object_path, document.getPhysicalPath())
      self.assertTrue(message.conflict_retry) # default value
      env.edit(max_retry=0, conflict_retry=False)
      self.assertFalse(message.conflict_retry) # edited value
      self.assertRaises(AttributeError, env.edit, foo='bar')
    finally:
      del document.__class__.doSomething

  def test_104_activityRuntimeEnvironmentSQLDict(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck ActivityRuntimeEnvironment (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckActivityRuntimeEnvironment('SQLDict')

  def test_105_activityRuntimeEnvironmentSQLQueue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck ActivityRuntimeEnvironment (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckActivityRuntimeEnvironment('SQLQueue')

  def CheckSerializationTag(self, activity):
    organisation = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    self.tic()
    activity_tool = self.getActivityTool()
    result = activity_tool.getMessageList()
    self.assertEqual(len(result), 0)
    # First scenario: activate, distribute, activate, distribute
    # Create first activity and distribute: it must be distributed
    organisation.activate(activity=activity, serialization_tag='1').getTitle()
    self.commit()
    result = activity_tool.getMessageList()
    self.assertEqual(len(result), 1)
    activity_tool.distribute()
    result = activity_tool.getMessageList()
    self.assertEqual(len([x for x in result if x.processing_node == 0]), 1)
    # Create second activity and distribute: it must *NOT* be distributed
    organisation.activate(activity=activity, serialization_tag='1').getTitle()
    self.commit()
    result = activity_tool.getMessageList()
    self.assertEqual(len(result), 2)
    activity_tool.distribute()
    result = activity_tool.getMessageList()
    self.assertEqual(len([x for x in result if x.processing_node == 0]), 1) # Distributed message list len is still 1
    self.tic()
    result = activity_tool.getMessageList()
    self.assertEqual(len(result), 0)
    # Second scenario: activate, activate, distribute
    # Both messages must be distributed (this is different from regular tags)
    organisation.activate(activity=activity, serialization_tag='1', priority=2).getTitle()
    # Use a different method just so that SQLDict doesn't merge both activities prior to insertion.
    organisation.activate(activity=activity, serialization_tag='1', priority=1).getId()
    self.commit()
    result = activity_tool.getMessageList()
    self.assertEqual(len(result), 2)
    activity_tool.distribute()
    result = activity_tool.getMessageList()
    # at most 1 activity for a given serialization tag can be validated
    message, = [x for x in result if x.processing_node == 0]
    self.assertEqual(message.method_id, 'getId')
    # the other one is still waiting for validation
    message, = [x for x in result if x.processing_node == -1]
    self.assertEqual(message.method_id, 'getTitle')
    self.tic()
    result = activity_tool.getMessageList()
    self.assertEqual(len(result), 0)
    # Check that giving a None value to serialization_tag does not confuse
    # CMFActivity
    organisation.activate(activity=activity, serialization_tag=None).getTitle()
    self.tic()
    self.assertEqual(len(activity_tool.getMessageList()), 0)

  def test_106_checkSerializationTagSQLDict(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck serialization tag (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckSerializationTag('SQLDict')

  def test_107_checkSerializationTagSQLQueue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck serialization tag (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckSerializationTag('SQLQueue')

  def test_108_testAbsoluteUrl(self):
    # Tests that absolute_url works in activities. The URL generation is based
    # on REQUEST information when the method was activated.
    request = self.portal.REQUEST

    request.setServerURL('http', 'test.erp5.org', '9080')
    request.other['PARENTS'] = [self.portal.organisation_module]
    request.setVirtualRoot('virtual_root')

    calls = []
    def checkAbsoluteUrl(self):
      calls.append(self.absolute_url())
    Organisation.checkAbsoluteUrl = checkAbsoluteUrl

    try:
      o = self.portal.organisation_module.newContent(
                    portal_type='Organisation', id='test_obj')
      self.assertEquals(o.absolute_url(),
          'http://test.erp5.org:9080/virtual_root/test_obj')
      o.activate().checkAbsoluteUrl()
      
      # Reset server URL and virtual root before executing messages.
      # This simulates the case of activities beeing executed with different
      # REQUEST, such as TimerServer.
      request.setServerURL('https', 'anotherhost.erp5.org', '443')
      request.other['PARENTS'] = [self.app]
      request.setVirtualRoot('')
      # obviously, the object url is different
      self.assertEquals(o.absolute_url(),
          'https://anotherhost.erp5.org/%s/organisation_module/test_obj'
           % self.portal.getId())

      # but activities are executed using the previous request information
      self.flushAllActivities(loop_size=1000)
      self.assertEquals(calls, ['http://test.erp5.org:9080/virtual_root/test_obj'])
    finally:
      delattr(Organisation, 'checkAbsoluteUrl')

  def CheckMissingActivityContextObject(self, activity):
    """
      Check that a message whose context has ben deleted goes to -3
      processing_node.
      This must happen on first message execution, without any delay.
    """
    activity_tool = self.getActivityTool()
    container = self.getPortal().organisation_module
    organisation = container.newContent(portal_type='Organisation')
    self.tic()
    organisation.activate(activity=activity).getTitle()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 1)
    # Here, we delete the subobject using most low-level method, to avoid
    # pending activity to be removed.
    organisation_id = organisation.id
    container._delOb(organisation_id)
    del organisation # Avoid keeping a reference to a deleted object.
    self.commit()
    self.assertEqual(getattr(container, organisation_id, None), None)
    self.assertEqual(len(activity_tool.getMessageList()), 1)
    activity_tool.distribute()
    self.assertEqual([], activity_tool.getMessageList(activity=activity,
                                                      processing_node=-3))
    activity_tool.tic()
    self.assertEqual(1, len(activity_tool.getMessageList(activity=activity,
                                                         processing_node=-3)))

  def test_109_checkMissingActivityContextObjectSQLDict(self, quiet=0,
      run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck missing activity context object (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckMissingActivityContextObject('SQLDict')

  def test_110_checkMissingActivityContextObjectSQLQueue(self, quiet=0,
      run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck missing activity context object (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckMissingActivityContextObject('SQLQueue')

  def test_111_checkMissingActivityContextObjectSQLDict(self, quiet=0,
      run=run_all_test):
    """
      This is similar to tst 108, but here the object will be missing for an
      activity with a group_method_id.
    """
    if not run: return
    if not quiet:
      message = '\nCheck missing activity context object with ' \
                'group_method_id (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    activity_tool = self.getActivityTool()
    container = self.getPortalObject().organisation_module
    organisation = container.newContent(portal_type='Organisation')
    organisation_2 = container.newContent(portal_type='Organisation')
    self.tic()
    organisation.reindexObject()
    organisation_2.reindexObject()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    # Here, we delete the subobject using most low-level method, to avoid
    # pending activity to be removed.
    organisation_id = organisation.id
    container._delOb(organisation_id)
    del organisation # Avoid keeping a reference to a deleted object.
    self.commit()
    self.assertEqual(getattr(container, organisation_id, None), None)
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    activity_tool.distribute()
    self.assertEqual([], activity_tool.getMessageList(activity="SQLDict",
                                                      processing_node=-3))
    activity_tool.tic()
    message, = activity_tool.getMessageList()
    # The message excuted on "organisation_2" must have succeeded.
    self.assertEqual(message.processing_node, -3)

  def CheckLocalizerWorks(self, activity):
    FROM_STRING = 'Foo'
    TO_STRING = 'Bar'
    LANGUAGE = 'xx'
    def translationTest(context):
      from Products.ERP5Type.Message import Message
      context.setTitle(context.Base_translateString(FROM_STRING))
      context.setDescription(str(Message('erp5_ui', FROM_STRING)))
    portal = self.getPortalObject()
    portal.Localizer.erp5_ui.manage_addLanguage(LANGUAGE)
    # Add FROM_STRING to the message catalog
    portal.Localizer.erp5_ui.gettext(FROM_STRING)
    # ...and translate it.
    portal.Localizer.erp5_ui.message_edit(message=FROM_STRING,
      language=LANGUAGE, translation=TO_STRING, note='')
    organisation = portal.organisation_module.newContent(
      portal_type='Organisation')
    self.tic()
    Organisation.translationTest = translationTest
    try:
      REQUEST = organisation.REQUEST
      # Simulate what a browser would have sent to Zope
      REQUEST.environ['HTTP_ACCEPT_LANGUAGE'] = LANGUAGE
      organisation.activate(activity=activity).translationTest()
      self.commit()
      # Remove request parameter to check that it was saved at activate call
      # and restored at message execution.
      del REQUEST.environ['HTTP_ACCEPT_LANGUAGE']
      self.tic()
    finally:
      delattr(Organisation, 'translationTest')
    self.assertEqual(TO_STRING, organisation.getTitle())
    self.assertEqual(TO_STRING, organisation.getDescription())

  def test_112_checkLocalizerWorksSQLQueue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck Localizer works (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckLocalizerWorks('SQLQueue')

  def test_113_checkLocalizerWorksSQLDict(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck Localizer works (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.CheckLocalizerWorks('SQLDict')

  def testMessageContainsFailureTraceback(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck message contains failure traceback'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    portal = self.getPortalObject()
    activity_tool = self.getActivityTool()
    def checkMessage(message, exception_type):
      self.assertNotEqual(message.getExecutionState(), 1) # 1 == MESSAGE_EXECUTED
      self.assertEqual(message.exc_type, exception_type)
      self.assertNotEqual(message.traceback, None)
    # With Message.__call__
    # 1: activity context does not exist when activity is executed
    organisation = portal.organisation_module.newContent(portal_type='Organisation')
    self.tic()
    organisation.activate().getTitle() # This generates the mssage we want to test.
    self.commit()
    message_list = activity_tool.getMessageList()
    self.assertEqual(len(message_list), 1)
    message = message_list[0]
    portal.organisation_module._delOb(organisation.id)
    message(activity_tool)
    checkMessage(message, KeyError)
    activity_tool.manageCancel(message.object_path, message.method_id)
    # 2: activity method does not exist when activity is executed
    portal.organisation_module.activate().this_method_does_not_exist()
    self.commit()
    message_list = activity_tool.getMessageList()
    self.assertEqual(len(message_list), 1)
    message = message_list[0]
    message(activity_tool)
    checkMessage(message, AttributeError)
    activity_tool.manageCancel(message.object_path, message.method_id)

    # With ActivityTool.invokeGroup
    # 1: activity context does not exist when activity is executed
    organisation = portal.organisation_module.newContent(portal_type='Organisation')
    self.tic()
    organisation.activate().getTitle() # This generates the mssage we want to test.
    self.commit()
    message_list = activity_tool.getMessageList()
    self.assertEqual(len(message_list), 1)
    message = message_list[0]
    portal.organisation_module._delOb(organisation.id)
    activity_tool.invokeGroup('getTitle', [message], 'SQLDict', True)
    checkMessage(message, KeyError)
    activity_tool.manageCancel(message.object_path, message.method_id)
    # 2: activity method does not exist when activity is executed
    portal.organisation_module.activate().this_method_does_not_exist()
    self.commit()
    message_list = activity_tool.getMessageList()
    self.assertEqual(len(message_list), 1)
    message = message_list[0]
    activity_tool.invokeGroup('this_method_does_not_exist',
                              [message], 'SQLDict', True)
    checkMessage(message, KeyError)
    activity_tool.manageCancel(message.object_path, message.method_id)

    # Unadressed error paths (in both cases):
    #  3: activity commit raises
    #  4: activity raises

  def test_114_checkSQLQueueActivitySucceedsAfterActivityChangingSkin(self,
    quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck SQLQueue activity succeeds after an activity changing skin selection'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    portal = self.getPortalObject()
    activity_tool = self.getActivityTool()
    # Check that a reference script can be reached
    script_id = 'ERP5Site_reindexAll'
    self.assertTrue(getattr(portal, script_id, None) is not None)
    # Create a new skin selection
    skin_selection_name = 'test_114'
    portal.portal_skins.manage_skinLayers(add_skin=1, skinpath=[''], skinname=skin_selection_name)
    # Create a dummy document
    organisation = portal.organisation_module.newContent(portal_type='Organisation')
    self.tic()
    # Set custom methods to call as activities.
    def first(context):
      context.changeSkin(skin_selection_name)
      if getattr(context, script_id, None) is not None:
        raise Exception, '%s is not supposed to be found here.' % (script_id, )
    def second(context):
      # If the wrong skin is selected this will raise.
      getattr(context, script_id)
    Organisation.firstTest = first
    Organisation.secondTest = second
    try:
      organisation.activate(tag='foo', activity='SQLQueue').firstTest()
      organisation.activate(after_tag='foo', activity='SQLQueue').secondTest()
      self.commit()
      import gc
      gc.disable()
      self.tic()
      gc.enable()
      # Forcibly restore skin selection, otherwise getMessageList would only
      # emit a log when retrieving the ZSQLMethod.
      portal.changeSkin(None)
      self.assertEquals(len(activity_tool.getMessageList()), 0)
    finally:
      delattr(Organisation, 'firstTest')
      delattr(Organisation, 'secondTest')

  def test_115_checkProcessShutdown(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that no activity is executed after process_shutdown has been called'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    # Thread execution plan for this test:
    # main                             ActivityThread           ProcessShutdownThread
    # start ActivityThread             None                     None
    # wait for rendez_vous_lock        (run)                    None
    # wait for rendez_vous_lock        release rendez_vous_lock None
    # start ProcessShutdownThread      wait for activity_lock   None
    # release activity_lock            wait for activity_lock   internal wait
    # wait for activity_thread         (finish)                 internal wait
    # wait for process_shutdown_thread None                     (finish)
    # 
    # This test only checks that:
    # - activity tool can exit between 2 processable activity batches
    # - activity tool won't process activities after process_shutdown was called
    # - process_shutdown returns before Activity.tic()
    #   This is not perfect though, since it would require to have access to
    #   the waiting queue of CMFActivity's internal lock (is_running_lock) to
    #   make sure that it's what is preventing process_shutdown from returning.
    portal = self.getPortalObject()
    activity_tool = self.getActivityTool()
    organisation = portal.organisation_module.newContent(portal_type='Organisation')
    self.tic()
    activity_event = threading.Event()
    rendez_vous_event = threading.Event()
    def waitingActivity(context):
      # Inform test that we arrived at rendez-vous.
      rendez_vous_event.set()
      # When this event is available, it means test has called process_shutdown.
      activity_event.wait()
    from Products.CMFActivity.Activity.SQLDict import SQLDict
    original_dequeue = SQLDict.dequeueMessage
    queue_tic_test_dict = {}
    def dequeueMessage(self, activity_tool, processing_node):
      # This is a one-shot method, revert after execution
      SQLDict.dequeueMessage = original_dequeue
      result = self.dequeueMessage(activity_tool, processing_node)
      queue_tic_test_dict['isAlive'] = process_shutdown_thread.isAlive()
      return result
    SQLDict.dequeueMessage = dequeueMessage
    Organisation.waitingActivity = waitingActivity
    try:
      # Use SQLDict with no group method so that both activities won't be
      # executed in the same batch, letting activity tool a chance to check
      # if execution should stop processing activities.
      organisation.activate(activity='SQLDict', tag='foo').waitingActivity()
      organisation.activate(activity='SQLDict', after_tag='foo').getTitle()
      self.commit()
      self.assertEqual(len(activity_tool.getMessageList()), 2)
      activity_tool.distribute()
      self.commit()

      # Start a tic in another thread, so they can meet at rendez-vous.
      class ActivityThread(threading.Thread):
        def run(self):
          # Call changeskin, since skin selection depend on thread id, and we
          # are in a new thread.
          activity_tool.changeSkin(None)
          activity_tool.tic()
      activity_thread = ActivityThread()
      # Do not try to outlive main thread.
      activity_thread.setDaemon(True)
      # Call process_shutdown in yet another thread because it will wait for
      # running activity to complete before returning, and we need to unlock
      # activity *after* calling process_shutdown to make sure the next
      # activity won't be executed.
      class ProcessShutdownThread(threading.Thread):
        def run(self):
          activity_tool.process_shutdown(3, 0)
      process_shutdown_thread = ProcessShutdownThread()
      # Do not try to outlive main thread.
      process_shutdown_thread.setDaemon(True)

      activity_thread.start()
      # Wait at rendez-vous for activity to arrive.
      rendez_vous_event.wait()
      # Initiate shutdown
      process_shutdown_thread.start()
      try:
        # Let waiting activity finish and wait for thread exit
        activity_event.set()
        activity_thread.join()
        process_shutdown_thread.join()
        # Check that there is still one activity pending
        message_list = activity_tool.getMessageList()
        self.assertEqual(len(message_list), 1)
        self.assertEqual(message_list[0].method_id, 'getTitle')
        # Check that process_shutdown_thread was still runing when Queue_tic returned.
        self.assertTrue(queue_tic_test_dict.get('isAlive'), repr(queue_tic_test_dict))
        # Call tic in foreground. This must not lead to activity execution.
        activity_tool.tic()
        self.assertEqual(len(activity_tool.getMessageList()), 1)
      finally:
        # Put activity tool back in a working state
        from Products.CMFActivity.ActivityTool import cancelProcessShutdown
        try:
          cancelProcessShutdown()
        except StandardException:
          # If something failed in process_shutdown, shutdown lock might not
          # be taken in CMFActivity, leading to a new esception here hiding
          # test error.
          pass
    finally:
      delattr(Organisation, 'waitingActivity')
      SQLDict.dequeueMessage = original_dequeue

  def test_hasActivity(self):
    active_object = self.portal.organisation_module.newContent(
                                            portal_type='Organisation')
    active_process = self.portal.portal_activities.newActiveProcess()
    self.tic()

    self.assertFalse(active_object.hasActivity())
    self.assertFalse(active_process.hasActivity())

    def test(obj, **kw):
      for activity in ('SQLDict', 'SQLQueue'):
        active_object.activate(activity=activity, **kw).getTitle()
        self.commit()
        self.assertTrue(obj.hasActivity(), activity)
        self.tic()
        self.assertFalse(obj.hasActivity(), activity)

    test(active_object)
    test(active_process, active_process=active_process)
    test(active_process, active_process=active_process.getPath())

  def test_active_object_hasActivity_does_not_catch_exceptions(self):
    """
    Some time ago, hasActivity was doing a silent try/except, and this was
    a possible disaster for some projects. Here we make sure that if the 
    SQL request fails, then the exception is not ignored
    """
    active_object = self.portal.organisation_module.newContent(
                                            portal_type='Organisation')
    self.tic()
    self.assertFalse(active_object.hasActivity())

    # Monkey patch to induce any error artificially in the sql connection.
    def query(self, query_string,*args, **kw):
      raise ValueError

    from Products.ZMySQLDA.db import DB
    DB.original_query = DB.query
    try:
      active_object.activate().getTitle()
      self.commit()
      self.assertTrue(active_object.hasActivity())
      # Make the sql request not working
      DB.original_query = DB.query
      DB.query = query
      # Make sure then that hasActivity fails
      self.assertRaises(ValueError, active_object.hasActivity)
    finally:
      DB.query = DB.original_query
      del DB.original_query

  def test_MAX_MESSAGE_LIST_SIZE_SQLQueue(self):
    from Products.CMFActivity.Activity import SQLQueue
    old_MAX_MESSAGE_LIST_SIZE = SQLQueue.MAX_MESSAGE_LIST_SIZE
    SQLQueue.MAX_MESSAGE_LIST_SIZE = 3

    try:
      global call_count
      call_count = 0
      def dummy_counter(self):
        global call_count
        call_count += 1

      Organisation.dummy_counter = dummy_counter
      o = self.portal.organisation_module.newContent(portal_type='Organisation',)

      for i in range(10):
        o.activate(activity='SQLQueue').dummy_counter()
        
      self.flushAllActivities()
      self.assertEquals(call_count, 10)
    finally:
      SQLQueue.MAX_MESSAGE_LIST_SIZE = old_MAX_MESSAGE_LIST_SIZE
      del Organisation.dummy_counter

  def test_MAX_MESSAGE_LIST_SIZE_SQLDict(self):
    from Products.CMFActivity.Activity import SQLDict
    old_MAX_MESSAGE_LIST_SIZE = SQLDict.MAX_MESSAGE_LIST_SIZE
    SQLDict.MAX_MESSAGE_LIST_SIZE = 3

    try:
      global call_count
      call_count = 0
      def dummy_counter(self):
        global call_count
        call_count += 1

      o = self.portal.organisation_module.newContent(portal_type='Organisation',)

      for i in range(10):
        method_name = 'dummy_counter_%s' % i
        setattr(Organisation, method_name, dummy_counter)
        getattr(o.activate(activity='SQLDict'), method_name)()
        
      self.flushAllActivities()
      self.assertEquals(call_count, 10)
    finally:
      SQLDict.MAX_MESSAGE_LIST_SIZE = old_MAX_MESSAGE_LIST_SIZE
      for i in range(10):
        method_name = 'dummy_counter_%s' % i
        delattr(Organisation, method_name)

  def test_115_TestSerializationTagSQLDictPreventsParallelExecution(self, quiet=0, run=run_all_test):
    """
      Test if there are multiple activities with the same serialization tag,
      then serialization tag guarantees that only one of the same serialization
      tagged activities can be processed at the same time.
    """
    if not run: return
    if not quiet:
      message = '\n'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    from Products.CMFActivity import ActivityTool

    portal = self.getPortal()
    activity_tool = portal.portal_activities
    self.tic()

    # Add 6 activities
    portal.organisation_module.activate(activity='SQLDict', tag='', serialization_tag='test_115').getId()
    self.commit()
    portal.organisation_module.activate(activity='SQLDict', serialization_tag='test_115').getTitle()
    self.commit()
    portal.organisation_module.activate(activity='SQLDict', tag='tag_1', serialization_tag='test_115').getId()
    self.commit()
    portal.person_module.activate(activity='SQLDict', serialization_tag='test_115').getId()
    self.commit()
    portal.person_module.activate(activity='SQLDict', tag='tag_2').getId()
    self.commit()
    portal.organisation_module.activate(activity='SQLDict', tag='', serialization_tag='test_115').getId()
    self.commit()

    # distribute and assign them to 3 nodes
    activity_tool.distribute()
    self.commit()

    from Products.CMFActivity import ActivityTool
    activity = ActivityTool.activity_dict['SQLDict']
    activity.getProcessableMessageList(activity_tool, 1)
    self.commit()
    activity.getProcessableMessageList(activity_tool, 2)
    self.commit()
    activity.getProcessableMessageList(activity_tool, 3)
    self.commit()

    result = activity._getMessageList(activity_tool)
    try:
      self.assertEqual(len([message
                            for message in result
                            if (message.processing_node>0 and
                                message.processing==1 and
                                message.serialization_tag=='test_115')]),
                       1)

      self.assertEqual(len([message
                            for message in result
                            if (message.processing_node==-1 and
                                message.serialization_tag=='test_115')]),
                       3)

      self.assertEqual(len([message
                            for message in result
                            if (message.processing_node>0 and
                                message.processing==1 and
                                message.serialization_tag=='')]),
                       1)
    finally:
      # Clear activities from all nodes
      activity_tool.SQLBase_delMessage(table=SQLDict.sql_table,
                                       uid=[message.uid for message in result])
      self.commit()

  def test_116_RaiseInCommitBeforeMessageExecution(self):
    """
      Test behaviour of CMFActivity when the commit just before message
      execution fails. In particular, CMFActivity should restart the
      activities it selected (processing=1) instead of ignoring them forever.
    """
    processed = []
    activity_tool = self.portal.portal_activities
    activity_tool.__class__.doSomething = processed.append
    try:
      for activity in 'SQLDict', 'SQLQueue':
        activity_tool.activate(activity=activity).doSomething(activity)
        self.commit()
        # Make first commit in dequeueMessage raise
        registerFailingTransactionManager()
        self.assertRaises(CommitFailed, activity_tool.tic)
        # Normally, the request stops here and Zope aborts the transaction
        self.abort()
        self.assertEqual(processed, [])
        # Activity is already in 'processing=1' state. Check tic reselects it.
        activity_tool.tic()
        self.assertEqual(processed, [activity])
        del processed[:]
    finally:
      del activity_tool.__class__.doSomething

  def test_117_PlacelessDefaultReindexParameters(self):
    """
      Test behaviour of PlacelessDefaultReindexParameters.
    """
    portal = self.portal
    
    # Make a new Person object to make sure that the portal type
    # is migrated to an instance of a portal type class, otherwise
    # the portal type may generate an extra active object.
    portal.person_module.newContent(portal_type='Person')
    self.tic()

    original_reindex_parameters = portal.getPlacelessDefaultReindexParameters()
    if original_reindex_parameters is None:
      original_reindex_parameters = {}
    
    tag = 'SOME_RANDOM_TAG'      
    activate_kw = original_reindex_parameters.get('activate_kw', {}).copy()
    activate_kw['tag'] = tag 
    portal.setPlacelessDefaultReindexParameters(activate_kw=activate_kw, \
                                                **original_reindex_parameters)
    current_default_reindex_parameters = portal.getPlacelessDefaultReindexParameters()
    self.assertEquals({'activate_kw': {'tag': tag}}, \
                       current_default_reindex_parameters)
    person = portal.person_module.newContent(portal_type='Person')
    self.commit()
    # as we specified it in setPlacelessDefaultReindexParameters we should have
    # an activity for this tags
    self.assertEquals(1, portal.portal_activities.countMessageWithTag(tag))
    self.tic()
    self.assertEquals(0, portal.portal_activities.countMessageWithTag(tag))
    
    # restore originals ones
    portal.setPlacelessDefaultReindexParameters(**original_reindex_parameters)
    person = portal.person_module.newContent(portal_type='Person')
    # .. now no messages with this tag should apper
    self.assertEquals(0, portal.portal_activities.countMessageWithTag(tag))    

  def TryNotificationSavedOnEventLogWhenNotifyUserRaises(self, activity):
    activity_tool = self.getActivityTool()
    self.tic()
    obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    self.tic()
    original_notifyUser = Message.notifyUser
    def failSendingEmail(self, *args, **kw):
      raise MailHostError, 'Mail is not sent'
    Message.notifyUser = failSendingEmail
    class ActivityUnitTestError(Exception):
      pass
    activity_unit_test_error = ActivityUnitTestError()
    def failingMethod(self):
      raise activity_unit_test_error
    Organisation.failingMethod = failingMethod
    self._catch_log_errors(ignored_level=sys.maxint) 

    try:
      import traceback
      obj.activate(activity=activity, priority=6).failingMethod()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)   
      message_list = activity_tool.getMessageList()
      self.assertEqual(len(message_list), 1)
      message = message_list[0]
      logged_errors = []
      logged_errors = self.logged
      self.commit()
      for log_record in self.logged:
        if log_record.name == 'ActivityTool' and log_record.levelname == 'WARNING':
          type, value, trace = log_record.exc_info
      self.commit()
      self.assertTrue(activity_unit_test_error is value)
    finally:
      self._ignore_log_errors()
      Message.notifyUser = original_notifyUser
      delattr(Organisation, 'failingMethod')

  def test_118_userNotificationSavedOnEventLogWhenNotifyUserRaisesWithSQLDict(self, quiet=0, run=run_all_test):
    """
      Check the error is saved on event log even if the mail notification is not sent.
    """
    if not run: return
    if not quiet:
      message = '\nCheck the error is saved on event log even if the mail notification is not sent (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryNotificationSavedOnEventLogWhenNotifyUserRaises('SQLDict')

  def test_119_userNotificationSavedOnEventLogWhenNotifyUserRaisesWithSQLQueue(self, quiet=0, run=run_all_test):
    """
      Check the error is saved on event log even if the mail notification is not sent.
    """
    if not run: return
    if not quiet:
      message = '\nCheck the error is saved on event log even if the mail notification is not sent (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryNotificationSavedOnEventLogWhenNotifyUserRaises('SQLQueue') 

  def TryUserMessageContainingNoTracebackIsStillSent(self, activity):
    portal = self.getPortalObject()
    activity_tool = self.getActivityTool()
    # With Message.__call__
    # 1: activity context does not exist when activity is executed
    self.tic()
    obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    self.tic()
    notification_done = []
    def fake_notifyUser(self, *args, **kw):
      notification_done.append(True)
      self.traceback = None
    original_notifyUser = Message.notifyUser
    def failingMethod(self):
      raise ValueError, "This method always fail"
    Message.notifyUser = fake_notifyUser
    Organisation.failingMethod = failingMethod
    try:
      obj.activate(activity=activity).failingMethod()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      message_list = activity_tool.getMessageList()
      self.assertEqual(len(message_list), 1)
      self.assertEqual(len(notification_done), 1)
      message = message_list[0]
      self.assertEqual(message.traceback, None)
      message(activity_tool)
      activity_tool.manageCancel(message.object_path, message.method_id)
    finally:
      Message.notifyUser = original_notifyUser
      delattr(Organisation, 'failingMethod')    

  def test_120_sendMessageWithNoTracebackWithSQLQueue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that message with no traceback is still sent (SQLQueue)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryUserMessageContainingNoTracebackIsStillSent('SQLQueue')

  def test_121_sendMessageWithNoTracebackWithSQLDict(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that message with no traceback is still sent (SQLDict)'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryUserMessageContainingNoTracebackIsStillSent('SQLDict')
  
  def TryNotificationSavedOnEventLogWhenSiteErrorLoggerRaises(self, activity):
    # Make sure that no active object is installed.
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities(keep=0)

    # Need an object.
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = organisation_module._getOb(self.company_id)
    self.commit()
    self.flushAllActivities(silent = 1, loop_size = 10)
    self.assertEquals(len(activity_tool.getMessageList()), 0)
    class ActivityUnitTestError(Exception):
      pass
    activity_unit_test_error = ActivityUnitTestError()
    def failingMethod(self):
      raise activity_unit_test_error
    from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
    SiteErrorLog.original_raising = SiteErrorLog.raising

    # Monkey patch Site Error to induce conflict errors artificially.
    def raising(self, info):
      from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
      raise AttributeError
      return self.original_raising(info)
    from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
    SiteErrorLog.original_raising = SiteErrorLog.raising
    SiteErrorLog.raising = raising
    Organisation.failingMethod = failingMethod
    self._catch_log_errors(ignored_level=sys.maxint)

    try:
      o.activate(activity = activity).failingMethod()
      self.commit()
      self.assertEquals(len(activity_tool.getMessageList()), 1)
      self.flushAllActivities(silent = 1)
      SiteErrorLog.raising = SiteErrorLog.original_raising
      logged_errors = self.logged
      self.commit()
      for log_record in self.logged:
        if log_record.name == 'ActivityTool' and log_record.levelname == 'WARNING':
          type, value, trace = log_record.exc_info     
      self.assertTrue(activity_unit_test_error is value)
    finally:
      self._ignore_log_errors()
      SiteErrorLog.raising = SiteErrorLog.original_raising
      delattr(Organisation, 'failingMethod')
      del SiteErrorLog.original_raising

  def test_122_userNotificationSavedOnEventLogWhenSiteErrorLoggerRaisesWithSQLDict(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that message not saved in site error logger is not lost'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryNotificationSavedOnEventLogWhenSiteErrorLoggerRaises('SQLDict')

  def test_123_userNotificationSavedOnEventLogWhenSiteErrorLoggerRaisesWithSQLQueue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nCheck that message not saved in site error logger is not lost'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    self.TryNotificationSavedOnEventLogWhenSiteErrorLoggerRaises('SQLQueue')

  def test_124_checkConflictErrorAndNoRemainingActivities(self):
    """
    When an activity creates several activities, make sure that all newly
    created activities are not commited if there is ZODB Conflict error
    """
    from Products.CMFActivity.Activity import SQLQueue
    old_MAX_MESSAGE_LIST_SIZE = SQLQueue.MAX_MESSAGE_LIST_SIZE
    SQLQueue.MAX_MESSAGE_LIST_SIZE = 1
    try:
      activity_tool = self.getPortal().portal_activities
      def doSomething(self):
        self.serialize()
        self.activate(activity='SQLQueue').getId()
        self.activate(activity='SQLQueue').getTitle()
        conn = self._p_jar
        tid = self._p_serial
        oid = self._p_oid
        try:
          conn.db().invalidate({oid: tid})
        except TypeError:
          conn.db().invalidate(tid, {oid: tid})
        
      activity_tool.__class__.doSomething = doSomething
      activity_tool.activate(activity='SQLQueue').doSomething()
      self.commit()
      activity_tool.tic()
      message_list = activity_tool.getMessageList()
      self.assertEquals(['doSomething'],[x.method_id for x in message_list])
      activity_tool.manageClearActivities(keep=0)
    finally:
      SQLQueue.MAX_MESSAGE_LIST_SIZE = old_MAX_MESSAGE_LIST_SIZE

  def test_125_CheckDistributeWithSerializationTagAndGroupMethodId(self):
    activity_tool = self.portal.portal_activities
    obj1 = activity_tool.newActiveProcess()
    obj2 = activity_tool.newActiveProcess()
    self.tic()
    group_method_call_list = []
    def doSomething(self, message_list):
      group_method_call_list.append(sorted((ob.getPath(), args, kw)
                                           for ob, args, kw, _ in message_list))
    activity_tool.__class__.doSomething = doSomething
    try:
      for activity in 'SQLDict', 'SQLQueue':
        activity_kw = dict(activity=activity, serialization_tag=self.id(),
                           group_method_id='portal_activities/doSomething')
        obj1.activate(**activity_kw).dummy(1, x=None)
        obj2.activate(**activity_kw).dummy(2, y=None)
        self.commit()
        activity_tool.distribute()
        activity_tool.tic()
        self.assertEqual(group_method_call_list.pop(),
                         sorted([(obj1.getPath(), (1,), dict(x=None)),
                                 (obj2.getPath(), (2,), dict(y=None))]))
        self.assertFalse(group_method_call_list)
        self.assertFalse(activity_tool.getMessageList())
        obj1.activate(priority=2, **activity_kw).dummy1(1, x=None)
        obj1.activate(priority=1, **activity_kw).dummy2(2, y=None)
        message1 = obj1.getPath(), (1,), dict(x=None)
        message2 = obj1.getPath(), (2,), dict(y=None)
        self.commit()
        activity_tool.distribute()
        self.assertEqual(len(activity_tool.getMessageList()), 2)
        activity_tool.tic()
        self.assertEqual(group_method_call_list.pop(),
                         dict(SQLDict=[message2],
                              SQLQueue=[message1, message2])[activity])
        self.assertFalse(group_method_call_list)
        self.assertFalse(activity_tool.getMessageList())
    finally:
      del activity_tool.__class__.doSomething

  def test_126_beforeCommitHook(self):
    """
    Check it is possible to activate an object from a before commit hook
    """
    def doSomething(person):
      person.activate(activity='SQLDict')._setFirstName('John')
      person.activate(activity='SQLQueue')._setLastName('Smith')
    person = self.portal.person_module.newContent()
    transaction.get().addBeforeCommitHook(doSomething, (person,))
    self.tic()
    self.assertEqual(person.getTitle(), 'John Smith')

  def test_connection_migration(self):
    """
    Make sure the cmf_activity_sql_connection is automatically migrated from
    the ZMySQLDA Connection class to ActivityConnection
    """
    # replace the activity connector with a standard ZMySQLDA one
    portal = self.portal
    activity_tool = portal.portal_activities
    stdconn = self.portal.cmf_activity_sql_connection
    portal._delObject('cmf_activity_sql_connection')
    portal.manage_addProduct['ZMySQLDA'].manage_addZMySQLConnection(
        stdconn.id,
        stdconn.title,
        stdconn.connection_string,
    )
    oldconn = portal.cmf_activity_sql_connection
    self.assertEquals(oldconn.meta_type, 'Z MySQL Database Connection')
    # de-initialize and check that migration of the connection happens
    # automatically
    Products.CMFActivity.ActivityTool.is_initialized = False
    activity_tool.activate(activity='SQLQueue').getId()
    self.tic()
    newconn = portal.cmf_activity_sql_connection
    self.assertEquals(newconn.meta_type, 'CMFActivity Database Connection')

  def test_connection_installable(self):
    """
    Test if the cmf_activity_sql_connector can be installed
    """
    # delete the activity connection
    portal = self.portal
    activity_tool = portal.portal_activities
    stdconn = self.portal.cmf_activity_sql_connection
    portal._delObject('cmf_activity_sql_connection')
    # check the installation form can be rendered
    portal.manage_addProduct['CMFActivity'].connectionAdd(
        portal.REQUEST
    )
    # check it can be installed
    portal.manage_addProduct['CMFActivity'].manage_addActivityConnection(
        stdconn.id,
        stdconn.title,
        stdconn.connection_string
    )
    newconn = portal.cmf_activity_sql_connection
    self.assertEquals(newconn.meta_type, 'CMFActivity Database Connection')

  def test_connection_sortkey(self):
    """
    Check that SQL connection has properly initialized sort key,
    even when its container (ZODB connection) is reused by another thread.
    """
    def sortKey():
      app = ZopeTestCase.app()
      try:
        c = app[self.getPortalName()].cmf_activity_sql_connection()
        return app._p_jar, c._access_db('sortKey', (), {})
      finally:
        ZopeTestCase.close(app)
    jar, sort_key = sortKey()
    self.assertNotEqual(1, sort_key)
    result = []
    t = threading.Thread(target=lambda: result.extend(sortKey()))
    t.daemon = True
    t.start()
    t.join()
    self.assertTrue(result[0] is jar)
    self.assertEqual(result[1], sort_key)

  def test_onErrorCallback(self):
    activity_tool = self.portal.portal_activities
    obj = activity_tool.newActiveProcess()
    self.tic()
    def _raise(exception): # I wish exceptions are callable raising themselves
      raise exception
    def doSomething(self, conflict_error, cancel):
      self.activity_count += 1
      error = ConflictError() if conflict_error else Exception()
      def onError(exc_type, exc_value, traceback):
        assert exc_value is error
        env = self.getActivityRuntimeEnvironment()
        weakref_list.extend(map(weakref.ref, (env, env._message)))
        self.on_error_count += 1
        return cancel
      self.getActivityRuntimeEnvironment().edit(on_error_callback=onError)
      if not self.on_error_count:
        if not conflict_error:
          raise error
        transaction.get().addBeforeCommitHook(_raise, (error,))
    obj.__class__.doSomething = doSomething
    try:
      for activity in 'SQLDict', 'SQLQueue':
        for conflict_error in False, True:
          weakref_list = []
          obj.activity_count = obj.on_error_count = 0
          obj.activate(activity=activity).doSomething(conflict_error, True)
          self.tic()
          self.assertEqual(obj.activity_count, 0)
          self.assertEqual(obj.on_error_count, 1)
          gc.collect()
          self.assertEqual([x() for x in weakref_list], [None, None])
          weakref_list = []
          obj.activate(activity=activity).doSomething(conflict_error, False)
          obj.on_error_count = 0
          self.tic()
          self.assertEqual(obj.activity_count, 1)
          self.assertEqual(obj.on_error_count, 1)
          gc.collect()
          self.assertEqual([x() for x in weakref_list], [None, None])
    finally:
      del obj.__class__.doSomething

  def test_duplicateGroupedMessage(self):
    activity_tool = self.portal.portal_activities
    obj = activity_tool.newActiveProcess()
    obj.reindexObject(activate_kw={'tag': 'foo', 'after_tag': 'bar'})
    self.commit()
    invoked = []
    def invokeGroup(self, *args):
      invoked.append(len(args[1]))
      return ActivityTool_invokeGroup(self, *args)
    ActivityTool_invokeGroup = activity_tool.__class__.invokeGroup
    try:
      activity_tool.__class__.invokeGroup = invokeGroup
      self.tic()
    finally:
      activity_tool.__class__.invokeGroup = ActivityTool_invokeGroup
    self.assertEqual(invoked, [1])

  def test_mergeParent(self):
    category_tool = self.portal.portal_categories
    # Test data:     c0
    #               /  \
    #             c1    c2
    #            /  \   |
    #           c3  c4  c5
    c = [category_tool.newContent()]
    for i in xrange(5):
      c.append(c[i//2].newContent())
    self.tic()
    def activate(i, priority=1, **kw):
      kw.setdefault('merge_parent', c[0].getPath())
      c[i].activate(priority=priority, **kw).doSomething()
    def check(*expected):
      self.tic()
      self.assertEquals(tuple(invoked), expected)
      del invoked[:]
    invoked = []
    def doSomething(self):
      invoked.append(c.index(self))
    Base.doSomething = doSomething
    try:
      for t in (0, 1), (0, 4, 2), (1, 0, 5), (3, 2, 0):
        for p, i in enumerate(t):
          activate(i, p)
        check(0)
      activate(1, 0); activate(5, 1); check(1, 5)
      activate(3, 0); activate(1, 1); check(1)
      activate(2, 0); activate(1, 1); activate(4, 2); check(2, 1)
      activate(4, 0); activate(5, 1); activate(3, 2); check(4, 5, 3)
      activate(3, 0, merge_parent=c[1].getPath()); activate(0, 1); check(3, 0)
      # Following test shows that a child can be merged with a parent even if
      # 'merge_parent' is not specified. This can't be avoided without loading
      # all found duplicates, which would be bad for performance.
      activate(0, 0); activate(4, 1, merge_parent=None); check(0)
    finally:
      del Base.doSomething
    def activate(i, priority=1, **kw):
      c[i].activate(group_method_id='portal_categories/invokeGroup',
                    merge_parent=c[(i-1)//2 or i].getPath(),
                    priority=priority, **kw).doSomething()
    def invokeGroup(self, message_list):
      invoked.append(sorted(c.index(m[0]) for m in message_list))
    category_tool.__class__.invokeGroup = invokeGroup
    try:
      activate(5, 0); activate(1, 1); check([1, 5])
      activate(4, 0); activate(1, 1); activate(2, 0); check([1, 2])
      activate(1, 0); activate(5, 0); activate(3, 1); check([1, 5])
      for p, i in enumerate((5, 3, 2, 1, 4)):
        activate(i, p, group_id=str(2 != i != 5))
      check([2], [1])
      for cost in 0.3, 0.1:
        activate(2, 0, group_method_cost=cost)
        activate(3, 1);  activate(4, 2); activate(1, 3)
        check([1, 2])
    finally:
      del category_tool.__class__.invokeGroup
    category_tool._delObject(c[0].getId())
    self.tic()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCMFActivity))
  return suite

