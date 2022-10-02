# -*- coding: utf-8 -*-
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
from base64 import b64encode, b64decode, b16encode
from lxml import etree
from unittest import expectedFailure
from six import string_types as basestring

from AccessControl.SecurityManagement import newSecurityManager
from ERP5Diff import ERP5Diff

from erp5.component.module.ERP5Conduit import ERP5Conduit
from erp5.component.module.XMLSyncUtils import encode, decode,\
     isDecodeEncodeTheSame
from erp5.component.module.XMLSyncUtils import getConduitByName
from erp5.component.module.SyncMLConstant import MAX_LEN
from erp5.component.document import SyncMLSubscription
from erp5.component.module.testERP5SyncMLMixin import TestERP5SyncMLMixin \
     as TestMixin

class TestERP5SyncMLMixin(TestMixin):

  # Different variables used for this test
  workflow_id = 'edit_workflow'
  first_name1 = 'Sebastien'
  last_name1 = 'Robin'
  # At the beginning, I was using iso-8859-15 strings, but actually
  # erp5 is using utf-8 everywhere
  #description1 = 'description1 --- $sdfrç_sdfsçdf_oisfsopf'
  description1 = 'description1 --- $sdfr\xc3\xa7_sdfs\xc3\xa7df_oisfsopf'
  lang1 = 'fr'
  format2 = 'html'
  format3 = 'xml'
  format4 = 'txt'
  first_name2 = 'Jean-Paul'
  last_name2 = 'Smets'
  #description2 = 'description2éà@  $*< <<<  ----- >>>></title>&oekd'
  description2 = 'description2\xc3\xa9\xc3\xa0@  $*< <<<  ----- >>>></title>&oekd'
  lang2 = 'en'
  first_name3 = 'Yoshinori'
  last_name3 = 'Okuji'
  #description3 = 'description3 çsdf__sdfççç_df___&&é]]]°°°°°°'
  description3 = 'description3 \xc3\xa7sdf__sdf\xc3\xa7\xc3\xa7\xc3\xa7_df___&&\xc3\xa9]]]\xc2\xb0\xc2\xb0\xc2\xb0\xc2\xb0\xc2\xb0\xc2\xb0'
  #description4 = 'description4 sdflkmooo^^^^]]]]]{{{{{{{'
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
  nb_message_first_sync_max_lines = 16
  activity_enabled = False


  def getTitle(self):
    return "ERP5SyncML Synchronous"

  def afterSetUp(self):
    """Setup."""
    self.login()
    self.portal.z_drop_syncml()
    self.portal.z_create_syncml()
    # This test creates Person inside Person, so we modifiy type information to
    # allow anything inside Person (we'll cleanup on teardown)
    self.getTypesTool().getTypeInfo('Person').filter_content_types = 0

    from Products.ERP5Type.tests.runUnitTest import tests_home
    self._subscription_url1 = tests_home + '/sync_client1'
    self._subscription_url2 = tests_home + '/sync_client2'
    self._publication_url = tests_home + '/sync_server'
    self.subscription_url1 = 'file:/' + self._subscription_url1
    self.subscription_url2 = 'file:/' + self._subscription_url2
    self.publication_url = 'file:/' + self._publication_url

  def beforeTearDown(self):
    """Clean up."""
    self.getTypesTool().getTypeInfo('Person').filter_content_types = 1
    self.clearFiles()
    self.getSynchronizationTool().manage_delObjects(
      ids=list(self.getSynchronizationTool().objectIds()))
    # clean modules
    for module in ["person_server", "person_client1", "person_client2"]:
      module = self.portal.get(module, None)
      if module:
        module.manage_delObjects(ids=list(module.objectIds()))
    self.tic()

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_core_proxy_field_legacy', 'erp5_base', 'erp5_syncml',)

  def getPersonClient1(self):
    return getattr(self.getPortalObject(), 'person_client1', None)

  def getPersonServer(self):
    return getattr(self.getPortalObject(), 'person_server', None)

  def getPersonClient2(self):
    return getattr(self.getPortalObject(), 'person_client2', None)

  def login(self, *args, **kw):
    uf = self.getPortal().acl_users
    uf._doAddUser('fab', 'myPassword', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    uf._doAddUser('syncml', '', ['Manager'], [])
    user = uf.getUserById('fab').__of__(uf)
    newSecurityManager(None, user)

  def initPersonModule(self):
    self.login()
    portal = self.getPortal()
    if getattr(portal, 'person_server', None) is None:
      portal.portal_types.constructContent(type_name = 'Person Module',
                                           container = portal,
                                           id = 'person_server')
    if getattr(portal, 'person_client1', None) is None:
      portal.portal_types.constructContent(type_name = 'Person Module',
                                           container = portal,
                                           id = 'person_client1')
    if getattr(portal, 'person_client2', None) is None:
      portal.portal_types.constructContent(type_name = 'Person Module',
                                           container = portal,
                                           id = 'person_client2')

  def populatePersonServer(self):
    self.login()
    self.initPersonModule()
    person_server = self.getPersonServer()
    if getattr(person_server, self.id1, None) is None:
      person_server.newContent(id=self.id1, portal_type='Person',
                               first_name=self.first_name1,
                               last_name=self.last_name1,
                               description=self.description1)
    if getattr(person_server, self.id2, None) is None:
      person_server.newContent(id=self.id2,
                               portal_type='Person',
                               first_name=self.first_name2,
                               last_name=self.last_name2,
                               description=self.description2)
    nb_person = len(person_server)
    self.assertEqual(nb_person, 2)
    return nb_person

  def populatePersonClient1(self):
    self.login()
    self.initPersonModule()
    person_client = self.getPersonClient1()
    number_of_object = 60
    for id_ in range(1, number_of_object+1):
      person_client.newContent(portal_type='Person',
                               id=id_,
                               first_name=self.first_name1,
                               last_name=self.last_name1,
                               description=self.description1)
    self.tic()
    nb_person = len(person_client)
    self.assertEqual(nb_person, number_of_object)
    return nb_person

  def clearFiles(self):
    # reset files, because we do sync by files
    file_ = open(self._subscription_url1, 'w')
    file_.write('')
    file_.close()
    file_ = open(self._subscription_url2, 'w')
    file_.write('')
    file_.close()
    file_ = open(self._publication_url, 'w')
    file_.write('')
    file_.close()

  def synchronize(self, id): # pylint: disable=redefined-builtin
    """
    This just define how we synchronize, we have
    to define it here because it is specific to the unit testing
    """
    portal_sync = self.getSynchronizationTool()
    subscription = portal_sync[id]
    pub_list = portal_sync.searchFolder(portal_type='SyncML Publication',
                       source_reference=subscription.getDestinationReference(),
                       validation_state='validated')
    self.assertEqual(len(pub_list), 1)
    publication = pub_list[0].getObject()
    self.clearFiles()
    nb_message = 1
    result = portal_sync.processClientSynchronization(subscription.getPath())
    # XXX-AUREL : in reality readResponse is called
    # Why is it not call here ? This make the behaviour of
    # the test rather different of what happens in real life !
    while len(result) > 0:
      result = portal_sync.processServerSynchronization(publication.getPath())
      self.tic()
      nb_message += 1
      if len(result) == 0:
        break
      result = portal_sync.processClientSynchronization(subscription.getPath())
      self.tic()
      nb_message += 1
    self.tic()
    return nb_message

  def synchronizeWithBrokenMessage(self, id): # pylint: disable=redefined-builtin
    """
    This just define how we synchronize, we have
    to define it here because it is specific to the unit testing
    """
    portal_sync = self.getSynchronizationTool()
    subscription = portal_sync[id]
    pub_list = portal_sync.searchFolder(portal_type='SyncML Publication',
                       source_reference=subscription.getDestinationReference(),
                       validation_state='validated')
    self.assertEqual(len(pub_list), 1)
    publication = pub_list[0].getObject()
    self.clearFiles()
    nb_message = 1
    result = portal_sync.processClientSynchronization(subscription.getPath())
    while result:
      # We do thing three times, so that we will test
      # if we manage well duplicate messages
      # only first call will return an answer
      result = portal_sync.processServerSynchronization(publication.getPath())
      self.tic()
      for _ in xrange(2):
        portal_sync.processServerSynchronization(publication.getPath())
        self.tic()
      nb_message += 1
      if not len(result):
        break
      result = portal_sync.processClientSynchronization(subscription.getPath())
      self.tic()
      for _ in xrange(2):
        portal_sync.processClientSynchronization(subscription.getPath())
        self.tic()
      nb_message += 1

    return nb_message

  def getSynchronizationState(self, context):
    """
    context : the context on which we are looking for state

    This functions have to retrieve the synchronization state,
    it will first look in the conflict list, if nothing is found,
    then we have to check on a publication/subscription.

    This method returns a mapping between subscription and states

    JPS suggestion:
      path -> object, document, context, etc.
      type -> '/titi/toto' or ('','titi', 'toto') or <Base instance 1562567>
      object = self.resolveContext(context) (method to add)

    """
    if context is None or isinstance(context, tuple):
      path = context
    elif isinstance(context, basestring):
      path = tuple(context.split('/'))
    else:
      path = context.getPhysicalPath()

    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    state_list = []
    append = state_list.append
    for conflict in conflict_list:
      if conflict.getOrigin() == path:
        append([conflict.getSubscriber(), 'conflict'])
    for domain in portal_sync.searchFolder():
      destination = domain.getSource()
      j_path = '/'.join(path)
      if destination in j_path:
        if domain.getPortalType() == 'SyncML Publication':
          subscriber_list = [result.getObject() for result in\
                             domain.searchFolder(portal_type='SyncML Subscription')]
        else:
          subscriber_list = [domain,]

        for subscriber in subscriber_list:
          gid = subscriber.getGidFromObject(context)
          signature = subscriber.getSignatureFromGid(gid)
          #XXX check if signature could be not None ...
          if signature is not None:
            state = signature.getValidationState()
            found = False
            # Make sure there is not already a conflict giving the state
            for state_item in state_list:
              if state_item[0] == subscriber:
                found = True
                break
            if not found:
              append([subscriber, state])
    return state_list


  def checkSynchronizationStateIsSynchronized(self):
    portal_sync = self.getSynchronizationTool()
    person_server = self.getPersonServer()
    for person in person_server.objectValues():
      state_list = self.getSynchronizationState(person)
      for state in state_list:
        self.assertEqual(state[1], 'no_conflict')
    person_client1 = self.getPersonClient1()
    for person in person_client1.objectValues():
      state_list = self.getSynchronizationState(person)
      for state in state_list:
        self.assertEqual(state[1], 'no_conflict')
    person_client2 = self.getPersonClient2()
    for person in person_client2.objectValues():
      state_list = self.getSynchronizationState(person)
      for state in state_list:
        self.assertEqual(state[1], 'no_conflict')
    # Check for each signature that the tempXML is None
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      for m in sub.contentValues():
        self.assertEqual(m.getTemporaryData(), None)
        self.assertEqual(m.getPartialData(), None)
        self.assertEqual(m.getValidationState(), "no_conflict")
    for pub in portal_sync.contentValues(portal_type='SyncML Publication'):
      for sub in pub.contentValues(portal_type='SyncML Subscription'):
        for m in sub.contentValues():
          self.assertEqual(m.getPartialData(), None)
          self.assertEqual(m.getValidationState(), "no_conflict")

  def verifyFirstNameAndLastNameAreNotSynchronized(self, first_name,
      last_name, person_server, person_client):
    """
      verify that the first and last name are NOT no_conflict
    """
    self.assertNotEqual(person_server.getFirstName(), first_name)
    self.assertNotEqual(person_server.getLastName(), last_name)
    self.assertEqual(person_client.getFirstName(), first_name)
    self.assertEqual(person_client.getLastName(), last_name)

  def checkFirstSynchronization(self, id=None, nb_person=0): # pylint: disable=redefined-builtin

    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync[self.sub_id1]
    subscription2 = portal_sync[self.sub_id2]
    self.assertEqual(len(subscription1.getDocumentList()), nb_person)
    person_server = self.getPersonServer() # We also check we don't
                                           # modify initial ob
    person1_s = person_server._getOb(self.id1)
    self.assertEqual(person1_s.getId(), self.id1)
    self.assertEqual(person1_s.getFirstName(), self.first_name1)
    self.assertEqual(person1_s.getLastName(), self.last_name1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(id)
    self.assertEqual(person1_c.getId(), id)
    self.assertEqual(person1_c.getFirstName(), self.first_name1)
    self.assertEqual(person1_c.getLastName(), self.last_name1)
    self.assertEqual(len(subscription2.getDocumentList()), nb_person)
    person_client2 = self.getPersonClient2()
    person2_c = person_client2._getOb(id)
    self.assertEqual(person2_c.getId(), id)
    self.assertEqual(person2_c.getFirstName(), self.first_name1)
    self.assertEqual(person2_c.getLastName(), self.last_name1)

  def resetSignaturePublicationAndSubscription(self):
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync[self.pub_id]
    subscription1 = portal_sync[self.sub_id1]
    publication.resetSubscriberList()
    subscription1.resetSignatureList()
    self.tic()

  def assertXMLViewIsEqual(self, sub_id, object_pub=None, object_sub=None,
                           force=False, ignore_processing_status_workflow=False):
    """
      Check the equality between two xml objects with gid as id
    """
    portal_sync = self.getSynchronizationTool()
    subscription = portal_sync[sub_id]
    publication = portal_sync[self.pub_id]
    gid_pub = publication.getGidFromObject(object_pub)
    gid_sub = publication.getGidFromObject(object_sub)
    self.assertEqual(gid_pub, gid_sub)
    conduit = getConduitByName(publication.getConduitModuleId())
    xml_pub = conduit.getXMLFromObjectWithGid(object=object_pub, gid=gid_pub,
                      xml_mapping=publication.getXmlBindingGeneratorMethodId())
    #if One Way From Server there is not xml_mapping for subscription
    conduit = getConduitByName(subscription.getConduitModuleId())
    xml_sub = conduit.getXMLFromObjectWithGid(object=object_sub, gid=gid_sub,
          xml_mapping=subscription.getXmlBindingGeneratorMethodId(force=force))
    erp5diff = ERP5Diff()
    erp5diff.compare(xml_pub, xml_sub)
    result = erp5diff.outputString()
    result = etree.XML(result)
    identity = True
    # edit workflow might not be updated, so discard workflow checking
    # revision is based on workflow history, can not be checked
    exclude_property_list = ('edit_workflow',)
    if object_pub.getPortalType() in self.portal.getPortalDocumentTypeList():
      exclude_property_list += ('revision',)
      # XXX: perhaps the tag could be added (insert-after or remove
      # for example) to check more precisely what property to ignore
      # in either the source or destination
      if ignore_processing_status_workflow:
        exclude_property_list += ('processing_status_workflow',)
    for update in result:
      select = update.get('select', '')
      new_edit_workflow_entry_xpath = 'xupdate:element/xupdate:attribute'\
                                     '[@name = "id"][text() = "edit_workflow"]'
      continue_for_excluded_property = False
      for exclude_property in exclude_property_list:
        if exclude_property in select:
          continue_for_excluded_property = True
      if continue_for_excluded_property or\
        update.xpath(new_edit_workflow_entry_xpath, namespaces=update.nsmap):
        continue
      else:
        identity = False
        break
    if not identity:
      self.fail('diff between pub:%s and sub:%s \n%s' % (object_pub.getPath(),
                                                         object_sub.getPath(),
                                   etree.tostring(result, pretty_print=True)))

  def deletePublicationAndSubscriptionList(self):
    portal_sync = self.getSynchronizationTool()
    id_list = [id_ for id_ in portal_sync.objectIds()]
    portal_sync.manage_delObjects(id_list)

class TestERP5SyncML(TestERP5SyncMLMixin):

  def getTitle(self):
    """
    """
    return "ERP5 SyncML"

  def setupPublicationAndSubscription(self):
    person_server = self.getPersonServer()
    if person_server is not None:
      portal = self.getPortal()
      portal._delObject(id='person_server')
      portal._delObject(id='person_client1')
      portal._delObject(id='person_client2')
      self.deletePublicationAndSubscriptionList()
    self.addPublication()
    self.addSubscription1()
    self.addSubscription2()

  def setupPublicationAndSubscriptionAndGid(self):
    self.setupPublicationAndSubscription()
    portal_sync = self.getSynchronizationTool()
    sub1 = portal_sync[self.sub_id1]
    sub2 = portal_sync[self.sub_id2]
    pub = portal_sync[self.pub_id]
    sub1.setConduitModuleId('ERP5ConduitTitleGid')
    sub2.setConduitModuleId('ERP5ConduitTitleGid')
    pub.setConduitModuleId('ERP5ConduitTitleGid')

  def checkSynchronizationStateIsConflict(self):
    person_server = self.getPersonServer()
    for person in person_server.objectValues():
      if person.getId()==self.id1:
        state_list = self.getSynchronizationState(person)
        for state in state_list:
          self.assertEqual(state[1], 'conflict')
    person_client1 = self.getPersonClient1()
    for person in person_client1.objectValues():
      if person.getId()==self.id1:
        state_list = self.getSynchronizationState(person)
        for state in state_list:
          self.assertEqual(state[1], 'conflict')
    person_client2 = self.getPersonClient2()
    for person in person_client2.objectValues():
      if person.getId()==self.id1:
        state_list = self.getSynchronizationState(person)
        for state in state_list:
          self.assertEqual(state[1], 'conflict')
    # make sure sub object are also in a conflict mode
    person = person_client1._getOb(self.id1)
    # use a temp_object to create a no persistent object in person
    sub_person =\
    person.newContent(id=self.id1, portal_type='Person', temp_object=1)
    state_list = self.getSynchronizationState(sub_person)
    for state in state_list:
      self.assertEqual(state[1], 'conflict')

  def populatePersonServerWithSubObject(self):
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
    person_server = self.getPersonServer()
    person1 = person_server._getOb(self.id1)
    sub_person1 = person1.newContent(id=self.id1, portal_type='Person')
    kw = {'first_name':self.first_name1,'last_name':self.last_name1,
        'description':self.description1}
    sub_person1.edit(**kw)
    sub_sub_person1 = sub_person1.newContent(id=self.id1, portal_type='Person')
    kw = {'first_name':self.first_name1,'last_name':self.last_name1,
        'description':self.description1, 'default_telephone_text':'0689778308'}
    sub_sub_person1.edit(**kw)
    sub_sub_person2 = sub_person1.newContent(id=self.id2, portal_type='Person')
    kw = {'first_name':self.first_name2,'last_name':self.last_name2,
          'description':self.description2}
    sub_sub_person2.edit(**kw)
    # remove ('','portal...','person_server')
    len_path = len(sub_sub_person1.getPhysicalPath()) - 3
    self.assertEqual(len_path, 3)
    len_path = len(sub_sub_person2.getPhysicalPath()) - 3
    self.assertEqual(len_path, 3)

  def addAuthenticationToPublication(self, publication_id, login, password,
      auth_format, auth_type):
    """
      add authentication to the publication
    """
    portal_sync = self.getSynchronizationTool()
    pub = portal_sync[publication_id]
    pub.setUserId(login)
    pub.setPassword(password)
    pub.setAuthenticationFormat(auth_format)
    pub.setAuthenticationType(auth_type)


  def addAuthenticationToSubscription(self, subscription_id, login, password,
      auth_format, auth_type):
    """
      add authentication to the subscription
    """
    portal_sync = self.getSynchronizationTool()
    sub = portal_sync[subscription_id]
    if sub.getAuthenticationState() != 'logged_out':
      sub.logout()
    sub.setUserId(login)
    sub.setPassword(password)
    sub.setAuthenticationFormat(auth_format)
    sub.setAuthenticationType(auth_type)


  def test_01_HasEverything(self):
    # Test if portal_synchronizations was created
    self.assertNotEqual(self.getSynchronizationTool(), None)
    #self.assertTrue(self.getPersonServer()!=None)
    #self.assertTrue(self.getPersonClient1()!=None)
    #self.assertTrue(self.getPersonClient2()!=None)

  def addPublication(self):
    portal_sync = self.getSynchronizationTool()
    if getattr(portal_sync, self.pub_id, None) is not None:
      portal_sync._delObject(self.pub_id)
    self.tic()
    publication = portal_sync.newContent(
                              portal_type='SyncML Publication',
                              id=self.pub_id,
                              url_string=self.publication_url,  # XXX to be removed, maybe
                              source='person_server',
                              source_reference='Person',
                              list_method_id='objectValues',
                              xml_binding_generator_method_id=self.xml_mapping,
                              conduit_module_id='ERP5Conduit',
                              is_activity_enabled=self.activity_enabled)
    publication.validate()
    self.tic()
    return publication

  def addSubscription1(self):
    portal_sync = self.getSynchronizationTool()
    if getattr(portal_sync, self.sub_id1, None) is not None:
      portal_sync._delObject(self.sub_id1)
    self.tic()
    subscription = portal_sync.newContent(portal_type='SyncML Subscription',
                              id=self.sub_id1,
                              url_string=self.publication_url,
                              subscription_url_string=self.subscription_url1,
                              source='person_client1',
                              source_reference='Person',
                              destination_reference='Person',
                              list_method_id='objectValues',
                              xml_binding_generator_method_id=self.xml_mapping,
                              conduit_module_id='ERP5Conduit',
                              is_activity_enabled=self.activity_enabled,
                              syncml_alert_code='two_way',
                              user_id='fab',
                              password='myPassword')
    subscription.validate()
    self.tic()

  def addSubscription2(self):
    portal_sync = self.getSynchronizationTool()
    if getattr(portal_sync, self.sub_id2, None) is not None:
      portal_sync._delObject(self.sub_id2)
    self.tic()
    subscription = portal_sync.newContent(portal_type='SyncML Subscription',
                              id=self.sub_id2,
                              url_string=self.publication_url,
                              subscription_url_string=self.subscription_url2,
                              source='person_client2',
                              source_reference='Person',
                              destination_reference='Person',
                              list_method_id='objectValues',
                              xml_binding_generator_method_id=self.xml_mapping,
                              conduit_module_id='ERP5Conduit',
                              is_activity_enabled=self.activity_enabled,
                              syncml_alert_code='two_way',
                              user_id='fab',
                              password='myPassword')
    subscription.validate()
    self.tic()

  def test_05_GetSynchronizationList(self):
    # This test the getSynchronizationList, ie,
    # We want to see if we retrieve both the subscription
    # and the publication
    self.setupPublicationAndSubscription()
    portal_sync = self.getSynchronizationTool()
    synchronization_list = portal_sync.objectValues()
    self.assertEqual(len(synchronization_list), self.nb_synchronization)

  def test_06_getDocumentList(self):
    """
    This test the default getDocumentList, ie, when the
    query is 'objectValues', and this also test if we enter
    a new method for the query
    """
    self.login()
    self.setupPublicationAndSubscription()
    nb_person = self.populatePersonServer()
    portal_sync = self.getSynchronizationTool()
    publication_list = portal_sync.contentValues(
                                              portal_type='SyncML Publication')
    publication = publication_list[0]
    object_list = publication.getDocumentList()
    self.assertEqual(len(object_list), nb_person)
    # now try to set a different method for query
    method_id = 'PersonServer_getDocumentList'
    ## add test cached method
    py_script_params = "**kw"
    py_script_body = """
return [context[%r]]
""" %  self.id1
    self.portal.manage_addProduct['PythonScripts'].manage_addPythonScript(
                                                                  id=method_id)
    py_script_obj = getattr(self.portal, method_id)
    py_script_obj.ZPythonScript_edit(py_script_params, py_script_body)
    publication.setListMethodId(method_id)
    object_list = publication.getDocumentList()
    self.assertEqual(len(object_list), 1)
    # Add the query path
    publication.setListMethodId('person_server/objectValues')
    object_list = publication.getDocumentList()
    self.assertEqual(len(object_list), nb_person)

  def test_07_ExportImport(self):
    """
    We will try to export a person with asXML
    And then try to add it to another folder with a conduit
    """
    self.login()
    self.populatePersonServer()
    person_server = self.getPersonServer()
    person_client1 = self.getPersonClient1()
    person = person_server._getOb(self.id1)
    xml_output = person.asXML()
    conduit = ERP5Conduit()
    conduit.addNode(object=person_client1, xml=xml_output)
    new_object = person_client1._getOb(self.id1)
    self.assertEqual(new_object.getLastName(), self.last_name1)
    self.assertEqual(new_object.getFirstName(), self.first_name1)
    self.assertEqual(person.asXML(), new_object.asXML())

  def test_08_FirstSynchronization(self):
    # We will try to populate the folder person_client1
    # with the data form person_server
    self.login()
    self.setupPublicationAndSubscription()
    nb_person = self.populatePersonServer()
    portal_sync = self.getSynchronizationTool()
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
    # Synchronize the first client
    nb_message1 = self.synchronize(self.sub_id1)
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      if sub.getTitle() == self.sub_id1:
        self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
      else:
        self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
    self.assertEqual(nb_message1, self.nb_message_first_synchronization)
    # Synchronize the second client
    nb_message2 = self.synchronize(self.sub_id2)
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
    self.assertEqual(nb_message2, self.nb_message_first_synchronization)
    self.checkFirstSynchronization(id=self.id1, nb_person=nb_person)

  def test_09_FirstSynchronizationWithLongLines(self):
    # We will try to populate the folder person_client1
    # with the data form person_server
    self.login()
    self.setupPublicationAndSubscription()
    nb_person = self.populatePersonServer()
    person_server = self.getPersonServer()
    long_line = 'a' * 10000 + ' --- '
    person1_s = person_server._getOb(self.id1)
    kw = {'first_name':long_line}
    person1_s.edit(**kw)
    # Synchronize the first client
    nb_message1 = self.synchronize(self.sub_id1)
    self.assertEqual(nb_message1, self.nb_message_first_synchronization)
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync[self.sub_id1]
    self.assertEqual(len(subscription1.getDocumentList()), nb_person)
    self.assertEqual(person1_s.getId(), self.id1)
    self.assertEqual(person1_s.getFirstName(), long_line)
    self.assertEqual(person1_s.getLastName(), self.last_name1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)

  def test_11_GetSynchronizationState(self):
    # We will try to get the state of objects
    # that are just synchronized
    self.test_08_FirstSynchronization()
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    state_list_s = self.getSynchronizationState(person1_s)
    self.assertEqual(len(state_list_s), self.nb_subscription) # one state
                                                  # for each subscriber
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    state_list_c = self.getSynchronizationState(person1_c)
    self.assertEqual(len(state_list_c), 1) # one state
                                        # for each subscriber
    self.checkSynchronizationStateIsSynchronized()

  def test_12_UpdateSimpleData(self):
    self.test_08_FirstSynchronization()
    # First we do only modification on server
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    kw = {'first_name':self.first_name3,'last_name':self.last_name3}
    person1_s.edit(**kw)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    self.assertEqual(person1_s.getFirstName(), self.first_name3)
    self.assertEqual(person1_s.getLastName(), self.last_name3)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    # Then we do only modification on a client
    kw = {'first_name':self.first_name1,'last_name':self.last_name1}
    person1_c.edit(**kw)
    #person1_c.setModificationDate(DateTime()+1)
    # import ipdb
    # ipdb.set_trace()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    person1_s = person_server._getOb(self.id1)
    self.assertEqual(person1_s.getFirstName(), self.first_name1)
    self.assertEqual(person1_s.getLastName(), self.last_name1)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    # Then we do only modification on both the client and the server
    # and of course, on the same object
    kw = {'first_name':self.first_name3}
    person1_s.edit(**kw)
    kw = {'description':self.description3}
    person1_c.edit(**kw)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    #person1_s = person_server._getOb(self.id1)
    self.assertEqual(person1_s.getFirstName(), self.first_name3)
    self.assertEqual(person1_s.getDescription(), self.description3)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)

  def test_13_GetConflictList(self):
    # We will try to generate a conflict and then to get it
    # We will also make sure it contains what we want
    self.test_08_FirstSynchronization()
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
    self.assertEqual(len(conflict_list), 1)
    conflict = conflict_list[0]
    self.assertEqual(person1_c.getDescription(), self.description3)
    self.assertEqual(person1_s.getDescription(), self.description2)
    self.assertEqual(conflict.getPropertyId(), 'description')
    self.assertEqual(conflict.getLocalValue(), self.description2)
    self.assertEqual(conflict.getRemoteValue(), self.description3)
    subscriber = conflict.getSubscriber()
    self.assertEqual(subscriber.getUrlString(), self.subscription_url1)

  def test_14_GetPublisherAndSubscriberDocument(self):
    # We will try to generate a conflict and then to get it
    # We will also make sure it contains what we want
    self.test_13_GetConflictList()
    # First we do only modification on server
    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    conflict = conflict_list[0]
    publisher_document = conflict.getPublisherDocument()
    self.assertEqual(publisher_document.getDescription(), self.description2)
    subscriber_document = conflict.getSubscriberDocument()
    self.assertEqual(subscriber_document.getDescription(), self.description3)

  def test_15_ApplyPublisherValue(self):
    # We will try to generate a conflict and then to get it
    # We will also make sure it contains what we want
    self.test_13_GetConflictList()
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
    self.assertEqual(person1_c.getDescription(), self.description2)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    conflict_list = portal_sync.getConflictList()
    self.assertEqual(len(conflict_list), 0)

  def test_16_ApplySubscriberValue(self):
    # We will try to generate a conflict and then to get it
    # We will also make sure it contains what we want
    self.test_13_GetConflictList()
    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    conflict = conflict_list[0]
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    conflict.applySubscriberValue()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(person1_s.getDescription(), self.description3)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    conflict_list = portal_sync.getConflictList()
    self.assertEqual(len(conflict_list), 0)

  def test_17_AddSubObject(self):
    """
    In this test, we synchronize, then add sub object on the
    server and then see if the next synchronization will also
    create sub-objects on the client
    """
    self.test_08_FirstSynchronization()
    self.populatePersonServerWithSubObject()
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
    self.assertEqual(len_path, 3)
    len_path = len(sub_sub_person2.getPhysicalPath()) - 3
    self.assertEqual(len_path, 3)
    self.assertEqual(sub_sub_person1.getDescription(), self.description1)
    self.assertEqual(sub_sub_person1.getFirstName(), self.first_name1)
    self.assertEqual(sub_sub_person1.getLastName(), self.last_name1)
    self.assertEqual(sub_sub_person1.getDefaultTelephoneText(), '+(0)-0689778308')
    self.assertEqual(sub_sub_person2.getDescription(), self.description2)
    self.assertEqual(sub_sub_person2.getFirstName(), self.first_name2)
    self.assertEqual(sub_sub_person2.getLastName(), self.last_name2)
    #check two side (client, server)
    person_server = self.getPersonServer()
    sub_sub_person_s = person_server._getOb(self.id1)._getOb(self.id1)._getOb(self.id1)
    self.assertXMLViewIsEqual(self.sub_id1, sub_sub_person_s, sub_sub_person1)

  def test_18_UpdateSubObject(self):
    """
      In this test, we start with a tree of object already
    synchronized, then we update a subobject, and we will see
    if it is updated correctly.
      To make this test a bit more harder, we will update on both
    the client and the server by the same time
    """
    self.test_17_AddSubObject()
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
    # refresh objects after synchronization
    sub_sub_person_c = sub_person1_c._getOb(self.id2)
    sub_sub_person_s = person_server._getOb(self.id1)._getOb(self.id1)._getOb(self.id2)
    #self.assertEqual(sub_sub_person_c.getDescription(), self.description3)
    #self.assertEqual(sub_sub_person_c.getFirstName(), self.first_name3)
    self.assertXMLViewIsEqual(self.sub_id1, sub_sub_person_s, sub_sub_person_c)

  def test_19_DeleteObject(self):
    """
      We will do a first synchronization, then delete an object on both
    sides, and we will see if nothing is left on the server and also
    on the two clients
    """
    self.test_08_FirstSynchronization()
    person_server = self.getPersonServer()
    person_server.manage_delObjects(self.id1)
    person_client1 = self.getPersonClient1()
    person_client1.manage_delObjects(self.id2)
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync[self.pub_id]
    subscription1 = portal_sync[self.sub_id1]
    subscription2 = portal_sync[self.sub_id2]
    self.assertEqual(len(publication.getDocumentList()), 0)
    self.assertEqual(len(subscription1.getDocumentList()), 0)
    self.assertEqual(len(subscription2.getDocumentList()), 0)

  def test_20_DeleteSubObject(self):
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
    self.test_17_AddSubObject()
    # Delete one on server
    person_server = self.getPersonServer()
    sub_object_s = person_server._getOb(self.id1)._getOb(self.id1)
    sub_object_s.manage_delObjects(self.id1)
    # Delete one on client 1
    person_client1 = self.getPersonClient1()
    sub_object_c1 = person_client1._getOb(self.id1)._getOb(self.id1)
    sub_object_c1.manage_delObjects(self.id2)
    # Do nothing on client 2
    person_client2 = self.getPersonClient2()
    sub_object_c2 = person_client2._getOb(self.id1)._getOb(self.id1)
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    # refresh objects
    sub_object_c1 = person_client1._getOb(self.id1)._getOb(self.id1)
    sub_object_c2 = person_client2._getOb(self.id1)._getOb(self.id1)
    len_s = len(sub_object_s.objectValues())
    len_c1 = len(sub_object_c1.objectValues())
    len_c2 = len(sub_object_c2.objectValues())
    self.assertTrue(len_s==len_c1==len_c2==0)

  def test_21_GetConflictListOnSubObject(self):
    """
    We will change several attributes on a sub object on both the server
    and a client, then we will see if we have correctly the conflict list
    """
    self.test_17_AddSubObject()
    person_server = self.getPersonServer()
    object_s = person_server._getOb(self.id1)
    sub_object_s = object_s._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    sub_object_c1 = person_client1._getOb(self.id1)._getOb(self.id1)
    # Change values so that we will get conflicts
    kw = {'language':self.lang2,'description':self.description2}
    sub_object_s.edit(**kw)
    kw = {'language':self.lang3,'description':self.description3}
    sub_object_c1.edit(**kw)
    self.synchronize(self.sub_id1)
    portal_sync = self.getSynchronizationTool()
    conflict_list = portal_sync.getConflictList()
    self.assertEqual(len(conflict_list), 2)
    conflict_list = portal_sync.getConflictList(sub_object_c1)
    self.assertEqual(len(conflict_list), 0)
    conflict_list = portal_sync.getConflictList(object_s)
    self.assertEqual(len(conflict_list), 0)
    conflict_list = portal_sync.getConflictList(sub_object_s)
    self.assertEqual(len(conflict_list), 2)

  def test_22_ApplyPublisherDocumentOnSubObject(self):
    """
    there's several conflict on a sub object, we will see if we can
    correctly have the publisher version of this document
    """
    self.test_21_GetConflictListOnSubObject()
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
    self.assertEqual(sub_object_s.getDescription(), self.description2)
    self.assertEqual(sub_object_s.getLanguage(), self.lang2)
    self.assertXMLViewIsEqual(self.sub_id1, sub_object_s, sub_object_c1)
    self.assertXMLViewIsEqual(self.sub_id2, sub_object_s, sub_object_c2)

  def test_23_ApplySubscriberDocumentOnSubObject(self):
    """
    there's several conflict on a sub object, we will see if we can
    correctly have the subscriber version of this document
    """
    self.test_21_GetConflictListOnSubObject()
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
    # refresh documents
    sub_object_s = person_server._getOb(self.id1)._getOb(self.id1)
    sub_object_c1 = person_client1._getOb(self.id1)._getOb(self.id1)
    sub_object_c2 = person_client2._getOb(self.id1)._getOb(self.id1)
    #self.assertEqual(sub_object_s.getDescription(), self.description3)
    #self.assertEqual(sub_object_s.getLanguage(), self.lang3)
    self.assertXMLViewIsEqual(self.sub_id1, sub_object_s, sub_object_c1)
    self.assertXMLViewIsEqual(self.sub_id2, sub_object_s, sub_object_c2)

  def test_24_SynchronizeWithStrangeGid(self):
    """
    By default, the synchronization process use the id in order to
    recognize objects (because by default, getGid==getId. Here, we will see
    if it also works with a somewhat strange getGid
    """
    self.login()
    self.setupPublicationAndSubscriptionAndGid()
    nb_person = self.populatePersonServer()
    # This will test adding object
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync[self.sub_id1]
    self.assertEqual(len(subscription1.getDocumentList()), nb_person)
    publication = portal_sync[self.pub_id]
    self.assertEqual(len(publication.getDocumentList()), nb_person)
    gid = self.first_name1 +  ' ' + self.last_name1 # ie the title 'Sebastien Robin'
    gid = b16encode(gid)
    person_c1 = subscription1.getDocumentFromGid(gid)
    person_s = publication.getSubscriber(self.subscription_url1).getDocumentFromGid(gid)
    id_s = person_s.getId()
    self.assertEqual(id_s, self.id1)
    # This will test updating object
    person_s.setDescription(self.description3)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(person_s.getDescription(), self.description3)
    self.assertEqual(person_c1.getDescription(), self.description3)
    self.assertXMLViewIsEqual(self.sub_id1, person_s, person_c1)
    # This will test deleting object
    person_server = self.getPersonServer()
    person_server.manage_delObjects(self.id2)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(len(subscription1.getDocumentList()), (nb_person-1))
    self.assertEqual(len(publication.getDocumentList()), (nb_person-1))
    person_s = publication.getSubscriber(self.subscription_url1).getDocumentFromGid(gid)
    person_c1 = subscription1.getDocumentFromGid(gid)
    self.assertEqual(person_s.getDescription(), self.description3)
    self.assertXMLViewIsEqual(self.sub_id1, person_s, person_c1)

  def test_25_MultiNodeConflict(self):
    """
    We will create conflicts with 3 differents nodes, and we will
    solve it by taking one full version of documents.
    """
    self.test_08_FirstSynchronization()
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
    self.assertEqual(len(conflict_list), 6)
    # check if we have the state conflict on all clients
    self.checkSynchronizationStateIsConflict()
    # we will take :
    # description on person_server
    # language on person_client1
    # format on person_client2

    for conflict in conflict_list :
      subscriber = conflict.getSubscriber()
      property_id = conflict.getPropertyId()
      resolve = 0
      if property_id == 'language':
        if subscriber.getUrlString() == self.subscription_url1:
          resolve = 1
          conflict.applySubscriberValue()
      if property_id == 'format':
        if subscriber.getUrlString() == self.subscription_url2:
          resolve = 1
          conflict.applySubscriberValue()
      if not resolve:
        conflict.applyPublisherValue()
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(person1_c1.getDescription(), self.description2)
    self.assertEqual(person1_c1.getLanguage(), self.lang3)
    self.assertEqual(person1_c1.getFormat(), self.format4)
    self.assertEqual(person1_s.getDescription(), self.description2)
    self.assertEqual(person1_s.getLanguage(), self.lang3)
    self.assertEqual(person1_s.getFormat(), self.format4)
    self.assertXMLViewIsEqual(self.sub_id2, person1_s, person1_c2)
    # the workflow has one more "edit_workflow" in person1_c1
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    self.assertXMLViewIsEqual(self.sub_id2, person1_s, person1_c2)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c1)

  def test_27_UpdateLocalRole(self):
    """
    We will do a first synchronization, then modify, add and delete
    an user role and see if it is correctly synchronized
    """
    self.test_08_FirstSynchronization()
    # First, Create a new user
    uf = self.getPortal().acl_users
    uf._doAddUser('jp', '', ['Manager'], [])
    # then update create and delete roles
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person2_s = person_server._getOb(self.id2)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    person2_c = person_client1._getOb(self.id2)
    person1_s.manage_setLocalRoles('fab',['Manager','Owner'])
    person2_s.manage_setLocalRoles('jp',['Manager','Owner'])
    person2_s.manage_delLocalRoles(['fab'])
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)
    # refresh documents
    person1_c = person_client1._getOb(self.id1)
    person2_c = person_client1._getOb(self.id2)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    self.assertXMLViewIsEqual(self.sub_id2, person2_s, person2_c)
    role_1_s = person1_s.get_local_roles()
    role_2_s = person2_s.get_local_roles()
    role_1_c = person1_c.get_local_roles()
    role_2_c = person2_c.get_local_roles()
    self.assertEqual(role_1_s,role_1_c)
    self.assertEqual(role_2_s,role_2_c)

  def test_28_PartialData(self):
    """
    We will do a first synchronization, then we will do a change, then
    we will modify the SyncCode max_line value so it
    it will generate many messages
    """
    self.test_08_FirstSynchronization()
    previous_max_lines = MAX_LEN
    try:
      SyncMLSubscription.MAX_LEN = 1 << 8
      self.populatePersonServerWithSubObject()
      self.checkSynchronizationStateIsSynchronized()
      self.synchronize(self.sub_id1)
      self.checkSynchronizationStateIsSynchronized()
      self.synchronize(self.sub_id2)
      self.checkSynchronizationStateIsSynchronized()
      person_client1 = self.getPersonClient1()
      person1_c = person_client1._getOb(self.id1)
      sub_person1_c = person1_c._getOb(self.id1)
      sub_sub_person1 = sub_person1_c._getOb(self.id1)
      sub_sub_person2 = sub_person1_c._getOb(self.id2)
      # remove ('','portal...','person_server')
      len_path = len(sub_sub_person1.getPhysicalPath()) - 3
      self.assertEqual(len_path, 3)
      len_path = len(sub_sub_person2.getPhysicalPath()) - 3
      self.assertEqual(len_path, 3)
      self.assertEqual(sub_sub_person1.getDescription(),self.description1)
      self.assertEqual(sub_sub_person1.getFirstName(),self.first_name1)
      self.assertEqual(sub_sub_person1.getLastName(),self.last_name1)
      self.assertEqual(sub_sub_person2.getDescription(),self.description2)
      self.assertEqual(sub_sub_person2.getFirstName(),self.first_name2)
      self.assertEqual(sub_sub_person2.getLastName(),self.last_name2)
    finally:
      SyncMLSubscription.MAX_LEN = previous_max_lines

  @expectedFailure
  def test_29_SameMessageSentMultipleTime(self):
    """
    XXX The way the synchronization is done make it loop forever

    With http synchronization, when a message is not well
    received, then we send message again, we want to
    be sure that is such case we don't do stupid things

    If we want to make this test more intersting, it is
    better to split messages
    """
    from erp5.component.module import SyncMLConstant
    previous_max_lines = SyncMLConstant.MAX_LEN
    try:
      SyncMLConstant.MAX_LEN = 1 << 8
      SyncMLSubscription.MAX_LEN = 1 << 8
      self.setupPublicationAndSubscription()
      nb_person = self.populatePersonServer()
      # Synchronize the first client
      self.synchronizeWithBrokenMessage(self.sub_id1)
      portal_sync = self.getSynchronizationTool()
      subscription1 = portal_sync[self.sub_id1]
      self.assertEqual(len(subscription1.getDocumentList()), nb_person)
      person_server = self.getPersonServer() # We also check we don't
                                             # modify initial ob
      person1_s = person_server._getOb(self.id1)
      person_client1 = self.getPersonClient1()
      person1_c = person_client1._getOb(self.id1)
      self.assertEqual(person1_s.getId(), self.id1)
      self.assertEqual(person1_s.getFirstName(), self.first_name1)
      self.assertEqual(person1_s.getLastName(), self.last_name1)
      self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    finally:
      SyncMLConstant.MAX_LEN = previous_max_lines
      SyncMLSubscription.MAX_LEN =previous_max_lines


  def test_30_GetSynchronizationType(self):
    # We will try to update some simple data, first
    # we change on the server side, then on the client side
    self.test_08_FirstSynchronization()
    # First we do only modification on server
    # Check for each subsription that the synchronization type
    # is TWO WAY
    portal_sync = self.getSynchronizationTool()
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    kw = {'first_name':self.first_name3,'last_name':self.last_name3}
    person1_s.edit(**kw)
    self.synchronize(self.sub_id1)
    # Then we do only modification on a client
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    kw = {'first_name':self.first_name1,'last_name':self.last_name1}
    person1_c.edit(**kw)
    self.synchronize(self.sub_id1)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
    # Then we do only modification on both the client and the server
    # and of course, on the same object
    kw = {'first_name':self.first_name3}
    person1_s.edit(**kw)
    kw = {'description':self.description3}
    person1_c.edit(**kw)
    self.synchronize(self.sub_id1)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')

  def test_31_UpdateLocalPermission(self):
    """
    We will do a first synchronization, then modify, add and delete
    an user role and see if it is correctly synchronized
    """
    self.test_08_FirstSynchronization()
    # then create roles
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person2_s = person_server._getOb(self.id2)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    person2_c = person_client1._getOb(self.id2)
    person1_s.manage_setLocalPermissions('View',['Manager','Owner'])
    person2_s.manage_setLocalPermissions('View',['Manager','Owner'])
    person2_s.manage_setLocalPermissions('View management screens',['Owner',])
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)

    # refresh documents
    person1_s = person_server._getOb(self.id1)
    person2_s = person_server._getOb(self.id2)
    person1_c = person_client1._getOb(self.id1)
    person2_c = person_client1._getOb(self.id2)

    role_1_s = person1_s.get_local_permissions()
    role_2_s = person2_s.get_local_permissions()
    role_1_c = person1_c.get_local_permissions()
    role_2_c = person2_c.get_local_permissions()
    self.assertEqual(role_1_s, role_1_c)
    self.assertEqual(role_2_s, role_2_c)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    self.assertXMLViewIsEqual(self.sub_id2, person2_s, person2_c)
    person1_s.manage_setLocalPermissions('View', ['Owner'])
    person2_s.manage_setLocalPermissions('View', None)
    person2_s.manage_setLocalPermissions('View management screens', ())
    self.synchronize(self.sub_id1)
    self.synchronize(self.sub_id2)

    # refresh documents
    person1_s = person_server._getOb(self.id1)
    person2_s = person_server._getOb(self.id2)
    person1_c = person_client1._getOb(self.id1)
    person2_c = person_client1._getOb(self.id2)

    role_1_s = person1_s.get_local_permissions()
    role_2_s = person2_s.get_local_permissions()
    role_1_c = person1_c.get_local_permissions()
    role_2_c = person2_c.get_local_permissions()
    self.assertEqual(role_1_s, role_1_c)
    self.assertEqual(role_2_s, role_2_c)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    self.assertXMLViewIsEqual(self.sub_id2, person2_s, person2_c)

  def addOneWayFromServerSubscription(self):
    portal_sync = self.getSynchronizationTool()
    syncml_alert_code = self.portal.portal_categories.syncml_alert_code.\
                                                            one_way_from_server
    subscription = portal_sync._getOb(self.sub_id1, None)
    if subscription is not None:
      subscription.edit(syncml_alert_code_value=syncml_alert_code)
    else:
      subscription = portal_sync.newContent(portal_type='SyncML Subscription',
                              id=self.sub_id1,
                              url_string=self.publication_url,
                              subscription_url_string=self.subscription_url1,
                              source='person_client1',
                              source_reference='Person',
                              destination_reference='Person',
                              list_method_id='objectValues',
                              xml_binding_generator_method_id=self.xml_mapping,
                              conduit_module_id='ERP5Conduit',
                              is_activity_enabled=self.activity_enabled,
                              syncml_alert_code_value=syncml_alert_code,
                              user_id='fab',
                              password='myPassword')

    self.tic()

  def test_33_OneWayFromServer(self):
    """
    We will test if we can synchronize only from to server to the client.
    We want to make sure in this case that all modifications on the client
    will not be taken into account.
    """
    person_server = self.getPersonServer()
    if person_server is not None:
      portal = self.getPortal()
      portal._delObject(id='person_server')
      portal._delObject(id='person_client1')
      portal._delObject(id='person_client2')
    self.deletePublicationAndSubscriptionList()
    self.addPublication()
    self.addOneWayFromServerSubscription()

    nb_person = self.populatePersonServer()
    portal_sync = self.getSynchronizationTool()
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'one_way_from_server')
    # First do the sync from the server to the client
    nb_message1 = self.synchronize(self.sub_id1)
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'one_way_from_server')
    self.assertEqual(nb_message1, self.nb_message_first_synchronization)
    subscription1 = portal_sync[self.sub_id1]
    self.assertEqual(len(subscription1.getDocumentList()), nb_person)
    person_server = self.getPersonServer() # We also check we don't
                                           # modify initial ob
    person1_s = person_server._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)
    self.assertEqual(person1_s.getId(), self.id1)
    self.assertEqual(person1_s.getFirstName(), self.first_name1)
    self.assertEqual(person1_s.getLastName(), self.last_name1)
    self.assertEqual(person1_c.getLastName(), self.last_name1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c, force=1)
    # Then we change things on both sides and we look if there
    # is synchronization from only one way
    person1_c.setFirstName(self.first_name2)
    person1_s.setLastName(self.last_name2)
    nb_message1 = self.synchronize(self.sub_id1)
    # In One_From_Server Sync mode, first_name of object on client side
    # doesn't change because no data is send from Subscription
    self.assertEqual(person1_c.getFirstName(), self.first_name2)
    self.assertEqual(person1_c.getLastName(), self.last_name2)
    self.assertEqual(person1_s.getFirstName(), self.first_name1)
    self.assertEqual(person1_s.getLastName(), self.last_name2)
    #reset for refresh sync
    #after synchronize, the client object retrieve value of server
    self.resetSignaturePublicationAndSubscription()
    nb_message1 = self.synchronize(self.sub_id1)

    # refresh documents
    person1_s = person_server._getOb(self.id1)
    person1_c = person_client1._getOb(self.id1)

    self.assertEqual(person1_s.getFirstName(), self.first_name1)
    self.assertEqual(person1_s.getLastName(), self.last_name2)
    self.checkSynchronizationStateIsSynchronized()
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c, force=1)

  def addOneWayFormClientSubscription(self):
    portal_sync = self.getSynchronizationTool()
    syncml_alert_code = self.portal.portal_categories.syncml_alert_code.\
                                                            one_way_from_client
    subscription = portal_sync._getOb(self.sub_id1, None)
    if subscription is not None:
      subscription.edit(syncml_alert_code_value=syncml_alert_code)
    else:
      subscription = portal_sync.newContent(portal_type='SyncML Subscription',
                              id=self.sub_id1,
                              url_string=self.publication_url,
                              subscription_url_string=self.subscription_url1,
                              source='person_client1',
                              source_reference='Person',
                              destination_reference='Person',
                              list_method_id='objectValues',
                              xml_binding_generator_method_id=self.xml_mapping,
                              conduit_module_id='ERP5Conduit',
                              is_activity_enabled=self.activity_enabled,
                              syncml_alert_code_value=syncml_alert_code,
                              user_id='fab',
                              password='myPassword')

    self.tic()

  def test_OneWayFromClient(self):
    """
    Check one way from client configuration
    """
    person_server = self.getPersonServer()
    if person_server is not None:
      portal = self.getPortal()
      portal._delObject(id='person_server')
      portal._delObject(id='person_client1')
      portal._delObject(id='person_client2')
    self.deletePublicationAndSubscriptionList()
    self.addPublication()
    self.addOneWayFormClientSubscription()

    nb_person = self.populatePersonClient1()
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync[self.sub_id1]
    self.assertEqual(subscription1.getSyncmlAlertCode(), 'one_way_from_client')
    # First do the sync from the server to the client
    self.synchronize(self.sub_id1)
    self.assertEqual(subscription1.getSyncmlAlertCode(),
                      'one_way_from_client')
    #self.assertEqual(nb_message1, self.nb_message_first_synchronization)
    self.assertEqual(len(subscription1), nb_person)
    client_person_module = self.getPersonClient1() # We also check we don't
                                           # modify initial ob
    object_id = '1'
    client_person = client_person_module._getOb(object_id)
    server_person_module = self.getPersonServer()
    server_person = server_person_module._getOb(object_id)
    self.assertEqual(client_person.getId(), object_id)
    self.assertEqual(client_person.getFirstName(), self.first_name1)
    self.assertEqual(client_person.getLastName(), self.last_name1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertXMLViewIsEqual(self.sub_id1, client_person, server_person,
                              force=True)
    # Change part of the title on both side
    # so that it generates a conflict
    client_person.setFirstName(self.first_name2)
    server_person.setLastName(self.last_name2)
    self.synchronize(self.sub_id1)

    # refresh documents
    server_person = server_person_module._getOb(object_id)
    client_person = client_person_module._getOb(object_id)

    # Conflict is generated on title
    # But first name still is processed
    # so first name must be up to date
    self.assertEqual(server_person.getFirstName(), self.first_name2)
    self.assertEqual(server_person.getLastName(), self.last_name2)
    # Client get no change from server as it is in one way from client
    self.assertEqual(client_person.getFirstName(), self.first_name2)
    self.assertEqual(client_person.getLastName(), self.last_name1)

    # reset for refresh sync
    # after synchronization, the client retrieves value from server
    self.resetSignaturePublicationAndSubscription()
    self.synchronize(self.sub_id1)

    # refresh documents
    server_person = server_person_module._getOb(object_id)
    client_person = client_person_module._getOb(object_id)

    self.assertEqual(server_person.getFirstName(), self.first_name2)
    self.assertEqual(server_person.getLastName(), self.last_name1)
    self.assertEqual(client_person.getFirstName(), self.first_name2)
    self.assertEqual(client_person.getLastName(), self.last_name1)

    self.checkSynchronizationStateIsSynchronized()

    self.assertXMLViewIsEqual(self.sub_id1, client_person, server_person,
                              force=True)

  def addRefreshFormClientOnlySubscription(self):
    portal_sync = self.getSynchronizationTool()
    syncml_alert_code = self.portal.portal_categories.syncml_alert_code.\
                                                            refresh_from_client_only
    subscription = portal_sync._getOb(self.sub_id1, None)
    if subscription is not None:
      subscription.edit(syncml_alert_code_value=syncml_alert_code)
    else:
      subscription = portal_sync.newContent(portal_type='SyncML Subscription',
                              id=self.sub_id1,
                              url_string=self.publication_url,
                              subscription_url_string=self.subscription_url1,
                              source='person_client1',
                              source_reference='Person',
                              destination_reference='Person',
                              list_method_id='objectValues',
                              xml_binding_generator_method_id=self.xml_mapping,
                              conduit_module_id='ERP5Conduit',
                              is_activity_enabled=self.activity_enabled,
                              syncml_alert_code_value=syncml_alert_code,
                              user_id='fab',
                              password='myPassword')

    self.tic()


  def test_refreshFromClientOnly(self):
    """
    Refresh from client only is used to send all data from the client to the
    server, the server updating all its data. Modifications on server side are
    not send to the client
    """
    publication = self.addPublication()
    self.addRefreshFormClientOnlySubscription()

    self.populatePersonClient1()
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync[self.sub_id1]
    self.assertEqual(subscription1.getSyncmlAlertCode(),
                      'refresh_from_client_only')
    # Execute first synchronization
    # data from client will be synced on server
    self.synchronize(self.sub_id1)
    self.assertEqual(subscription1.getSyncmlAlertCode(),
                      'refresh_from_client_only')
    # Check no signature created
    self.assertEqual(len(subscription1), 0)
    subscriber_list = publication.contentValues(portal_type="SyncML Subscription")
    self.assertEqual(len(subscriber_list), 1)
    subscriber = subscriber_list[0]
    self.assertEqual(len(subscriber), 0)

    # Check same person on client & server side
    client_person_module = self.getPersonClient1()
    server_person_module = self.getPersonServer()
    for x in xrange(1, 61):
      client_person = client_person_module._getOb(str(x))
      server_person = server_person_module._getOb(str(x))
      self.assertEqual(client_person.getFirstName(), self.first_name1)
      self.assertEqual(client_person.getLastName(), self.last_name1)
      self.assertEqual(server_person.getFirstName(), self.first_name1)
      self.assertEqual(server_person.getLastName(), self.last_name1)
      self.assertXMLViewIsEqual(self.sub_id1, client_person, server_person,
                                force=True)

      # Modify data of persons on both side
      client_person.setFirstName(self.first_name2)
      server_person.setDescription(self.last_name2)

    self.tic()
    # Second synchronization
    # Only client modification must have been synchronized
    # Server modification will get ereased
    self.synchronize(self.sub_id1)
    # Check no signature created
    self.assertEqual(len(subscription1), 0)
    self.assertEqual(len(subscriber), 0)

    for x in xrange(1, 61):
      client_person = client_person_module._getOb(str(x))
      server_person = server_person_module._getOb(str(x))
      self.assertEqual(client_person.getFirstName(), self.first_name2)
      self.assertEqual(client_person.getDescription(), self.description1)
      self.assertEqual(server_person.getFirstName(), self.first_name2)
      self.assertEqual(server_person.getDescription(), self.description1)
      self.assertXMLViewIsEqual(self.sub_id1, client_person, server_person,
                                force=True)
      # Modify same data of person on both side
      client_person.setLastName(self.last_name2)
      server_person.setLastName(self.first_name2)

    # Third synchronization
    # Client modifications must win over server modifications
    self.synchronize(self.sub_id1)
    # Check no signature created
    self.assertEqual(len(subscription1), 0)
    self.assertEqual(len(subscriber), 0)

    for x in xrange(1, 61):
      client_person = client_person_module._getOb(str(x))
      server_person = server_person_module._getOb(str(x))
      self.assertEqual(client_person.getLastName(), self.last_name2)
      self.assertEqual(server_person.getLastName(), self.last_name2)
      # These property should not have changed
      self.assertEqual(client_person.getFirstName(), self.first_name2)
      self.assertEqual(client_person.getDescription(), self.description1)
      self.assertEqual(server_person.getFirstName(), self.first_name2)
      self.assertEqual(server_person.getDescription(), self.description1)
      self.assertXMLViewIsEqual(self.sub_id1, client_person, server_person,
                                force=True)


  def test_34_encoding(self):
    """
    We will test if we can encode strings with b64encode to encode
    the login and password for authenticated sessions
    """
    #when there will be other format implemented with encode method,
    #there will be tested here

    self.test_08_FirstSynchronization()
    #define some strings :
    python = 'www.python.org'
    awaited_result_python = "d3d3LnB5dGhvbi5vcmc="
    long_string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNO\
PQRSTUVWXYZéèçà@^~µ&²0123456789!@#0^&*();:<>,. []{}\xc3\xa7sdf__\
sdf\xc3\xa7\xc3\xa7\xc3\xa7_df___&&\xc3\xa9]]]\xc2\xb0\xc2\xb0\xc2\
\xb0\xc2\xb0\xc2\xb0\xc2\xb0"
    #= "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZéèçà@^~µ&²012345
    #6789!@#0^&*();:<>,. []{}çsdf__sdfççç_df___&&é]]]°°°°°°'"

    awaited_result_long_string = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXpBQkNERUZH\
