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
from base64 import b16encode
from unittest import expectedFailure
import unittest

from AccessControl.SecurityManagement import newSecurityManager

from Products.ERP5Type.tests.runUnitTest import tests_home
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5SyncML.Tool import SynchronizationTool
from Products.ERP5SyncML.tests.testERP5SyncML import TestERP5SyncMLMixin
from Products.ERP5SyncML.Document import SyncMLSubscription

test_files = os.path.join(os.path.dirname(__file__), 'test_document')
FILENAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})-\
(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})(-\
(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"

def makeFileUpload(name):
  path = os.path.join(test_files, name)
  return FileUpload(path, name)

class TestERP5DocumentSyncMLMixin(TestERP5SyncMLMixin):

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
  publication_url = 'file:/%s/sync_server' % tests_home
  subscription_url = {'two_way': 'file:/%s/sync_client1' % tests_home,
      'from_server': 'file:/%s/sync_client_from_server' % tests_home}
  #for this tests
  nb_message_first_synchronization = 6
  nb_message_multi_first_synchronization = 12
  activity_enable=False


  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return list(TestERP5SyncMLMixin.getBusinessTemplateList(self)) + \
        ['erp5_ingestion', 'erp5_ingestion_mysql_innodb_catalog',
        'erp5_web', 'erp5_dms']

  def afterSetUp(self):
    """Setup."""
    self.login()
    self.portal.z_drop_syncml()
    self.portal.z_create_syncml()
    self.addPublications()
    self.addSubscriptions()
    self.portal = self.getPortal()
    self.setSystemPreferences()
    self.tic()

  def beforeTearDown(self):
    """
      Do some stuff after each test:
      - clear document module of server and client
      - clear the publications and subscriptions
    """
    self.clearDocumentModules()
    self.clearPublicationsAndSubscriptions()


  def clearFiles(self):
    # reset files, because we do sync by files
    for filename in self.subscription_url.values():
      file = open(filename[len('file:/'):], 'w')
      file.write('')
      file.close()
    file = open(self.publication_url[len('file:/'):], 'w')
    file.write('')
    file.close()


  def setSystemPreferences(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredDocumentFileNameRegularExpression(FILENAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)
    if default_pref.getPreferenceState() == 'disabled':
      default_pref.enable()

  def addSubscriptions(self):
    portal_sync = self.getSynchronizationTool()
    if self.sub_id1 not in portal_sync.objectIds():
      subscription = portal_sync.newContent(portal_type='SyncML Subscription',
                      id=self.sub_id1,
                      url_string=self.publication_url,
                      subscription_url_string=self.subscription_url['two_way'],
                      source='document_client1',
                      source_reference='Document:',
                      destination_reference='Document',
                      list_method_id= self.sub_query1,
                      xml_binding_generator_method_id=self.xml_mapping,
                      conduit_module_id=self.sub_conduit1,
                      sync_alert_code='two_way',
                      is_activity_enabled=self.activity_enable,
                      user_id='daniele',
                      password='myPassword')
      subscription.validate()
      self.tic()

  def addPublications(self):
    portal_sync = self.getSynchronizationTool()
    if self.pub_id not in portal_sync.objectIds():
      publication = portal_sync.newContent(portal_type='SyncML Publication',
                             id=self.pub_id,
                             url_string=self.publication_url,
                             source='document_server',
                             source_reference='Document',
                             list_method_id=self.pub_query,
                             xml_binding_generator_method_id=self.xml_mapping,
                             conduit_module_id=self.pub_conduit,
                             is_activity_enabled=self.activity_enable,)
      publication.validate()
      self.tic()

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
    if getattr(self.portal, 'document_server', None) is not None:
      self.portal._delObject(id='document_server')
    if getattr(self.portal, 'document_client1', None) is not None:
      self.portal._delObject(id='document_client1')
    self.tic()

  def clearPublicationsAndSubscriptions(self):
    portal_sync = self.getSynchronizationTool()
    id_list = [object_id for object_id in portal_sync.objectIds()]
    portal_sync.manage_delObjects(id_list)
    self.tic()

  ####################
  ### Usefull methods
  ####################


  def getDocumentClient1(self):
    return getattr(self.portal, 'document_client1')

  def getDocumentClientFromServer(self):
    return getattr(self.portal, 'document_client_from_server')

  def getDocumentServer(self):
    return getattr(self.portal, 'document_server')

  def login(self):
    uf = self.portal.acl_users
    uf._doAddUser('daniele', 'myPassword', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    uf._doAddUser('syncml', '', ['Manager'], [])
    user = uf.getUserById('daniele').__of__(uf)
    newSecurityManager(None, user)

  def resetSignaturePublicationAndSubscription(self):
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync[self.pub_id]
    subscription1 = portal_sync[self.sub_id1]
    publication.resetSubscriberList()
    subscription1.resetSignatureList()
    subscription1.resetAnchorList()
    self.tic()

  def documentMultiServer(self):
    # create different document by category documents
    self.createDocumentModules()
    document_server = self.getDocumentServer()
    #plain text document
    for id in self.ids[:self.id_max_text]:
      reference = "Test-Text-%s" % (id,)
      self.createDocument(id=id, file_name=self.filename_text, reference=reference)
    self.commit()
    nb_document = len(document_server.objectValues())
    self.assertEqual(nb_document, len(self.ids[:self.id_max_text]))
    #binary document
    for id in self.ids[self.id_max_text:]:
      reference = "Test-Odt-%s" % (id, )
      self.createDocument(id=id, file_name=self.filename_odt, reference=reference)
    self.tic()
    nb_document = len(document_server.objectValues())
    self.assertEqual(nb_document, len(self.ids))
    return nb_document

  def createDocumentServerList(self, one_way=False):
    """
    create document in document_server
     """
    self.createDocumentModules(one_way)
    document_server = self.getDocumentServer()
    document_text = document_server.newContent(id=self.id1,
                                               portal_type='Text')
    kw = {'reference': self.reference1, 'Version': self.version1,
          'Language': self.language1, 'Description': self.description1}
    document_text.edit(**kw)
    file = makeFileUpload(self.filename_text)
    document_text.edit(file=file)
    self.tic()
    document_pdf = document_server.newContent(id=self.id2,
                                              portal_type='PDF')
    kw = {'reference': self.reference2, 'Version': self.version2,
          'Language': self.language2, 'Description': self.description2}
    document_pdf.edit(**kw)
    file = makeFileUpload(self.filename_pdf)
    document_pdf.edit(file=file)
    self.tic()
    nb_document = len(document_server)
    self.assertEqual(nb_document, 2)
    return nb_document

  def createDocument(self, id, file_name=None, portal_type='Text',
             reference='P-SYNCML.Text', version='001', language='en'):
    """
      Create a text document
    """
    document_server = self.getDocumentServer()
    doc_text = document_server.newContent(id=id, portal_type=portal_type)
    kw = {'reference': reference, 'version': version, 'language': language}
    doc_text.edit(**kw)
    if file_name is not None:
      file = makeFileUpload(file_name)
      doc_text.edit(file=file)
    return doc_text

  def checkSynchronizationStateIsSynchronized(self):
    portal_sync = self.getSynchronizationTool()
    document_server = self.getDocumentServer()
    for document in document_server.objectValues():
      state_list = self.getSynchronizationState(document)
      for state in state_list:
        self.assertEqual(state[1], 'no_conflict')
    document_client1 = self.getDocumentClient1()
    for document in document_client1.objectValues():
      state_list = self.getSynchronizationState(document)
      for state in state_list:
        self.assertEqual(state[1], 'no_conflict')
    # Check for each signature that the tempXML is None
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      for m in sub.contentValues():
        self.assertEqual(m.getTemporaryData(), None)
        self.assertEqual(m.getPartialData(), None)
    for pub in portal_sync.contentValues(portal_type='SyncML Publication'):
      for sub in pub.contentValues(portal_type='SyncML Subscription'):
        for m in sub.contentValues():
          self.assertEqual(m.getPartialData(), None)

  def checkFirstSynchronization(self, nb_document=0):

   portal_sync = self.getSynchronizationTool()
   subscription1 = portal_sync[self.sub_id1]
   self.assertEqual(len(subscription1), nb_document)
   document_server = self.getDocumentServer() # We also check we don't
                                            # modify initial ob
   doc1_s = document_server._getOb(self.id1)
   self.assertEqual(doc1_s.getId(), self.id1)
   self.assertEqual(doc1_s.getReference(), self.reference1)
   self.assertEqual(doc1_s.getVersion(), self.version1)
   self.assertEqual(doc1_s.getLanguage(), self.language1)
   self.assertEqual(doc1_s.getFilename(), self.filename_text)
   self.assertEqual(self.size_filename_text, doc1_s.get_size())
   doc2_s = document_server._getOb(self.id2)
   self.assertEqual(doc2_s.getReference(), self.reference2)
   self.assertEqual(doc2_s.getVersion(), self.version2)
   self.assertEqual(doc2_s.getLanguage(), self.language2)
   self.assertEqual(doc2_s.getFilename(), self.filename_pdf)
   self.assertEqual(self.size_filename_pdf, doc2_s.get_size())
   document_client1 = self.getDocumentClient1()
   document_c = document_client1._getOb(self.id1)
   self.assertEqual(document_c.getId(), self.id1)
   self.assertEqual(document_c.getReference(), self.reference1)
   self.assertEqual(document_c.getVersion(), self.version1)
   self.assertEqual(document_c.getLanguage(), self.language1)
   self.assertEqual(document_c.getFilename(), self.filename_text)
   self.assertEqual(self.size_filename_text, document_c.get_size())
   self.assertXMLViewIsEqual(self.sub_id1, doc1_s, document_c)
   self.assertXMLViewIsEqual(self.sub_id1, doc2_s,
                             document_client1._getOb(self.id2))

  def checkDocument(self, id, document, filename=None,
                    size_filename=None, reference='P-SYNCML.Text',
                    portal_type='Text', version='001', language='en',
                    description=''):
    """
      Check synchronization with a document and the information provided
    """
    if document is not None:
      self.assertEqual(document.getId(), id)
      self.assertEqual(document.getReference(), reference)
      self.assertEqual(document.getVersion(), version)
      self.assertEqual(document.getLanguage(), language)
      self.assertEqual(document.getDescription(), description)
      if filename is not None:
        self.assertEqual(document.getFilename(), filename)
        self.assertEqual(size_filename, document.get_size())
    else:
      self.fail("Document is None to check this information")

  def checkXMLsSynchronized(self):
    document_server = self.getDocumentServer()
    document_client1 = self.getDocumentClient1()
    for id in self.ids:
      doc_s = document_server._getOb(str(id))
      doc_c = document_client1._getOb(str(id))
      self.assertXMLViewIsEqual(self.sub_id1, doc_s, doc_c)


  def checkFirstSynchronizationWithMultiDocument(self, nb_document=0):
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync[self.sub_id1]
    self.assertEqual(len(subscription1.getDocumentList()), nb_document)
    document_server = self.getDocumentServer()
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

class TestERP5DocumentSyncML(TestERP5DocumentSyncMLMixin):

  def getTitle(self):
    return "ERP5 Document SyncML"

  def checkSynchronizationStateIsConflict(self, portal_type='Text'):
    document_server = self.getDocumentServer()
    for document in document_server.objectValues():
      if document.getId()==self.id1:
        state_list = self.getSynchronizationState(document)
        for state in state_list:
          self.assertEqual(state[1], 'conflict')
    document_client1 = self.getDocumentClient1()
    for document in document_client1.objectValues():
      if document.getId()==self.id1:
        state_list = self.getSynchronizationState(document)
        for state in state_list:
          self.assertEqual(state[1], 'conflict')
   # make sure sub object are also in a conflict mode
    document = document_client1._getOb(self.id1)
    state_list = self.getSynchronizationState(document)
    for state in state_list:
      self.assertEqual(state[1], 'conflict')


  def test_02_FirstSynchronization(self):
    # We will try to populate the folder document_client1
    # with the data form document_server
    nb_document = self.createDocumentServerList()
    portal_sync = self.getSynchronizationTool()
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')

    # Synchronize the first client
    nb_message1 = self.synchronize(self.sub_id1)
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
    self.assertEqual(nb_message1, self.nb_message_first_synchronization)
    self.checkSynchronizationStateIsSynchronized()
    self.checkFirstSynchronization(nb_document=nb_document)

  @expectedFailure
  def test_03_UpdateSimpleData(self):
    # Add two objects
    self.test_02_FirstSynchronization()
    # First we do only modification on server
    document_server = self.getDocumentServer()
    document_s = document_server._getOb(self.id1)
    # We modified GID information so we get
    # - deletion of former document
    # - addition of new document
    kw = {'reference':self.reference3, 'language':self.language3,
    'version':self.version3}
    document_s.edit(**kw)
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    document_client1 = self.getDocumentClient1()
    document_c = document_client1._getOb(self.id1)
    self.assertEqual(document_s.getReference(), self.reference3)
    self.assertEqual(document_s.getLanguage(), self.language3)
    self.assertEqual(document_s.getVersion(), self.version3)
    self.assertEqual(document_c.getFilename(), self.filename_text)
    self.assertEqual(self.size_filename_text, document_c.get_size())
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)
    # Then we do only modification on a client (the gid) of client => add a object
    kw = {'reference':self.reference1,'version':self.version3}
    document_c.edit(**kw)
    file = makeFileUpload(self.filename_odt)
    document_c.edit(file=file)
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    document_s = document_server._getOb(self.id1)
    self.assertEqual(document_s.getReference(), self.reference1)
    self.assertEqual(document_s.getLanguage(), self.language3)
    self.assertEqual(document_s.getVersion(), self.version3)
    self.assertEqual(document_c.getFilename(), self.filename_odt)
    self.assertEqual(self.size_filename_odt, document_c.get_size())
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)
    # Then we do only modification the field (useless for the gid)
    # on both the client and the server and of course, on the same object
    kw = {'description':self.description2}
    document_s.edit(**kw)
    kw = {'short_title':self.short_title1}
    document_c.edit(**kw)
    # The gid is modify so the synchronization add a object
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    document_c = document_client1._getOb(self.id1)
    self.assertEqual(document_c.getDescription(), self.description2)
    self.assertEqual(document_s.getShortTitle(), self.short_title1)
    self.assertEqual(document_s.getBaseData(), document_c.getBaseData())
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)

  def test_04_DeleteObject(self):
    """
      We will do a first synchronization, then delete an object on both
    sides, and we will see if nothing is left on the server and also
    on the two clients
    """
    self.test_02_FirstSynchronization()
    document_server = self.getDocumentServer()
    document_server.manage_delObjects(self.id1)
    document_client1 = self.getDocumentClient1()
    document_client1.manage_delObjects(self.id2)
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    portal_sync = self.getSynchronizationTool()
    publication = portal_sync[self.pub_id]
    subscription1 = portal_sync[self.sub_id1]
    self.assertEqual(len(publication.getDocumentList()), 0)
    self.assertEqual(len(subscription1.getDocumentList()), 0)

  def test_05_FirstMultiSynchronization(self):
    # Add document on the server and first synchronization for client
    nb_document = self.documentMultiServer()
    portal_sync = self.getSynchronizationTool()
    self.synchronize(self.sub_id1)
    # It has transmitted some object
    for sub in portal_sync.contentValues(portal_type='SyncML Subscription'):
      self.assertEqual(sub.getSyncmlAlertCode(), 'two_way')
    self.checkSynchronizationStateIsSynchronized()
    self.checkFirstSynchronizationWithMultiDocument(nb_document=nb_document)

  @expectedFailure
  def test_06_UpdateMultiData(self):
    # XXX This tests modify GID of document and so signature
    # get added and removed, due to bad behaviour in conduit, it fails
    # Add various data in server
    # modification in client and server for synchronize
    self.test_05_FirstMultiSynchronization()
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
    # Side client modification gid of a odt document
    id_odt = str(self.ids[self.id_max_text+1])
    doc_c = document_client1._getOb(id_odt)
    kw = {'description':self.description3}
    doc_c.edit(**kw)
    file = makeFileUpload(self.filename_text)
    doc_c.edit(file=file)
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

  def test_07_SynchronizeWithStrangeIdGenerator(self):
    """
    By default, the synchronization process use the id in order to
    recognize objects (because by default, getGid==getId. Here, we will see
    if it also works with a somewhat strange getGid
    """
    nb_document = self.createDocumentServerList()
    # This will test adding object
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    portal_sync = self.getSynchronizationTool()
    subscription1 = portal_sync[self.sub_id1]
    self.assertEqual(len(subscription1), nb_document)
    publication = portal_sync[self.pub_id]
    self.assertEqual(len(publication['1']), nb_document)
    gid = self.reference1 +  '-' + self.version1 + '-' + self.language1 # ie the title ''
    gid = b16encode(gid)
    document_c1 = subscription1.getDocumentFromGid(gid)
    document_s = publication.getSubscriber(self.subscription_url['two_way']).getDocumentFromGid(gid)
    id_s = document_s.getId()
    self.assertEqual(id_s, self.id1)
    # This will test updating object
    document_s.setDescription(self.description3)
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(document_s.getDescription(), self.description3)
    self.assertEqual(document_c1.getDescription(), self.description3)
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c1)
    # This will test deleting object
    document_server = self.getDocumentServer()
    document_server.manage_delObjects(self.id2)
    self.tic()
    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(len(subscription1.getDocumentList()), (nb_document-1))
    self.assertEqual(len(publication.getDocumentList()), (nb_document-1))
    document_s = publication.getSubscriber(self.subscription_url['two_way']).getDocumentFromGid(gid)
    id_s = document_s.getId()
    self.assertEqual(id_s, self.id1)
    document_c1 = subscription1.getDocumentFromGid(gid)
    self.assertEqual(document_s.getDescription(), self.description3)
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c1)

  @expectedFailure
  def test_08_MultiNodeConflict(self):
    """
    We will create conflicts with 3 differents nodes, and we will
    solve it by taking one full version of documents.
    """
    # XXX-Aurel Note that this test does no do what it describes !
    # Only conflict between one client and one server is done
    # so this is node multinodes at all !!

    # Do a first synchronization
    self.test_02_FirstSynchronization()
    # Then modify data on both side to generate conflicts on different
    # properties of the same document

    # Modify on server side
    document_server = self.getDocumentServer()
    document_s = document_server._getOb(self.id1)
    kw = {'description': self.description2, 'short_title': self.short_title2 }
    document_s.edit(**kw)
    file = makeFileUpload(self.filename_ppt)
    document_s.edit(file=file)
    self.tic()

    # Modify on client side
    document_client1 = self.getDocumentClient1()
    document_c1 = document_client1._getOb(self.id1)
    kw = {'description': self.description3, 'short_title': self.short_title3 }
    document_c1.edit(**kw)
    file = makeFileUpload(self.filename_odt)
    document_c1.edit(file=file)
    self.tic()

    self.synchronize(self.sub_id1)
    # Check conflicts generated
    conflict_list = self.getSynchronizationTool().getConflictList()
    self.assertEqual(len(conflict_list), 8)
    self.assertEqual(sorted([x.getPropertyId() for x in conflict_list]),
                     ['content_md5', 'content_type',
                      'data', 'description', 'filename', 'short_title',
                      'size', 'title'])
    # check if we have the state conflict on all clients
    self.checkSynchronizationStateIsConflict()
    # Fix conflict :
    # apply description & file property on document_server
    # short_title on document_client1
    for conflict in conflict_list :
      subscriber = conflict.getSubscriber()
      property_id = conflict.getPropertyId()
      if property_id == 'description' and \
          subscriber.getUrlString() == self.publication_url:
        conflict.applySubscriberValue()
        continue
      if property_id == 'short_title' and \
          subscriber.getUrlString() == self.subscription_url['two_way']:
        conflict.applySubscriberValue()
        continue
      conflict.applyPublisherValue()

    self.synchronize(self.sub_id1)
    self.checkSynchronizationStateIsSynchronized()
    self.assertEqual(document_c1.getDescription(), self.description2)
    self.assertEqual(document_c1.getShortTitle(), self.short_title3)
    self.assertEqual(document_c1.getFilename(), self.filename_ppt)
    #XXX Error in convert XML
    #self.assertEqual(self.size_filename_text, document_c1.get_size())
    document_s = document_server._getOb(self.id1)
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c1,
                              ignore_processing_status_workflow=True)

  @expectedFailure
  def test_10_BrokenMessage(self):
    """
    With http synchronization, when a message is not well
    received, then we send message again, we want to
    be sure that is such case we don't do stupid things

    If we want to make this test more intersting, it is
    better to split messages
    """
    previous_max_lines = SyncMLSubscription.MAX_LEN
    try:
      SynchronizationTool.MAX_LEN = 1 << 8
      nb_document = self.createDocumentServerList()
      # Synchronize the first client
      self.synchronizeWithBrokenMessage(self.sub_id1)

      portal_sync = self.getSynchronizationTool()
      subscription1 = portal_sync[self.sub_id1]
      self.assertEqual(len(subscription1.getDocumentList()), nb_document)
      document_server = self.getDocumentServer() # We also check we don't
                                             # modify initial ob
      document_s = document_server._getOb(self.id1)
      document_client1 = self.getDocumentClient1()
      document_c = document_client1._getOb(self.id1)
      self.assertEqual(document_s.getId(), self.id1)
      self.assertEqual(document_s.getReference(), self.reference1)
      self.assertEqual(document_s.getLanguage(), self.language1)
      self.assertEqual(document_s.getFilename(), self.filename_text)
      self.assertEqual(self.size_filename_text, document_c.get_size())
      self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c)
    finally:
      SyncMLSubscription.MAX_LEN = previous_max_lines

  def addOneWaySyncFromServerSubscription(self):
    portal_sync = self.getSynchronizationTool()
    portal_sync.newContent(portal_type='SyncML Subscription',
                  id=self.sub_id_from_server,
                  url_string=self.publication_url,
                  subscription_url_string=self.subscription_url['from_server'],
                  source='document_client_from_server',
                  source_reference='DocumentSubscription',
                  destination_reference='Document',
                  list_method_id='objectValues',
                  xml_binding_generator_method_id=self.xml_mapping,
                  conduit_module_id='ERP5DocumentConduit',
                  is_activity_enabled=self.activity_enable,
                  syncml_alert_code='one_way_from_server',
                  user_id='daniele',
                  password='myPassword')

  def test_12_OneWaySyncFromServer(self):
    """
    We will test if we can synchronize only from to server to the client.
    We want to make sure in this case that all modifications on the client
    will not be taken into account.
    """
    self.addOneWaySyncFromServerSubscription()
    nb_document = self.createDocumentServerList(one_way=True)
    portal_sync = self.getSynchronizationTool()
    sub_from_server = portal_sync[self.sub_id_from_server]
    self.assertEqual(sub_from_server.getSyncmlAlertCode(), 'one_way_from_server')
    # First do the sync from the server to the client
    nb_message1 = self.synchronize(self.sub_id_from_server)
    sub_from_server = portal_sync[self.sub_id_from_server]
    self.assertEqual(sub_from_server.getSyncmlAlertCode(), 'one_way_from_server')
    self.assertEqual(nb_message1, self.nb_message_first_synchronization)
    self.assertEqual(len(sub_from_server.getDocumentList()), nb_document)
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

    kw = {'short_title' : self.short_title2}
    document_s.edit(**kw)
    self.tic()
    self.assertEqual(document_s.getFilename(), self.filename_text)
    self.assertEqual(self.size_filename_text, document_s.get_size())
    nb_message1 = self.synchronize(self.sub_id_from_server)
    #In One_From_Server Sync not modify the first_name in client because any
    #datas client sent
    self.assertEqual(document_c.getFilename(), self.filename_odt)
    self.assertEqual(self.size_filename_odt, document_c.get_size())
    self.assertEqual(document_c.getShortTitle(), self.short_title2)
    self.assertEqual(document_s.getFilename(), self.filename_text)
    self.assertEqual(self.size_filename_text, document_s.get_size())
    self.assertEqual(document_s.getShortTitle(), self.short_title2)

    #reset for refresh sync
    #after synchronize, the client object retrieve value of server
    self.resetSignaturePublicationAndSubscription()
    nb_message1 = self.synchronize(self.sub_id_from_server)
    self.assertEqual(document_c.getFilename(), self.filename_text)
    self.assertEqual(self.size_filename_text, document_c.get_size())
    self.assertEqual(document_c.getShortTitle(), self.short_title2)
    self.checkSynchronizationStateIsSynchronized()
    document_s = document_server._getOb(self.id1)
    document_c = document_client1._getOb(self.id1)
    # Ignore processing status workflow as
    self.assertXMLViewIsEqual(self.sub_id1, document_s, document_c, force=True,
                              ignore_processing_status_workflow=True)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5DocumentSyncML))
    return suite
