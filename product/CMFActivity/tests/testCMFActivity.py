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

import inspect
import unittest

from Products.ERP5Type.tests.utils import LogInterceptor
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.Base import Base
from Products.CMFActivity.Activity.SQLBase import INVOKE_ERROR_STATE
from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
from Products.CMFActivity.Activity.SQLDict import SQLDict
import Products.CMFActivity.ActivityTool
from Products.CMFActivity.Errors import ActivityPendingError, ActivityFlushError
from erp5.portal_type import Organisation
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from ZODB.POSException import ConflictError
from DateTime import DateTime
from Products.CMFActivity.ActivityTool import Message
from _mysql_exceptions import OperationalError
from Products.ZMySQLDA.db import DB
from sklearn.externals.joblib.hashing import hash as joblib_hash
import gc
import random
import threading
import weakref
import transaction
from Products.CMFActivity.ActivityTool import getCurrentNode, getServerAddress
from App.config import getConfiguration
from asyncore import socket_map
import socket

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
    return ('erp5_base', 'erp5_joblib')

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

  def login(self):
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
    self.assertEqual(self.title1,organisation.getTitle())
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),1)
    portal.portal_activities.manageCancel(organisation.getPhysicalPath(),'_setTitle')
    # Needed so that the message are removed from the queue
    self.commit()
    self.assertEqual(self.title1,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),1)
    portal.portal_activities.manageInvoke(organisation.getPhysicalPath(),'_setTitle')
    # Needed so that the message are removed from the queue
    self.commit()
    self.assertEqual(self.title2,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)

  def DeferredSetTitleActivity(self, activity):
    """
    We check that the title is changed only after that
    the activity was called
    """
    portal = self.getPortal()
    organisation = portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
    self.assertEqual(self.title1,organisation.getTitle())
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    self.commit()
    self.assertEqual(self.title1,organisation.getTitle())
    portal.portal_activities.tic()
    self.assertEqual(self.title2,organisation.getTitle())
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)

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
    self.assertEqual(0,organisation.getFoobar())
    organisation.activate(activity=activity).setFoobar()
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),1)
    portal.portal_activities.tic()
    self.assertEqual(1,organisation.getFoobar())
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)
    organisation.activate(activity=activity).setFoobar()
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),1)
    portal.portal_activities.manageInvoke(organisation.getPhysicalPath(),'setFoobar')
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)
    self.assertEqual(2,organisation.getFoobar())

  def TryFlushActivity(self, activity):
    """
    Check the method flush
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
    organisation.activate(activity=activity)._setTitle(self.title2)
    organisation.flushActivity(invoke=1)
    self.assertEqual(organisation.getTitle(),self.title2)
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)
    self.assertEqual(organisation.getTitle(),self.title2)
    # Try again with different commit order
    organisation._setTitle(self.title1)
    organisation.activate(activity=activity)._setTitle(self.title2)
    self.commit()
    organisation.flushActivity(invoke=1)
    self.assertEqual(len(message_list),0)
    self.assertEqual(organisation.getTitle(),self.title2)
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
    self.assertEqual(len(message_list),0)
    self.assertEqual(organisation.getTitle(),self.title2)

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
    self.assertEqual(len(message_list),0)
    self.assertEqual(organisation.getTitle(),self.title1)
    self.assertEqual(organisation.getDescription(),self.title1)

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
    self.assertEqual(len(message_list),0)
    self.assertEqual(organisation.getTitle(),self.title1)
    self.assertEqual(organisation.getDescription(),self.title1)

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
    self.assertEqual(len(message_list),0)
    self.assertEqual(organisation.getTitle(),self.title1)
    self.assertEqual(organisation.getDescription(),self.title1)

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
    self.assertEqual(len(message_list),1)
    portal.portal_activities.tic()
    # XXX HERE WE SHOULD USE TIME SHIFT IN ORDER TO SIMULATE MULTIPLE TICS
    # Test if there is still the message after it crashed
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),1)
    portal.portal_activities.manageCancel(organisation.getPhysicalPath(),'crashThisActivity')
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)

  def DeferredSetTitleWithRenamedObject(self, activity):
    """
    make sure that it is impossible to rename an object
    if some activities are still waiting for this object
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
    self.assertEqual(self.title1,organisation.getTitle())
    organisation.activate(activity=activity)._setTitle(self.title2)
    # Needed so that the message are commited into the queue
    self.commit()
    self.assertEqual(self.title1,organisation.getTitle())
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
    self.assertEqual(self.title1,organisation.getTitle())
    organisation.activate(activity=activity,active_process=active_process).getTitle()
    # Needed so that the message are commited into the queue
    self.commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    self.assertEqual(self.title1,organisation.getTitle())
    result = active_process.getResultList()[0]
    self.assertEqual(result.method_id , 'getTitle')
    self.assertEqual(result.result , self.title1)
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)

  def TryActiveProcessWithResultDict(self, activity):
    """
    Try to store the result inside an active process using result list
    """
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    organisation._setTitle(self.title1)
    active_process = portal.portal_activities.newActiveProcess()
    self.assertEqual(self.title1,organisation.getTitle())

    # Post SQLjoblib tasks with explicit signature 
    organisation.activate(activity=activity,active_process=active_process, signature=1).getTitle()
    organisation.activate(activity=activity,active_process=active_process, signature=2).getTitle()
    organisation.activate(activity=activity,active_process=active_process, signature=3).getTitle()
    
    self.commit()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()
    result_dict = active_process.getResultDict()
    result = result_dict[1]
    self.assertEqual(result_dict[1].method_id, 'getTitle')
    self.assertEqual(result.result , self.title1)
    result = result_dict[2]
    self.assertEqual(result_dict[2].method_id, 'getTitle')
    self.assertEqual(result.result , self.title1)
    result = result_dict[3]
    self.assertEqual(result_dict[3].method_id, 'getTitle')
    self.assertEqual(result.result , self.title1)
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),0)


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
    self.assertEqual(o.getTitle(), 'a')
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
    self.assertEqual(o.getTitle(), 'acb')

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
    self.assertEqual(o.getTitle(), '?')
    self.tic()

    o.activate(after_tag = 'toto', activity = activity).setTitle('b')
    o.activate(tag = 'toto', activity = activity).setTitle('a')
    self.tic()
    self.assertEqual(o.getTitle(), 'b')

    o.setDefaultActivateParameterDict({'tag': 'toto'})
    def titi(self):
      self.setCorporateName(self.getTitle() + 'd')
    o.__class__.titi = titi
    o.activate(after_tag_and_method_id=('toto', 'setTitle'), activity = activity).titi()
    o.activate(activity = activity).setTitle('c')
    self.tic()
    self.assertEqual(o.getCorporateName(), 'cd')

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
    self.assertEqual(o.getTitle(), '?')
    self.assertEqual(o.getDescription(), '?')
    self.tic()

    o.activate(after_tag = 'toto', activity = activity).setDescription('b')
    o.activate(tag = 'toto', activity = activity).setTitle('a')
    self.commit()
    tool = self.getActivityTool()
    self.assertRaises(ActivityFlushError,tool.manageInvoke,o.getPath(),'setDescription')
    tool.manageInvoke(o.getPath(),'setTitle')
    self.commit()
    self.assertEqual(o.getTitle(), 'a')
    self.assertEqual(o.getDescription(), '?')
    self.tic()
    self.assertEqual(len(tool.getMessageList()),0)
    self.assertEqual(o.getTitle(), 'a')
    self.assertEqual(o.getDescription(), 'b')

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
    self.assertEqual(o.getTitle(), '?')
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
    self.assertEqual(o.getTitle(), 'cb')

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
    self.assertEqual(o.getTitle(), 'last')

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
    self.assertEqual(o.getTitle(), '?')
    self.assertEqual(portal_activities.countMessageWithTag('toto'), 1)
    self.tic()
    self.assertEqual(o.getTitle(), 'a')
    self.assertEqual(portal_activities.countMessageWithTag('toto'), 0)

  def TryConflictErrorsWhileValidating(self, activity):
    """Try to execute active objects which may throw conflict errors
    while validating, and check if they are still executed."""
    # Make sure that no active object is installed.
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities()

    # Need an object.
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = organisation_module._getOb(self.company_id)
    self.commit()
    self.flushAllActivities(silent = 1, loop_size = 10)
    self.assertEqual(len(activity_tool.getMessageList()), 0)

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
        self.assertEqual(len(activity_tool.getMessageList()), 0)
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
    activity_tool.manageClearActivities()

    # Need an object.
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = organisation_module._getOb(self.company_id)
    self.commit()
    self.flushAllActivities(silent=1, loop_size=10)
    self.assertEqual(len(activity_tool.getMessageList()), 0)

    # Monkey patch Queue to induce conflict errors artificially.
    def query(self, query_string,*args, **kw):
      # Not so nice, this is specific to zsql method
      if "REPLACE INTO" in query_string:
        raise OperationalError
      return self.original_query(query_string,*args, **kw)
    portal = self.getPortal()

    # Test some range of conflict error occurences.
    organisation_module.reindexObject()
    self.commit()
    self.assertTrue(len(activity_tool.getMessageList()), 1)
    try:
      DB.original_query = DB.query
      DB.query = query
      portal.portal_activities.distribute()
      portal.portal_activities.tic()
      self.commit()
    finally:
      DB.query = DB.original_query
      del DB.original_query
    self.assertEqual(len(portal.portal_activities.getMessageList()), 1)

  def checkIsMessageRegisteredMethod(self, activity):
    activity_tool = self.getPortal().portal_activities
    object_a = self.getOrganisationModule()
    if not object_a.hasContent(self.company_id):
      object_a.newContent(id=self.company_id)
    object_b = object_a._getOb(self.company_id)
    activity_tool.manageClearActivities()
    self.commit()
    # First case: creating the same activity twice must only register one.
    self.assertEqual(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_a.activate(activity=activity).getId()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 1)
    activity_tool.manageClearActivities()
    self.commit()
    # Second case: creating activity with same tag must only register one.
    # This behaviour is actually the same as the no-tag behaviour.
    self.assertEqual(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity, tag='foo').getId()
    object_a.activate(activity=activity, tag='foo').getId()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 1)
    activity_tool.manageClearActivities()
    self.commit()
    # Third case: creating activities with different tags must register both.
    self.assertEqual(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity, tag='foo').getId()
    object_a.activate(activity=activity, tag='bar').getId()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities()
    self.commit()
    # Fourth case: creating activities on different objects must register
    # both.
    self.assertEqual(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_b.activate(activity=activity).getId()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities()
    self.commit()
    # Fifth case: creating activities with different method must register
    # both.
    self.assertEqual(len(activity_tool.getMessageList()), 0) # Sanity check
    object_a.activate(activity=activity).getId()
    object_a.activate(activity=activity).getTitle()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    activity_tool.manageClearActivities()
    self.commit()

  def test_01_DeferredSetTitleSQLDict(self):
    # Test if we can add a complete sales order
    self.DeferredSetTitleActivity('SQLDict')

  def test_02_DeferredSetTitleSQLQueue(self):
    # Test if we can add a complete sales order
    self.DeferredSetTitleActivity('SQLQueue')

  def test_03_DeferredSetTitleSQLJoblib(self):
    # Test if we can add a complete sales order
    self.DeferredSetTitleActivity('SQLJoblib')

  def test_05_InvokeAndCancelSQLDict(self):
    # Test if we can add a complete sales order
    self.InvokeAndCancelActivity('SQLDict')

  def test_06_InvokeAndCancelSQLQueue(self):
    # Test if we can add a complete sales order
    self.InvokeAndCancelActivity('SQLQueue')

  def test_07_InvokeAndCancelSQLJoblib(self):
    self.InvokeAndCancelActivity('SQLJoblib')

  def test_09_CallOnceWithSQLDict(self):
    # Test if we call methods only once
    self.CallOnceWithActivity('SQLDict')

  def test_10_CallOnceWithSQLQueue(self):
    # Test if we call methods only once
    self.CallOnceWithActivity('SQLQueue')

  def test_11_CallOnceWithSQLJoblib(self):
    self.CallOnceWithActivity('SQLJoblib')

  def test_13_TryMessageWithErrorOnSQLDict(self):
    # Test if we call methods only once
    self.TryMessageWithErrorOnActivity('SQLDict')

  def test_14_TryMessageWithErrorOnSQLQueue(self):
    # Test if we call methods only once
    self.TryMessageWithErrorOnActivity('SQLQueue')
  
  def test_15_TryMessageWithErrorOnSQLJoblib(self):
    self.TryMessageWithErrorOnActivity('SQLJoblib')

  def test_17_TryFlushActivityWithSQLDict(self):
    # Test if we call methods only once
    self.TryFlushActivity('SQLDict')

  def test_18_TryFlushActivityWithSQLQueue(self):
    # Test if we call methods only once
    self.TryFlushActivity('SQLQueue')

  def test_19_TryFlushActivityWithSQLJoblib(self):
    # Test if we call methods only once
    self.TryFlushActivity('SQLJoblib')

  def test_21_TryActivateInsideFlushWithSQLDict(self):
    # Test if we call methods only once
    self.TryActivateInsideFlush('SQLDict')

  def test_22_TryActivateInsideFlushWithSQLQueue(self):
    # Test if we call methods only once
    self.TryActivateInsideFlush('SQLQueue')

  def test_23_TryActivateInsideFlushWithSQLQueue(self):
    # Test if we call methods only once
    self.TryActivateInsideFlush('SQLJoblib')

  def test_25_TryTwoMethodsWithSQLDict(self):
    # Test if we call methods only once
    self.TryTwoMethods('SQLDict')

  def test_26_TryTwoMethodsWithSQLQueue(self):
    # Test if we call methods only once
    self.TryTwoMethods('SQLQueue')

  def test_27_TryTwoMethodsWithSQLJoblib(self):
    # Test if we call methods only once
    self.TryTwoMethods('SQLJoblib')

  def test_29_TryTwoMethodsAndFlushThemWithSQLDict(self):
    # Test if we call methods only once
    self.TryTwoMethodsAndFlushThem('SQLDict')

  def test_30_TryTwoMethodsAndFlushThemWithSQLQueue(self):
    # Test if we call methods only once
    self.TryTwoMethodsAndFlushThem('SQLQueue')

  def test_31_TryTwoMethodsAndFlushThemWithSQLJoblib(self):
    # Test if we call methods only once
    self.TryTwoMethodsAndFlushThem('SQLJoblib')

  def test_33_TryActivateFlushActivateTicWithSQLDict(self):
    # Test if we call methods only once
    self.TryActivateFlushActivateTic('SQLDict')

  def test_34_TryActivateFlushActivateTicWithSQLQueue(self):
    # Test if we call methods only once
    self.TryActivateFlushActivateTic('SQLQueue')

  def test_37_TryActivateFlushActivateTicWithMultipleActivities(self):
    # Test if we call methods only once
    self.TryActivateFlushActivateTic('SQLQueue',second='SQLDict')
    self.TryActivateFlushActivateTic('SQLDict',second='SQLQueue')

  def test_38_TryCommitSubTransactionWithSQLDict(self):
    # Test if we call methods only once
    self.TryActivateFlushActivateTic('SQLDict',commit_sub=1)

  def test_39_TryCommitSubTransactionWithSQLQueue(self):
    # Test if we call methods only once
    self.TryActivateFlushActivateTic('SQLQueue',commit_sub=1)

  def test_42_TryRenameObjectWithSQLDict(self):
    # Test if we call methods only once
    self.DeferredSetTitleWithRenamedObject('SQLDict')

  def test_43_TryRenameObjectWithSQLQueue(self):
    # Test if we call methods only once
    self.DeferredSetTitleWithRenamedObject('SQLQueue')

  def test_44_TryRenameObjectWithSQLJoblib(self):
    # Test if we call methods only once
    self.DeferredSetTitleWithRenamedObject('SQLJoblib')

  def test_46_TryActiveProcessWithSQLDict(self):
    # Test if we call methods only once
    self.TryActiveProcess('SQLDict')

  def test_47_TryActiveProcessWithSQLQueue(self):
    # Test if we call methods only once
    self.TryActiveProcess('SQLQueue')

  def test_48_TryActiveProcessWithSQLJoblib(self):
    # Test if we call methods only once
    self.TryActiveProcessWithResultDict('SQLJoblib')

  def test_54_TryAfterMethodIdWithSQLDict(self):
    # Test if after_method_id can be used
    self.TryMethodAfterMethod('SQLDict')

  def test_55_TryAfterMethodIdWithSQLQueue(self):
    # Test if after_method_id can be used
    self.TryMethodAfterMethod('SQLQueue')

  def test_56_TryAfterMethodIdWithSQLJoblib(self):
    # Test if after_method_id can be used
    self.TryMethodAfterMethod('SQLJoblib')

  def test_57_TryCallActivityWithRightUser(self):
    # Test if me execute methods with the right user
    # This should be independant of the activity used
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
    self.assertEqual(email.getOwnerInfo()['id'],'toto')

  def test_59_TryAfterTagWithSQLDict(self):
    # Test if after_tag can be used
    self.TryAfterTag('SQLDict')

  def test_60_TryAfterTagWithSQLQueue(self):
    # Test if after_tag can be used
    self.TryAfterTag('SQLQueue')

  def test_61_TryAfterTagWithSQLJoblib(self):
    # Test if after_tag can be used
    self.TryAfterTag('SQLJoblib')

  def test_62_CheckSchedulingWithSQLDict(self):
    # Test if scheduling is correct with SQLDict
    self.CheckScheduling('SQLDict')

  def test_63_CheckSchedulingWithSQLQueue(self):
    # Test if scheduling is correct with SQLQueue
    self.CheckScheduling('SQLQueue')

  def test_64_CheckSchedulingWithSQLJoblib(self):
    # Test if scheduling is correct with SQLQueue
    self.CheckScheduling('SQLJoblib')

  def test_65_CheckSchedulingAfterTagListWithSQLDict(self):
    # Test if scheduling is correct with SQLDict
    self.CheckSchedulingAfterTagList('SQLDict')

  def test_66_CheckSchedulingWithAfterTagListSQLQueue(self):
    # Test if scheduling is correct with SQLQueue
    self.CheckSchedulingAfterTagList('SQLQueue')

  def test_67_CheckSchedulingWithAfterTagListSQLJoblib(self):
    # Test if scheduling is correct with SQLQueue
    self.CheckSchedulingAfterTagList('SQLJoblib')

  def flushAllActivities(self, silent=0, loop_size=1000):
    """Executes all messages until the queue only contains failed
    messages.
    """
    activity_tool = self.getPortal().portal_activities
    for _ in xrange(loop_size):
      activity_tool.distribute(node_count=1)
      activity_tool.tic(processing_node=1)

      finished = 1
      for message in activity_tool.getMessageList():
        if message.processing_node != INVOKE_ERROR_STATE:
          finished = 0

      activity_tool.timeShift(3 * VALIDATION_ERROR_DELAY)
      self.commit()
      if finished:
        return
    if not silent:
      self.fail('flushAllActivities maximum loop count reached')

  def test_68_TestMessageValidationAndFailedActivities(self):
    """after_method_id and failed activities.

    Tests that if we have an active method scheduled by
    after_method_id and a failed activity with this method id, the
    method is NOT executed.

    Note: earlier version of this test checked exactly the contrary, but it
    was eventually agreed that this was a bug. If an activity fails, all the
    activities that depend on it should be block until the first one is
    resolved."""
    activity_tool = self.getPortal().portal_activities
    original_title = 'something'
    obj = self.getPortal().organisation_module.newContent(
                    portal_type='Organisation',
                    title=original_title)
    # Monkey patch Organisation to add a failing method
    def failingMethod(self):
      raise ValueError, 'This method always fail'
    Organisation.failingMethod = failingMethod

    activity_list = ['SQLQueue', 'SQLDict', 'SQLJoblib']
    for activity in activity_list:
      # reset
      activity_tool.manageClearActivities()
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
      if len(full_message_list) != 3:
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
      if len(full_message_list) != 4:
        self.fail('failingMethod should not have been flushed')
      if len(remaining_messages) != 1:
        self.fail('Activity tool should have one blocked setTitle activity')
      self.assertEqual(remaining_messages[0].activity_kw['after_method_id'],
          ['failingMethod'])
      self.assertEqual(obj.getTitle(), original_title)

  def test_69_TestCountMessageWithTagWithSQLDict(self):
    """
      Test new countMessageWithTag function with SQLDict.
    """
    self.CheckCountMessageWithTag('SQLDict')

  def test_70_TestCancelFailedActiveObject(self):
    """Cancel an active object to make sure that it does not refer to
    a persistent object.

    XXX: this test fails if run first
    """
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities()

    original_title = 'something'
    obj = self.getPortal().organisation_module.newContent(
                    portal_type='Organisation',
                    title=original_title)

    # Monkey patch Organisation to add a failing method
    def failingMethod(self):
      raise ValueError, 'This method always fail'
    Organisation.failingMethod = failingMethod

    # First, index the object.
    self.commit()
    self.flushAllActivities(silent=1, loop_size=100)
    self.assertEqual(len(activity_tool.getMessageList()), 0)

    # Insert a failing active object.
    obj.activate().failingMethod()
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 1)

    # Just wait for the active object to be abandoned.
    self.flushAllActivities(silent=1, loop_size=100)
    self.assertEqual(len(activity_tool.getMessageList()), 1)
    self.assertEqual(activity_tool.getMessageList()[0].processing_node,
                      INVOKE_ERROR_STATE)

    # Make sure that persistent objects are not present in the connection
    # cache to emulate a restart of Zope. So all volatile attributes will
    # be flushed, and persistent objects will be reloaded.
    activity_tool._p_jar._resetCache()

    # Cancel it via the management interface.
    message = activity_tool.getMessageList()[0]
    activity_tool.manageCancel(message.object_path, message.method_id)
    self.commit()
    self.assertEqual(len(activity_tool.getMessageList()), 0)

  def test_71_RetryMessageExecution(self):
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
      for activity in 'SQLDict', 'SQLQueue', 'SQLJoblib':
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

  def test_72_TestConflictErrorsWhileValidatingWithSQLDict(self):
    """
      Test if conflict errors spoil out active objects with SQLDict.
    """
    self.TryConflictErrorsWhileValidating('SQLDict')

  def test_73_TestConflictErrorsWhileValidatingWithSQLQueue(self):
    """
      Test if conflict errors spoil out active objects with SQLQueue.
    """
    self.TryConflictErrorsWhileValidating('SQLQueue')

  def test_74_TestConflictErrorsWhileValidatingWithSQLJoblib(self):
    """
      Test if conflict errors spoil out active objects with SQLJoblib.
    """
    self.TryConflictErrorsWhileValidating('SQLJoblib')

  def test_75_TestErrorsWhileFinishingCommitDBWithSQLDict(self):
    """
    """
    self.TryErrorsWhileFinishingCommitDB('SQLDict')

  def test_76_TestErrorsWhileFinishingCommitDBWithSQLQueue(self):
    """
    """
    self.TryErrorsWhileFinishingCommitDB('SQLQueue')

  def test_77_TryFlushActivityWithAfterTagSQLDict(self):
    # Test if after_tag can be used
    self.TryFlushActivityWithAfterTag('SQLDict')

  def test_78_TryFlushActivityWithAfterTagWithSQLQueue(self):
    # Test if after_tag can be used
    self.TryFlushActivityWithAfterTag('SQLQueue')

  def test_79_ActivateKwForNewContent(self):
    o1 = self.getOrganisationModule().newContent(
                                  activate_kw=dict(tag='The Tag'))
    self.commit()
    messages_for_o1 = [m for m in self.getActivityTool().getMessageList()
                       if m.object_path == o1.getPhysicalPath()]
    self.assertNotEquals(0, len(messages_for_o1))
    for m in messages_for_o1:
      self.assertEqual(m.activity_kw.get('tag'), 'The Tag')


  def test_80_FlushAfterMultipleActivate(self):
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

  def test_81_IsMessageRegisteredSQLDict(self):
    """
      This test tests behaviour of IsMessageRegistered method.
    """
    self.checkIsMessageRegisteredMethod('SQLDict')

  def test_82_AbortTransactionSynchronously(self):
    """
      This test checks if transaction.abort() synchronizes connections. It
      didn't do so back in Zope 2.7
    """
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


  def callWithGroupIdParamater(self, activity):
    portal = self.getPortal()
    organisation =  portal.organisation._getOb(self.company_id)
    # Defined a group method
    foobar_list = []
    def setFoobar(self, object_list):
      foobar_list.append(len(object_list))
      for m in object_list:
        obj = m.object
        obj.foobar = getattr(obj.aq_base, 'foobar', 0) + m.kw.get('number', 1)
        m.result = None
    from Products.ERP5Type.Core.Folder import Folder
    Folder.setFoobar = setFoobar

    def getFoobar(self):
      return (getattr(self,'foobar',0))
    Organisation.getFoobar = getFoobar

    organisation.foobar = 0
    self.assertEqual(0,organisation.getFoobar())

    # Test group_method_id is working without group_id
    for x in xrange(5):
      organisation.activate(activity=activity, group_method_id="organisation_module/setFoobar").reindexObject(number=1)
      self.commit()

    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),5)
    portal.portal_activities.tic()
    expected = dict(SQLDict=1, SQLQueue=5, SQLJoblib=1)[activity]
    self.assertEqual(expected, organisation.getFoobar())


    # Test group_method_id is working with one group_id defined
    for x in xrange(5):
      organisation.activate(activity=activity, group_method_id="organisation_module/setFoobar", group_id="1").reindexObject(number=1)
      self.commit()

    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list),5)
    portal.portal_activities.tic()
    self.assertEqual(expected * 2, organisation.getFoobar())

    self.assertEqual([expected, expected], foobar_list)
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
    self.assertEqual(len(message_list),20)
    portal.portal_activities.tic()
    self.assertEqual(dict(SQLDict=11, SQLQueue=60, SQLJoblib=11)[activity],
                      organisation.getFoobar())
    self.assertEqual(dict(SQLDict=[1, 1, 1], SQLQueue=[5, 5, 10], SQLJoblib=[1,1,1])[activity],
                      sorted(foobar_list))
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list), 0)

  def test_83a_CallWithGroupIdParamaterSQLDict(self):
    """
    Test that group_id parameter is used to separate execution of the same method
    """
    self.callWithGroupIdParamater('SQLDict')

  def test_83b_CallWithGroupIdParamaterSQLQueue(self):
    """
    Test that group_id parameter is used to separate execution of the same method
    """
    self.callWithGroupIdParamater('SQLQueue')

  def test_83c_CallWithGroupIdParamaterSQLJoblib(self):
    """
    Test that group_id parameter is used to separate execution of the same method
    """
    self.callWithGroupIdParamater('SQLJoblib')

  def test_84_ActivateKwForWorkflowTransition(self):
    """
    Test call of a workflow transition with activate_kw parameter propagate them
    """
    o1 = self.getOrganisationModule().newContent()
    self.tic()
    o1.validate(activate_kw=dict(tag='The Tag'))
    self.commit()
    messages_for_o1 = [m for m in self.getActivityTool().getMessageList()
                       if m.object_path == o1.getPhysicalPath()]
    self.assertNotEquals(0, len(messages_for_o1))
    for m in messages_for_o1:
      self.assertEqual(m.activity_kw.get('tag'), 'The Tag')

  def test_85_LossOfVolatileAttribute(self):
    """
    Test that the loss of volatile attribute doesn't loose activities
    """
    self.tic()
    activity_tool = self.getActivityTool()
    message_list = activity_tool.getMessageList()
    self.assertEqual(len(message_list), 0)
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
    self.assertEqual(len(message_list), 2)

  def test_88_ProcessingMultipleMessagesMustRevertIndividualMessagesOnError(self):
    """
      Check that, on queues which support it, processing a batch of multiple
      messages doesn't cause failed ones to becommited along with succesful
      ones.

      Queues supporting message batch processing:
       - SQLQueue
    """
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

  def test_89_RequestIsolationInsideSameTic(self):
    """
      Check that request information do not leak from one activity to another
      inside the same TIC invocation.
      This only apply to queues supporting batch processing:
        - SQLQueue
    """
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
    message_list = self.portal.MailHost._message_list
    del message_list[:]
    obj = self.portal.organisation_module.newContent(portal_type='Organisation')
    self.tic()
    def failingMethod(self): raise ValueError('This method always fails')
    Organisation.failingMethod = failingMethod
    try:
      # MESSAGE_NOT_EXECUTED
      obj.activate(activity=activity).failingMethod()
      self.commit()
      self.assertFalse(message_list)
      self.flushAllActivities(silent=1, loop_size=100)
      # Check there is a traceback in the email notification
      sender, recipients, mail = message_list.pop()
      self.assertTrue("Module %s, line %s, in failingMethod" % (
        __name__, inspect.getsourcelines(failingMethod)[1]) in mail, mail)
      self.assertTrue("ValueError:" in mail, mail)
      # MESSAGE_NOT_EXECUTABLE
      obj.getParentValue()._delObject(obj.getId())
      obj.activate(activity=activity).failingMethod()
      self.commit()
      self.assertTrue(obj.hasActivity())
      self.tic()
      self.assertFalse(obj.hasActivity())
      self.assertFalse(message_list)
    finally:
      del Organisation.failingMethod

  def test_90_userNotificationOnActivityFailureWithSQLDict(self):
    """
      Check that a user notification method is called on message when activity
      fails and will not be tried again.
    """
    self.TryUserNotificationOnActivityFailure('SQLDict')

  def test_91_userNotificationOnActivityFailureWithSQLJoblib(self):
    """
      Check user notification sent on activity final error
    """
    self.TryUserNotificationOnActivityFailure('SQLJoblib')

  def test_92_userNotificationOnActivityFailureWithSQLQueue(self):
    """
      Check that a user notification method is called on message when activity
      fails and will not be tried again.
    """
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

  def test_93_userNotificationRaiseWithSQLDict(self):
    """
      Check that activities are not left with processing=1 when notifyUser raises.
    """
    self.TryUserNotificationRaise('SQLDict')

  def test_94_userNotificationRaiseWithSQLQueue(self):
    """
      Check that activities are not left with processing=1 when notifyUser raises.
    """
    self.TryUserNotificationRaise('SQLQueue')

  def test_95_userNotificationRaiseWithSQLJoblib(self):
    """
      Check that activities are not left with processing=1 when notifyUser raises.
    """
    self.TryUserNotificationRaise('SQLJoblib')

  def TryActivityRaiseInCommitDoesNotStallActivityConection(self, activity):
    """
      Check that an activity which commit raises (as would a regular conflict
      error be raised in tpc_vote) does not cause activity connection to
      stall.
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
      # Check that cmf_activity SQL connection still works
      connection_da = self.getPortalObject().cmf_activity_sql_connection()
      self.assertFalse(connection_da._registered)
      connection_da.query('select 1')
      self.assertTrue(connection_da._registered)
      self.commit()
      self.assertFalse(connection_da._registered)
    finally:
      delattr(Organisation, 'registerFailingTransactionManager')

  def test_96_ActivityRaiseInCommitDoesNotStallActivityConectionSQLDict(self):
    self.TryActivityRaiseInCommitDoesNotStallActivityConection('SQLDict')

  def test_97_ActivityRaiseInCommitDoesNotStallActivityConectionSQLQueue(self):
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
      self.assertEqual(activity_tool.countMessage(method_id='registerFailingTransactionManager'), 1)
    finally:
      delattr(Organisation, 'registerFailingTransactionManager')

  def test_98_ActivityRaiseInCommitDoesNotLooseMessagesSQLDict(self):
    self.TryActivityRaiseInCommitDoesNotLooseMessages('SQLDict')

  def test_99_ActivityRaiseInCommitDoesNotLooseMessagesSQLQueue(self):
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
      self.assertEqual(len(activity_tool.getMessageList()), 1)
      self.flushAllActivities(silent=1, loop_size=100)
      self.assertEqual(len(activity_tool.getMessageList()), 0)
    finally:
      delattr(Organisation, 'changeSkinToNone')

  def test_100_TryChangeSkinInActivitySQLDict(self):
    self.TryChangeSkinInActivity('SQLDict')

  def test_101_TryChangeSkinInActivitySQLQueue(self):
    self.TryChangeSkinInActivity('SQLQueue')

  def test_102_TryChangeSkinInActivitySQLJoblib(self):
    self.TryChangeSkinInActivity('SQLJoblib')

  def test_103_1_CheckSQLDictDoesNotDeleteSimilaritiesBeforeExecution(self):
    """
      Test that SQLDict does not delete similar messages which have the same
      method_id and path but a different tag before execution.
    """
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

  def test_103_2_CheckSQLDictDoesNotDeleteDuplicatesBeforeExecution(self):
    """
      Test that SQLDict does not delete messages before execution
      even if messages have the same method_id and path and tag.
      There could be other things which differ (ex: serialization_tag) and may
      not all be cheap to check during validation. Validation node is the only
      non-paralelisable Zope-side task around activities, so it should be kept
      simple.
      Deduplication is cheap:
      - inside the transaction which spawned duplicate activities, because it
        has to have created activities around anyway, and can keep track
      - inside the CMFActvitiy-level processing surrounding activity execution
        because it has to load the activities to process them anyway
    """
    activity_tool = self.getActivityTool()
    # Adds two same activities.
    activity_tool.activate(activity='SQLDict', after_tag='foo', priority=2,
      tag='a').getId()
    self.commit()
    uid1, = [x.uid for x in activity_tool.getMessageList()]
    activity_tool.activate(activity='SQLDict', after_tag='bar', priority=1,
      tag='a').getId()
    self.commit()
    uid2, = [x.uid for x in activity_tool.getMessageList() if x.uid != uid1]
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    activity_tool.distribute()
    # After distribute, duplicate is still present.
    self.assertItemsEqual([uid1, uid2], [x.uid for x in activity_tool.getMessageList()])
    activity_tool.tic()
    self.assertEqual(len(activity_tool.getMessageList()), 0)

  def test_103_3_CheckSQLJoblibDoesNotDeleteDuplicatesBeforeExecution(self):
    """
    (see test_103_2_CheckSQLDictDoesNotDeleteDuplicatesBeforeExecution)
    """
    activity_tool = self.getActivityTool()
    # Adds two same activities.
    activity_tool.activate(activity='SQLJoblib', after_tag='foo', priority=2,
      tag='a').getId()
    self.commit()
    uid1, = [x.uid for x in activity_tool.getMessageList()]
    activity_tool.activate(activity='SQLJoblib', after_tag='bar', priority=1,
      tag='a').getId()
    self.commit()
    uid2, = [x.uid for x in activity_tool.getMessageList() if x.uid != uid1]
    self.assertEqual(len(activity_tool.getMessageList()), 2)
    activity_tool.distribute()
    # After distribute, duplicate is still present.
    self.assertItemsEqual([uid1, uid2], [x.uid for x in activity_tool.getMessageList()])
    activity_tool.tic()
    self.assertEqual(len(activity_tool.getMessageList()), 0)

  def test_103_4_CheckSQLDictDistributeWithSerializationTagAndGroupMethodId(
      self):
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

  def test_104_interQueuePriorities(self):
    """
      Important note: there is no way to really reliably check that this
      feature is correctly implemented, as activity execution order is
      non-deterministic.
      The best which can be done is to check that under certain circumstances
      the activity exeicution order match expectations.
    """
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

  def test_105_activityRuntimeEnvironmentSQLDict(self):
    self.CheckActivityRuntimeEnvironment('SQLDict')

  def test_106_activityRuntimeEnvironmentSQLQueue(self):
    self.CheckActivityRuntimeEnvironment('SQLQueue')

  def test_107_activityRuntimeEnvironmentSQLJoblib(self):
    self.CheckActivityRuntimeEnvironment('SQLJoblib')

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

  def test_108_checkSerializationTagSQLDict(self):
    self.CheckSerializationTag('SQLDict')

  def test_109_checkSerializationTagSQLQueue(self):
    self.CheckSerializationTag('SQLQueue')

  def test_110_testAbsoluteUrl(self):
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
      self.assertEqual(o.absolute_url(),
          'http://test.erp5.org:9080/virtual_root/test_obj')
      o.activate().checkAbsoluteUrl()

      # Reset server URL and virtual root before executing messages.
      # This simulates the case of activities beeing executed with different
      # REQUEST, such as TimerServer.
      request.setServerURL('https', 'anotherhost.erp5.org', '443')
      request.other['PARENTS'] = [self.app]
      request.setVirtualRoot('')
      # obviously, the object url is different
      self.assertEqual(o.absolute_url(),
          'https://anotherhost.erp5.org/%s/organisation_module/test_obj'
           % self.portal.getId())

      # but activities are executed using the previous request information
      self.flushAllActivities(loop_size=1000)
      self.assertEqual(calls, ['http://test.erp5.org:9080/virtual_root/test_obj'])
    finally:
      delattr(Organisation, 'checkAbsoluteUrl')

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

  def test_112_checkLocalizerWorksSQLQueue(self):
    self.CheckLocalizerWorks('SQLQueue')

  def test_113_checkLocalizerWorksSQLDict(self):
    self.CheckLocalizerWorks('SQLDict')

  def test_114_checkSQLQueueActivitySucceedsAfterActivityChangingSkin(self):
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
      self.assertEqual(len(activity_tool.getMessageList()), 0)
    finally:
      delattr(Organisation, 'firstTest')
      delattr(Organisation, 'secondTest')

  def test_115_checkProcessShutdown(self):
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
      for activity in ('SQLDict', 'SQLQueue', 'SQLJoblib'):
        active_object.activate(activity=activity, **kw).getTitle()
        self.commit()
        self.assertTrue(obj.hasActivity(), activity)
        self.tic()
        self.assertFalse(obj.hasActivity(), activity)

    test(active_object)
    test(active_process, active_process=active_process)
    test(active_process, active_process=active_process.getPath())

  def _test_hasErrorActivity_error(self, activity):
    # Monkey patch Organisation to add a failing method
    def failingMethod(self):
      raise ValueError('This method always fail')
    Organisation.failingMethod = failingMethod
    active_object = self.portal.organisation_module.newContent(
                                            portal_type='Organisation')
    active_process = self.portal.portal_activities.newActiveProcess()
    self.tic()


    self.assertFalse(active_object.hasErrorActivity())
    self.assertFalse(active_process.hasErrorActivity())

    active_object.activate(
      activity=activity, active_process=active_process).failingMethod()
    self.commit()
    # assert that any activity is created
    self.assertTrue(active_object.hasActivity())
    self.assertTrue(active_process.hasActivity())
    # assert that no error is reported
    self.assertFalse(active_object.hasErrorActivity())
    self.assertFalse(active_process.hasErrorActivity())
    self.flushAllActivities()
    # assert that any activity is created
    self.assertTrue(active_object.hasActivity())
    self.assertTrue(active_process.hasActivity())
    # assert that an error has been seen
    self.assertTrue(active_object.hasErrorActivity())
    self.assertTrue(active_process.hasErrorActivity())

  def test_hasErrorActivity_error_SQLQueue(self):
    self._test_hasErrorActivity_error('SQLQueue')

  def test_hasErrorActivity_error_SQLDict(self):
    self._test_hasErrorActivity_error('SQLDict')

  def test_hasErrorActivity_error_SQLJoblib(self):
    self._test_hasErrorActivity_error('SQLJoblib')

  def _test_hasErrorActivity(self, activity):
    active_object = self.portal.organisation_module.newContent(
                                            portal_type='Organisation')
    active_process = self.portal.portal_activities.newActiveProcess()
    self.tic()

    self.assertFalse(active_object.hasErrorActivity())
    self.assertFalse(active_process.hasErrorActivity())

    active_object.activate(
      activity=activity, active_process=active_process).getTitle()
    self.commit()
    # assert that any activity is created
    self.assertTrue(active_object.hasActivity())
    self.assertTrue(active_process.hasActivity())
    # assert that no error is reported
    self.assertFalse(active_object.hasErrorActivity())
    self.assertFalse(active_process.hasErrorActivity())
    self.flushAllActivities()
    # assert that any activity is created
    self.assertFalse(active_object.hasActivity())
    self.assertFalse(active_process.hasActivity())
    # assert that no error is reported
    self.assertFalse(active_object.hasErrorActivity())
    self.assertFalse(active_process.hasErrorActivity())

  def test_hasErrorActivity_SQLQueue(self):
    self._test_hasErrorActivity('SQLQueue')

  def test_hasErrorActivity_SQLDict(self):
    self._test_hasErrorActivity('SQLDict')

  def test_hasErrorActivity_SQLJoblib(self):
    self._test_hasErrorActivity('SQLJoblib')

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

  def test_MAX_MESSAGE_LIST_SIZE(self):
    from Products.CMFActivity.Activity import SQLBase
    MAX_MESSAGE_LIST_SIZE = SQLBase.MAX_MESSAGE_LIST_SIZE
    try:
      SQLBase.MAX_MESSAGE_LIST_SIZE = 3
      def dummy_counter(o):
        self.__call_count += 1
      o = self.portal.organisation_module.newContent(portal_type='Organisation')

      for activity in "SQLDict", "SQLQueue", "SQLJoblib":
        self.__call_count = 0
        try:
          for i in xrange(10):
            method_name = 'dummy_counter_%s' % i
            getattr(o.activate(activity=activity), method_name)()
            setattr(Organisation, method_name, dummy_counter)
          self.flushAllActivities()
        finally:
          for i in xrange(10):
            delattr(Organisation, 'dummy_counter_%s' % i)
        self.assertEqual(self.__call_count, 10)
    finally:
      SQLBase.MAX_MESSAGE_LIST_SIZE = MAX_MESSAGE_LIST_SIZE

  def test_115_TestSerializationTagSQLDictPreventsParallelExecution(self):
    """
      Test if there are multiple activities with the same serialization tag,
      then serialization tag guarantees that only one of the same serialization
      tagged activities can be processed at the same time.
    """
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
                                message.serialization_tag=='test_115')]),
                       1)

      self.assertEqual(len([message
                            for message in result
                            if (message.processing_node==-1 and
                                message.serialization_tag=='test_115')]),
                       4)

      self.assertEqual(len([message
                            for message in result
                            if (message.processing_node>0 and
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
      for activity in 'SQLDict', 'SQLQueue', 'SQLJoblib':
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
    self.assertEqual({'activate_kw': {'tag': tag}}, \
                       current_default_reindex_parameters)
    person = portal.person_module.newContent(portal_type='Person')
    self.commit()
    # as we specified it in setPlacelessDefaultReindexParameters we should have
    # an activity for this tags
    self.assertEqual(1, portal.portal_activities.countMessageWithTag(tag))
    self.tic()
    self.assertEqual(0, portal.portal_activities.countMessageWithTag(tag))

    # restore originals ones
    portal.setPlacelessDefaultReindexParameters(**original_reindex_parameters)
    person = portal.person_module.newContent(portal_type='Person')
    # .. now no messages with this tag should apper
    self.assertEqual(0, portal.portal_activities.countMessageWithTag(tag))

  def TryNotificationSavedOnEventLogWhenNotifyUserRaises(self, activity):
    activity_tool = self.getActivityTool()
    self.tic()
    obj = self.getPortal().organisation_module.newContent(portal_type='Organisation')
    self.tic()
    original_notifyUser = Message.notifyUser.im_func
    def failSendingEmail(self, *args, **kw):
      raise MailHostError, 'Mail is not sent'
    activity_unit_test_error = Exception()
    def failingMethod(self):
      raise activity_unit_test_error
    try:
      Message.notifyUser = failSendingEmail
      Organisation.failingMethod = failingMethod
      self._catch_log_errors()
      obj.activate(activity=activity, priority=6).failingMethod()
      self.commit()
      self.flushAllActivities(silent=1, loop_size=100)
      message, = activity_tool.getMessageList()
      self.commit()
      for log_record in self.logged:
        if log_record.name == 'ActivityTool' and log_record.levelname == 'WARNING':
          type, value, trace = log_record.exc_info
      self.commit()
      self.assertTrue(activity_unit_test_error is value)
    finally:
      Message.notifyUser = original_notifyUser
      del Organisation.failingMethod
      self._ignore_log_errors()

  def test_118_userNotificationSavedOnEventLogWhenNotifyUserRaisesWithSQLDict(self):
    """
      Check the error is saved on event log even if the mail notification is not sent.
    """
    self.TryNotificationSavedOnEventLogWhenNotifyUserRaises('SQLDict')

  def test_119_userNotificationSavedOnEventLogWhenNotifyUserRaisesWithSQLQueue(self):
    """
      Check the error is saved on event log even if the mail notification is not sent.
    """
    self.TryNotificationSavedOnEventLogWhenNotifyUserRaises('SQLQueue')

  def test_120_userNotificationSavedOnEventLogWhenNotifyUserRaisesWithSQLJoblib(self):
    """
      Check the error is saved on event log even if the mail notification is not sent.
    """
    self.TryNotificationSavedOnEventLogWhenNotifyUserRaises('SQLJoblib')

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

  def test_121_sendMessageWithNoTracebackWithSQLQueue(self):
    self.TryUserMessageContainingNoTracebackIsStillSent('SQLQueue')

  def test_122_sendMessageWithNoTracebackWithSQLDict(self):
    self.TryUserMessageContainingNoTracebackIsStillSent('SQLDict')

  def test_123_sendMessageWithNoTracebackWithSQLJoblib(self):
    """
      Check that message with no traceback is still sen
    """
    self.TryUserMessageContainingNoTracebackIsStillSent('SQLJoblib')

  def TryNotificationSavedOnEventLogWhenSiteErrorLoggerRaises(self, activity):
    # Make sure that no active object is installed.
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities()

    # Need an object.
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
    o = organisation_module._getOb(self.company_id)
    self.commit()
    self.flushAllActivities(silent = 1, loop_size = 10)
    self.assertEqual(len(activity_tool.getMessageList()), 0)
    class ActivityUnitTestError(Exception):
      pass
    activity_unit_test_error = ActivityUnitTestError()
    def failingMethod(self):
      raise activity_unit_test_error
    from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
    original_raising = SiteErrorLog.raising.im_func

    # Monkey patch Site Error to induce conflict errors artificially.
    def raising(self, info):
      raise AttributeError
    try:
      SiteErrorLog.raising = raising
      Organisation.failingMethod = failingMethod
      self._catch_log_errors()
      o.activate(activity = activity).failingMethod()
      self.commit()
      self.assertEqual(len(activity_tool.getMessageList()), 1)
      self.flushAllActivities(silent = 1)
      SiteErrorLog.raising = original_raising
      self.commit()
      for log_record in self.logged:
        if log_record.name == 'ActivityTool' and log_record.levelname == 'WARNING':
          type, value, trace = log_record.exc_info
      self.assertTrue(activity_unit_test_error is value)
    finally:
      SiteErrorLog.raising = original_raising
      del Organisation.failingMethod
      self._ignore_log_errors()

  def test_124_userNotificationSavedOnEventLogWhenSiteErrorLoggerRaisesWithSQLJoblib(self):
    """
      Check that message not saved in site error logger is not lost
    """
    self.TryNotificationSavedOnEventLogWhenSiteErrorLoggerRaises('SQLJoblib')

  def test_125_userNotificationSavedOnEventLogWhenSiteErrorLoggerRaisesWithSQLDict(self):
    """
      Check that message not saved in site error logger is not lost'
    """
    self.TryNotificationSavedOnEventLogWhenSiteErrorLoggerRaises('SQLDict')

  def test_125_userNotificationSavedOnEventLogWhenSiteErrorLoggerRaisesWithSQLJoblib(self):
    """
      Check that message not saved in site error logger is not lost'
    """
    self.TryNotificationSavedOnEventLogWhenSiteErrorLoggerRaises('SQLJoblib')

  def test_126_userNotificationSavedOnEventLogWhenSiteErrorLoggerRaisesWithSQLQueue(self):
    self.TryNotificationSavedOnEventLogWhenSiteErrorLoggerRaises('SQLQueue')

  def test_127_checkConflictErrorAndNoRemainingActivities(self):
    """
    When an activity creates several activities, make sure that all newly
    created activities are not commited if there is ZODB Conflict error
    """
    from Products.CMFActivity.Activity import SQLBase
    MAX_MESSAGE_LIST_SIZE = SQLBase.MAX_MESSAGE_LIST_SIZE
    try:
      SQLBase.MAX_MESSAGE_LIST_SIZE = 1
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
      self.assertEqual(['doSomething'],[x.method_id for x in message_list])
      activity_tool.manageClearActivities()
    finally:
      SQLBase.MAX_MESSAGE_LIST_SIZE = MAX_MESSAGE_LIST_SIZE

  def test_128_CheckDistributeWithSerializationTagAndGroupMethodId(self):
    activity_tool = self.portal.portal_activities
    obj1 = activity_tool.newActiveProcess()
    obj2 = activity_tool.newActiveProcess()
    self.tic()
    group_method_call_list = []
    def doSomething(self, message_list):
      r = []
      for m in message_list:
        m.result = r.append((m.object.getPath(), m.args, m.kw))
      r.sort()
      group_method_call_list.append(r)
    activity_tool.__class__.doSomething = doSomething
    try:
      for activity in 'SQLDict', 'SQLQueue', 'SQLJoblib':
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
                              SQLQueue=[message1, message2],
                              SQLJoblib=[message2])[activity])
        self.assertFalse(group_method_call_list)
        self.assertFalse(activity_tool.getMessageList())
    finally:
      del activity_tool.__class__.doSomething

  def test_129_beforeCommitHook(self):
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
    self.assertEqual(oldconn.meta_type, 'Z MySQL Database Connection')
    # force rebootstrap and check that migration of the connection happens
    # automatically
    from Products.ERP5Type.dynamic import portal_type_class
    portal_type_class._bootstrapped.clear()
    portal_type_class.synchronizeDynamicModules(activity_tool, True)
    activity_tool.activate(activity='SQLQueue').getId()
    self.tic()
    newconn = portal.cmf_activity_sql_connection
    self.assertEqual(newconn.meta_type, 'CMFActivity Database Connection')

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
    self.assertEqual(newconn.meta_type, 'CMFActivity Database Connection')

  def test_connection_sortkey(self):
    """
    Check that SQL connection has properly initialized sort key,
    even when its container (ZODB connection) is reused by another thread.
    """
    def sortKey():
      app = ZopeTestCase.app()
      try:
        c = app[self.getPortalName()].cmf_activity_sql_connection()
        return app._p_jar, c.sortKey()
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
      for activity in 'SQLDict', 'SQLQueue', 'SQLJoblib':
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
      self.assertEqual(tuple(invoked), expected)
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
      r = []
      for m in message_list:
        m.result = r.append(c.index(m.object))
      r.sort()
      invoked.append(r)
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

  def test_getMessageList(self):
    activity_tool = self.portal.portal_activities
    module = self.portal.person_module
    module.activate(after_tag="foo").getUid()
    module.activate(activity='SQLQueue', tag="foo").getId()
    activity_tool.activate(priority=-1).getId()
    def check(expected, **kw):
      self.assertEqual(expected, len(activity_tool.getMessageList(**kw)))
    def test(check=lambda _, **kw: check(0, **kw)):
      check(2, path=module.getPath())
      check(3, method_id=("getId", "getUid"))
      check(1, tag="foo")
      check(0, tag="foo", method_id="getUid")
      check(1, processing_node=-1)
      check(3, processing_node=range(-5,5))
    test()
    self.commit()
    test(check)
    self.tic()
    test()

  def test_MessageNonExecutable(self):
    message_list = self.portal.MailHost._message_list
    del message_list[:]
    activity_tool = self.portal.portal_activities
    kw = {}
    self._catch_log_errors(subsystem='CMFActivity')
    try:
      for kw['activity'] in 'SQLDict', 'SQLQueue', 'SQLJoblib':
        for kw['group_method_id'] in '', None:
          obj = activity_tool.newActiveProcess()
          self.tic()
          obj.activate(**kw).getId()
          activity_tool._delOb(obj.getId())
          obj = activity_tool.newActiveProcess(id=obj.getId(),
                                               is_indexable=False)
          self.commit()
          self.assertEqual(1, activity_tool.countMessage())
          self.flushAllActivities()
          sender, recipients, mail = message_list.pop()
          self.assertTrue('OID mismatch' in mail, mail)
          m, = activity_tool.getMessageList()
          self.assertEqual(m.processing_node, INVOKE_ERROR_STATE)
          obj.flushActivity()
          obj.activate(**kw).getId()
          activity_tool._delOb(obj.getId())
          self.commit()
          self.assertEqual(1, activity_tool.countMessage())
          activity_tool.tic()
          self.assertTrue('no object found' in self.logged.pop().getMessage())
    finally:
      self._ignore_log_errors()
    self.assertFalse(self.logged)
    self.assertFalse(message_list, message_list)

  def test_activateByPath(self):
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
      self.tic()
    organisation = organisation_module._getOb(self.company_id)
    portal.portal_activities.activateObject(
      organisation.getPath(),
      activity='SQLDict',
      active_process=None
      ).getTitle()
    self.tic()

  def test_activateOnZsqlBrain(self):
    portal = self.getPortal()
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
      self.tic()
    organisation = organisation_module.searchFolder(id=self.company_id)[0]
    organisation.activate().getTitle()
    self.tic()

  def test_flushActivitiesOnDelete(self):
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
      self.tic()

    organisation = organisation_module[self.company_id]
    organisation_module.manage_delObjects(ids=[organisation.getId()])
    organisation.activate().getTitle()
    self.tic()

  def test_flushActivitiesOnDeleteWithAcquierableObject(self):
    organisation_module = self.getOrganisationModule()
    if not organisation_module.hasContent(self.company_id):
      organisation_module.newContent(id=self.company_id)
      self.tic()

    # Create an object with the same ID that can be acquired
    self.portal._setObject(self.company_id, Organisation(self.company_id))

    organisation = organisation_module[self.company_id]
    organisation_module.manage_delObjects(ids=[organisation.getId()])
    organisation.reindexObject()
    self.tic()

  def test_failingGroupMethod(self):
    activity_tool = self.portal.portal_activities
    obj = activity_tool.newActiveProcess()
    self.tic()
    obj.x = 1
    def doSomething(self):
      self.x %= self.x
    obj.__class__.doSomething = doSomething
    try:
      activity_kw = dict(activity="SQLQueue", group_method_id=None)
      obj.activate(**activity_kw).doSomething()
      obj.activate(**activity_kw).doSomething()
      obj.activate(**activity_kw).doSomething()
      self.commit()
      self.assertEqual(3, len(activity_tool.getMessageList()))
      activity_tool.tic()
      self.assertEqual(obj.x, 0)
      skipped, failed = activity_tool.getMessageList()
      self.assertEqual(0, skipped.retry)
      self.assertEqual(1, failed.retry)
      obj.x = 1
      self.commit()
      activity_tool.timeShift(VALIDATION_ERROR_DELAY)
      activity_tool.tic()
      m, = activity_tool.getMessageList()
      self.assertEqual(1, failed.retry)
      obj.x = 1
      self.commit()
      activity_tool.timeShift(VALIDATION_ERROR_DELAY)
      activity_tool.tic()
      self.assertFalse(activity_tool.getMessageList())
    finally:
      del obj.__class__.doSomething

  def test_restrictedGroupMethod(self):
    skin = self.portal.portal_skins.custom
    script_id = self.id()
    script = createZODBPythonScript(skin, script_id, "message_list", """if 1:
      for m in message_list:
        m.result = m.object.getProperty(*m.args, **m.kw)
    """)
    script.manage_proxy(("Manager",))
    obj = self.portal.portal_activities.newActiveProcess(causality_value_list=(
      self.portal.person_module, self.portal.organisation_module))
    obj.manage_permission('Access contents information', ['Manager'])
    self.logout()
    foo = obj.activate(activity='SQLQueue',
                       group_method_id=script_id,
                       active_process=obj.getPath()).foo
    foo('causality', portal_type='Organisation Module')
    foo('stop_date', 'bar')
    self.tic()
    self.assertEqual(sorted(x.getResult() for x in obj.getResultList()),
                     ['bar', 'organisation_module'])
    skin.manage_delObjects([script_id])
    self.tic()

  def testGetCurrentNode(self):
    current_node = getattr(getConfiguration(),'product_config',{},).get('cmfactivity', {}).get('node-id')
    if not current_node:
      current_node = getServerAddress()
    node = getCurrentNode()
    self.assertEqual(node, current_node)
    portal = self.getPortal()
    activity_node = portal.portal_activities.getCurrentNode()
    self.assertEqual(activity_node, current_node)

  def testGetServerAddress(self):
    ip = port = ''
    for k, v in socket_map.items():
      if hasattr(v, 'addr'):
        type = str(getattr(v, '__class__', 'unknown'))
        if type == 'ZServer.HTTPServer.zhttp_server':
          ip, port = v.addr
          break
    if ip == '0.0.0.0':
      ip = socket.gethostbyname(socket.gethostname())
    server_address = '%s:%s' %(ip, port)
    address = getServerAddress()
    self.assertEqual(address, server_address)
    portal = self.getPortal()
    activity_address = portal.portal_activities.getServerAddress()
    self.assertEqual(activity_address, server_address)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCMFActivity))
  return suite

