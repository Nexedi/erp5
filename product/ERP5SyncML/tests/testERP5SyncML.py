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
from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
from zLOG import LOG
import time

class TestERP5SyncML(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  workflow_id = 'edit_workflow'
  first_name1 = 'Sebastien'
  last_name1 = 'Robin'
  description1 = 'description1 $sdfrç_sdfsçdf_oisfsopf'
  lang1 = 'fr'
  format2 = 'html'
  format3 = 'xml'
  format4 = 'txt'
  first_name2 = 'Jean-Paul'
  last_name2 = 'Smets'
  description2 = 'description2éà@  $*< <<<  >>>></title>&oekd'
  lang2 = 'en'
  first_name3 = 'Yoshinori'
  last_name3 = 'Okuji'
  description3 = 'description3 çsdf__sdfççç_df___&&é]]]°°°°°°'
  description4 = 'description4 sdflkmooo^^^^]]]]]{{{{{{{'
  lang3 = 'jp'
  lang4 = 'ca'
  xml_mapping = 'asXML'
  id1 = '170'
  id2 = '171'
  pub_id = 'Publication'
  sub_id1 = 'Subscription1'
  sub_id2 = 'Subscription2'
  nb_subscription = 2
  nb_publication = 1
  nb_synchronization = 3
  nb_message_first_synchronization = 6
  subscription_url1 = 'client1@localhost'
  subscription_url2 = 'client2@localhost'

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

      the business template crm give 3 folders:
      /person_server with persons: 170,171, 180
      /person_client1 : empty
      /person_client2 : empty
    """
    return ('crm',)

  def getSynchronizationTool(self):
    return getattr(self.getPortal(), 'portal_synchronizations', None)

  def getPersonClient1(self):
    return getattr(self.getPortal(), 'person_client1', None)

  def getPersonServer(self):
    return getattr(self.getPortal(), 'person_server', None)

  def getPersonClient2(self):
    return getattr(self.getPortal(), 'person_client2', None)

  def getPortalId(self):
    return self.getPortal().getId()

  def testHasEverything(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getSynchronizationTool()!=None)
    self.failUnless(self.getPersonServer()!=None)
    self.failUnless(self.getPersonClient1()!=None)
    self.failUnless(self.getPersonClient2()!=None)

  def testAddPublication(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Add a Publication ')
      LOG('Testing... ',0,'testAddPublication')
    portal_id = self.getPortalName()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addPublication(self.pub_id,'server@localhost',
                                      '/%s/person_server' % portal_id,'',
                                      self.xml_mapping)
    pub = portal_sync.getPublication(self.pub_id)
    self.failUnless(pub is not None)

  def testAddSubscription1(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Add First Subscription ')
      LOG('Testing... ',0,'testAddSubscription1')
    portal_id = self.getPortalId()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addSubscription(self.sub_id1,'server@localhost',
                          self.subscription_url1,'/%s/person_client1' % portal_id,'',
                          self.xml_mapping)
    sub = portal_sync.getSubscription(self.sub_id1)
    self.failUnless(sub is not None)

  def testAddSubscription2(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Add Second Subscription ')
      LOG('Testing... ',0,'testAddSubscription2')
    portal_id = self.getPortalId()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addSubscription(self.sub_id2,'server@localhost',
                          self.subscription_url2,'/%s/person_client2' % portal_id,'',
                          self.xml_mapping)
    sub = portal_sync.getSubscription(self.sub_id2)
    self.failUnless(sub is not None)

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def populatePersonServer(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Populate Person Server ')
      LOG('Testing... ',0,'populatePersonServer')
    self.login()
    person_server = self.getPersonServer()
    person_id = ''
    person1 = person_server.newContent(id=self.id1,portal_type='Person')
    kw = {'first_name':self.first_name1,'last_name':self.last_name1,
          'description':self.description1}
    person1.edit(**kw)
    person2 = person_server.newContent(id=self.id2,portal_type='Person')
    kw = {'first_name':self.first_name2,'last_name':self.last_name2,
          'description':self.description2}
    person2.edit(**kw)
    nb_person = len(person_server.objectValues())
    self.failUnless(nb_person==2)
    return nb_person

  def setupPublicationAndSubscription(self, quiet=0, run=run_all_test):
    self.testAddPublication(quiet=1,run=1)
    self.testAddSubscription1(quiet=1,run=1)
    self.testAddSubscription2(quiet=1,run=1)
      
  def setupPublicationAndSubscriptionAndGid(self, quiet=0, run=run_all_test):
    self.setupPublicationAndSubscription(quiet=1,run=1)
    def getGid(object):
      return object.getTitle()
    portal_sync = self.getSynchronizationTool()
    sub1 = portal_sync.getSubscription(self.sub_id1)
    sub2 = portal_sync.getSubscription(self.sub_id2)
    pub = portal_sync.getPublication(self.pub_id)
    pub.setGidGenerator(getGid)
    sub1.setGidGenerator(getGid)
    sub2.setGidGenerator(getGid)
    pub.setIdGenerator('generateNewId')
    sub1.setIdGenerator('generateNewId')
    sub2.setIdGenerator('generateNewId')

  def testGetSynchronizationList(self, quiet=0, run=run_all_test):
    # This test the getSynchronizationList, ie,
    # We want to see if we retrieve both the subscription
    # and the publication
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest getSynchronizationList ')
      LOG('Testing... ',0,'testGetSynchronizationList')
    self.setupPublicationAndSubscription(quiet=1,run=1)
    portal_sync = self.getSynchronizationTool()
    synchronization_list = portal_sync.getSynchronizationList()
    self.failUnless(len(synchronization_list)==self.nb_synchronization)

  def testGetObjectList(self, quiet=0, run=run_all_test):
    """
    This test the default getObjectList, ie, when the
    query is 'objectValues', and this also test if we enter
    a new method for the query
    """
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest getObjectList ')
      LOG('Testing... ',0,'testGetObjectList')
    self.login()
    self.setupPublicationAndSubscription(quiet=1,run=1)
    nb_person = self.populatePersonServer(quiet=1,run=1)
    portal_sync = self.getSynchronizationTool()
    publication_list = portal_sync.getPublicationList()
    publication = publication_list[0]
    object_list = publication.getObjectList()
    self.failUnless(len(object_list)==nb_person)
    # now try to set a different method for query
    def query(object):
      object_list = object.objectValues()
      return_list = []
      for o in object_list:
        if o.getId()==self.id1:
          return_list.append(o)
      return return_list
    publication.setQuery(query)
    object_list = publication.getObjectList()
    self.failUnless(len(object_list)==1)

  def testExportImport(self, quiet=0, run=run_all_test):
    """
    We will try to export a person with asXML
    And then try to add it to another folder with a conduit
    """
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Export and Import ')
      LOG('Testing... ',0,'testExportImport')
    self.login()
    self.populatePersonServer(quiet=1,run=1)
    person_server = self.getPersonServer()
    person_client1 = self.getPersonClient1()
    person = person_server._getOb(self.id1)
    xml_output = person.asXML()
    conduit = ERP5Conduit()
    conduit.addNode(object=person_client1,xml=xml_output)
    self.failUnless(len(person_client1.objectValues())==1)
    new_object = person_client1._getOb(self.id1)
    self.failUnless(new_object.getLastName()==self.last_name1)
    self.failUnless(new_object.getFirstName()==self.first_name1)
    # XXX We should also looks at the workflow history
    self.failUnless(len(new_object.workflow_history[self.workflow_id])==2)
    s_local_role = person_server.get_local_roles()
    c_local_role = person_client1.get_local_roles()
    self.assertEqual(s_local_role,c_local_role)

  def synchronize(self, id, run=run_all_test):
    """
    This just define how we synchronize, we have
    to define it here because it is specific to the unit testing
    """
    portal_sync = self.getSynchronizationTool()
    portal_sync.email = None
    subscription = portal_sync.getSubscription(id)
    publication = None
    for publication in portal_sync.getPublicationList():
      if publication.getPublicationUrl()==subscription.getSubscriptionUrl():
        publication = publication
    self.failUnless(publication is not None)
    # reset files, because we do sync by files
    file = open('/tmp/sync_client','w')
    file.write('')
    file.close()
    file = open('/tmp/sync','w')
    file.write('')
    file.close()
    nb_message = 1
    has_response = portal_sync.SubSync(subscription.getId())
    while has_response==1:
      portal_sync.PubSync(publication.getId())
      has_response = portal_sync.SubSync(subscription.getId())
      nb_message += 1 + has_response
    return nb_message

  def testFirstSynchronization(self, quiet=0, run=run_all_test):
    # We will try to populate the folder person_client1
    # with the data form person_server
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest First Synchronization ')
      LOG('Testing... ',0,'testFirstSynchronization')
    self.login()
    self.setupPublicationAndSubscription(quiet=1,run=1)
    nb_person = self.populatePersonServer(quiet=1,run=1)
    # Synchronize the first client
    nb_message1 = self.synchronize(self.sub_id1)
    self.failUnless(nb_message1==self.nb_message_first_synchronization)
    # Synchronize the second client
    nb_message2 = self.synchronize(self.sub_id2)
    self.failUnless(nb_message2==self.nb_message_first_synchronization)
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync.getSubscription(self.sub_id1)
    subscription2 = portal_sync.getSubscription(self.sub_id2)
    self.failUnless(len(subscription1.getObjectList())==nb_person)
    person_server = self.getPersonServer() # We also check we don't
                                           # modify initial ob
    person1_s = person_server._getOb(self.id1)
    self.failUnless(person1_s.getId()==self.id1)
    self.failUnless(person1_s.getFirstName()==self.first_name1)
    self.failUnless(person1_s.getLastName()==self.last_name1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    self.failUnless(person1_c.getId()==self.id1)
    self.failUnless(person1_c.getFirstName()==self.first_name1)
    self.failUnless(person1_c.getLastName()==self.last_name1)
    self.failUnless(len(subscription2.getObjectList())==nb_person)
    person_client2 = self.getPersonClient2()
    person2_c = person_client2._getOb(self.id1)
    self.failUnless(person2_c.getId()==self.id1)
    self.failUnless(person2_c.getFirstName()==self.first_name1)
    self.failUnless(person2_c.getLastName()==self.last_name1)

  def testGetObjectFromGid(self, quiet=0, run=run_all_test):
    # We will try to get an object from a publication
    # just by givin the gid
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest getObjectFromGid ')
      LOG('Testing... ',0,'testGetObjectFromGid')
    self.login()
    self.setupPublicationAndSubscription(quiet=1,run=1)
    self.populatePersonServer(quiet=1,run=1)
    # By default we can just give the id
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync.getPublication(self.pub_id)
    object = publication.getObjectFromGid(self.id1)
    self.failUnless(object is not None)
    self.failUnless(object.getId()==self.id1)

  def testGetSynchronizationState(self, quiet=0, run=run_all_test):
    # We will try to get the state of objects
    # that are just synchronized,
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest getSynchronizationState ')
      LOG('Testing... ',0,'testGetSynchronizationState')
    self.testFirstSynchronization(quiet=1,run=1)
    portal_sync = self.getSynchronizationTool()
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    state_list_s = portal_sync.getSynchronizationState(person1_s)
    self.failUnless(len(state_list_s)==self.nb_subscription) # one state
                                                  # for each subscriber
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    state_list_c = portal_sync.getSynchronizationState(person1_c)
    self.failUnless(len(state_list_c)==1) # one state
                                        # for each subscriber
    self.checkSynchronizationStateIsSynchronized()

  def checkSynchronizationStateIsSynchronized(self, quiet=0, run=run_all_test):
    portal_sync = self.getSynchronizationTool()
    person_server = self.getPersonServer()
    for person in person_server.objectValues():
      state_list = portal_sync.getSynchronizationState(person)
      for state in state_list:
        self.failUnless(state[1]==state[0].SYNCHRONIZED)
    person_client1 = self.getPersonClient1()
    for person in person_client1.objectValues():
      state_list = portal_sync.getSynchronizationState(person)
      for state in state_list:
        self.failUnless(state[1]==state[0].SYNCHRONIZED)
    person_client2 = self.getPersonClient2()
    for person in person_client2.objectValues():
      state_list = portal_sync.getSynchronizationState(person)
      for state in state_list:
        self.failUnless(state[1]==state[0].SYNCHRONIZED)

  def testUpdateSimpleData(self, quiet=0, run=run_all_test):
    # We will try to update some simple data, first
    # we change on the server side, the on the client side
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Update Simple Data ')
      LOG('Testing... ',0,'testUpdateSimpleData')
    self.testFirstSynchronization(quiet=1,run=1)
    # First we do only modification on server
    portal_sync = self.getSynchronizationTool()
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    kw = {'first_name':self.first_name3,'last_name':self.last_name3}
    person1_s.edit(**kw)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    self.failUnless(person1_s.getFirstName()==self.first_name3)
    self.failUnless(person1_s.getLastName()==self.last_name3)
    self.failUnless(person1_c.getFirstName()==self.first_name3)
    self.failUnless(person1_c.getLastName()==self.last_name3)
    # Then we do only modification on a client
    kw = {'first_name':self.first_name1,'last_name':self.last_name1}
    person1_c.edit(**kw)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(person1_s.getFirstName()==self.first_name1)
    self.failUnless(person1_s.getLastName()==self.last_name1)
    self.failUnless(person1_c.getFirstName()==self.first_name1)
    self.failUnless(person1_c.getLastName()==self.last_name1)
    # Then we do only modification on both the client and the server
    # and of course, on the same object
    kw = {'first_name':self.first_name3}
    person1_s.edit(**kw)
    kw = {'description':self.description3}
    person1_c.edit(**kw)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(person1_s.getFirstName()==self.first_name3)
    self.failUnless(person1_s.getDescription()==self.description3)
    self.failUnless(person1_c.getFirstName()==self.first_name3)
    self.failUnless(person1_c.getDescription()==self.description3)

  def testGetConflictList(self, quiet=0, run=run_all_test):
    # We will try to generate a conflict and then to get it
    # We will also make sure it contains what we want
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Get Conflict List ')
      LOG('Testing... ',0,'testGetConflictList')
    self.testFirstSynchronization(quiet=1,run=1)
    # First we do only modification on server
    portal_sync = self.getSynchronizationTool()
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person1_s.setDescription(self.description2)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    person1_c.setDescription(self.description3)
    self.synchronize(self.sub_id1)
    conflict_list = portal_sync.getConflictList()
    self.failUnless(len(conflict_list)==1)
    conflict = conflict_list[0]
    self.failUnless(person1_c.getDescription()==self.description3)
    self.failUnless(person1_s.getDescription()==self.description2)
    self.failUnless(conflict.getPropertyId()=='description')
    self.failUnless(conflict.getPublisherValue()==self.description2)
    self.failUnless(conflict.getSubscriberValue()==self.description3)
    subscriber = conflict.getSubscriber()
    self.failUnless(subscriber.getSubscriptionUrl()==self.subscription_url1)

  def testApplyPublisherValue(self, quiet=0, run=run_all_test):
    # We will try to generate a conflict and then to get it
    # We will also make sure it contains what we want
    if not run: return
    self.testGetConflictList(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Apply Publisher Value ')
      LOG('Testing... ',0,'testApplyPublisherValue')
    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    conflict = conflict_list[0]
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    conflict.applyPublisherValue()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(person1_c.getDescription()==self.description2)
    self.failUnless(person1_s.getDescription()==self.description2)
    conflict_list = portal_sync.getConflictList()
    self.failUnless(len(conflict_list)==0)

  def testApplySubscriberValue(self, quiet=0, run=run_all_test):
    # We will try to generate a conflict and then to get it
    # We will also make sure it contains what we want
    if not run: return
    self.testGetConflictList(quiet=1,run=1)
    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    if not quiet:
      ZopeTestCase._print('\nTest Apply Subscriber Value ')
      LOG('Testing... ',0,'testApplySubscriberValue')
    conflict = conflict_list[0]
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    conflict.applySubscriberValue()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(person1_s.getDescription()==self.description3)
    self.failUnless(person1_c.getDescription()==self.description3)
    conflict_list = portal_sync.getConflictList()
    self.failUnless(len(conflict_list)==0)

  def populatePersonServerWithSubObject(self, quiet=0, run=run_all_test):
    """
    Before this method, we need to call populatePersonServer
    Then it will give the following tree :
    - person_server :
      - id1
        - id1
          - id2
          - id1
      - id2
    """
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Populate Person Server With Sub Object ')
      LOG('Testing... ',0,'populatePersonServerWithSubObject')
    person_server = self.getPersonServer()
    person1 = person_server._getOb(self.id1)
    sub_person1 = person1.newContent(id=self.id1,portal_type='Person')
    kw = {'first_name':self.first_name1,'last_name':self.last_name1,
          'description':self.description1}
    sub_person1.edit(**kw)
    sub_sub_person1 = sub_person1.newContent(id=self.id1,portal_type='Person')
    kw = {'first_name':self.first_name1,'last_name':self.last_name1,
          'description':self.description1}
    sub_sub_person1.edit(**kw)
    sub_sub_person2 = sub_person1.newContent(id=self.id2,portal_type='Person')
    kw = {'first_name':self.first_name2,'last_name':self.last_name2,
          'description':self.description2}
    sub_sub_person2.edit(**kw)
    # remove ('','portal...','person_server')
    len_path = len(sub_sub_person1.getPhysicalPath()) - 3 
    self.failUnless(len_path==3)
    len_path = len(sub_sub_person2.getPhysicalPath()) - 3 
    self.failUnless(len_path==3)

  def testAddSubObject(self, quiet=0, run=run_all_test):
    """
    In this test, we synchronize, then add sub object on the
    server and then see if the next synchronization will also
    create sub-objects on the client
    """
    if not run: return
    self.testFirstSynchronization(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Add Sub Object ')
      LOG('Testing... ',0,'testAddSubObject')
    self.populatePersonServerWithSubObject(quiet=1,run=1)
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    sub_person1_c = person1_c._getOb(self.id1)
    sub_sub_person1 = sub_person1_c._getOb(self.id1)
    sub_sub_person2 = sub_person1_c._getOb(self.id2)
    # remove ('','portal...','person_server')
    len_path = len(sub_sub_person1.getPhysicalPath()) - 3 
    self.failUnless(len_path==3)
    len_path = len(sub_sub_person2.getPhysicalPath()) - 3 
    self.failUnless(len_path==3)
    self.failUnless(sub_sub_person1.getDescription()==self.description1)
    self.failUnless(sub_sub_person1.getFirstName()==self.first_name1)
    self.failUnless(sub_sub_person1.getLastName()==self.last_name1)
    self.failUnless(sub_sub_person2.getDescription()==self.description2)
    self.failUnless(sub_sub_person2.getFirstName()==self.first_name2)
    self.failUnless(sub_sub_person2.getLastName()==self.last_name2)

  def testUpdateSubObject(self, quiet=0, run=run_all_test):
    """
      In this test, we start with a tree of object already
    synchronized, then we update a subobject, and we will see
    if it is updated correctly.
      To make this test a bit more harder, we will update on both
    the client and the server by the same time
    """
    if not run: return
    self.testAddSubObject(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Update Sub Object ')
      LOG('Testing... ',0,'testUpdateSubObject')
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    sub_person1_c = person1_c._getOb(self.id1)
    sub_sub_person_c = sub_person1_c._getOb(self.id2)
    person_server = self.getPersonServer()
    sub_sub_person_s = person_server._getOb(self.id1)._getOb(self.id1)._getOb(self.id2)
    kw = {'first_name':self.first_name3}
    sub_sub_person_c.edit(**kw)
    kw = {'description':self.description3}
    sub_sub_person_s.edit(**kw)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(sub_sub_person_c.getDescription()==self.description3)
    self.failUnless(sub_sub_person_c.getFirstName()==self.first_name3)
    self.failUnless(sub_sub_person_s.getDescription()==self.description3)
    self.failUnless(sub_sub_person_s.getFirstName()==self.first_name3)

  def testDeleteObject(self, quiet=0, run=run_all_test):
    """
      We will do a first synchronization, then delete an object on both
    sides, and we will see if nothing is left on the server and also
    on the two clients
    """
    if not run: return
    self.testFirstSynchronization(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Delete Object ')
      LOG('Testing... ',0,'testDeleteObject')
    person_server = self.getPersonServer()
    person_server.manage_delObjects(self.id1)
    person_client1 = self.getPersonClient1()
    person_client1.manage_delObjects(self.id2)
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync.getPublication(self.pub_id)
    subscription1 = portal_sync.getSubscription(self.sub_id1)
    subscription2 = portal_sync.getSubscription(self.sub_id2)
    self.failUnless(len(publication.getObjectList())==0)
    self.failUnless(len(subscription1.getObjectList())==0)
    self.failUnless(len(subscription2.getObjectList())==0)

  def testDeleteSubObject(self, quiet=0, run=run_all_test):
    """
      We will do a first synchronization, then delete a sub-object on both
    sides, and we will see if nothing is left on the server and also
    on the two clients
    - before :         after :
      - id1             - id1 
        - id1             - id1
          - id2         - id2
          - id1
      - id2
    """
    if not run: return
    self.testAddSubObject(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Delete Sub Object ')
      LOG('Testing... ',0,'testDeleteSubObject')
    person_server = self.getPersonServer()
    sub_object_s = person_server._getOb(self.id1)._getOb(self.id1)
    sub_object_s.manage_delObjects(self.id1)
    person_client1 = self.getPersonClient1()
    sub_object_c1 = person_client1._getOb(self.id1)._getOb(self.id1)
    sub_object_c1.manage_delObjects(self.id2)
    person_client2 = self.getPersonClient2()
    sub_object_c2 = person_client2._getOb(self.id1)._getOb(self.id1)
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    len_s = len(sub_object_s.objectValues())
    len_c1 = len(sub_object_c1.objectValues())
    len_c2 = len(sub_object_c2.objectValues())
    self.failUnless(len_s==len_c1==len_c2==0)

  def testGetConflictListOnSubObject(self, quiet=0, run=run_all_test):
    """
    We will change several attributes on a sub object on both the server
    and a client, then we will see if we have correctly the conflict list
    """
    if not run: return
    self.testAddSubObject(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Get Conflict List On Sub Object ')
      LOG('Testing... ',0,'testGetConflictListOnSubObject')
    person_server = self.getPersonServer()
    object_s = person_server._getOb(self.id1)
    sub_object_s = object_s._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    sub_object_c1 = person_client1._getOb(self.id1)._getOb(self.id1)
    person_client2 = self.getPersonClient2()
    sub_object_c2 = person_client2._getOb(self.id1)._getOb(self.id1)
    # Change values so that we will get conflicts
    kw = {'language':self.lang2,'description':self.description2}
    sub_object_s.edit(**kw)
    kw = {'language':self.lang3,'description':self.description3}
    sub_object_c1.edit(**kw)
    self.synchronize(self.sub_id1)
    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    self.failUnless(len(conflict_list)==2)
    conflict_list = portal_sync.getConflictList(sub_object_c1)
    self.failUnless(len(conflict_list)==0)
    conflict_list = portal_sync.getConflictList(object_s)
    self.failUnless(len(conflict_list)==0)
    conflict_list = portal_sync.getConflictList(sub_object_s)
    self.failUnless(len(conflict_list)==2)

  def testApplyPublisherDocumentOnSubObject(self, quiet=0, run=run_all_test):
    """
    there's several conflict on a sub object, we will see if we can
    correctly have the publisher version of this document
    """
    if not run: return
    self.testGetConflictListOnSubObject(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Apply Publisher Document On Sub Object ')
      LOG('Testing... ',0,'testApplyPublisherDocumentOnSubObject')
    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    conflict = conflict_list[0]
    conflict.applyPublisherDocument()
    person_server = self.getPersonServer()
    sub_object_s = person_server._getOb(self.id1)._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    sub_object_c1 = person_client1._getOb(self.id1)._getOb(self.id1)
    person_client2 = self.getPersonClient2()
    sub_object_c2 = person_client2._getOb(self.id1)._getOb(self.id1)
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(sub_object_s.getDescription()==self.description2)
    self.failUnless(sub_object_s.getLanguage()==self.lang2)
    self.failUnless(sub_object_c1.getDescription()==self.description2)
    self.failUnless(sub_object_c1.getLanguage()==self.lang2)
    self.failUnless(sub_object_c2.getDescription()==self.description2)
    self.failUnless(sub_object_c2.getLanguage()==self.lang2)

  def testApplySubscriberDocumentOnSubObject(self, quiet=0, run=run_all_test):
    """
    there's several conflict on a sub object, we will see if we can
    correctly have the subscriber version of this document
    """
    if not run: return
    self.testGetConflictListOnSubObject(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Apply Subscriber Document On Sub Object ')
      LOG('Testing... ',0,'testApplySubscriberDocumentOnSubObject')
    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    conflict = conflict_list[0]
    conflict.applySubscriberDocument()
    person_server = self.getPersonServer()
    sub_object_s = person_server._getOb(self.id1)._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    sub_object_c1 = person_client1._getOb(self.id1)._getOb(self.id1)
    person_client2 = self.getPersonClient2()
    sub_object_c2 = person_client2._getOb(self.id1)._getOb(self.id1)
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(sub_object_s.getDescription()==self.description3)
    self.failUnless(sub_object_s.getLanguage()==self.lang3)
    self.failUnless(sub_object_c1.getDescription()==self.description3)
    self.failUnless(sub_object_c1.getLanguage()==self.lang3)
    self.failUnless(sub_object_c2.getDescription()==self.description3)
    self.failUnless(sub_object_c2.getLanguage()==self.lang3)

  def testSynchronizeWithStrangeGid(self, quiet=0, run=run_all_test):
    """
    By default, the synchronization process use the id in order to
    recognize objects (because by default, getGid==getId. Here, we will see 
    if it also works with a somewhat strange getGid
    """
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Synchronize With Strange Gid ')
      LOG('Testing... ',0,'testSynchronizeWithStrangeGid')
    self.login()
    self.setupPublicationAndSubscriptionAndGid(quiet=1,run=1)
    nb_person = self.populatePersonServer(quiet=1,run=1)
    # This will test adding object
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync.getSubscription(self.sub_id1)
    self.failUnless(len(subscription1.getObjectList())==nb_person)
    publication = portal_sync.getPublication(self.pub_id)
    self.failUnless(len(publication.getObjectList())==nb_person)
    gid = self.first_name1 +  ' ' + self.last_name1 # ie the title 'Sebastien Robin'
    person_c1 = subscription1.getObjectFromGid(gid)
    id_c1 = person_c1.getId()
    self.failUnless(id_c1 in ('1','2')) # id given by the default generateNewId
    person_s = publication.getObjectFromGid(gid)
    id_s = person_s.getId()
    self.failUnless(id_s==self.id1)
    # This will test updating object
    person_s.setDescription(self.description3)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(person_s.getDescription()==self.description3)
    self.failUnless(person_c1.getDescription()==self.description3)
    # This will test deleting object
    person_server = self.getPersonServer()
    person_client1 = self.getPersonClient1()
    person_server.manage_delObjects(self.id2)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(len(subscription1.getObjectList())==(nb_person-1))
    self.failUnless(len(publication.getObjectList())==(nb_person-1))
    person_s = publication.getObjectFromGid(gid)
    person_c1 = subscription1.getObjectFromGid(gid)
    self.failUnless(person_s.getDescription()==self.description3)
    self.failUnless(person_c1.getDescription()==self.description3)

  def testMultiNodeConflict(self, quiet=0, run=run_all_test):
    """
    We will create conflicts with 3 differents nodes, and we will
    solve it by taking one full version of documents.
    """
    if not run: return
    self.testFirstSynchronization(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Multi Node Conflict ')
      LOG('Testing... ',0,'testMultiNodeConflict')
    portal_sync = self.getSynchronizationTool()
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    kw = {'language':self.lang2,'description':self.description2,
          'format':self.format2}
    person1_s.edit(**kw)
    person_client1 = self.getPersonClient1()
    person1_c1 = person_client1._getOb(self.id1)
    kw = {'language':self.lang3,'description':self.description3,
          'format':self.format3}
    person1_c1.edit(**kw)
    person_client2 = self.getPersonClient2()
    person1_c2 = person_client2._getOb(self.id1)
    kw = {'language':self.lang4,'description':self.description4,
          'format':self.format4}
    person1_c2.edit(**kw)
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    conflict_list = portal_sync.getConflictList()
    self.failUnless(len(conflict_list)==6)
    # we will take :
    # description on person_server
    # language on person_client1
    # format on person_client2
    for conflict in conflict_list:
      subscriber = conflict.getSubscriber()
      property = conflict.getPropertyId()
      resolve = 0
      if property == 'language':
        if subscriber.getSubscriptionUrl()==self.subscription_url1:
          resolve = 1
          conflict.applySubscriberValue()
      if property == 'format':
        if subscriber.getSubscriptionUrl()==self.subscription_url2:
          resolve = 1
          conflict.applySubscriberValue()
      if not resolve:
        conflict.applyPublisherValue()
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(person1_s.getDescription()==self.description2)
    self.failUnless(person1_c1.getDescription()==self.description2)
    self.failUnless(person1_c2.getDescription()==self.description2)
    self.failUnless(person1_s.getLanguage()==self.lang3)
    self.failUnless(person1_c1.getLanguage()==self.lang3)
    self.failUnless(person1_c2.getLanguage()==self.lang3)
    self.failUnless(person1_s.getFormat()==self.format4)
    self.failUnless(person1_c1.getFormat()==self.format4)
    self.failUnless(person1_c2.getFormat()==self.format4)

  def testSynchronizeWorkflowHistory(self, quiet=0, run=run_all_test):
    """
    We will do a synchronization, then we will edit two times
    the object on the server, then two times the object on the
    client, and see if the global history as 4 more actions.
    """
    if not run: return
    self.testFirstSynchronization(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Synchronize WorkflowHistory ')
      LOG('Testing... ',0,'testSynchronizeWorkflowHistory')
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    kw1 = {'description':self.description1}
    kw2 = {'description':self.description2}
    len_wf = len(person1_s.workflow_history[self.workflow_id])
    person1_s.edit(**kw2)
    person1_c.edit(**kw2)
    person1_s.edit(**kw1)
    person1_c.edit(**kw1)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.failUnless(len(person1_s.workflow_history[self.workflow_id])==len_wf+4)
    self.failUnless(len(person1_c.workflow_history[self.workflow_id])==len_wf+4)

  def testUpdateLocalRole(self, quiet=0, run=run_all_test):
    """
    We will do a first synchronization, then modify, add and delete
    an user role and see if it is correctly synchronized
    """
    if not run: return
    self.testFirstSynchronization(quiet=1,run=1)
    if not quiet:
      ZopeTestCase._print('\nTest Update Local Role ')
      LOG('Testing... ',0,'testUpdateLocalRole')
    # First, Create a new user
    uf = self.getPortal().acl_users
    uf._doAddUser('jp', '', ['Manager'], [])
    user = uf.getUserById('jp').__of__(uf)
    # then update create and delete roles
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person2_s = person_server._getOb(self.id2)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    person2_c = person_client1._getOb(self.id2)
    person1_s.manage_setLocalRoles('seb',['Manager','Owner'])
    person2_s.manage_setLocalRoles('jp',['Manager','Owner'])
    person2_s.manage_delLocalRoles(['seb'])
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    role_1_s = person1_s.get_local_roles()
    role_2_s = person2_s.get_local_roles()
    role_1_c = person1_c.get_local_roles()
    role_2_c = person2_c.get_local_roles()
    self.assertEqual(role_1_s,role_1_c)
    self.assertEqual(role_2_s,role_2_c)

  # We may add a test in order to check if the slow_sync mode works fine, ie
  # if we do have both object on the client and server side, we must make sure
  # that the server first sends is own data

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestERP5SyncML))
        return suite