SElKS0xNTk9QUVJTVFVWV1hZWsOpw6jDp8OgQF5+wrUmwrIwMTIzNDU2Nzg5IUAjMF4mKigpOzo8Pi\
wuIFtde33Dp3NkZl9fc2Rmw6fDp8OnX2RmX19fJibDqV1dXcKwwrDCsMKwwrDCsA=="
    #test just b64encode
    self.assertEqual(b64encode(python), awaited_result_python)
    self.assertEqual(b64encode(""), "")
    self.assertEqual(b64encode(long_string), awaited_result_long_string)

    self.assertEqual(b64decode(awaited_result_python), python)
    self.assertEqual(b64decode(""), "")
    self.assertEqual(b64decode(awaited_result_long_string), long_string)

    # test with the ERP5 functions
    string_encoded = encode('b64', python)
    self.assertEqual(string_encoded, awaited_result_python)
    string_decoded = decode('b64', awaited_result_python)
    self.assertEqual(string_decoded, python)
    self.assertTrue(isDecodeEncodeTheSame(string_encoded,
                    python, 'b64'))
    self.assertTrue(isDecodeEncodeTheSame(string_encoded,
                    string_decoded, 'b64'))

    string_encoded = encode('b64', long_string)
    self.assertEqual(string_encoded, awaited_result_long_string)
    string_decoded = decode('b64', awaited_result_long_string)
    self.assertEqual(string_decoded, long_string)
    self.assertTrue(isDecodeEncodeTheSame(string_encoded,
                    long_string, 'b64'))
    self.assertTrue(isDecodeEncodeTheSame(string_encoded,
                    string_decoded, 'b64'))

    self.assertEqual(encode('b64', ''), '')
    self.assertEqual(decode('b64', ''), '')
    self.assertTrue(isDecodeEncodeTheSame(
                    encode('b64', ''), '', 'b64'))

  def test_35_authentication(self):
    """
    Check :
    - synchronization failed if bad authentication
    - authentication is case sensitive
    - authentication work in utf-8
    XXX Missing tests :
    - no authentication provided on client
    - sending authentication when not required
    - empty password on client/server
    """
    self.test_08_FirstSynchronization()
    # First we do only modification on client
    person_server = self.getPersonServer()
    person1_s = person_server._getOb(self.id1)
    person_client1 = self.getPersonClient1()
    person1_c = person_client1._getOb(self.id1)

    kw = {'first_name':self.first_name3,'last_name':self.last_name3}
    person1_c.edit(**kw)

    # check that it's not synchronize
    self.verifyFirstNameAndLastNameAreNotSynchronized(self.first_name3,
      self.last_name3, person1_s, person1_c)
    self.synchronize(self.sub_id1)
    # now it should be synchronize
    self.checkSynchronizationStateIsSynchronized()
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    self.assertEqual(person1_s.getFirstName(), self.first_name3)
    self.assertEqual(person1_s.getLastName(), self.last_name3)

    # adding diferent authentication parameter on pub/sub
    self.addAuthenticationToPublication(self.pub_id, 'fab', 'myPassword', 'b64',
        'syncml:auth-basic')
    self.addAuthenticationToSubscription(self.sub_id1, 'pouet', 'pouet',
        'b64', 'syncml:auth-basic')
    # Do some modification
    kw = {'first_name':self.first_name2,'last_name':self.last_name2}
    person1_c.edit(**kw)
    self.verifyFirstNameAndLastNameAreNotSynchronized(self.first_name2,
      self.last_name2, person1_s, person1_c)
    # try to synchronize with a wrong authentication on the subscription, it
    # should failed
    self.assertRaises(ValueError, self.synchronize, self.sub_id1)
    self.verifyFirstNameAndLastNameAreNotSynchronized(self.first_name2,
      self.last_name2, person1_s, person1_c)

    # now make the authentication match
    self.addAuthenticationToSubscription(self.sub_id1, 'fab', 'myPassword',
        'b64', 'syncml:auth-basic')
    self.synchronize(self.sub_id1)
    # data must now have been synchronized
    self.checkSynchronizationStateIsSynchronized()
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    self.assertEqual(person1_s.getFirstName(), self.first_name2)
    self.assertEqual(person1_s.getLastName(), self.last_name2)

    # try to synchronize with a bad login and/or password
    # test if login is case sensitive (it should be !)
    self.addAuthenticationToSubscription(self.sub_id1, 'fAb', 'myPassword',
        'b64', 'syncml:auth-basic')
    kw = {'first_name':self.first_name1,'last_name':self.last_name1}
    person1_c.edit(**kw)
    self.assertRaises(ValueError, self.synchronize, self.sub_id1)
    self.verifyFirstNameAndLastNameAreNotSynchronized(self.first_name1,
      self.last_name1, person1_s, person1_c)

    # with a paswword case sensitive
    self.addAuthenticationToSubscription(self.sub_id1, 'fab', 'mypassword',
        'b64', 'syncml:auth-basic')
    kw = {'first_name':self.first_name1,'last_name':self.last_name1}
    person1_c.edit(**kw)
    self.assertRaises(ValueError, self.synchronize, self.sub_id1)
    self.verifyFirstNameAndLastNameAreNotSynchronized(self.first_name1,
      self.last_name1, person1_s, person1_c)

    # with the good password
    self.addAuthenticationToSubscription(self.sub_id1, 'fab', 'myPassword',
        'b64', 'syncml:auth-basic')
    # now it should be correctly synchronize
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    self.assertEqual(person1_s.getFirstName(), self.first_name1)
    self.assertEqual(person1_s.getLastName(), self.last_name1)

    # verify that the login and password with utf8 caracters are accecpted

    # add a user with an utf8 login
    uf = self.getPortal().acl_users
    uf._doAddUser('\xc3\xa9pouet', 'ploum', ['Manager'], []) # \xc3\xa9pouet = épouet
    user = uf.getUserById('\xc3\xa9pouet').__of__(uf)
    newSecurityManager(None, user)

    self.addAuthenticationToPublication(self.pub_id, '\xc3\xa9pouet', 'ploum',
        'b64', 'syncml:auth-basic')
    # first, try with a wrong login :
    self.addAuthenticationToSubscription(self.sub_id1, 'pouet', 'ploum',
        'b64', 'syncml:auth-basic')
    kw = {'first_name':self.first_name3,'last_name':self.last_name3}
    person1_c.edit(**kw)
    self.verifyFirstNameAndLastNameAreNotSynchronized(self.first_name3,
      self.last_name3, person1_s, person1_c)
    self.assertRaises(ValueError, self.synchronize, self.sub_id1)
    self.verifyFirstNameAndLastNameAreNotSynchronized(self.first_name3,
      self.last_name3, person1_s, person1_c)
    # now with the good :
    self.addAuthenticationToSubscription(self.sub_id1, '\xc3\xa9pouet', 'ploum',
        'b64', 'syncml:auth-basic')
    self.synchronize(self.sub_id1)
    self.assertXMLViewIsEqual(self.sub_id1, person1_s, person1_c)
    self.assertEqual(person1_s.getFirstName(), self.first_name3)
    self.assertEqual(person1_s.getLastName(), self.last_name3)
    self.checkSynchronizationStateIsSynchronized()

  @expectedFailure
  def test_36_SynchronizationSubscriptionMaxLines(self):
    """
    XXX This has not been implemented in new syncml version

    Check that messages are well splited when getting too many lines
    """
    self.login()
    self.setupPublicationAndSubscription()
    nb_person = self.populatePersonClient1()
    portal_sync = self.getSynchronizationTool()
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
    # Synchronize the first client
    # data_Sub1 -> Pub (the data are in sub1 to pub is empty)
    nb_message1 = self.synchronize(self.sub_id1)
    #Verification number object synchronized
    self.assertEqual(nb_message1, self.nb_message_first_sync_max_lines)
    # Synchronize the second client
    nb_message2 = self.synchronize(self.sub_id2)
    self.assertEqual(nb_message2, self.nb_message_first_sync_max_lines)
    person_server = self.getPersonServer()
    person_client1 = self.getPersonClient1()
    person_client2 = self.getPersonClient2()
    # Check we have all data synchronized
    self.assertEqual(nb_person, len(person_server.objectValues()))
    self.assertEqual(nb_person, len(person_client1.objectValues()))
    self.assertEqual(nb_person, len(person_client2.objectValues()))

    for id_ in range(1, 60):
      person_s = person_server._getOb(str(id_))
      person_c1 = person_client1._getOb(str(id_))
      person_c2 = person_client2._getOb(str(id_))
      self.assertXMLViewIsEqual(self.sub_id1, person_s, person_c1)
      self.assertXMLViewIsEqual(self.sub_id1, person_s, person_c2)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5SyncML))
  return suite