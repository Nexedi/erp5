# -*- coding: utf-8 -*-
##############################################################################
# vim: set fileencoding=utf-8
# 
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Fabien Morin <fabien.morin@gmail.com>
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


import os, sys

from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5SyncML.Conduit.VCardConduit import VCardConduit
from testERP5SyncML import TestERP5SyncMLMixin
import transaction
from zLOG import LOG

class TestERP5SyncMLVCard(TestERP5SyncMLMixin):

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

      the business template sync_crm give 3 folders:
      /person_server 
      /person_client1 : empty
      /person_client2 : empty
    """
    return ('erp5_base', 'erp5_syncml',)
 
  def getTitle(self):
    return 'testERP5SyncMLVCard'

  def addVCardPublication(self):
    portal_sync = self.getSynchronizationTool()
    if getattr(portal_sync, self.pub_id, None) is None:
      pub = portal_sync.newContent(portal_type='SyncML Publication',
                             id=self.pub_id,
                             url_string=self.publication_url,
                             source='person_server',
                             source_reference='Person',
                             list_method_id='objectValues',
                             xml_binding_generator_method_id='Person_exportAsVCard',
                             conduit_module_id='SharedVCardConduit',
                             synchronisation_id_generator_method_id='generateNewId')
      pub.validate()
      transaction.commit()
      self.tic()

  def addVCardSubscription1(self):
    portal_sync = self.getSynchronizationTool()
    if getattr(portal_sync, self.sub_id1, None) is None:
      sub = portal_sync.newContent(portal_type='SyncML Subscription',
                             id=self.sub_id1,
                             url_string=self.publication_url,
                             subscription_url_string=self.subscription_url1,
                             source='person_client1',
                             source_reference='Person',
                             destination_reference='Person',
                             list_method_id='objectValues',
                             xml_binding_generator_method_id='Person_exportAsVCard',
                             conduit_module_id='SharedVCardConduit',
                             synchronisation_id_generator_method_id='generateNewId',
                             user_id='fab',
                             password='myPassword')
      sub.validate()
      transaction.commit()
      self.tic()

  def addVCardSubscription2(self):
    portal_sync = self.getSynchronizationTool()
    if getattr(portal_sync, self.sub_id2, None) is None:
      sub = portal_sync.newContent(portal_type='SyncML Subscription',
                             id=self.sub_id2,
                             url_string=self.publication_url,
                             subscription_url_string=self.subscription_url2,
                             source='person_client2',
                             source_reference='Person',
                             destination_reference='Person',
                             list_method_id='objectValues',
                             xml_binding_generator_method_id='Person_exportAsVCard',
                             conduit_module_id='SharedVCardConduit',
                             synchronisation_id_generator_method_id='generateNewId',
                             user_id='fab',
                             password='myPassword')
      sub.validate()
      transaction.commit()
      self.tic()

  def test_04_FirstVCardSynchronization(self):
    # We will try to populate the folder person_client1
    # with the data form person_server
    self.login()
    self.deletePublicationAndSubscriptionList()
    if 'person_server' in self.portal.objectIds():
      self.portal._delObject('person_server')
    if 'person_client1' in self.portal.objectIds():
      self.portal._delObject('person_client1')
    if 'person_client2' in self.portal.objectIds():
      self.portal._delObject('person_client2')
    self.addVCardPublication()
    self.addVCardSubscription1()
    self.addVCardSubscription2()
    nb_person = self.populatePersonServer()
    portal_sync = self.getSynchronizationTool()
    for sub in portal_sync.searchFolder(portal_type='SyncML Subscription'):
      self.assertEquals(sub.getSyncmlAlertCode(), 'two_way')
    # Synchronize the first client
    nb_message1 = self.synchronize(self.sub_id1)
    for sub in portal_sync.searchFolder(portal_type='SyncML Subscription'):
      self.assertEquals(sub.getSyncmlAlertCode(), 'two_way')
    self.assertEquals(nb_message1, self.nb_message_first_synchronization)
    # Synchronize the second client
    nb_message2 = self.synchronize(self.sub_id2)
    for sub in portal_sync.searchFolder(portal_type='SyncML Subscription'):
      self.assertEquals(sub.getSyncmlAlertCode(), 'two_way')
    self.assertEquals(nb_message2, self.nb_message_first_synchronization)
    self.checkFirstSynchronization(id='1', nb_person=nb_person)

  def test_05_basicVCardSynchronization(self):
    """
    synchronize two ERP5Sites using VCards
    """

    self.test_04_FirstVCardSynchronization()
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb('1') #The new person is added with a 
                                           #generate id (the first is 1)

    # try to synchronize    
    kw = {'first_name':self.first_name3,'last_name':self.last_name3}
    person1_c.edit(**kw)
    #before synchornization, First and Last name souldn't be the same
    self.verifyFirstNameAndLastNameAreNotSynchronized(self.first_name3,
      self.last_name3, person1_s, person1_c)
    self.synchronize(self.sub_id1)
    #after synchronization, a new person is create on the server
    person1_s = person_server._getOb('1')

    #after the synchro, the client and server should be synchronized
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(person1_s.getFirstName(), self.first_name3)
    self.assertEqual(person1_s.getLastName(), self.last_name3)
    self.assertEqual(person1_c.getFirstName(), self.first_name3)
    self.assertEqual(person1_c.getLastName(), self.last_name3)

  def test_05_verifyNoDuplicateDataWhenAdding(self):
    """
    this test permit to verify that if the server already have the person, 
    he don't add it a second time
    """
    self.test_04_FirstVCardSynchronization()
    portal_sync = self.getSynchronizationTool()
    pub = portal_sync[self.pub_id]
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb('1') #The new person is added with a 
                                           #generate id (the first is 1)

    # try to synchronize    
    kw = {'first_name':self.first_name3,'last_name':self.last_name3}
    person1_c.edit(**kw)
    person1_s.edit(**kw) #the same person is added on client AND server
    #before synchornization, First and Last name souldn't be the same
    self.assertEquals(person1_s.getFirstName(), self.first_name3)
    self.assertEquals(person1_s.getLastName(), self.last_name3)
    self.assertEquals(person1_c.getFirstName(), self.first_name3)
    self.assertEquals(person1_c.getLastName(), self.last_name3)
    nb_person_serv_before_sync = len(pub.getObjectList())
    self.synchronize(self.sub_id1)
    #after synchronization, no new person is created on server because it 
    #already have this person
    #person1_s = person_server._getOb('1') #The new person is added on the 
                                      #serverwith a generate id (the first is 1)

    #after the synchro, the client and server should be synchronized
    self.checkSynchronizationStateIsSynchronized()
    self.assertEquals(person1_s.getFirstName(), self.first_name3)
    self.assertEquals(person1_s.getLastName(), self.last_name3)
    self.assertEquals(person1_c.getFirstName(), self.first_name3)
    self.assertEquals(person1_c.getLastName(), self.last_name3)

    nb_person_serv_after_sync = len(pub.getObjectList())
    #the number of person on server before and after the synchronization should
    #be the same
    nb_person_serv_after_sync = len(pub.getObjectList())
    self.assertEquals(nb_person_serv_after_sync, nb_person_serv_before_sync)


import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5SyncMLVCard))
  return suite
