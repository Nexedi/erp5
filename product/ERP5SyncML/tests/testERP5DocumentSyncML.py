# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Danièle Vanbaelinghem <daniele@nexedi.com>
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

import os
import unittest
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5SyncML.Conduit.ERP5DocumentConduit import ERP5DocumentConduit
from Products.ERP5SyncML.SyncCode import SyncCode
from zLOG import LOG
from base64 import b16encode 
import transaction
from ERP5Diff import ERP5Diff
from lxml import etree
from Products.ERP5Type.tests.utils import FileUpload

ooodoc_coordinates = ('127.0.0.1', 8008)
test_files = os.path.join(os.path.dirname(__file__), 'test_document')
FILE_NAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})-\
(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})(-\
(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"

def makeFileUpload(name):
  path = os.path.join(test_files, name)
  return FileUpload(path, name)

class TestERP5DocumentSyncMLMixin:
  
  nb_objects = 10
  #for objects
  ids = range(1, nb_objects+1)
  #id_max_text : number of document text
  id_max_text = nb_objects/2
  id1 = '2'
  id2 = '3'
  #for documents (encoding in unicode for utf-8)
  #files
  filename_text = 'TEST-en-002.txt'
  size_filename_text = len(makeFileUpload(filename_text).read())
  filename_odt = 'TEST-en-002.odt'
  size_filename_odt = len(makeFileUpload(filename_odt).read())
  filename_ppt = 'TEST-en-002.ppt'
  size_filename_ppt = len(makeFileUpload(filename_ppt).read())
  filename_pdf = 'TEST-en-002.pdf'
  size_filename_pdf = len(makeFileUpload(filename_pdf).read())
  #properties
  reference1 = 'P-SYNCML.Text'
  version1 = '001'
  language1 = 'en'
  #description1 - blaàéc1
  description1 = 'description1 - blac\xc3\xa0\xc3\xa91'
  short_title1 = 'P-SYNCML-Text'
  reference2 = 'P-SYNCML-SyncML.Document.Pdf'
  version2 = '001'
  language2 = 'fr'
  #description2 - file $£µ%c2éè!
  description2 = 'description2 - file $\xc2\xa3\xc2\xb5%c2\xc3\xa9\xc3\xa8!'
  short_title2 = 'P-SYNCML-Pdf'
  reference3 = 'P-SYNCML-SyncML.Document.WebPage'
  version3 = '001'
  language3 = 'ja'
  #description3 - file description3 - file ù@
  description3 = 'description3 - file \xc3\xb9@'
  short_title3 = 'P-SYNCML-WebPage'
  #for synchronization
  pub_id = 'Publication'
  sub_id1 = 'Subscription1'
  sub_id_from_server = 'SubscriptionFromServer'
  pub_query = 'objectValues'
  sub_query1 = 'objectValues'
  xml_mapping = 'asXML'
  pub_conduit = 'ERP5DocumentConduit'
  sub_conduit1 = 'ERP5DocumentConduit'
  activity_enabled = True
  publication_url = 'file://tmp/sync_server'
  subscription_url = { 'two_way' : 'file://tmp/sync_client1', \
        'from_server' : 'file://tmp/sync_client_from_server'}
  #for this tests
  nb_message_first_synchronization = 12
  nb_message_multi_first_synchronization = 14
  nb_synchronization = 2
  nb_subscription = 1
  nb_publication = 1
  #default edit_workflow
  workflow_id = 'processing_status_workflow'
  

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_base', 'erp5_ingestion',\
    'erp5_ingestion_mysql_innodb_catalog', 'erp5_web',\
    'erp5_dms')


  def afterSetUp(self):
    """Setup."""
    self.login()
    self.addPublications()
    self.addSubscriptions()
    self.portal = self.getPortal()
    self.setSystemPreferences()
    transaction.commit()
    self.tic()
  
  def beforeTearDown(self):
    """
      Do some stuff after each test:
      - clear document module of server and client
      - clear the publications and subscriptions
    """
    self.clearDocumentModules()
    self.clearPublicationsAndSubscriptions()

  def setSystemPreferences(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(ooodoc_coordinates[0])
    default_pref.setPreferredOoodocServerPortNumber(ooodoc_coordinates[1])
    default_pref.setPreferredDocumentFileNameRegularExpression(FILE_NAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)
    if default_pref.getPreferenceState() == 'disabled':
      default_pref.enable()

  def addSubscriptions(self):
    portal_id = self.getPortalId()
    portal_sync = self.getSynchronizationTool()
    if portal_sync.getSubscription(self.sub_id1) is None:
      portal_sync.manage_addSubscription(title=self.sub_id1, 
                  publication_url=self.publication_url,
                  subscription_url=self.subscription_url['two_way'], 
                  destination_path='/%s/document_client1' % portal_id,
                  source_uri='Document:', 
                  target_uri='Document', 
                  query= self.sub_query1, 
                  xml_mapping=self.xml_mapping, 
                  conduit=self.sub_conduit1, 
                  #alert_code=SyncCode.TWO_WAY,
                  gpg_key='',
                  activity_enabled=True,
                  login='daniele',
                  password='myPassword')
    sub = portal_sync.getSubscription(self.sub_id1)
    self.assertTrue(sub is not None)

  def addPublications(self):
    portal_id = self.getPortalName()
    portal_sync = self.getSynchronizationTool()
    if portal_sync.getPublication(self.pub_id) is None:
      portal_sync.manage_addPublication(title=self.pub_id,
                  publication_url=self.publication_url, 
                  destination_path='/%s/document_server' % portal_id, 
                  source_uri='Document', 
                  query=self.pub_query, 
                  xml_mapping=self.xml_mapping, 
                  conduit=self.pub_conduit,
                  gpg_key='',
                  activity_enabled=True,
                  authentication_format='b64',
                  authentication_type='syncml:auth-basic') 
    pub = portal_sync.getPublication(self.pub_id)
    self.assertTrue(pub is not None)

  def createDocumentModules(self, one_way=False):
    if not hasattr(self.portal, 'document_server'):
      self.portal.portal_types.constructContent(type_name = 'Document Module',
                                             container = self.portal,
                                             id = 'document_server')

    if not hasattr(self.portal, 'document_client1'):
      self.portal.portal_types.constructContent(type_name = 'Document Module',
                                             container = self.portal,
                                             id = 'document_client1')
        
    if one_way:
      if not hasattr(self.portal, 'document_client_from_server'):
        self.portal.portal_types.constructContent(type_name = 'Document Module',
                                               container = self.portal,
                                               id = 'document_client_from_server')
  def clearDocumentModules(self):
    portal_sync = self.getSynchronizationTool()
    document_server = self.getDocumentServer()
    if document_server is not None:
      self.portal._delObject(id='document_server')
      self.portal._delObject(id='document_client1')
    transaction.commit()
    self.tic()
 
  def clearPublicationsAndSubscriptions(self):
    portal_sync = self.getSynchronizationTool()
    for pub in portal_sync.getPublicationList():
      portal_sync.manage_deletePublication(pub.getTitle())
    for sub in portal_sync.getSubscriptionList():
      portal_sync.manage_deleteSubscription(sub.getTitle())
    transaction.commit()
    self.tic()

  ####################
  ### Usefull methods
  ####################

  def getSynchronizationTool(self):
    return getattr(self.portal, 'portal_synchronizations', None)

  def getDocumentClient1(self):
    return getattr(self.portal, 'document_client1', None)

  def getDocumentClientFromServer(self):
    return getattr(self.portal, 'document_client_from_server', None)
  
  def getDocumentServer(self):
    return getattr(self.portal, 'document_server', None)

  def getPortalId(self):
    return self.portal.getId()

  def login(self, quiet=0):
    uf = self.portal.acl_users
    uf._doAddUser('daniele', 'myPassword', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    uf._doAddUser('syncml', '', ['Manager'], [])
    user = uf.getUserById('daniele').__of__(uf)
    newSecurityManager(None, user)
 
  def resetSignaturePublicationAndSubscription(self):
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync.getPublication(self.pub_id)
    subscription1 = portal_sync.getSubscription(self.sub_id1)
    publication.resetAllSubscribers()
    subscription1.resetAllSignatures()
    transaction.commit()
    self.tic()

  def documentMultiServer(self, quiet=0):
    # create different document by category documents
    if not quiet:
      ZopeTestCase._print('\nTest Document Multi Server')
      LOG('Testing... ', 0, 'documentMultiServer')
    self.createDocumentModules()
    document_id = ''
    document_server = self.getDocumentServer()
    #plain text document
    for id in self.ids[:self.id_max_text]:
      reference = "Test-Text-%s" % (id,)
      self.createDocument(id=id, file_name=self.filename_text, reference=reference)
    transaction.commit()
    nb_document = len(document_server.objectValues())
    self.assertEqual(nb_document, len(self.ids[:self.id_max_text]))
    #binary document
    for id in self.ids[self.id_max_text:]:
      reference = "Test-Odt-%s" % (id, )
      self.createDocument(id=id, file_name=self.filename_odt, reference=reference)
    transaction.commit()
    self.tic()
    nb_document = len(document_server.objectValues())
    self.assertEqual(nb_document, len(self.ids))
    return nb_document
   
  def documentServer(self, quiet=0, one_way=False):
    """
    create document in document_server
     """
    if not quiet:
      ZopeTestCase._print('\nTest Document Server')
      LOG('Testing... ', 0, 'documentServer')
    self.createDocumentModules(one_way) 
    document_id = ''
    document_server = self.getDocumentServer()
    if getattr(document_server, self.id1, None) is not None:
      self.clearDocumentModules()
    document_text = document_server.newContent(id=self.id1,\
                                               portal_type='Text')
    kw = {'reference':self.reference1, 'Version':self.version1,\
          'Language':self.language1, 'Description':self.description1}
    document_text.edit(**kw)
    file = makeFileUpload(self.filename_text)
    document_text.edit(file=file)
    transaction.commit()
    self.tic()
    document_pdf = document_server.newContent(id=self.id2,\
                                              portal_type='PDF')
    kw = {'reference':self.reference2, 'Version':self.version2,\
          'Language':self.language2, 'Description':self.description2}
    document_pdf.edit(**kw)
    file = makeFileUpload(self.filename_pdf)
    document_pdf.edit(file=file)
    transaction.commit()
    self.tic()
    nb_document = len(document_server.objectValues())
    self.assertEqual(nb_document, 2)
    return nb_document

  def createDocument(self, id, file_name=None, portal_type='Text',
             reference='P-SYNCML.Text', version='001', language='en'):
    """
      Create a text document
    """
    document_server = self.getDocumentServer()
    if getattr(document_server, str(id), None) is not None:
      self.clearDocumentModules()  
    doc_text = document_server.newContent(id=id, portal_type=portal_type)
    kw = {'reference': reference, 'version': version, 'language': language}
    doc_text.edit(**kw)
    if file_name is not None:
      file = makeFileUpload(file_name)
      doc_text.edit(file=file)
    return doc_text

  def synchronize(self, id):
    """
    This just define how we synchronize, we have
    to define it here because it is specific to the unit testing
    """
    portal_sync = self.getSynchronizationTool()
    subscription = portal_sync.getSubscription(id)
    publication = None
    for pub in portal_sync.getPublicationList():
      if pub.getPublicationUrl()==subscription.getPublicationUrl():
        publication = pub
    self.assertTrue(publication is not None)
    # reset files, because we do sync by files
    file = open(subscription.getSubscriptionUrl()[len('file:/'):], 'w')
    file.write('')
    file.close()
    file = open(self.publication_url[len('file:/'):], 'w')
    file.write('')
    file.close()
    transaction.commit()
    self.tic()
    nb_message = 1
    result = portal_sync.SubSync(subscription.getPath())
    while result['has_response']==1:
      portal_sync.PubSync(publication.getPath())
      if self.activity_enabled:
        transaction.commit()
        self.tic()
      result = portal_sync.SubSync(subscription.getPath())
      if self.activity_enabled:
        transaction.commit()
        self.tic()
      nb_message += 1 + result['has_response']
    return nb_message

  def synchronizeWithBrokenMessage(self, id):
    """
    This just define how we synchronize, we have
    to define it here because it is specific to the unit testing
    """
    portal_sync = self.getSynchronizationTool()
    #portal_sync.email = None # XXX To be removed
    subscription = portal_sync.getSubscription(id)
    publication = None
    for publication in portal_sync.getPublicationList():
      if publication.getPublicationUrl()==subscription.getSubscriptionUrl():
        publication = publication
    self.assertTrue(publication is not None)
    # reset files, because we do sync by files
    file = open(subscription.getSubscriptionUrl()[len('file:/'):], 'w')
    file.write('')
    file.close()
    file = open(self.publication_url[len('file:/'):], 'w')
    file.write('')
    file.close()
    transaction.commit()
    self.tic()
    nb_message = 1
    result = portal_sync.SubSync(subscription.getPath())
    while result['has_response']==1:
      # We do thing three times, so that we will test
      # if we manage well duplicate messages
      portal_sync.PubSync(publication.getPath())
      if self.activity_enabled:
        transaction.commit()
        self.tic()
      portal_sync.PubSync(publication.getPath())
      if self.activity_enabled:
        transaction.commit()
        self.tic()
      portal_sync.PubSync(publication.getPath())
      if self.activity_enabled:
        transaction.commit()
        self.tic()
      result = portal_sync.SubSync(subscription.getPath())
      if self.activity_enabled:
        transaction.commit()
        self.tic()
      result = portal_sync.SubSync(subscription.getPath())
      if self.activity_enabled:
        transaction.commit()
        self.tic()
      result = portal_sync.SubSync(subscription.getPath())
      if self.activity_enabled:
        transaction.commit()
        self.tic()
      nb_message += 1 + result['has_response']
    return nb_message

  def checkSynchronizationStateIsSynchronized(self, quiet=0):
    portal_sync = self.getSynchronizationTool()
    document_server = self.getDocumentServer()
    for document in document_server.objectValues():
      state_list = portal_sync.getSynchronizationState(document)
      for state in state_list:
        self.assertEqual(state[1], state[0].SYNCHRONIZED)
    document_client1 = self.getDocumentClient1()
    for document in document_client1.objectValues():
      state_list = portal_sync.getSynchronizationState(document)
      for state in state_list:
        self.assertEqual(state[1], state[0].SYNCHRONIZED)
    # Check for each signature that the tempXML is None
    for sub in portal_sync.getSubscriptionList():
      for m in sub.getSignatureList():
        self.assertEquals(m.getTempXML(), None)
        self.assertEquals(m.getPartialXML(), None)
    for pub in portal_sync.getPublicationList():
      for sub in pub.getSubscriberList():
        for m in sub.getSignatureList():
          self.assertEquals(m.getPartialXML(), None)

  def checkFirstSynchronization(self, nb_document=0):

   portal_sync = self.getSynchronizationTool()
   subscription1 = portal_sync.getSubscription(self.sub_id1)
   self.assertEqual(len(subscription1.getObjectList()), nb_document)
   document_server = self.getDocumentServer() # We also check we don't
                                            # modify initial ob
   doc1_s = document_server._getOb(self.id1)
   self.assertEqual(doc1_s.getId(), self.id1)
   self.assertEqual(doc1_s.getReference(), self.reference1)
   self.assertEqual(doc1_s.getVersion(), self.version1)
   self.assertEqual(doc1_s.getLanguage(), self.language1)
   self.assertEqual(doc1_s.getSourceReference(), self.filename_text)
   self.assertEquals(self.size_filename_text, doc1_s.get_size())
   doc2_s = document_server._getOb(self.id2)
   self.assertEqual(doc2_s.getReference(), self.reference2)
   self.assertEqual(doc2_s.getVersion(), self.version2)
   self.assertEqual(doc2_s.getLanguage(), self.language2)
   self.assertEqual(doc2_s.getSourceReference(), self.filename_pdf)
   self.assertEquals(self.size_filename_pdf, doc2_s.get_size())
   document_client1 = self.getDocumentClient1()
   document_c = document_client1._getOb(self.id1)
   self.assertEqual(document_c.getId(), self.id1)
   self.assertEqual(document_c.getReference(), self.reference1)
   self.assertEqual(document_c.getVersion(), self.version1)
   self.assertEqual(document_c.getLanguage(), self.language1)
   self.assertEqual(document_c.getSourceReference(), self.filename_text)
   self.assertEquals(self.size_filename_text, document_c.get_size())
   self.assertXMLViewIsEqual(self.sub_id1, doc1_s, document_c)
   self.assertXMLViewIsEqual(self.sub_id1, doc2_s,\
       document_client1._getOb(self.id2))

  def checkDocument(self, id=id, document=None, filename=None,
                    size_filename=None, reference='P-SYNCML.Text', 
                    portal_type='Text', version='001', language='en',
                    description=''):
    """
      Check synchronization with a document and the informations provided
    """
    if document is not None:
      self.assertEqual(document.getId(), id)
      self.assertEqual(document.getReference(), reference)
      self.assertEqual(document.getVersion(), version)
      self.assertEqual(document.getLanguage(), language)
      self.assertEqual(document.getDescription(), description)
      if filename is not None:
        self.assertEqual(document.getSourceReference(), filename)
        self.assertEquals(size_filename, document.get_size())
    else:
      self.fail("Document is None for check these informations")
 
  def checkXMLsSynchronized(self):
    document_server = self.getDocumentServer()
    document_client1 = self.getDocumentClient1()
    for id in self.ids:
      doc_s = document_server._getOb(str(id))
      doc_c = document_client1._getOb(str(id))
      self.assertXMLViewIsEqual(self.sub_id1, doc_s, doc_c)

  
  def checkFirstSynchronizationWithMultiDocument(self, nb_document=0):
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync.getSubscription(self.sub_id1)
    self.assertEqual(len(subscription1.getObjectList()), nb_document)
    document_server = self.getDocumentServer()
    document_client1 = self.getDocumentClient1()
    id = str(self.ids[0])
    doc_text_s = document_server._getOb(id)
    reference = 'Test-Text-%s' % id
    self.checkDocument(id=id, document=doc_text_s,
                       reference=reference,
                       filename=self.filename_text,
                       size_filename=self.size_filename_text)
    id = str(self.ids[self.id_max_text])
    doc_odt_s = document_server._getOb(id)
    reference = 'Test-Odt-%s' % id
    self.checkDocument(id=id, document=doc_odt_s,
                       reference=reference,
                       filename=self.filename_odt,
                       size_filename=self.size_filename_odt)
    self.checkXMLsSynchronized() 

  def assertXMLViewIsEqual(self, sub_id, object_pub=None, object_sub=None,\
                           force=0):
    """
      Check the equality between two xml objects with gid as id
    """
    portal_sync = self.getSynchronizationTool()
    subscription = portal_sync.getSubscription(sub_id)
    publication = portal_sync.getPublication(self.pub_id)
    gid_pub = publication.getGidFromObject(object_pub)
    gid_sub = publication.getGidFromObject(object_sub)
    self.assertEqual(gid_pub, gid_sub)
    conduit = ERP5DocumentConduit()
    xml_pub = conduit.getXMLFromObjectWithGid(object=object_pub, gid=gid_pub,\
              xml_mapping=publication.getXMLMapping())
    #if One Way From Server there is not xml_mapping for subscription
    xml_sub = conduit.getXMLFromObjectWithGid(object=object_sub, gid=gid_sub,\
              xml_mapping=subscription.getXMLMapping(force))
    erp5diff = ERP5Diff()
    erp5diff.compare(xml_pub, xml_sub)
    result = erp5diff.outputString()
    result = etree.XML(result)
    if len(result) != 0 :
      for update in result:
        #XXX edit workflow is not replaced, so discard workflow checking
        if update.get('select').find('workflow') != -1 or\
           update.find('block_data') != -1:
          continue
        else :
          self.fail('diff between pub:\n%s \n => \n%s' %\
              (xml_pub, etree.tostring(result, pretty_print=True)))
  
  
class TestERP5DocumentSyncML(TestERP5DocumentSyncMLMixin, ERP5TypeTestCase):
  
  def getTitle(self):
    """
    """
    return "ERP5 SyncML"

     
  def setupPublicationAndSubscriptionIdGenerator(self, quiet=0):
    portal_sync = self.getSynchronizationTool()
    sub1 = portal_sync.getSubscription(self.sub_id1)
    pub = portal_sync.getPublication(self.pub_id)
    pub.setSynchronizationIdGenerator('generateNewId')
    sub1.setSynchronizationIdGenerator('generateNewId')

  def checkSynchronizationStateIsConflict(self, quiet=0,
                                          portal_type='Text'):
    portal_sync = self.getSynchronizationTool()
    document_server = self.getDocumentServer()
    for document in document_server.objectValues():
      if document.getId()==self.id1:
        state_list = portal_sync.getSynchronizationState(document)
        for state in state_list:
          self.assertEqual(state[1], state[0].CONFLICT)
    document_client1 = self.getDocumentClient1()
    for document in document_client1.objectValues():
      if document.getId()==self.id1:
        state_list = portal_sync.getSynchronizationState(document)
        for state in state_list:
          self.assertEqual(state[1], state[0].CONFLICT)
   # make sure sub object are also in a conflict mode
    document = document_client1._getOb(self.id1)
    state_list = portal_sync.getSynchronizationState(document)
    for state in state_list:
      self.assertEqual(state[1], state[0].CONFLICT)

  def test_01_GetSynchronizationList(self, quiet=0):
    # This test the getSynchronizationList, ie,
    # We want to see if we retrieve both the subscription
    # and the publication
    if not quiet:
      ZopeTestCase._print('\nTest getSynchronizationList ')
      LOG('Testing... ', 0, 'test_01_GetSynchronizationList')
    portal_sync = self.getSynchronizationTool()
    synchronization_list = portal_sync.getSynchronizationList()
    self.assertEqual(len(synchronization_list), self.nb_synchronization)

  def test_02_FirstSynchronization(self, quiet=0):
    # We will try to populate the folder document_client1
    # with the data form document_server
    if not quiet:
      ZopeTestCase._print('\nTest First Synchronization ')
      LOG('Testing... ', 0, 'test_02_FirstSynchronization')
    nb_document = self.documentServer(quiet=1)
    portal_sync = self.getSynchronizationTool()
    for sub in portal_sync.getSubscriptionList():
      self.assertEquals(sub.getSynchronizationType(), SyncCode.SLOW_SYNC)
    document_server = self.getDocumentServer()
    doc1_s = document_server._getOb(self.id1)
    self.assertEqual(doc1_s.getSourceReference(), self.filename_text)
    self.assertEquals(self.size_filename_text, doc1_s.get_size())
    doc2_s = document_server._getOb(self.id2)
    self.assertEqual(doc2_s.getSourceReference(), self.filename_pdf)
    self.assertEquals(self.size_filename_pdf, doc2_s.get_size())
    # Synchronize the first client
    nb_message1 = self.synchronize(self.sub_id1)
    for sub in portal_sync.getSubscriptionList():
      if sub.getTitle() == self.sub_id1:
        self.assertEquals(sub.getSynchronizationType(), SyncCode.TWO_WAY)
      else:
        self.assertEquals(sub.getSynchronizationType(), SyncCode.SLOW_SYNC)
    self.assertEqual(nb_message1, self.nb_message_first_synchronization)
    self.checkSynchronizationStateIsSynchronized()
    self.checkFirstSynchronization(nb_document=nb_document)
  
  def test_03_UpdateSimpleData(self, quiet=0):
    if not quiet:
      ZopeTestCase._print('\nTest Update Simple Data ')
      LOG('Testing... ', 0, 'test_03_UpdateSimpleData')
    # Add two objects
    self.test_02_FirstSynchronization(quiet=1)
    # First we do only modification on server
    portal_sync = self.getSynchronizationTool()
    document_server = self.getDocumentServer()
    document_s = document_server._getOb(self.id1)
    kw = {'reference':self.reference3, 'language':self.language3,
    'version':self.version3}
    document_s.edit(**kw)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    document_client1 = self.getDocumentClient1()
    document_c = document_client1._getOb(self.id1)
    self.assertEqual(document_s.getReference(), self.reference3)
    self.assertEqual(document_s.getLanguage(), self.language3)
    self.assertEqual(document_s.getVersion(), self.version3)
    self.assertEqual(document_c.getSourceReference(), self.filename_text)
    self.assertEquals(self.size_filename_text, document_c.get_size())
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)
    # Then we do only modification on a client (the gid) of client => add a object
    kw = {'reference':self.reference1,'version':self.version3}
    document_c.edit(**kw)
    file = makeFileUpload(self.filename_odt)
    document_c.edit(file=file)
    transaction.commit()
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    document_s = document_server._getOb(self.id1)
    self.assertEqual(document_s.getReference(), self.reference1)
    self.assertEqual(document_s.getLanguage(), self.language3)
    self.assertEqual(document_s.getVersion(), self.version3)
    self.assertEqual(document_c.getSourceReference(), self.filename_odt)
    self.assertEquals(self.size_filename_odt, document_c.get_size())
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)
    # Then we do only modification the field (useless for the gid)
    # on both the client and the server and of course, on the same object
    kw = {'description':self.description2}
    document_s.edit(**kw)
    kw = {'short_title':self.short_title1}
    document_c.edit(**kw)
    # The gid is modify so the synchronization add a object
    transaction.commit()
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    document_s = document_server._getOb(self.id1)
    self.assertEqual(document_s.getDescription(), self.description2)
    self.assertEqual(document_s.getShortTitle(), self.short_title1)
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)

  def test_04_DeleteObject(self, quiet=0):
    """
      We will do a first synchronization, then delete an object on both
    sides, and we will see if nothing is left on the server and also
    on the two clients
    """
    self.test_02_FirstSynchronization(quiet=1)
    if not quiet:
      ZopeTestCase._print('\nTest Delete Object ')
      LOG('Testing... ', 0, 'test_04_DeleteObject')
    document_server = self.getDocumentServer()
    document_server.manage_delObjects(self.id1)
    document_client1 = self.getDocumentClient1()
    document_client1.manage_delObjects(self.id2)
    transaction.commit()
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync.getPublication(self.pub_id)
    subscription1 = portal_sync.getSubscription(self.sub_id1)
    self.assertEqual(len(publication.getObjectList()), 0)
    self.assertEqual(len(subscription1.getObjectList()), 0)

  def test_05_FirstMultiSynchronization(self, quiet=0):
    #Add document on the server and first synchronization for client
    if not quiet:
      ZopeTestCase._print('\nTest First Multi Synchronization ')
      LOG('Testing... ', 0, 'test_05_FirstMultiSynchronization')
    nb_document = self.documentMultiServer(quiet=1)
    portal_sync = self.getSynchronizationTool()
    document_server = self.getDocumentServer()
    document_client = self.getDocumentClient1()
    nb_message1 = self.synchronize(self.sub_id1)
    self.assertNotEqual(nb_message1, 6)
    # It has transmitted some object
    for sub in portal_sync.getSubscriptionList():
      self.assertEquals(sub.getSynchronizationType(), SyncCode.TWO_WAY)
    self.checkSynchronizationStateIsSynchronized()
    self.checkFirstSynchronizationWithMultiDocument(nb_document=nb_document)

  def test_06_UpdateMultiData(self, quiet=0):
    # Add various data in server 
    # modification in client and server for synchronize
    if not quiet:
      ZopeTestCase._print('\nTest Update Multi Data ')
      LOG('Testing... ', 0, 'test_06_UpdateMultiData')
    self.test_05_FirstMultiSynchronization(quiet=1)
    # Side server modification gid of a text document
    document_server = self.getDocumentServer()
    document_client1= self.getDocumentClient1()
    id_text = str(self.ids[3])
    doc_s = document_server._getOb(id_text)
    kw = {'reference':self.reference3, 'language':self.language3,
        'version':self.version3, 'description':self.description3}
    doc_s.edit(**kw)
    # Side client modification gid of a odt document
    id_odt = str(self.ids[self.id_max_text+1])
    doc_c = document_client1._getOb(id_odt)
    kw = {'reference':self.reference2, 'language':self.language2,
        'version':self.version2, 'description':self.description2}
    doc_c.edit(**kw)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    # Check that the datas modified after synchronization
    doc_s = document_server._getOb(id_text)
    self.checkDocument(id=id_text, document=doc_s,\
                       filename=self.filename_text,\
                       size_filename=self.size_filename_text,\
                       reference=self.reference3,\
                       language=self.language3,\
                       version=self.version3,\
                       description = self.description3)
    doc_c = document_client1._getOb(id_odt)
    self.checkDocument(id=id_odt, document=doc_c,\
                       filename=self.filename_odt,\
                       size_filename=self.size_filename_odt,\
                       reference=self.reference2,\
                       language=self.language2,\
                       version=self.version2,\
                       description = self.description2)
    # Others
    doc_c = document_client1._getOb(str(self.ids[2]))
    reference = 'Test-Text-%s' % str(self.ids[2])
    self.checkDocument(id=str(self.ids[2]), document=doc_c,\
                       reference=reference, filename=self.filename_text,\
                       size_filename=self.size_filename_text)
    # Check the XMLs
    self.checkXMLsSynchronized()
    # Replace description and filename
    doc_s = document_server._getOb(id_text)
    kw = {'description':self.description1}
    doc_s.edit(**kw)
    file = makeFileUpload(self.filename_odt)
    doc_s.edit(file=file)
    #doc_s.convertToBaseFormat()
    # Side client modification gid of a odt document
    id_odt = str(self.ids[self.id_max_text+1])
    doc_c = document_client1._getOb(id_odt)
    kw = {'description':self.description3}
    doc_c.edit(**kw)
    file = makeFileUpload(self.filename_text)
    doc_c.edit(file=file)
    #doc_c.convertToBaseFormat()
    transaction.commit()
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    # Check that the datas modified after synchronization
    doc_s = document_server._getOb(id_text)
    self.checkDocument(id=id_text, document=doc_s,\
                       filename=self.filename_odt,\
                       size_filename=self.size_filename_odt,\
                       reference=self.reference3,\
                       language=self.language3,\
                       version=self.version3,\
                       description=self.description1)
    doc_c = document_client1._getOb(id_odt)
    self.checkDocument(id=id_odt, document=doc_c,\
                       filename=self.filename_text,\
                       size_filename=self.size_filename_text,\
                       reference=self.reference2,\
                       language=self.language2,\
                       version=self.version2,\
                       description = self.description3)
    doc_c = document_client1._getOb(str(self.ids[2]))
    reference = 'Test-Text-%s' % str(self.ids[2])
    self.checkDocument(id=str(self.ids[2]), document=doc_c,\
                       reference=reference, filename=self.filename_text,\
                       size_filename=self.size_filename_text)
    # Check the XMLs
    self.checkXMLsSynchronized()

  def test_07_SynchronizeWithStrangeIdGenerator(self, quiet=0):
    """
    By default, the synchronization process use the id in order to
    recognize objects (because by default, getGid==getId. Here, we will see 
    if it also works with a somewhat strange getGid
    """
    if not quiet:
      ZopeTestCase._print('\nTest Synchronize With Strange Gid ')
      LOG('Testing... ', 0, 'test_07_SynchronizeWithStrangeIdGenerator')
    self.setupPublicationAndSubscriptionIdGenerator(quiet=1)
    nb_document = self.documentServer(quiet=1)
    # This will test adding object
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync.getSubscription(self.sub_id1)
    self.assertEqual(len(subscription1.getObjectList()), nb_document)
    publication = portal_sync.getPublication(self.pub_id)
    self.assertEqual(len(publication.getObjectList()), nb_document)
    gid = self.reference1 +  '-' + self.version1 + '-' + self.language1 # ie the title ''
    gid = b16encode(gid)
    document_c1 = subscription1.getObjectFromGid(gid)
    id_c1 = document_c1.getId()
    self.assertTrue(id_c1 in ('1', '2')) # id given by the default generateNewId
    document_s = publication.getSubscriber(self.subscription_url['two_way']).getObjectFromGid(gid)
    id_s = document_s.getId()
    self.assertEqual(id_s, self.id1)
    # This will test updating object
    document_s.setDescription(self.description3)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(document_s.getDescription(), self.description3)
    self.assertEqual(document_c1.getDescription(), self.description3)
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c1)
    # This will test deleting object
    document_server = self.getDocumentServer()
    document_client1 = self.getDocumentClient1()
    document_server.manage_delObjects(self.id2)
    transaction.commit()
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(len(subscription1.getObjectList()), (nb_document-1))
    self.assertEqual(len(publication.getObjectList()), (nb_document-1))
    document_s = publication.getSubscriber(self.subscription_url['two_way']).getObjectFromGid(gid)
    id_s = document_s.getId()
    self.assertEqual(id_s, self.id1)
    document_c1 = subscription1.getObjectFromGid(gid)
    id_c1 = document_c1.getId()
    self.assertTrue(id_c1 in ('1', '2')) # id given by the default generateNewId
    self.assertEqual(document_s.getDescription(), self.description3)
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c1)

  def test_08_MultiNodeConflict(self, quiet=0):
    """
    We will create conflicts with 3 differents nodes, and we will
    solve it by taking one full version of documents.
    """
    #not conflict because is gid
    self.test_02_FirstSynchronization(quiet=1)
    if not quiet:
      ZopeTestCase._print('\nTest Multi Node Conflict ')
      LOG('Testing... ', 0, 'test_08_MultiNodeConflict')
    portal_sync = self.getSynchronizationTool()
    document_server = self.getDocumentServer()
    document_s = document_server._getOb(self.id1)
    kw = {'description':self.description2, 'short_title':self.short_title2}
    document_s.edit(**kw)
    file = makeFileUpload(self.filename_ppt)
    # XXX error with filename_pdf , may be is a PDF?
    document_s.edit(file=file)
    transaction.commit()
    self.tic()
    document_client1 = self.getDocumentClient1()
    document_c1 = document_client1._getOb(self.id1)
    kw = {'description':self.description3, 'short_title':self.short_title3}
    document_c1.edit(**kw)
    file = makeFileUpload(self.filename_odt)
    document_c1.edit(file=file)
    #document_c1.convertToBaseFormat()
    transaction.commit()
    self.tic()
    self.synchronize(self.sub_id1)
    conflict_list = portal_sync.getConflictList()
    self.assertEqual(len(conflict_list), 5)
    # check if we have the state conflict on all clients
    self.checkSynchronizationStateIsConflict()
    # we will take :
    # description et file on document_server
    # short_title on document_client1
    for conflict in conflict_list : 
      subscriber = conflict.getSubscriber()
      property = conflict.getPropertyId()
      resolve = 0
      if property == 'description':
        if subscriber.getSubscriptionUrl()==self.publication_url:
          resolve = 1
          conflict.applySubscriberValue()
      if property == 'short_title':
        if subscriber.getSubscriptionUrl()==self.subscription_url['two_way']:
          resolve = 1
          conflict.applySubscriberValue()
      if not resolve:
        conflict.applyPublisherValue()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(document_c1.getDescription(), self.description2)
    self.assertEqual(document_c1.getShortTitle(), self.short_title3)
    self.assertEqual(document_c1.getSourceReference(), self.filename_ppt)
    #XXX Error in convert XML
    #self.assertEquals(self.size_filename_text, document_c1.get_size())
    document_s = document_server._getOb(self.id1)
    document_c = document_client1._getOb(self.id1)
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c1)
    # the workflow has one more "workflow" in document_c1 
    #self.synchronize(self.sub_id1)
    #self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c1)

  def test_09_SynchronizeWorkflowHistory(self, quiet=0):
    """
    We will do a synchronization, then we will edit two times
    the object on the server, then two times the object on the
    client, and see if the global history as 4 more actions.
    """
    self.test_02_FirstSynchronization(quiet=1)
    if not quiet:
      ZopeTestCase._print('\nTest Synchronize WorkflowHistory ')
      LOG('Testing... ', 0, 'test_09_SynchronizeWorkflowHistory')
    document_server = self.getDocumentServer()
    document_s = document_server._getOb(self.id1)
    document_client1 = self.getDocumentClient1()
    document_c = document_client1._getOb(self.id1)
    kw1 = {'short_title':self.short_title1}
    kw2 = {'short_title':self.short_title2}
    len_wf = len(document_s.workflow_history[self.workflow_id])
    document_s.edit(**kw2)
    document_c.edit(**kw2)
    document_s.edit(**kw1)
    document_c.edit(**kw1)
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)
    self.assertEqual(len(document_s.workflow_history[self.workflow_id]), len_wf)
    self.assertEqual(len(document_c.workflow_history[self.workflow_id]), len_wf)

  def test_10_BrokenMessage(self, quiet=0):
    """
    With http synchronization, when a message is not well
    received, then we send message again, we want to
    be sure that is such case we don't do stupid things
    
    If we want to make this test more intersting, it is
    better to split messages
    """
    if not quiet:
      ZopeTestCase._print('\nTest Broken Message ')
      LOG('Testing... ', 0, 'test_10_BrokenMessage')
    previous_max_lines = SyncCode.MAX_LINES
    SyncCode.MAX_LINES = 10
    nb_document = self.documentServer(quiet=1)
    # Synchronize the first client
    nb_message1 = self.synchronizeWithBrokenMessage(self.sub_id1)
    #self.failUnless(nb_message1==self.nb_message_first_synchronization)
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync.getSubscription(self.sub_id1)
    self.assertEqual(len(subscription1.getObjectList()), nb_document)
    document_server = self.getDocumentServer() # We also check we don't
                                           # modify initial ob
    document_s = document_server._getOb(self.id1)
    document_client1 = self.getDocumentClient1()
    document_c = document_client1._getOb(self.id1)
    self.assertEqual(document_s.getId(), self.id1)
    self.assertEqual(document_s.getReference(), self.reference1)
    self.assertEqual(document_s.getLanguage(), self.language1)
    self.assertEqual(document_s.getSourceReference(), self.filename_text)
    self.assertEquals(self.size_filename_text, document_c.get_size())
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)
    SyncCode.MAX_LINES = previous_max_lines

  def test_11_AddOneWaySubscription(self, quiet=0):
    if not quiet:
      ZopeTestCase._print('\nTest Add One Way Subscription ')
      LOG('Testing... ', 0, 'test_11_AddOneWaySubscription')
    portal_id = self.getPortalId()
    portal_sync = self.getSynchronizationTool()
    portal_sync.manage_addSubscription(title=self.sub_id_from_server,
        publication_url=self.publication_url,
        subscription_url=self.subscription_url['from_server'],
        destination_path='/%s/document_client_from_server' % portal_id,
        source_uri='Document',
        target_uri='Document',
        query='objectValues',
        xml_mapping=self.xml_mapping,
        conduit='ERP5DocumentConduit',
        gpg_key='',
        activity_enabled=True,
        alert_code = SyncCode.ONE_WAY_FROM_SERVER,
        login = 'daniele',
        password = 'myPassword')
    sub = portal_sync.getSubscription(self.sub_id_from_server)
    self.assertTrue(sub.isOneWayFromServer())
    self.failUnless(sub is not None)

  def test_12_OneWaySync(self, quiet=0):
    """
    We will test if we can synchronize only from to server to the client.
    We want to make sure in this case that all modifications on the client
    will not be taken into account.
    """
    if not quiet:
      ZopeTestCase._print('\nTest One Way Sync ')
      LOG('Testing... ', 0, 'test_12_OneWaySync')
    self.test_11_AddOneWaySubscription(quiet=1)
    nb_document = self.documentServer(quiet=1, one_way=True)
    portal_sync = self.getSynchronizationTool()
    sub_from_server = portal_sync.getSubscription(self.sub_id_from_server)
    self.assertEquals(sub_from_server.getSynchronizationType(), SyncCode.SLOW_SYNC)
    # First do the sync from the server to the client
    nb_message1 = self.synchronize(self.sub_id_from_server)
    sub_from_server = portal_sync.getSubscription(self.sub_id_from_server)
    self.assertEquals(sub_from_server.getSynchronizationType(), SyncCode.ONE_WAY_FROM_SERVER)
    self.assertEquals(nb_message1, self.nb_message_first_synchronization)
    self.assertEquals(len(sub_from_server.getObjectList()), nb_document)
    document_server = self.getDocumentServer() # We also check we don't
                                           # modify initial ob
    document_s = document_server._getOb(self.id1)
    document_client1 = self.getDocumentClientFromServer()
    document_c = document_client1._getOb(self.id1)
    self.assertEqual(document_s.getId(), self.id1)
    self.assertEqual(document_s.getReference(), self.reference1)
    self.assertEqual(document_s.getLanguage(), self.language1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertXMLViewIsEqual(self.sub_id_from_server, document_s, document_c, force=1)
    # Then we change things on both sides and we look if there
    # is synchronization from only one way
    file = makeFileUpload(self.filename_odt)
    document_c.edit(file=file)
    #document_c.convertToBaseFormat()
    kw = {'short_title' : self.short_title2} 
    document_s.edit(**kw)
    transaction.commit()
    self.tic()
    self.assertEqual(document_s.getSourceReference(), self.filename_text)
    self.assertEquals(self.size_filename_text, document_s.get_size())
    nb_message1 = self.synchronize(self.sub_id_from_server)
    #In One_From_Server Sync not modify the first_name in client because any
    #datas client sent
    self.assertEqual(document_c.getSourceReference(), self.filename_odt)
    self.assertEquals(self.size_filename_odt, document_c.get_size())
    self.assertEquals(document_c.getShortTitle(), self.short_title2)
    self.assertEqual(document_s.getSourceReference(), self.filename_text)
    self.assertEquals(self.size_filename_text, document_s.get_size())
    self.assertEquals(document_s.getShortTitle(), self.short_title2) 
    
    #reset for refresh sync
    #after synchronize, the client object retrieve value of server
    self.resetSignaturePublicationAndSubscription()
    nb_message1 = self.synchronize(self.sub_id_from_server)
    self.assertEqual(document_c.getSourceReference(), self.filename_text)
    self.assertEquals(self.size_filename_text, document_c.get_size())
    self.assertEquals(document_c.getShortTitle(), self.short_title2) 
    self.checkSynchronizationStateIsSynchronized()
    document_s = document_server._getOb(self.id1)
    document_c = document_client1._getOb(self.id1)
    # FIXME we have to manage workflow
    #self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c, force=1)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5DocumentSyncML))
    return suite
