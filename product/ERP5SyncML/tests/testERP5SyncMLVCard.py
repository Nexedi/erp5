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
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
  
# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'
  
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5SyncML.Conduit.VCardConduit import VCardConduit
from Products.ERP5SyncML.SyncCode import SyncCode
from testERP5SyncML import TestERP5SyncMLMixin
from zLOG import LOG

class TestERP5SyncMLVCard(TestERP5SyncMLMixin, ERP5TypeTestCase):
  
  run_all_test = True

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

      the business template sync_crm give 3 folders:
      /person_server 
      /person_client1 : empty
      /person_client2 : empty
    """
    return ('erp5_base','fabien_bt')

  def test_01_AddVCardPublication(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Add a VCard Publication ')
      LOG('Testing... ',0,'test_36_AddVCardPublication')
    portal_id = self.getPortalName()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addPublication(self.pub_id, self.publication_url, 
        '/%s/person_server' % portal_id, 'Person', 'objectValues', 
        'Person_exportAsVCard', 'VCardConduit', '', 'generateNewId', 
        'getId', SyncCode.MEDIA_TYPE['TEXT_VCARD'])
    pub = portal_sync.getPublication(self.pub_id)
    self.failUnless(pub is not None)

  def test_02_AddVCardSubscription1(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Add First VCard Subscription ')
      LOG('Testing... ',0,'test_02_AddVCardSubscription1')
    portal_id = self.getPortalId()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addSubscription(self.sub_id1, self.publication_url, 
        self.subscription_url1, '/%s/person_client1' % portal_id,
        'Person', 'Person', 'objectValues', 'Person_exportAsVCard', 
        'VCardConduit', '', 'generateNewId', 'getId', 
        SyncCode.MEDIA_TYPE['TEXT_VCARD'])
    sub = portal_sync.getSubscription(self.sub_id1)
    self.failUnless(sub is not None)

  def test_03_AddVCardSubscription2(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Add Second VCard Subscription ')
      LOG('Testing... ',0,'test_03_AddVCardSubscription2')
    portal_id = self.getPortalId()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addSubscription(self.sub_id2, self.publication_url,
        self.subscription_url2, '/%s/person_client2' % portal_id,
        'Person', 'Person', 'objectValues', 'Person_exportAsVCard', 
        'VCardConduit', '', 'generateNewId', 'getId', 
        SyncCode.MEDIA_TYPE['TEXT_VCARD'])
    sub = portal_sync.getSubscription(self.sub_id2)
    self.failUnless(sub is not None)

  def test_04_FirstVCardSynchronization(self, quiet=0, run=run_all_test):
    # We will try to populate the folder person_client1
    # with the data form person_server
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest First VCard Synchronization ')
      LOG('Testing... ',0,'test_04_FirstVCardSynchronization')
    self.login()
    self.test_01_AddVCardPublication(quiet=True, run=True)
    self.test_02_AddVCardSubscription1(quiet=True, run=True)
    self.test_03_AddVCardSubscription2(quiet=True, run=True)
    nb_person = self.populatePersonServer(quiet=1,run=1)
    portal_sync = self.getSynchronizationTool()
    for sub in portal_sync.getSubscriptionList():
      self.assertEquals(sub.getSynchronizationType(),SyncCode.SLOW_SYNC)
    # Synchronize the first client
    nb_message1 = self.synchronize(self.sub_id1)
    for sub in portal_sync.getSubscriptionList():
      if sub.getTitle() == self.sub_id1:
        self.assertEquals(sub.getSynchronizationType(),SyncCode.TWO_WAY)
      else:
        self.assertEquals(sub.getSynchronizationType(),SyncCode.SLOW_SYNC)
    self.failUnless(nb_message1==self.nb_message_first_synchronization)
    # Synchronize the second client
    nb_message2 = self.synchronize(self.sub_id2)
    for sub in portal_sync.getSubscriptionList():
      self.assertEquals(sub.getSynchronizationType(),SyncCode.TWO_WAY)
    self.failUnless(nb_message2==self.nb_message_first_synchronization)
    self.checkFirstSynchronization(id='1', nb_person=nb_person)

  def test_05_basicVCardSynchronization(self, quiet=0, run=run_all_test):
    """
    synchronize two ERP5Sites using VCards
    """

    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Basic VCard Synchronization')
      LOG('Testing... ',0,'test_05_basicVCardSynchronization')

    self.test_04_FirstVCardSynchronization(quiet=True, run=True)
        
    
    portal_sync = self.getSynchronizationTool()
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
    person1_s = person_server._getOb('1') #The new person is added on the 
                                      #serverwith a generate id (the first is 1)

    #after the synchro, the client and server should be synchronized
    self.checkSynchronizationStateIsSynchronized()
    self.verifyFirstNameAndLastNameAreSynchronized(self.first_name3,
      self.last_name3, person1_s, person1_c)

  def test_05_verifyNoDuplicateDataWhenAdding(self, quiet=0, run=run_all_test):
    """
    this test permit to verify that if the server already have the person, 
    he don't add it a second time
    """
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest No Duplicate Data When Adding')
      LOG('Testing... ',0,'test_05_verifyNoDuplicateDataWhenAdding')
    self.test_04_FirstVCardSynchronization(quiet=True, run=True)
    portal_sync = self.getSynchronizationTool()
    sub1 = portal_sync.getSubscription(self.sub_id1)
    sub2 = portal_sync.getSubscription(self.sub_id2)
    pub = portal_sync.getPublication(self.pub_id)
    
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
    self.verifyFirstNameAndLastNameAreSynchronized(self.first_name3,
      self.last_name3, person1_s, person1_c)
    nb_person_serv_before_sync = len(pub.getObjectList())
    self.synchronize(self.sub_id1)
    #after synchronization, no new person is created on server because it 
    #already have this person
    #person1_s = person_server._getOb('1') #The new person is added on the 
                                      #serverwith a generate id (the first is 1)

    #after the synchro, the client and server should be synchronized
    self.checkSynchronizationStateIsSynchronized()
    self.verifyFirstNameAndLastNameAreSynchronized(self.first_name3,
      self.last_name3, person1_s, person1_c)
    
    nb_person_serv_after_sync = len(pub.getObjectList())
    #the number of person on server before and after the synchronization should
    #be the same
    nb_person_serv_after_sync = len(pub.getObjectList())
    self.failUnless(nb_person_serv_after_sync==nb_person_serv_before_sync)

    
    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestERP5SyncMLVCard))
        return suite
