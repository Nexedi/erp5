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
  first_name1 = 'Sebastien'
  last_name1 = 'Robin'
  description1 = 'description1'
  first_name2 = 'Jean-Paul'
  last_name2 = 'Smets'
  description2 = 'description2'
  first_name3 = 'Yoshinori'
  last_name3 = 'Okuji'
  description3 = 'description3'
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

  def testHasEverything(self, quiet=0):
    # Test if portal_synchronizations was created
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getSynchronizationTool()!=None)
    self.failUnless(self.getPersonServer()!=None)
    self.failUnless(self.getPersonClient1()!=None)
    self.failUnless(self.getPersonClient2()!=None)

  def testAddPublication(self, quiet=0):
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

  def testAddSubscription1(self, quiet=0):
    if not quiet:
      ZopeTestCase._print('\nTest Add First Subscription ')
      LOG('Testing... ',0,'testAddSubscription1')
    portal_id = self.getPortalId()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addSubscription(self.sub_id1,'server@localhost',
                          'client1@localhost','/%s/person_client1' % portal_id,'',
                          self.xml_mapping)
    sub = portal_sync.getSubscription(self.sub_id1)
    self.failUnless(sub is not None)

  def testAddSubscription2(self, quiet=0):
    if not quiet:
      ZopeTestCase._print('\nTest Add Second Subscription ')
      LOG('Testing... ',0,'testAddSubscription2')
    portal_id = self.getPortalId()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addSubscription(self.sub_id2,'server@localhost',
                          'client2@localhost','/%s/person_client2' % portal_id,'',
                          self.xml_mapping)
    sub = portal_sync.getSubscription(self.sub_id2)
    self.failUnless(sub is not None)

  def login(self, quiet=0):
    uf = self.getPortal().acl_users
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('ERP5TypeTestCase').__of__(uf)
    newSecurityManager(None, user)

  def testPopulatePersonServer(self, quiet=0):
    if not quiet:
      ZopeTestCase._print('\nTest Populate Person Server ')
      LOG('Testing... ',0,'testPopulatePersonServer')
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

  def setupPublicationAndSubscription(self, quiet=0):
    self.testAddPublication(quiet=quiet)
    self.testAddSubscription1(quiet=quiet)
    self.testAddSubscription2(quiet=quiet)

  def testGetSynchronizationList(self, quiet=0):
    # This test the getSynchronizationList, ie,
    # We want to see if we retrieve both the subscription
    # and the publication
    if not quiet:
      ZopeTestCase._print('\nTest getSynchronizationList ')
      LOG('Testing... ',0,'testGetSynchronizationList')
    self.setupPublicationAndSubscription(quiet=1)
    portal_sync = self.getSynchronizationTool()
    synchronization_list = portal_sync.getSynchronizationList()
    self.failUnless(len(synchronization_list)==self.nb_synchronization)

  def testGetObjectList(self, quiet=0):
    # This test the default getObjectList, ie, when the
    # query is 'objectValues', and this also test if we enter
    # a new method for the query
    if not quiet:
      ZopeTestCase._print('\nTest getObjectList ')
      LOG('Testing... ',0,'testGetObjectList')
    self.login()
    self.setupPublicationAndSubscription(quiet=1)
    nb_person = self.testPopulatePersonServer(quiet=1)
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

  def testExportImport(self, quiet=0):
    # We will try to export a person with asXML
    # And then try to add it to another folder with a conduit
    if not quiet:
      ZopeTestCase._print('\nTest Export and Import ')
      LOG('Testing... ',0,'testExportImport')
    self.login()
    self.testPopulatePersonServer(quiet=1)
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

  def synchronize(self, id):
    # This just define how we synchronize, we have
    # to define it here because it is specific to the unit testing
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

  def testFirstSynchronization(self, quiet=0):
    # We will try to populate the folder person_client1
    # with the data form person_server
    if not quiet:
      ZopeTestCase._print('\nTest First Synchronization ')
      LOG('Testing... ',0,'testFirstSynchronization')
    self.login()
    self.setupPublicationAndSubscription(quiet=1)
    nb_person = self.testPopulatePersonServer(quiet=1)
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

  def testGetObjectFromGid(self, quiet=0):
    # We will try to get an object from a publication
    # just by givin the gid
    if not quiet:
      ZopeTestCase._print('\nTest getObjectFromGid ')
      LOG('Testing... ',0,'testGetObjectFromGid')
    self.login()
    self.setupPublicationAndSubscription(quiet=1)
    self.testPopulatePersonServer(quiet=1)
    # By default we can just give the id
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync.getPublication(self.pub_id)
    object = publication.getObjectFromGid(self.id1)
    self.failUnless(object is not None)
    self.failUnless(object.getId()==self.id1)

  def testGetSynchronizationState(self, quiet=0):
    # We will try to get the state of objects
    # that are just synchronized,
    if not quiet:
      ZopeTestCase._print('\nTest getSynchronizationState ')
      LOG('Testing... ',0,'testGetSynchronizationState')
    self.testFirstSynchronization(quiet=1)
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

  def checkSynchronizationStateIsSynchronized(self, quiet=0):
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

  def testUpdateSimpleData(self, quiet=0):
    # We will try to update some simple data, first
    # we change on the server side, the on the client side
    if not quiet:
      ZopeTestCase._print('\nTest Update Simple Data ')
      LOG('Testing... ',0,'testUpdateSimpleData')
    self.testFirstSynchronization(quiet=1)
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
    # XXX Warning XXX This does not works actually, need to be CORRECTED !!!!
#     self.synchronize(self.sub_id1)
#     self.checkSynchronizationStateIsSynchronized()
#     self.failUnless(person1_s.getFirstName()==self.first_name3)
#     self.failUnless(person1_s.getDescription()==self.description3)
#     self.failUnless(person1_c.getFirstName()==self.first_name3)
#     self.failUnless(person1_c.getDescription()==self.description3)

  def testGetConflictList(self, quiet=0):
    # We will try to generate a conflict and then to get it
    if not quiet:
      ZopeTestCase._print('\nTest Get Conflict List ')
      LOG('Testing... ',0,'testGetConflictList')
    self.testFirstSynchronization(quiet=1)
    # First we do only modification on server
    portal_sync = self.getSynchronizationTool()
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person1_s.setDescription(self.description2)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    person1_c.setDescription(self.description3)
    self.synchronize(self.sub_id1)
    #self.checkSynchronizationStateIsSynchronized()



if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestERP5SyncML))
        return suite

