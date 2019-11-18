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

"""
  A test suite for Document Management System functionality.
  This will test:
  - creating Text Document objects
  - setting properties of a document, assigning local roles
  - setting relations between documents (explicit and implicity)
  - searching in basic and advanced modes
  - document publication workflow settings
  - sourcing external content
  - (...)
  This will NOT test:
  - contributing files of various types
  - convertion between many formats
  - metadata extraction and editing
  - email ingestion
  These are subject to another suite "testIngestion".
"""

import unittest
import time
import StringIO
from subprocess import Popen, PIPE
from cgi import FieldStorage
from unittest import expectedFailure

import ZPublisher.HTTPRequest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Type.tests.utils import DummyLocalizer
from Products.ERP5OOo.OOoUtils import OOoBuilder
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import getSecurityManager
from Products.ERP5.Document.Document import NotConvertedError
from Products.ERP5Form.PreferenceTool import Priority
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.Globals import get_request
import os
from threading import Thread
import httplib
import urllib
import difflib
import re
from AccessControl import Unauthorized
from Products.ERP5Type import Permissions
from DateTime import DateTime
from ZTUtils import make_query

QUIET = 0

TEST_FILES_HOME = os.path.join(os.path.dirname(__file__), 'test_document')
FILENAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})(-(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"

def makeFilePath(name):
  return os.path.join(os.path.dirname(__file__), 'test_document', name)

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)

def getFileSize(name):
  path = makeFilePath(name)
  f = open(path, "r")
  file_size = len(f.read())
  f.close()
  return file_size

class TestDocumentMixin(ERP5TypeTestCase):

  business_template_list = ['erp5_core_proxy_field_legacy',
                            'erp5_jquery',
                            'erp5_full_text_mroonga_catalog',
                            'erp5_base',
                            'erp5_ingestion_mysql_innodb_catalog',
                            'erp5_ingestion',
                            'erp5_web',
                            'erp5_dms']

  def setUpOnce(self):
    # set a dummy localizer (because normally it is cookie based)
    self.portal.Localizer = DummyLocalizer()

  def afterSetUp(self):
    TestDocumentMixin.login(self)
    self.setSystemPreference()
    self.tic()
    self.login()

  def setSystemPreference(self):
    pref = self.getDefaultSystemPreference()
    id = self.__class__.__name__
    if pref.getPreferredConversionCacheFactory() != id:
      try:
        self.portal.portal_caches[id]
      except KeyError:
        self.setCacheFactory(
          self.portal.portal_caches.newContent(id, 'Cache Factory'))
      pref.setPreferredConversionCacheFactory(id)
    pref.setPreferredDocumentFilenameRegularExpression(FILENAME_REGULAR_EXPRESSION)
    pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)

  def setCacheFactory(self, cache_factory):
    cache_factory.cache_duration = 36000
    cache_plugin = cache_factory.newContent(portal_type='Ram Cache')
    cache_plugin.cache_expire_check_interval = 54000

  def getDocumentModule(self):
    return getattr(self.getPortal(),'document_module')

  def getBusinessTemplateList(self):
    return self.business_template_list

  def getNeededCategoryList(self):
    return ()

  def beforeTearDown(self):
    """
      Do some stuff after each test:
      - clear document module
    """
    self.abort()
    self.clearRestrictedSecurityHelperScript()
    activity_tool = self.portal.portal_activities
    activity_status = {m.processing_node < -1
                       for m in activity_tool.getMessageList()}
    if True in activity_status:
      activity_tool.manageClearActivities()
    else:
      assert not activity_status
    self.clearDocumentModule()

  conversion_format_permission_script_id_list = [
      'Document_checkConversionFormatPermission',
      'Image_checkConversionFormatPermission',
      'PDF_checkConversionFormatPermission']
  def clearRestrictedSecurityHelperScript(self):
    for script_id in self.conversion_format_permission_script_id_list:
      custom = self.getPortal().portal_skins.custom
      if script_id in custom.objectIds():
        custom.manage_delObjects(ids=[script_id])
        self.commit()

  def clearDocumentModule(self):
    """
      Remove everything after each run
    """
    self.abort()
    doc_module = self.getDocumentModule()
    doc_module.manage_delObjects(list(doc_module.objectIds()))
    self.tic()

class TestDocument(TestDocumentMixin):
  """
    Test basic document - related operations
  """

  def getTitle(self):
    return "DMS"

  ## setup


  ## helper methods

  def createTestDocument(self, filename=None, portal_type='Text', reference='TEST', version='002', language='en'):
    """
      Creates a text document
    """
    dm=self.getPortal().document_module
    doctext=dm.newContent(portal_type=portal_type)
    if filename is not None:
      f = open(makeFilePath(filename), 'rb')
      doctext.setTextContent(f.read())
      f.close()
    doctext.setReference(reference)
    doctext.setVersion(version)
    doctext.setLanguage(language)
    return doctext

  def getDocument(self, id):
    """
      Returns a document with given ID in the
      document module.
    """
    document_module = self.portal.document_module
    return getattr(document_module, id)

  def getPreferences(self, image_display):
    preference_tool = self.portal.portal_preferences
    height_preference = 'preferred_%s_image_height' % (image_display,)
    width_preference = 'preferred_%s_image_width' % (image_display,)
    height = int(preference_tool.getPreference(height_preference))
    width = int(preference_tool.getPreference(width_preference))
    return (width, height)

  def getURLSizeList(self, uri, **kw):
    # __ac=RVJQNVR5cGVUZXN0Q2FzZTo%3D is encoded ERP5TypeTestCase with empty password
    url = '%s?%s&__ac=%s' %(uri, make_query(kw), 'RVJQNVR5cGVUZXN0Q2FzZTo%3D')
    format=kw.get('format', 'jpeg')
    infile = urllib.urlopen(url)
    # save as file with proper incl. format filename (for some reasons PIL uses this info)
    filename = "%s%stest-image-format-resize.%s" %(os.getcwd(), os.sep, format)
    f = open(filename, "w")
    image_data = infile.read()
    f.write(image_data)
    f.close()
    infile.close()
    file_size = len(image_data)
    try:
      from PIL import Image
      image = Image.open(filename)
      image_size = image.size
    except ImportError:
      identify_output = Popen(['identify', filename],
                              stdout=PIPE).communicate()[0]
      image_size = tuple(map(lambda x:int(x),
                             identify_output.split()[2].split('x')))
    os.remove(filename)
    return image_size, file_size

  ## tests

  def test_01_HasEverything(self):
    """
      Standard test to make sure we have everything we need - all the tools etc
    """
    self.assertNotEqual(self.getCategoryTool(), None)
    self.assertNotEqual(self.getSimulationTool(), None)
    self.assertNotEqual(self.getTypeTool(), None)
    self.assertNotEqual(self.getSQLConnection(), None)
    self.assertNotEqual(self.getCatalogTool(), None)
    self.assertNotEqual(self.getWorkflowTool(), None)

  def test_02_RevisionSystem(self):
    """
      Test revision mechanism
    """
    # create a test document
    # revision should be 1
    # upload file (can be the same) into it
    # revision should now be 2
    # edit the document with any value or no values
    # revision should now be 3
    # contribute the same file through portal_contributions
    # the same document should now have revision 4 (because it should have done mergeRevision)
    # getRevisionList should return (1, 2, 3, 4)
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)
    self.tic()
    document_url = document.getRelativeUrl()
    def getTestDocument():
      return self.portal.restrictedTraverse(document_url)
    self.assertEqual(getTestDocument().getRevision(), '1')
    getTestDocument().edit(file=file)
    self.tic()
    self.assertEqual(getTestDocument().getRevision(), '2')
    getTestDocument().edit(title='Hey Joe')
    self.tic()
    self.assertEqual(getTestDocument().getRevision(), '3')
    another_document = self.portal.portal_contributions.newContent(file=file)
    self.tic()
    self.assertEqual(getTestDocument().getRevision(), '4')
    self.assertEqual(getTestDocument().getRevisionList(), ['1', '2', '3', '4'])

  def test_03_Versioning(self):
    """
      Test versioning
    """
    # create a document 1, set coordinates (reference=TEST, version=002, language=en)
    # create a document 2, set coordinates (reference=TEST, version=002, language=en)
    # create a document 3, set coordinates (reference=TEST, version=004, language=en)
    # run isVersionUnique on 1, 2, 3 (should return False, False, True)
    # change version of 2 to 003
    # run isVersionUnique on 1, 2, 3  (should return True)
    # run getLatestVersionValue on all (should return 3)
    # run getVersionValueList on 2 (should return [3, 2, 1])
    document_module = self.getDocumentModule()
    docs = {}
    docs[1] = self.createTestDocument(reference='TEST', version='002', language='en')
    docs[2] = self.createTestDocument(reference='TEST', version='002', language='en')
    docs[3] = self.createTestDocument(reference='TEST', version='004', language='en')
    docs[4] = self.createTestDocument(reference='ANOTHER', version='002', language='en')
    self.tic()
    self.assertFalse(docs[1].isVersionUnique())
    self.assertFalse(docs[2].isVersionUnique())
    self.assertTrue(docs[3].isVersionUnique())
    docs[2].setVersion('003')
    self.tic()
    self.assertTrue(docs[1].isVersionUnique())
    self.assertTrue(docs[2].isVersionUnique())
    self.assertTrue(docs[3].isVersionUnique())
    self.assertTrue(docs[1].getLatestVersionValue() == docs[3])
    self.assertTrue(docs[2].getLatestVersionValue() == docs[3])
    self.assertTrue(docs[3].getLatestVersionValue() == docs[3])
    version_list = [br.getRelativeUrl() for br in docs[2].getVersionValueList()]
    self.assertTrue(version_list == [docs[3].getRelativeUrl(), docs[2].getRelativeUrl(), docs[1].getRelativeUrl()])

  def test_04_VersioningWithLanguage(self):
    """
      Test versioning with multi-language support
    """
    # create empty test documents, set their coordinates as follows:
    # (1) TEST, 002, en
    # (2) TEST, 002, fr
    # (3) TEST, 002, pl
    # (4) TEST, 003, en
    # (5) TEST, 003, sp
    # the following calls (on any doc) should produce the following output:
    # getOriginalLanguage() = 'en'
    # getLanguageList = ('en', 'fr', 'pl', 'sp')
    # getLatestVersionValue() = 4
    # getLatestVersionValue('en') = 4
    # getLatestVersionValue('fr') = 2
    # getLatestVersionValue('pl') = 3
    # getLatestVersionValue('ru') = None
    # change user language into 'sp'
    # getLatestVersionValue() = 5
    # add documents:
    # (6) TEST, 004, pl
    # (7) TEST, 004, en
    # getLatestVersionValue() = 7
    localizer = self.portal.Localizer
    document_module = self.getDocumentModule()
    docs = {}
    docs[1] = self.createTestDocument(reference='TEST', version='002', language='en')
    time.sleep(1) # time span here because catalog records only full seconds
    docs[2] = self.createTestDocument(reference='TEST', version='002', language='fr')
    time.sleep(1)
    docs[3] = self.createTestDocument(reference='TEST', version='002', language='pl')
    time.sleep(1)
    docs[4] = self.createTestDocument(reference='TEST', version='003', language='en')
    time.sleep(1)
    docs[5] = self.createTestDocument(reference='TEST', version='003', language='sp')
    time.sleep(1)
    self.tic()
    doc = docs[2] # can be any
    self.assertTrue(doc.getOriginalLanguage() == 'en')
    self.assertTrue(doc.getLanguageList() == ['en', 'fr', 'pl', 'sp'])
    self.assertTrue(doc.getLatestVersionValue() == docs[4]) # there are two latest - it chooses the one in user language
    self.assertTrue(doc.getLatestVersionValue('en') == docs[4])
    self.assertTrue(doc.getLatestVersionValue('fr') == docs[2])
    self.assertTrue(doc.getLatestVersionValue('pl') == docs[3])
    self.assertTrue(doc.getLatestVersionValue('ru') == None)
    localizer.changeLanguage('sp') # change user language
    self.assertTrue(doc.getLatestVersionValue() == docs[5]) # there are two latest - it chooses the one in user language
    docs[6] = document_module.newContent(reference='TEST', version='004', language='pl')
    docs[7] = document_module.newContent(reference='TEST', version='004', language='en')
    self.tic()
    self.assertTrue(doc.getLatestVersionValue() == docs[7]) # there are two latest, neither in user language - it chooses the one in original language

  def test_06_testExplicitRelations(self):
    """
      Test explicit relations.
      Explicit relations are just like any other relation, so no need to test them here
      except for similarity cloud which we test.
    """
    # create test documents:
    # (1) TEST, 002, en
    # (2) TEST, 003, en
    # (3) ONE, 001, en
    # (4) TWO, 001, en
    # (5) THREE, 001, en
    # set 3 similar to 1, 4 to 3, 5 to 4
    # getSimilarCloudValueList on 4 should return 1, 3 and 5
    # getSimilarCloudValueList(depth=1) on 4 should return 3 and 5

    # create documents for test version and language
    # reference, version, language
    kw = {'portal_type': 'Drawing'}
    document1 = self.portal.document_module.newContent(**kw)
    document2 = self.portal.document_module.newContent(**kw)
    document3 = self.portal.document_module.newContent(**kw)
    document4 = self.portal.document_module.newContent(**kw)
    document5 = self.portal.document_module.newContent(**kw)

    document6 = self.portal.document_module.newContent(reference='SIX', version='001',
                                                                                    language='en',  **kw)
    document7 = self.portal.document_module.newContent(reference='SEVEN', version='001',
                                                                                    language='en',  **kw)
    document8 = self.portal.document_module.newContent(reference='SEVEN', version='001',
                                                                                    language='fr',  **kw)
    document9 = self.portal.document_module.newContent(reference='EIGHT', version='001',
                                                                                    language='en',  **kw)
    document10 = self.portal.document_module.newContent(reference='EIGHT', version='002',
                                                                                      language='en',  **kw)
    document11 = self.portal.document_module.newContent(reference='TEN', version='001',
                                                                                      language='en',  **kw)
    document12 = self.portal.document_module.newContent(reference='TEN', version='001',
                                                                                      language='fr',  **kw)
    document13 = self.portal.document_module.newContent(reference='TEN', version='002',
                                                                                      language='en',  **kw)

    document3.setSimilarValue(document1)
    document4.setSimilarValue(document3)
    document5.setSimilarValue(document4)

    document6.setSimilarValueList([document8,  document13])
    document7.setSimilarValue([document9])
    document11.setSimilarValue(document7)

    self.tic()

    #if user language is 'en'
    self.portal.Localizer.changeLanguage('en')

    # 4 is similar to 3 and 5, 3 similar to 1, last version are the same
    self.assertSameSet([document1, document3, document5],
                       document4.getSimilarCloudValueList())
    self.assertSameSet([document3, document5],
                       document4.getSimilarCloudValueList(depth=1))

    self.assertSameSet([document7, document13],
                       document6.getSimilarCloudValueList())
    self.assertSameSet([document10, document13],
                       document7.getSimilarCloudValueList())
    self.assertSameSet([document7, document13],
                       document9.getSimilarCloudValueList())
    self.assertSameSet([],
                       document10.getSimilarCloudValueList())
    # 11 similar to 7, last version of 7 (en) is 7, similar of 7 is 9, last version of 9 (en) is 10
    self.assertSameSet([document7, document10],
                       document11.getSimilarCloudValueList())
    self.assertSameSet([document6, document7],
                       document13.getSimilarCloudValueList())

    self.commit()

    # if user language is 'fr', test that latest documents are prefferable returned in user_language (if available)
    self.portal.Localizer.changeLanguage('fr')

    self.assertSameSet([document8, document13],
                       document6.getSimilarCloudValueList())
    self.assertSameSet([document6, document13],
                       document8.getSimilarCloudValueList())
    self.assertSameSet([document8, document10],
                       document11.getSimilarCloudValueList())
    self.assertSameSet([],
                       document12.getSimilarCloudValueList())
    self.assertSameSet([document6, document8],
                       document13.getSimilarCloudValueList())

    self.commit()

    # if user language is "bg"
    self.portal.Localizer.changeLanguage('bg')
    self.assertSameSet([document8, document13],
                       document6.getSimilarCloudValueList())

  def test_07_testImplicitRelations(self):
    """
      Test implicit (wiki-like) relations.
    """
    # XXX this test should be extended to check more elaborate language selection

    def sqlresult_to_document_list(result):
      return [i.getObject() for i in result]

    # create docs to be referenced:
    # (1) TEST, 002, en
    filename = 'TEST-en-002.odt'
    file = makeFileUpload(filename)
    document1 = self.portal.portal_contributions.newContent(file=file)

    # (2) TEST, 002, fr
    as_name = 'TEST-fr-002.odt'
    file = makeFileUpload(filename, as_name)
    document2 = self.portal.portal_contributions.newContent(file=file)

    # (3) TEST, 003, en
    as_name = 'TEST-en-003.odt'
    file = makeFileUpload(filename, as_name)
    document3 = self.portal.portal_contributions.newContent(file=file)

    # create docs to contain references in text_content:
    # REF, 001, en; "I use reference to look up TEST"
    filename = 'REF-en-001.odt'
    file = makeFileUpload(filename)
    document4 = self.portal.portal_contributions.newContent(file=file)

    # REF, 002, en; "I use reference to look up TEST"
    filename = 'REF-en-002.odt'
    file = makeFileUpload(filename)
    document5 = self.portal.portal_contributions.newContent(file=file)

    # REFLANG, 001, en: "I use reference and language to look up TEST-fr"
    filename = 'REFLANG-en-001.odt'
    file = makeFileUpload(filename)
    document6 = self.portal.portal_contributions.newContent(file=file)

    # REFVER, 001, en: "I use reference and version to look up TEST-002"
    filename = 'REFVER-en-001.odt'
    file = makeFileUpload(filename)
    document7 = self.portal.portal_contributions.newContent(file=file)

    # REFVERLANG, 001, en: "I use reference, version and language to look up TEST-002-en"
    filename = 'REFVERLANG-en-001.odt'
    file = makeFileUpload(filename)
    document8 = self.portal.portal_contributions.newContent(file=file)

    self.tic()
    # the implicit predecessor will find documents by reference.
    # version and language are not used.
    # the implicit predecessors should be:

    # for (1): REF-002, REFLANG, REFVER, REFVERLANG
    # document1's reference is TEST. getImplicitPredecessorValueList will
    # return latest version of documents which contains string "TEST".
    self.assertSameSet(
      [document5, document6, document7, document8],
      sqlresult_to_document_list(document1.getImplicitPredecessorValueList()))

    # clear transactional variable cache
    self.commit()

    # the implicit successors should be return document with appropriate
    # language.

    # if user language is 'en'.
    self.portal.Localizer.changeLanguage('en')

    self.assertSameSet(
      [document3],
      sqlresult_to_document_list(document5.getImplicitSuccessorValueList()))

    # clear transactional variable cache
    self.commit()

    # if user language is 'fr'.
    self.portal.Localizer.changeLanguage('fr')
    self.assertSameSet(
      [document2],
      sqlresult_to_document_list(document5.getImplicitSuccessorValueList()))

    # clear transactional variable cache
    self.commit()

    # if user language is 'ja'.
    self.portal.Localizer.changeLanguage('ja')
    self.assertSameSet(
      [document3],
      sqlresult_to_document_list(document5.getImplicitSuccessorValueList()))

    # with empty reference no implicit relation should exists even though some documents
    # used to reference us with previous reference
    document1.setReference(None)
    self.tic()
    self.assertSameSet([],
      sqlresult_to_document_list(document1.getImplicitPredecessorValueList()))

  def testOOoDocument_get_size(self):
    # test get_size on OOoDocument
    doc = self.portal.document_module.newContent(portal_type='Spreadsheet')
    doc.edit(file=makeFileUpload('import_data_list.ods'))
    self.assertEqual(len(makeFileUpload('import_data_list.ods').read()),
                      doc.get_size())

  def testTempOOoDocument_get_size(self):
    # test get_size on temporary OOoDocument
    from Products.ERP5Type.Document import newTempOOoDocument
    doc = newTempOOoDocument(self.portal, 'tmp')
    doc.edit(data='OOo')
    self.assertEqual(len('OOo'), doc.get_size())

  def testOOoDocument_hasData(self):
    # test hasData on OOoDocument
    doc = self.portal.document_module.newContent(portal_type='Spreadsheet')
    self.assertFalse(doc.hasData())
    doc.edit(file=makeFileUpload('import_data_list.ods'))
    self.assertTrue(doc.hasData())

  def testTempOOoDocument_hasData(self):
    # test hasData on TempOOoDocument
    from Products.ERP5Type.Document import newTempOOoDocument
    doc = newTempOOoDocument(self.portal, 'tmp')
    self.assertFalse(doc.hasData())
    doc.edit(file=makeFileUpload('import_data_list.ods'))
    self.assertTrue(doc.hasData())

  def test_Owner_Base_download(self):
    # tests that owners can download original documents and OOo
    # documents, and all headers (including filenames) are set
    # correctly
    doc = self.portal.document_module.newContent(
                                  filename='test.ods',
                                  portal_type='Spreadsheet')
    doc.edit(file=makeFileUpload('TEST-en-002.doc'))
    self.tic()

    uf = self.portal.acl_users
    uf._doAddUser('member_user1', 'secret', ['Member', 'Owner'], [])
    user = uf.getUserById('member_user1').__of__(uf)
    newSecurityManager(None, user)

    response = self.publish('%s/Base_download' % doc.getPath(),
                            basic='member_user1:secret')
    self.assertEqual(makeFileUpload('TEST-en-002.doc').read(),
                      response.getBody())
    self.assertEqual('application/msword',
                      response.headers['content-type'])
    self.assertEqual('attachment; filename="TEST-en-002.doc"',
                      response.headers['content-disposition'])
    response = self.publish('%s/OOoDocument_getOOoFile' % doc.getPath(),
                            basic='member_user1:secret')
    self.assertEqual('application/vnd.oasis.opendocument.text',
                      response.headers['content-type'])
    self.assertEqual('attachment; filename="TEST-en-002.odt"',
                      response.headers['content-disposition'])

  def test_Member_download_pdf_format(self):
    # tests that members can download OOo documents in pdf format (at least in
    # published state), and all headers (including filenames) are set correctly
    doc = self.portal.document_module.newContent(
                                  filename='test.ods',
                                  portal_type='Spreadsheet')
    doc.edit(file=makeFileUpload('import.file.with.dot.in.filename.ods'))
    doc.publish()
    self.tic()

    uf = self.portal.acl_users
    uf._doAddUser('member_user2', 'secret', ['Member'], [])
    user = uf.getUserById('member_user2').__of__(uf)
    newSecurityManager(None, user)

    response = self.publish('%s?format=pdf' % doc.getPath(),
                            basic='member_user2:secret')
    self.assertEqual('application/pdf', response.getHeader('content-type'))
    self.assertEqual('attachment; filename="import.file.with.dot.in.filename.pdf"',
                      response.getHeader('content-disposition'))
    response_body = response.getBody()
    conversion = str(doc.convert('pdf')[1])
    diff = '\n'+'\n'.join(difflib.unified_diff(response_body.splitlines(),
                                          conversion.splitlines(),
                                          fromfile='first_call.pdf',
                                          tofile='second_call.pdf'))
    self.assertEqual(response_body, conversion, diff)

    # test Print icon works on OOoDocument
    response = self.publish('%s/OOoDocument_print' % doc.getPath())
    self.assertEqual('application/pdf',
                      response.headers['content-type'])
    self.assertEqual('attachment; filename="import.file.with.dot.in.filename.pdf"',
                      response.headers['content-disposition'])

  def test_05_getCreationDate(self):
    """
    Check getCreationDate on all document types.
    """
    portal = self.getPortalObject()
    for document_type in portal.getPortalDocumentTypeList():
      module = portal.getDefaultModule(document_type)
      obj = module.newContent(portal_type=document_type)
      self.assertNotEquals(obj.getCreationDate(),
                           module.getCreationDate())
      self.assertNotEquals(obj.getCreationDate(),
                           portal.CreationDate())

  def test_06_ProcessingStateOfAClonedDocument(self):
    """
    Check that the processing state of a cloned document
    is not draft
    """
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)

    self.assertEqual('converting', document.getExternalProcessingState())
    self.commit()
    self.assertEqual('converting', document.getExternalProcessingState())

    # Clone a uploaded document
    container = document.getParentValue()
    clipboard = container.manage_copyObjects(ids=[document.getId()])
    paste_result = container.manage_pasteObjects(cb_copy_data=clipboard)
    new_document = container[paste_result[0]['new_id']]

    self.assertEqual('converting', new_document.getExternalProcessingState())
    self.commit()
    self.assertEqual('converting', new_document.getExternalProcessingState())

    # Change workflow state to converted
    self.tic()
    self.assertEqual('converted', document.getExternalProcessingState())
    self.assertEqual('converted', new_document.getExternalProcessingState())

    # Clone a converted document
    container = document.getParentValue()
    clipboard = container.manage_copyObjects(ids=[document.getId()])
    paste_result = container.manage_pasteObjects(cb_copy_data=clipboard)
    new_document = container[paste_result[0]['new_id']]

    self.assertEqual('converted', new_document.getExternalProcessingState())
    self.commit()
    self.assertEqual('converted', new_document.getExternalProcessingState())
    self.tic()
    self.assertEqual('converted', new_document.getExternalProcessingState())

  def test_07_EmbeddedDocumentOfAClonedDocument(self):
    """
    Check the validation state of embedded document when its container is
    cloned
    """
    document = self.portal.person_module.newContent(portal_type='Person')

    sub_document = document.newContent(portal_type='Embedded File')
    self.assertEqual('embedded', sub_document.getValidationState())
    self.tic()
    self.assertEqual('embedded', sub_document.getValidationState())

    # Clone document
    container = document.getParentValue()
    clipboard = container.manage_copyObjects(ids=[document.getId()])

    paste_result = container.manage_pasteObjects(cb_copy_data=clipboard)
    new_document = container[paste_result[0]['new_id']]

    new_sub_document_list = new_document.contentValues(portal_type='Embedded File')
    self.assertEqual(1, len(new_sub_document_list))
    new_sub_document = new_sub_document_list[0]
    self.assertEqual('embedded', new_sub_document.getValidationState())
    self.tic()
    self.assertEqual('embedded', new_sub_document.getValidationState())

  def test_08_NoImagesCreatedDuringHTMLConversion(self):
    """Converting an ODT to html no longer creates Images embedded in the
    document.
    """
    filename = 'EmbeddedImage-en-002.odt'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)

    self.tic()

    self.assertEqual(0, len(document.contentValues(portal_type='Image')))
    document.convert(format='html')
    image_list = document.contentValues(portal_type='Image')
    self.assertEqual(0, len(image_list))

  def test_09_SearchableText(self):
    """
    Check DMS SearchableText capabilities.
    """
    portal = self.portal

    # Create a document.
    document_1 = self.portal.document_module.newContent(
                        portal_type = 'File',
                        description = 'Hello. ScriptableKey is very useful if you want to make your own search syntax.',
                        language = 'en',
                        version = '001')
    document_2 = self.portal.document_module.newContent(
                        portal_type='File',
                        description = 'This test make sure that scriptable key feature on ZSQLCatalog works.',
                        language='fr',
                        version = '002')
    document_3 = portal.document_module.newContent(
                   portal_type = 'Presentation',
                   title = "Complete set of tested reports with a long title.",
                   version = '003',
                   language = 'bg',
                   reference = 'tio-test-doc-3')
    person = portal.person_module.newContent(portal_type = 'Person', \
                                             reference= "john",
                                             title='John Doe Great')
    web_page = portal.web_page_module.newContent(portal_type = 'Web Page',
                                                 reference = "page_great_site",
                                                 text_content = 'Great website',
                                                 language='en',
                                                 version = '003')
    organisation = portal.organisation_module.newContent( \
                            portal_type = 'Organisation', \
                            reference = 'organisation-1',
                            title='Super nova organisation')
    self.tic()

    def getAdvancedSearchTextResultList(searchable_text, portal_type=None,src__=0):
      kw = {'full_text': searchable_text}
      if portal_type is not None:
        kw['portal_type'] = portal_type
      if src__==1:
        print portal.portal_catalog(src__=src__,**kw)
      return [x.getObject() for x in portal.portal_catalog(**kw)]

    # full text search
    self.assertSameSet([document_1], \
      getAdvancedSearchTextResultList('ScriptableKey'))
    self.assertEqual(len(getAdvancedSearchTextResultList('RelatedKey')), 0)
    self.assertSameSet([document_1, document_2], \
      getAdvancedSearchTextResultList('make', ('File',)))
    self.assertSameSet([web_page, person], \
      getAdvancedSearchTextResultList("Great", ('Person', 'Web Page')))
    # full text search with whole title of a document
    self.assertSameSet([document_3], \
      getAdvancedSearchTextResultList(document_3.getTitle(), ('Presentation',)))
    # full text search with reference part of searchable_text
    # (i.e. not specified with 'reference:' - simply part of search text)
    self.assertSameSet([document_3], \
      getAdvancedSearchTextResultList(document_3.getReference(), ('Presentation',)))

   # full text search with reference
    self.assertSameSet([web_page], \
      getAdvancedSearchTextResultList("reference:%s Great" %web_page.getReference()))
    self.assertSameSet([person],
          getAdvancedSearchTextResultList('reference:%s' %person.getReference()))

    # full text search with portal_type
    self.assertSameSet([person], \
      getAdvancedSearchTextResultList('%s portal_type:%s' %(person.getTitle(), person.getPortalType())))

    self.assertSameSet([organisation], \
      getAdvancedSearchTextResultList('%s portal_type:%s' \
                                       %(organisation.getTitle(),
                                         organisation.getPortalType())))

    # full text search with portal_type passed outside searchable_text
    self.assertSameSet([web_page, person],
                       getAdvancedSearchTextResultList('Great',
                          ('Person', 'Web Page')))
    self.assertSameSet([web_page], \
                       getAdvancedSearchTextResultList('Great', web_page.getPortalType()))
    self.assertSameSet([person], \
                       getAdvancedSearchTextResultList('Great', person.getPortalType()))

    # full text search with portal_type & reference
    self.assertSameSet([person], \
      getAdvancedSearchTextResultList('reference:%s portal_type:%s' \
                                        %(person.getReference(), person.getPortalType())))
    # full text search with language
    self.assertSameSet([document_1, web_page], \
      getAdvancedSearchTextResultList('language:en'))
    self.assertSameSet([document_1], \
      getAdvancedSearchTextResultList('ScriptableKey language:en'))
    self.assertSameSet([document_2], \
      getAdvancedSearchTextResultList('language:fr'))
    self.assertSameSet([web_page], \
      getAdvancedSearchTextResultList('%s reference:%s language:%s' \
                                       %(web_page.getTextContent(),
                                         web_page.getReference(),
                                         web_page.getLanguage())))
    # full text search with version
    self.assertSameSet([web_page], \
      getAdvancedSearchTextResultList('%s reference:%s language:%s version:%s' \
                                       %(web_page.getTextContent(),
                                         web_page.getReference(),
                                         web_page.getLanguage(),
                                         web_page.getVersion())))

    document = portal.document_module.newContent(
                   portal_type = 'Presentation',)
    # searchable text is empty by default
    self.assertEqual('', document.SearchableText())
    # it contains title
    document.setTitle('foo')
    self.assertEqual('foo', document.SearchableText())
    # and description
    document.setDescription('bar')
    self.assertTrue('bar' in document.SearchableText(),
      document.SearchableText())

  def test_10_SearchString(self):
    """
    Test search string search generation and parsing.
    """

    portal = self.portal
    assemble = portal.Base_assembleSearchString
    parse = portal.Base_parseSearchString

    # directly pasing searchable string
    self.assertEqual('searchable text',
                      assemble(**{'searchabletext': 'searchable text'}))
    kw = {'searchabletext_any': 'searchabletext_any',
          'searchabletext_phrase': 'searchabletext_phrase1 searchabletext_phrase1'}
    # exact phrase
    search_string = assemble(**kw)
    self.assertEqual('%s "%s"' %(kw['searchabletext_any'], kw['searchabletext_phrase']), \
                      search_string)
    parsed_string = parse(search_string)
    self.assertEqual(['searchabletext'], parsed_string.keys())


    # search "with all of the words"
    kw["searchabletext_all"] = "searchabletext_all1 searchabletext_all2"
    search_string = assemble(**kw)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2', \
                      search_string)
    parsed_string = parse(search_string)
    self.assertEqual(['searchabletext'], parsed_string.keys())

    # search without these words
    kw["searchabletext_without"] = "searchabletext_without1 searchabletext_without2"
    search_string = assemble(**kw)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2', \
                      search_string)
    parsed_string = parse(search_string)
    self.assertEqual(['searchabletext'], parsed_string.keys())

    # search limited to a certain date range
    kw['created_within'] = '1w'
    search_string = assemble(**kw)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w', \
                      search_string)
    parsed_string = parse(search_string)
    self.assertSameSet(['searchabletext', 'creation_from'], parsed_string.keys())

    # search with portal_type
    kw['search_portal_type'] = 'Document'
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w AND (portal_type:Document)', \
                      search_string)
    self.assertSameSet(['searchabletext', 'creation_from', 'portal_type'], \
                        parsed_string.keys())
    self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])

    # search by reference
    kw['reference'] = 'Nxd-test'
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w AND (portal_type:Document) reference:Nxd-test', \
                      search_string)
    self.assertSameSet(['searchabletext', 'creation_from', 'portal_type', 'reference'], \
                        parsed_string.keys())
    self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])
    self.assertEqual(kw['reference'], parsed_string['reference'])

    # search by version
    kw['version'] = '001'
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w AND (portal_type:Document) reference:Nxd-test version:001', \
                      search_string)
    self.assertSameSet(['searchabletext', 'creation_from', 'portal_type', 'reference', 'version'], \
                        parsed_string.keys())
    self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])
    self.assertEqual(kw['reference'], parsed_string['reference'])
    self.assertEqual(kw['version'], parsed_string['version'])

    # search by language
    kw['language'] = 'en'
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w AND (portal_type:Document) reference:Nxd-test version:001 language:en', \
                      search_string)
    self.assertSameSet(['searchabletext', 'creation_from', 'portal_type', 'reference', \
                        'version', 'language'], \
                        parsed_string.keys())
    self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])
    self.assertEqual(kw['reference'], parsed_string['reference'])
    self.assertEqual(kw['version'], parsed_string['version'])
    self.assertEqual(kw['language'], parsed_string['language'])

    # contributor title search
    kw['contributor_title'] = 'John'
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w AND (portal_type:Document) reference:Nxd-test version:001 language:en contributor_title:John', \
                      search_string)
    self.assertSameSet(['searchabletext', 'creation_from', 'portal_type', 'reference', \
                        'version', 'language', 'contributor_title'], \
                        parsed_string.keys())
    self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])
    self.assertEqual(kw['reference'], parsed_string['reference'])
    self.assertEqual(kw['version'], parsed_string['version'])
    self.assertEqual(kw['language'], parsed_string['language'])

    # only my docs
    kw['mine'] = 'yes'
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w AND (portal_type:Document) reference:Nxd-test version:001 language:en contributor_title:John mine:yes', \
                      search_string)
    self.assertSameSet(['searchabletext', 'creation_from', 'portal_type', 'reference', \
                        'version', 'language', 'contributor_title', 'mine'], \
                        parsed_string.keys())
    self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])
    self.assertEqual(kw['reference'], parsed_string['reference'])
    self.assertEqual(kw['version'], parsed_string['version'])
    self.assertEqual(kw['language'], parsed_string['language'])
    self.assertEqual(kw['mine'], parsed_string['mine'])

    # only newest versions
    kw['newest'] = 'yes'
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w AND (portal_type:Document) reference:Nxd-test version:001 language:en contributor_title:John mine:yes newest:yes', \
                      search_string)
    self.assertSameSet(['searchabletext', 'creation_from', 'portal_type', 'reference', \
                        'version', 'language', 'contributor_title', 'mine', 'newest'], \
                        parsed_string.keys())
    self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])
    self.assertEqual(kw['reference'], parsed_string['reference'])
    self.assertEqual(kw['version'], parsed_string['version'])
    self.assertEqual(kw['language'], parsed_string['language'])
    self.assertEqual(kw['mine'], parsed_string['mine'])
    self.assertEqual(kw['newest'], parsed_string['newest'])

    # search mode
    kw['search_mode'] = 'in_boolean_mode'
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('searchabletext_any "searchabletext_phrase1 searchabletext_phrase1"  +searchabletext_all1 +searchabletext_all2 -searchabletext_without1 -searchabletext_without2 created:1w AND (portal_type:Document) reference:Nxd-test version:001 language:en contributor_title:John mine:yes newest:yes mode:boolean', \
                      search_string)
    self.assertSameSet(['searchabletext', 'creation_from', 'portal_type', 'reference', \
                        'version', 'language', 'contributor_title', 'mine', 'newest', 'mode'], \
                        parsed_string.keys())
    self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])
    self.assertEqual(kw['reference'], parsed_string['reference'])
    self.assertEqual(kw['version'], parsed_string['version'])
    self.assertEqual(kw['language'], parsed_string['language'])
    self.assertEqual(kw['mine'], parsed_string['mine'])
    self.assertEqual(kw['newest'], parsed_string['newest'])
    self.assertEqual('boolean', parsed_string['mode'])

    # search with multiple portal_type
    kw = {'search_portal_type': ['Document','Presentation','Web Page'],
           'searchabletext_any': 'erp5'}
    search_string = assemble(**kw)
    parsed_string = parse(search_string)
    self.assertEqual('erp5 AND (portal_type:Document OR portal_type:Presentation OR portal_type:"Web Page")', \
                      search_string)
    self.assertSameSet(['searchabletext', 'portal_type'], \
                        parsed_string.keys())
    #self.assertEqual(kw['search_portal_type'], parsed_string['portal_type'])

    # parse with multiple portal_type containing spaces in one portal_type
    search_string = 'erp5 AND (portal_type:Document OR portal_type:Presentation OR portal_type:"Web Page")'
    parsed_string = parse(search_string)
    self.assertEqual(parsed_string['portal_type'], ['Document','Presentation','"Web Page"'])

  def test_11_Base_getAdvancedSearchResultList(self):
    """
    Test search string search capabilities using Base_getAdvancedSearchResultList script.
    """
    portal = self.portal
    assemble = portal.Base_assembleSearchString
    search = portal.Base_getAdvancedSearchResultList

    def getAdvancedSearchStringResultList(**kw):
      search_string = assemble(**kw)
      return [x.getObject() for x in search(search_string)]

    # create some objects
    document_1 = portal.document_module.newContent(
                   portal_type = 'File',
                   description = 'standalone software linux python free',
                   version = '001',
                   language = 'en',
                   reference = 'nxd-test-doc-1')
    document_2 = portal.document_module.newContent(
                   portal_type = 'Presentation',
                   description = 'standalone free python linux knowledge system management different',
                   version = '002',
                   language = 'fr',
                   reference = 'nxd-test-doc-2')
    document_3 = portal.document_module.newContent(
                   portal_type = 'Presentation',
                   description = 'just a copy',
                   version = '003',
                   language = 'en',
                   reference = 'nxd-test-doc-2')
    # multiple revisions of a Web Page
    web_page_1 = portal.web_page_module.newContent(
                   portal_type = 'Web Page',
                   text_content = 'software based solutions document management product standalone owner different',
                   version = '003',
                   language = 'jp',
                   reference = 'nxd-test-web-page-3')
    web_page_2 = portal.web_page_module.newContent(
                   portal_type = 'Web Page',
                   text_content = 'new revision (004) of nxd-test-web-page-3',
                   version = '004',
                   language = 'jp',
                   reference = 'nxd-test-web-page-3')
    web_page_3 = portal.web_page_module.newContent(
                   portal_type = 'Web Page',
                   text_content = 'new revision (005) of nxd-test-web-page-3',
                   version = '005',
                   language = 'jp',
                   reference = 'nxd-test-web-page-3')
    # publish documents so we can test searching within owned documents for an user
    for document in (document_1, document_2, document_3, web_page_1, web_page_2, web_page_3):
      document.publish()
    # create test Person objects and add pseudo local security
    person1 =  self.createUser(reference='user1')
    person1.setTitle('Another Contributor')
    portal.document_module.manage_setLocalRoles(person1.Person_getUserId(), ['Assignor',])
    self.tic()

    # login as another user
    super(TestDocument, self).loginByUserName('user1')
    document_4 = portal.document_module.newContent(
                   portal_type = 'Presentation',
                   description = 'owner different user contributing document',
                   version = '003',
                   language = 'bg',
                   reference = 'tlv-test-doc-1')
    self.login()
    contributor_list = document_4.getContributorValueList()
    contributor_list.append(person1)
    document_4.setContributorValueList(contributor_list)
    document_4.publish()
    self.tic()

    # search arbitrary word
    kw = {'searchabletext_any': 'software'}
    self.assertSameSet([document_1,web_page_1], getAdvancedSearchStringResultList(**kw))

    # exact word search
    kw = {'searchabletext_any': '',
          'searchabletext_phrase': 'linux python'}
    self.assertSameSet([document_1], getAdvancedSearchStringResultList(**kw))
    kw = {'searchabletext_any': '',
          'searchabletext_phrase': 'python linux'}
    self.assertSameSet([document_2], getAdvancedSearchStringResultList(**kw))
    kw = {'searchabletext_any': '',
          'searchabletext_phrase': 'python linux knowledge system'}
    self.assertSameSet([document_2], getAdvancedSearchStringResultList(**kw))

    # search "with all of the words" - each word prefixed by "+"
    kw = {'searchabletext_any': 'standalone',
          'searchabletext_all': 'python'}
    self.assertSameSet([document_1, document_2], getAdvancedSearchStringResultList(**kw))

    # search without these words - every word prefixed by "-"
    kw = {'searchabletext_any': 'standalone',
          'searchabletext_without': 'python'}
    self.assertSameSet([web_page_1], getAdvancedSearchStringResultList(**kw))

    # only given portal_types - add "type:Type" or type:(Type1,Type2...)
    kw = {'searchabletext_any': 'python',
          'search_portal_type': 'Presentation'}
    self.assertSameSet([document_2], getAdvancedSearchStringResultList(**kw))
    kw = {'searchabletext_any': 'python',
          'search_portal_type': 'File'}
    self.assertSameSet([document_1], getAdvancedSearchStringResultList(**kw))
    kw = {'searchabletext_any': 'management',
          'search_portal_type': 'File'}
    self.assertSameSet([], getAdvancedSearchStringResultList(**kw))

    # search by reference
    kw = {'reference': document_2.getReference()}
    self.assertSameSet([document_2, document_3], getAdvancedSearchStringResultList(**kw))
    kw = {'searchabletext_any': 'copy',
          'reference': document_2.getReference()}
    self.assertSameSet([document_3], getAdvancedSearchStringResultList(**kw))
    kw = {'searchabletext_any': 'copy',
          'reference': document_2.getReference(),
          'search_portal_type': 'File'}
    self.assertSameSet([], getAdvancedSearchStringResultList(**kw))

    # search by version
    kw = {'reference': document_2.getReference(),
          'version': document_2.getVersion()}
    self.assertSameSet([document_2], getAdvancedSearchStringResultList(**kw))
    kw = {'reference': document_2.getReference(),
          'version': document_2.getVersion(),
          'search_portal_type': 'File'}
    self.assertSameSet([], getAdvancedSearchStringResultList(**kw))

    # search by language
    kw = {'reference': document_2.getReference(),
          'language': document_2.getLanguage()}
    self.assertSameSet([document_2], getAdvancedSearchStringResultList(**kw))
    kw = {'reference': document_2.getReference(),
          'language': document_3.getLanguage()}
    self.assertSameSet([document_3], getAdvancedSearchStringResultList(**kw))
    kw = {'reference': document_2.getReference(),
          'language': document_3.getLanguage(),
          'search_portal_type': 'File'}
    self.assertSameSet([], getAdvancedSearchStringResultList(**kw))

    # only my docs
    super(TestDocument, self).loginByUserName('user1')
    kw = {'searchabletext_any': 'owner'}
    # should return all documents matching a word no matter if we're owner or not
    self.assertSameSet([web_page_1, document_4], getAdvancedSearchStringResultList(**kw))
    kw = {'searchabletext_any': 'owner',
          'mine': 'yes'}
    # should return ONLY our own documents matching a word
    self.assertSameSet([document_4], getAdvancedSearchStringResultList(**kw))
    self.login()

    # only newest versions
    # should return ALL documents for a reference
    kw = {'reference': web_page_1.getReference()}
    self.assertSameSet([web_page_1, web_page_2, web_page_3], getAdvancedSearchStringResultList(**kw))
    # should return ONLY newest document for a reference
    kw = {'reference': web_page_1.getReference(),
          'newest': 'yes'}
    self.assertSameSet([web_page_3], getAdvancedSearchStringResultList(**kw))

    # contributor title search
    kw = {'searchabletext_any': 'owner'}
    # should return all documents matching a word no matter of contributor
    self.assertSameSet([web_page_1, document_4], getAdvancedSearchStringResultList(**kw))
    kw = {'searchabletext_any': 'owner',
          'contributor_title': '%Contributor%'}
    self.assertSameSet([document_4], getAdvancedSearchStringResultList(**kw))

    # multiple portal_type specified
    kw = {'search_portal_type': 'File,Presentation'}
    self.assertSameSet([document_1, document_2, document_3, document_4], getAdvancedSearchStringResultList(**kw))

    # XXX: search limited to a certain date range
    # XXX: search mode

  # &nbsp; and &#160; are equivalent, and "pdftohtml" can generate
  # either depending on the version of the "poppler" package used.
  re_html_nbsp = re.compile('&(nbsp|#160);')

  def test_PDFTextContent(self):
    upload_file = makeFileUpload('REF-en-001.pdf')
    document = self.portal.portal_contributions.newContent(file=upload_file)
    self.assertEqual('PDF', document.getPortalType())
    self.assertEqual('I use reference to look up TEST\n',
                      document._convertToText())
    html_data = re.sub(self.re_html_nbsp, ' ', document._convertToHTML())
    self.assert_('I use reference to look up TEST' in html_data)
    self.assert_('I use reference to look up TEST' in
                 document.SearchableText())

  def test_PDFToImage(self):
    upload_file = makeFileUpload('REF-en-001.pdf')
    document = self.portal.portal_contributions.newContent(file=upload_file)
    self.assertEqual('PDF', document.getPortalType())

    content_type, image_data = document.convert(format='png',
                                                frame=0,
                                                display='thumbnail')
    # it's a valid PNG
    self.assertEqual('PNG', image_data[1:4])

  def test_PDF_content_information(self):
    upload_file = makeFileUpload('REF-en-001.pdf')
    document = self.portal.portal_contributions.newContent(file=upload_file)
    self.assertEqual('PDF', document.getPortalType())
    content_information = document.getContentInformation()
    self.assertEqual('1', content_information['Pages'])
    self.assertEqual('subject', content_information['Subject'])
    self.assertEqual('title', content_information['Title'])
    self.assertEqual('application/pdf', document.getContentType())

  def test_PDF_content_information_extra_metadata(self):
    # Extra metadata, such as those stored by pdftk update_info are also
    # available in document.getContentInformation()
    upload_file = makeFileUpload('metadata.pdf', as_name='REF-en-001.pdf')
    document = self.portal.portal_contributions.newContent(file=upload_file)
    self.tic()
    self.assertEqual('PDF', document.getPortalType())
    content_information = document.getContentInformation()
    self.assertEqual('the value', content_information['NonStandardMetadata'])
    self.assertEqual('1', content_information['Pages'])
    self.assertEqual('REF', document.getReference())

    # contribute file which will be merged to current document in synchronous mode
    # and check content_type recalculated
    upload_file = makeFileUpload('Forty-Two.Pages-en-001.pdf', as_name='REF-en-001.pdf')
    contributed_document = self.portal.Base_contribute(file=upload_file, \
                                                       synchronous_metadata_discovery=True)
    self.tic()
    content_information = contributed_document.getContentInformation()

    # we should have same data, respectively same PDF pages
    self.assertEqual(contributed_document.getSize(), document.getSize())
    self.assertEqual(contributed_document.getContentInformation()['Pages'], \
                     document.getContentInformation()['Pages'])
    self.assertEqual('42', \
                     document.getContentInformation()['Pages'])

    # upload with another file and check content_type recalculated
    upload_file = makeFileUpload('REF-en-001.pdf')
    document.setFile(upload_file)
    self.tic()
    content_information = document.getContentInformation()
    self.assertEqual('1', content_information['Pages'])

  def test_empty_PDF_content_information(self):
    document = self.portal.document_module.newContent(portal_type='PDF')
    content_information = document.getContentInformation()
    # empty PDF have no content information
    self.assertEqual({}, content_information)

  def test_apple_PDF_metadata(self):
    # PDF created with Apple software have a special 'AAPL:Keywords' info tag
    # and when pypdf extracts pdf information, it is returned as an
    # IndirectObject instance which is not picklable
    document = self.portal.document_module.newContent(
      portal_type='PDF',
      file=makeFileUpload('apple_metadata.pdf'))
    # content_information is picklable
    content_information = document.getContentInformation()
    from pickle import dumps
    dumps(content_information)
    # so document can be saved in ZODB
    self.commit()
    self.tic()

  def test_upload_bad_pdf_file(self):
    """ Test that pypdf2 handle wrong formatted PDF """
    path = os.path.join(os.path.dirname(__file__), 'test_document',
      'FEUILLE BLANCHE.pdf')
    file_upload = FileUpload(path, 'FEUILLE BLANCHE.pdf')
    pdf = self.portal.document_module.newContent(
      portal_type='PDF',
      file=file_upload,
      title='Bad PDF')
    self.tic()
    pdf.share()
    self.tic()
    self.assertEqual(pdf.getValidationState(), "shared")
    result = pdf.getContentInformation()
    self.assertNotEquals(result, None)

  def test_PDF_content_content_type(self):
    upload_file = makeFileUpload('REF-en-001.pdf')
    document = self.portal.document_module.newContent(portal_type='PDF')
    # Here we use edit instead of setFile,
    # because only edit method set filename as filename.
    document.edit(file=upload_file)
    self.assertEqual('application/pdf', document.getContentType())

  def test_PDF_watermark(self):
    original_document = self.portal.portal_contributions.newContent(
      file=makeFileUpload('REF-en-001.pdf'))
    # This watermark.pdf document is a pdf with a transparent background. Such
    # document can be created using GIMP
    watermark_document = self.portal.portal_contributions.newContent(
      file=makeFileUpload('watermark.pdf'))
    watermarked_data = original_document.getWatermarkedData(
      watermark_data=watermark_document.getData(),
      repeat_watermark=False)

    # this looks like a pdf
    self.assertTrue(watermarked_data.startswith('%PDF-1.3'))

    # and ERP5 can make a PDF Document out of it
    watermarked_document = self.portal.document_module.newContent(
      portal_type='PDF',
      data=watermarked_data)
    self.assertEqual('1', watermarked_document.getContentInformation()['Pages'])
    self.assertNotEqual(original_document.getData(),
      watermarked_document.getData())

  def test_PDF_watermark_repeat(self):
    # watermark a pdf, repeating the watermark
    original_document = self.portal.portal_contributions.newContent(
      file=makeFileUpload('Forty-Two.Pages-en-001.pdf'))
    watermark_document = self.portal.portal_contributions.newContent(
      file=makeFileUpload('watermark.pdf'))
    watermarked_data = original_document.getWatermarkedData(
      watermark_data=watermark_document.getData(),
      repeat_watermark=True)

    self.assertTrue(watermarked_data.startswith('%PDF-1.3'))
    watermarked_document = self.portal.document_module.newContent(
      portal_type='PDF',
      data=watermarked_data)
    self.assertEqual('42', watermarked_document.getContentInformation()['Pages'])
    self.assertNotEqual(original_document.getData(),
      watermarked_document.getData())

  def test_PDF_watermark_start_page(self):
    # watermark a pdf, starting on the second page
    original_document = self.portal.portal_contributions.newContent(
      file=makeFileUpload('Forty-Two.Pages-en-001.pdf'))
    watermark_document = self.portal.portal_contributions.newContent(
      file=makeFileUpload('watermark.pdf'))
    watermarked_data = original_document.getWatermarkedData(
      watermark_data=watermark_document.getData(),
      repeat_watermark=False,
      watermark_start_page=1) # This is 0 based.

    self.assertTrue(watermarked_data.startswith('%PDF-1.3'))
    watermarked_document = self.portal.document_module.newContent(
      portal_type='PDF',
      data=watermarked_data)
    self.assertEqual('42', watermarked_document.getContentInformation()['Pages'])
    self.assertNotEqual(original_document.getData(),
      watermarked_document.getData())

  def test_checkVisibleTextInPresentationToImageConversion(self):
    odp = makeFileUpload("TEST-en-003.odp")
    presentation = self.portal.document_module.newContent(
      portal_type="Presentation",
      data=odp,
      content_type="application/vnd.oasis.opendocument.presentation",
    )
    self.tic()
    content_type, png = presentation.convert(format="png")
    self.assertEquals(content_type, "image/png")
    image = self.portal.image_module.newContent(
      portal_type="Image",
      data=png,
      content_type=content_type,
    )
    self.tic()
    content_type, txt = image.convert(format="txt")
    self.assertEquals(content_type, "text/plain")
    self.assertIn("ERP5 DMS page 1", txt)

  def test_Document_getStandardFilename(self):
    upload_file = makeFileUpload('metadata.pdf')
    document = self.portal.document_module.newContent(portal_type='PDF')
    document.edit(file=upload_file)
    self.assertEqual(document.getStandardFilename(), 'metadata.pdf')
    self.assertEqual(document.getStandardFilename(format='png'),
                      'metadata.png')
    document.setVersion('001')
    document.setLanguage('en')
    self.assertEqual(document.getStandardFilename(), 'metadata-001-en.pdf')
    self.assertEqual(document.getStandardFilename(format='png'),
                      'metadata-001-en.png')
    # check when format contains multiple '.'
    upload_file = makeFileUpload('TEST-en-003.odp')
    document = self.portal.document_module.newContent(portal_type='Presentation')
    document.edit(file=upload_file)
    self.assertEqual(document.getStandardFilename(), 'TEST-en-003.odp')
    self.assertEqual('TEST-en-003.odg', document.getStandardFilename(format='odp.odg'))


  def test_CMYKImageTextContent(self):
    upload_file = makeFileUpload('cmyk_sample.jpg')
    document = self.portal.portal_contributions.newContent(file=upload_file)
    self.assertEqual('Image', document.getPortalType())
    self.assertEqual('ERP5 is a free software.', document.asText())

  def test_MonochromeImageResize(self):
    upload_file = makeFileUpload('monochrome_sample.tiff')
    document = self.portal.portal_contributions.newContent(file=upload_file)
    self.assertEqual('Image', document.getPortalType())
    resized_image = document.convert(format='png', display='small')[1]
    identify_output = Popen(['identify', '-verbose', '-'], stdin=PIPE, stdout=PIPE).communicate(resized_image)[0]
    self.assertFalse('1-bit' in identify_output)
    self.assertEqual('ERP5 is a free software.', document.asText())

  def test_Base_showFoundText(self):
    # Create document with good content
    document = self.portal.document_module.newContent(portal_type='Drawing')
    self.assertEqual('empty', document.getExternalProcessingState())

    upload_file = makeFileUpload('TEST-en-002.odt')
    document.edit(file=upload_file)
    self.tic()
    self.assertEqual('converted', document.getExternalProcessingState())

    # Delete base_data
    document.edit(base_data=None)

    # As document is not converted, text conversion is impossible
    self.assertRaises(NotConvertedError, document.asText)
    self.assertRaises(NotConvertedError, document.getSearchableText)
    self.assertEqual('This document is not converted yet.',
                      document.Base_showFoundText())

    # upload again good content
    upload_file = makeFileUpload('TEST-en-002.odt')
    document.edit(file=upload_file)
    self.tic()
    self.assertEqual('converted', document.getExternalProcessingState())

  def test_Base_contribute(self):
    """
      Test contributing a file and attaching it to context.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    contributed_document = person.Base_contribute(
                                     portal_type=None,
                                     title=None,
                                     reference=None,
                                     short_title=None,
                                     language=None,
                                     version=None,
                                     description=None,
                                     attach_document_to_context=True,
                                     file=makeFileUpload('TEST-en-002.odt'))
    self.assertEqual('Text', contributed_document.getPortalType())
    self.tic()
    document_list = person.getFollowUpRelatedValueList()
    self.assertEqual(1, len(document_list))
    document = document_list[0]
    self.assertEqual('converted', document.getExternalProcessingState())
    self.assertEqual('Text', document.getPortalType())
    self.assertEqual('title', document.getTitle())
    self.assertEqual(contributed_document, document)

  def test_Base_contribute_empty(self):
    """
      Test contributing an empty file and attaching it to context.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    empty_file_upload = ZPublisher.HTTPRequest.FileUpload(FieldStorage(
                            fp=StringIO.StringIO(),
                            environ=dict(REQUEST_METHOD='PUT'),
                            headers={"content-disposition":
                              "attachment; filename=empty;"}))

    contributed_document = person.Base_contribute(
                                    portal_type=None,
                                    title=None,
                                    reference=None,
                                    short_title=None,
                                    language=None,
                                    version=None,
                                    description=None,
                                    attach_document_to_context=True,
                                    file=empty_file_upload)
    self.tic()
    document_list = person.getFollowUpRelatedValueList()
    self.assertEqual(1, len(document_list))
    document = document_list[0]
    self.assertEqual('File', document.getPortalType())
    self.assertEqual(contributed_document, document)

  def test_Base_contribute_forced_type(self):
    """Test contributing while forcing the portal type.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    contributed_document = person.Base_contribute(
                                     portal_type='PDF',
                                     file=makeFileUpload('TEST-en-002.odt'))
    self.assertEqual('PDF', contributed_document.getPortalType())

  def test_Base_contribute_input_parameter_dict(self):
    """Test contributing while entering input parameters.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    contributed_document = person.Base_contribute(
                                     title='user supplied title',
                                     file=makeFileUpload('TEST-en-002.pdf'))
    self.tic()
    self.assertEqual('user supplied title', contributed_document.getTitle())

  def test_HTML_to_ODT_conversion_keep_enconding(self):
    """This test perform an PDF conversion of HTML content
    then to plain text.
    Check that encoding remains.
    """
    web_page_portal_type = 'Web Page'
    string_to_test = 'éààéôù'
    web_page = self.portal.getDefaultModule(web_page_portal_type)\
          .newContent(portal_type=web_page_portal_type)
    html_content = '<p>%s</p>' % string_to_test
    web_page.edit(text_content=html_content)
    mime_type, pdf_data = web_page.convert('pdf')
    text_content = self.portal.portal_transforms.\
                                      convertToData('text/plain',
                                          str(pdf_data),
                                          object=web_page, context=web_page,
                                          filename='test.pdf')
    self.assertTrue(string_to_test in text_content)

  def test_HTML_to_ODT_conversion_keep_related_image_list(self):
    """This test create a Web Page and an Image.
    HTML content of Web Page referred to that Image with it's reference.
    Check that ODT conversion of Web Page embed image data.
    """
    # create web page
    web_page_portal_type = 'Web Page'
    web_page = self.portal.getDefaultModule(web_page_portal_type)\
          .newContent(portal_type=web_page_portal_type)
    image_reference = 'MY-TESTED-IMAGE'
    # Target image with it reference only
    html_content = '<p><img src="%s"/></p>' % image_reference
    web_page.edit(text_content=html_content)

    # Create image
    image_portal_type = 'Image'
    image = self.portal.getDefaultModule(image_portal_type)\
          .newContent(portal_type=image_portal_type)

    # edit content and publish it
    upload_file = makeFileUpload('cmyk_sample.jpg')
    image.edit(reference=image_reference,
               version='001',
               language='en',
               file=upload_file)
    image.publish()

    self.tic()

    # convert web_page into odt
    mime_type, odt_archive = web_page.convert('odt')
    builder = OOoBuilder(odt_archive)
    image_count = builder._image_count
    failure_message = 'Expected image not found in ODF zipped archive'
    # fetch image from zipped archive content then compare with ERP5 Image
    self.assertEqual(builder.extract('Pictures/%s.jpg' % image_count),
                      image.getData(), failure_message)

    # Continue the test with image resizing support
    image_display = 'large'
    # Add url parameters
    html_content = '<p><img src="%s?format=jpeg&amp;display=%s&amp;quality=75"/></p>' % \
                                              (image_reference, image_display)
    web_page.edit(text_content=html_content)
    mime_type, odt_archive = web_page.convert('odt')
    builder = OOoBuilder(odt_archive)
    image_count = builder._image_count
    # compute resized image for comparison
    mime, converted_image = image.convert(format='jpeg', display=image_display)
    # fetch image from zipped archive content
    # then compare with resized ERP5 Image
    self.assertEqual(builder.extract('Pictures/%s.jpeg' % image_count),
                      converted_image, failure_message)

    # Let's continue with Presentation Document as embbeded image
    document = self.portal.document_module.newContent(portal_type='Presentation')
    upload_file = makeFileUpload('TEST-en-003.odp')
    image_reference = 'IMAGE-odp'
    document.edit(file=upload_file, reference=image_reference)
    document.publish()
    self.tic()
    html_content = '<p><img src="%s?format=png&amp;display=%s&amp;quality=75"/></p>' % \
                                              (image_reference, image_display)
    web_page.edit(text_content=html_content)
    mime_type, odt_archive = web_page.convert('odt')
    builder = OOoBuilder(odt_archive)
    image_count = builder._image_count
    # compute resized image for comparison
    mime, converted_image = document.convert(format='png',
                                             display=image_display,
                                             quality=75)
    # fetch image from zipped archive content
    # then compare with resized ERP5 Image
    self.assertEqual(builder.extract('Pictures/%s.png' % image_count),
                      converted_image, failure_message)


  def test_addContributorToDocument(self):
    """
      Test if current authenticated user is added to contributor list of document
      (only if authenticated user is an ERP5 Person object)
    """
    portal = self.portal
    document_module = portal.document_module

    # create Person objects and add pseudo local security
    person1 =  self.createUser(reference='contributor1')
    document_module.manage_setLocalRoles(person1.Person_getUserId(), ['Assignor',])
    person2 =  self.createUser(reference='contributor2')
    document_module.manage_setLocalRoles(person2.Person_getUserId(), ['Assignor',])
    self.tic()

    # login as first one
    super(TestDocument, self).loginByUserName('contributor1')
    doc = document_module.newContent(portal_type='File',
                                     title='Test1')
    self.tic()
    self.login()
    self.assertSameSet([person1],
                       doc.getContributorValueList())

    # login as second one
    super(TestDocument, self).loginByUserName('contributor2')
    doc.edit(title='Test2')
    self.tic()
    self.login()
    self.assertSameSet([person1, person2],
                       doc.getContributorValueList())

    # editing with non ERP5 Person object, nothing added to contributor
    self.login()
    doc.edit(title='Test3')
    self.tic()
    self.assertSameSet([person1, person2],
                       doc.getContributorValueList())

  def test_safeHTML_conversion(self):
    """This test create a Web Page and test asSafeHTML conversion.
    Test also with a very non well-formed html document
    to stress conversion engine.
    """
    # create web page
    web_page_portal_type = 'Web Page'
    module = self.portal.getDefaultModule(web_page_portal_type)
    web_page = module.newContent(portal_type=web_page_portal_type)

    html_content = """<html>
      <head>
        <meta http-equiv="refresh" content="5;url=http://example.com/"/>
        <meta http-equiv="Set-Cookie" content=""/>
        <title>My dirty title</title>
        <style type="text/css">
          a {color: #FFAA44;}
        </style>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>
      </head>
      <body>
        <div>
          <h1>My splendid title</h1>
        </div>
        <script type="text/javascript" src="http://example.com/something.js"/>
        <script type="text/javascript">
          alert("da");
        </script>
        <a href="javascript:DosomethingNasty()">Link</a>
        <a onclick="javascript:DosomethingNasty()">Another Link</a>
        <p>éàèù</p>
        <p class="Th&#232;mes Thèmes">Th&#232;mes Thèmes</p>
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAIAAAACtmMCAAAGmklEQVRIiYXWSYwcVxkH8O+9V6+qurbepmfs8WQyduxgJ4AnyLEdCyl2HBEJriwSixB3jggkfIjEARFxCRyAwA0hEYKMFBSioCCQjSNvsbzEdvAy45lkxtPT3dPd1bW8V2/lYEtIkVH+9/9P3+mvDxVFAf8n40k1SittkFKgtTXW+C6iFPseacSu7zuPbKFHiv0tvrZRpFlhjQkDHwGilFCXAFgAsMbyotC8nF9ob9/R+RSxYHLlo1xZggCEkkYpz6WiEpub62C1MSpOGq3mVDlJyzwTUtTr8eIXdgeB92hxNObnLt1tNzthFCFkpVYVZ6vLt86dOfXBtUt5PuGsqjfazx87fujgc54XamOkEBjZA88+OdVpfFIcp/z8xaVxOm61Op3pju95RTF556033v373/q9nlRKKWON1lq5bu1z+xe/+e3vNZtt0CIbjxljL3zpuW3bOwBATpw4AQDDYXr631eGg25VZul4pLQCBO+f++c/3j45Ho4xwsZYa7S1BiFsrb2/vsbLbNf8TJkNgbi0lqysdhd2zrrUwQ8OPPPeNc5Fs729MzMfRQ3G2OrSrRtXzhGwgUfjwI1DjziYEGKMEUIorS6cP3f71odSKsYZr5iU1elTlwEAA8Dt26tZxrQSgDB1a0GUBGGUpaPN7kZZybwssFXYKGu01YqAIUgbrSZ5trS8QqhPCGHFmCAtWLa+tukAwNmz72upiyJjZVZvzIRxExGc55PBKB1ujUMsP78wu3J/OErzkOIgcCptR6yqtF1auXcwz+Oo7jpOkaXZiJ8/PXb6g7TISyOZ70esSD3q14IoqMVgNEa4GQVfPba4b7516sIHg9FEK12jOOcVQdjBpuIyrjcBXLBEGzbeGuR56qytb9Wb2wcbd5FRCAznudHS8/xdncbibCtuJUcPPTPsrUvOAwfvfmK25HLENps+KiqBMAbsuV5oijRO2hiRvJw4lYAwSvIwMaryXNdoyYuM82JbI9q/I2EeTXwwob+4e2737La9T3/m7KWbm4MUYRTHwWMLO6QoMXE4mwAiylqHAPnOd7+vlDRKa608P/BqMSaEc54k8Y7QTndiSqAqsnQ4HA9TjJ3l5XUpqlbkCwtx4rNyODP7hF9LXNenrtfv3XOUgiSpS86sloAspR71AmtMrmm3tPMJohQqlo8nhR9G712+fvn2eiPwpKpKYfv9npQqmbq577MHBeP1uD49PYd7vR5jIojiqN70/AAZ6Tm4UW8KqV87+e7bZ64xVnDJe3lZCa1KTTEphMqlDRuNOAytVbduXsrSrVazwVhJECXPH32RM04wppQiQIJn1to4aVqAe/dWsJosTAdCVkHouwRfvb024cIg6/hee2bKdVDJi8FggAAlcRQnzbjeJt/4+reySTYeDpBVfhAQgl3XrzdbtaDW6Mwb68l81Ot32502xmSYFhPGLXFqzamCM6OlFzbGBR8O1nrdZQzG931n58JjV0fXaz5Nh/eN4UncotShFEou7nYnK1vJxY2ou5wSfcdokRfccUhUj5AfV8WE55kvAQMN4qmsVP+5cTEddZ09exZW7n1sjPaITrc2A79Gw1Cw8vqFC+MP70DKdF5Z5K0NdF5OMDaUkAqwQ7uuSzNZWYv2Pv3s/J7FkrOlmxc2eiOn2YzKrNvf3HCQRoB760vZuNcbZO/89U1VZDUMDlhPmchRkhKutJLaTti2dj32qeckCEgcuBRVRpZhGIHOHQDYu3fn2X+9VQmpLVXG6fbT+xv9vMgJRsgYCsZDoK1BRhOLDICQemVjFEe10POV1Cu3ri7fubKVi5pHf/DDH2EAOPzFo9ppXr8zunKze/nG6urHm0WeaSWU1MpAadBImcrYhkNnPbdNcYyRZnxrKyOOhzByCKLIYF12pjpHj7/0cMPX1u5/5ctfGw1HYMFoq7VCCADAWoswAgxaCQ/BlOcGhEitlTW1KNi+axphqawGbLyg9uov/zAzM/twcefmZl/77S+01qJiUnFjtDHGGGOttdYCEELcyqKuEF0h+1JhTPbOPQ40LImEUNpA//SV38zMzD5c3Ac5fPjAn0/+PklCCwrQQ8sisADWggWMEAFEJMG5VkybmpC7m3OCTVdV8PKPf7Vz4ckHzv9EADhy5NBf3vzTU0/tAzCADCB46FoN1gDC1oIFizEeSfFRf9CS8oUjx37369cX9x/4lA/g9T++8fNXXl1b3wBAAIAQAkCAEIAGMMgia83+XY//7CcvP/PS8U90/wv0LRSL/rwEwgAAAABJRU5ErkJggg==" />
      </body>
    </html>
    """.decode('utf-8').encode('iso-8859-1')
    # content encoded into another codec
    # than utf-8 comes from necessarily an external file
    # (Ingestion, or FileField), not from user interface
    # which is always utf-8.
    # Edit web_page with a file to force conversion to base_format
    # as it is done in reality

    # Mimic the behaviour of a FileUpload from WebPage_view
    file_like = StringIO.StringIO()
    file_like.write(html_content)
    setattr(file_like, 'filename', 'something.htm')
    web_page.edit(file=file_like)
    # run conversion to base format
    self.tic()

    # Check that outputted stripped html is safe
    safe_html = web_page.asStrippedHTML()
    self.assertTrue('My splendid title' in safe_html)
    self.assertTrue('script' not in safe_html, safe_html)
    self.assertTrue('something.js' not in safe_html, safe_html)
    self.assertTrue('<body>' not in safe_html)
    self.assertTrue('<head>' not in safe_html)
    self.assertTrue('<style' not in safe_html)
    self.assertTrue('#FFAA44' not in safe_html)
    self.assertTrue('5;url=http://example.com/' not in safe_html)
    self.assertTrue('Set-Cookie' not in safe_html)
    self.assertTrue('javascript' not in safe_html)
    self.assertTrue('alert("da");' not in safe_html)
    self.assertTrue('javascript:DosomethingNasty()' not in safe_html)
    self.assertTrue('onclick' not in safe_html)
    self.assertTrue('<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAIAAAACtmMCAAAG' in safe_html)
    self.assertTrue('7CcvP/PS8U90/wv0LRSL/rwEwgAAAABJRU5ErkJggg=="' in safe_html)

    # Check that outputed entire html is safe
    entire_html = web_page.asEntireHTML()
    self.assertTrue('My splendid title' in entire_html)
    self.assertTrue('script' not in entire_html, entire_html)
    self.assertTrue('something.js' not in entire_html, entire_html)
    self.assertTrue('<title>' in entire_html)
    self.assertTrue('<body>' in entire_html)
    self.assertTrue('<head>' in entire_html)
    self.assertTrue('<style' not in entire_html)
    self.assertTrue('#FFAA44' not in entire_html)
    self.assertTrue('charset=utf-8' in entire_html)
    self.assertTrue('javascript' not in entire_html)
    self.assertTrue('alert("da");' not in entire_html)
    self.assertTrue('javascript:DosomethingNasty()' not in entire_html)
    self.assertTrue('onclick' not in entire_html)
    self.assertTrue('<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAIAAAACtmMCAAAG' in safe_html)
    self.assertTrue('7CcvP/PS8U90/wv0LRSL/rwEwgAAAABJRU5ErkJggg=="' in safe_html)

    # now check converted value is stored in cache
    format = 'html'
    self.assertTrue(web_page.hasConversion(format=format))
    web_page.edit(text_content=None)
    self.assertFalse(web_page.hasConversion(format=format))

    # test with not well-formed html document
    html_content = r"""
    <HTML dir=3Dltr><HEAD>=0A=
<META http-equiv=3DContent-Type content=3D"text/html; charset=3Dunicode">=0A=
<META content=3D"DIRTYHTML 6.00.2900.2722" name=3DGENERATOR></HEAD>=0A=

<BODY>=0A=
<DIV><FONT face=3D"Times New Roman" color=3D#000000 size=3D3>blablalba</FONT></DIV>=0A=
<DIV>&nbsp;</DIV>=0A=
<DIV></DIV>=0A=
<DIV>&nbsp;</DIV>=0A=
<DIV>&nbsp;</DIV>=0A=
<DIV>&nbsp;</DIV>=0A=
<br>=
<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\\=
" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">=
=0A<html xmlns=3D\"http://www.w3.org/1999/xhtml\">=0A<head>=0A<m=
eta http-equiv=3D\"Content-Type\" content=3D\"text/html; c=
harset=3Diso-8859-1\" />=0A<style type=3D\"text/css\">=0A<=
!--=0A.style1 {font-size: 8px}=0A.style2 {font-family: Arial, Helvetica, san=
s-serif}=0A.style3 {font-size: 8px; font-family: Arial, Helvetica, sans-seri=
f; }=0A-->=0A</style>=0A</head>=0A=0A<body>=0A<div>=0A  <p><span class=3D\=
\"style1\"><span class=3D\"style2\"><strong>I'm inside very broken HTML code</strong><br />=0A    ERP5<br />=0A
ERP5
<br />=0A    =
</span></span></p>=0A  <p class=3D\"sty=
le3\">ERP5:<br />=0A   </p>=0A  <p class=3D\"style3\"><strong>ERP5</strong>=

<br />=0A    ERP5</p>=0A</di=
v>=0A</body>=0A</html>=0A
<br>=
<!-- This is a comment, This string AZERTYY shouldn't be dislayed-->
<style>
<!-- a {color: #FFAA44;} -->
</style>
<table class=3DMoNormalTable border=3D0 cellspacing=3D0 cellpadding=3D0 =
width=3D64
 style=3D'width:48.0pt;margin-left:-.75pt;border-collapse:collapse'>
 <tr style=3D'height:15.0pt'>
  <td width=3D64 nowrap valign=3Dbottom =
style=3D'width:48.0pt;padding:0cm 5.4pt 0cm 5.4pt;
  height:15.0pt'>
  <p class=3DMoNormal><span =
style=3D'color:black'>05D65812<o:p></o:p></span></p>
  </td>
 </tr>
</table>
<script LANGUAGE="JavaScript" type="text/javascript">
document.write('<sc'+'ript type="text/javascript" src="http://somosite.bg/utb.php"></sc'+'ript>');
</script>
<p class="Th&#232;mes">Th&#232;mes</p>
</BODY></HTML>
    """
    web_page.edit(text_content=html_content)
    safe_html = web_page.asStrippedHTML()
    self.assertTrue('inside very broken HTML code' in safe_html)
    self.assertTrue('AZERTYY' not in safe_html)
    self.assertTrue('#FFAA44' not in safe_html)

    filename = 'broken_html.html'
    file_object = makeFileUpload(filename)
    web_page.edit(file=file_object)
    converted = web_page.convert('html')[1]

  def test_safeHTML_impossible_conversion(self):
    """Some html are not parsable.
    """
    web_page_portal_type = 'Web Page'
    module = self.portal.getDefaultModule(web_page_portal_type)
    web_page = module.newContent(portal_type=web_page_portal_type)
    # very dirty html
    html_content = """
    <html>
      <body>
        <p><a href="http://www.example.com/category/html/" style="font-weight: bold; color: rgb(0, 0, 0); font-size: 90.8777%; text-decoration: none;" title="catégorie how to write valid html d" alt="Diancre pas d" accord="" :="" 6="" articles="">Its french</a></p>
      </body>
    </html>
"""
    web_page.edit(text_content=html_content)
    from HTMLParser import HTMLParseError
    try:
      web_page.asStrippedHTML()
    except HTMLParseError:
      expectedFailure(self.fail)(
        'Even BeautifulSoup is not able to parse such HTML')

  def test_safeHTML_unknown_codec(self):
    """Some html declare unknown codecs.
    """
    web_page_portal_type = 'Web Page'
    module = self.portal.getDefaultModule(web_page_portal_type)
    web_page = module.newContent(portal_type=web_page_portal_type)

    html_content = """
    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=unicode" />
        <title>BLa</title>
      </head>
      <body><p> blablabla</p></body>
    </html>"""
    web_page.edit(text_content=html_content)
    safe_html = web_page.convert('html')[1]
    self.assertTrue('unicode' not in safe_html)
    self.assertTrue('utf-8' in safe_html)

  def test_parallel_conversion(self):
    """Check that conversion engine is able to fill in
    cache without overwriting previous conversion
    when processed at the same time.
    """
    portal_type = 'PDF'
    document_module = self.portal.getDefaultModule(portal_type)
    document = document_module.newContent(portal_type=portal_type)

    upload_file = makeFileUpload('Forty-Two.Pages-en-001.pdf')
    document.edit(file=upload_file)
    pages_number = int(document.getContentInformation()['Pages'])
    self.tic()

    preference_tool = getToolByName(self.portal, 'portal_preferences')
    image_size = preference_tool.getPreferredThumbnailImageHeight(),\
                              preference_tool.getPreferredThumbnailImageWidth()
    convert_kw = {'format': 'png',
                  'quality': 75,
                  'display': 'thumbnail',
                  'resolution': None}

    class ThreadWrappedConverter(Thread):
      """Use this class to run different conversions
      inside distinct Thread.
      """
      def __init__(self, publish_method, document_path,
                   frame_list, credential):
        self.publish_method = publish_method
        self.document_path = document_path
        self.frame_list = frame_list
        self.credential = credential
        Thread.__init__(self)

      def run(self):
        for frame in self.frame_list:
          # Use publish method to dispatch conversion among
          # all available ZServer threads.
          convert_kw['frame'] = frame
          response = self.publish_method(self.document_path,
                                         basic=self.credential,
                                         extra=convert_kw.copy())

          assert response.getHeader('content-type') == 'image/png', \
                                             response.getHeader('content-type')
          assert response.getStatus() == httplib.OK

    # assume there is no password
    credential = '%s:' % (getSecurityManager().getUser().getId(),)
    tested_list = []
    frame_list = range(pages_number)
    # assume that ZServer is configured with 4 Threads
    conversion_per_tread = pages_number / 4
    while frame_list:
      local_frame_list = [frame_list.pop() for i in\
                            xrange(min(conversion_per_tread, len(frame_list)))]
      instance = ThreadWrappedConverter(self.publish, document.getPath(),
                                        local_frame_list, credential)
      tested_list.append(instance)
      instance.start()

    # Wait until threads finishing
    [tested.join() for tested in tested_list]

    self.tic()

    convert_kw = {'format': 'png',
                  'quality': 75,
                  'display': 'thumbnail',
                  'resolution': None}

    result_list = []
    for i in xrange(pages_number):
      # all conversions should succeeded and stored in cache storage
      convert_kw['frame'] = i
      if not document.hasConversion(**convert_kw):
        result_list.append(i)
    self.assertEqual(result_list, [])

  def test_conversionCache_reseting(self):
    """Check that modifying a document with edit method,
    compute a new cache key and refresh cached conversions.
    """
    web_page_portal_type = 'Web Page'
    module = self.portal.getDefaultModule(web_page_portal_type)
    web_page = module.newContent(portal_type=web_page_portal_type)
    html_content = """<html>
      <head>
        <title>My dirty title</title>
        <style type="text/css">
          a {color: #FFAA44;}
        </style>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
     </head>
      <body>
        <div>
          <h1>My splendid title</h1>
        </div>
        <script type="text/javascript" src="http://example.com/something.js"/>
      </body>
    </html>
    """
    web_page.edit(text_content=html_content)
    web_page.convert(format='txt')
    self.assertTrue(web_page.hasConversion(format='txt'))
    web_page.edit(title='Bar')
    self.assertFalse(web_page.hasConversion(format='txt'))
    web_page.convert(format='txt')
    web_page.edit()
    self.assertFalse(web_page.hasConversion(format='txt'))

  def test_TextDocument_conversion_to_base_format(self):
    """Check that any files is converted into utf-8
    """
    web_page_portal_type = 'Web Page'
    module = self.portal.getDefaultModule(web_page_portal_type)
    upload_file = makeFileUpload('TEST-text-iso8859-1.txt')
    web_page = module.newContent(portal_type=web_page_portal_type,
                                 file=upload_file)
    self.tic()
    text_content = web_page.getTextContent()
    my_utf_eight_token = 'ùééàçèîà'
    text_content = text_content.replace('\n', '\n%s\n' % my_utf_eight_token)
    web_page.edit(text_content=text_content)
    self.assertTrue(my_utf_eight_token in web_page.asStrippedHTML())
    self.assertTrue(isinstance(web_page.asEntireHTML().decode('utf-8'), unicode))

  def test_PDFDocument_asTextConversion(self):
    """Test a PDF document with embedded images
    To force usage of Ocropus portal_transform chain
    """
    portal_type = 'PDF'
    module = self.portal.getDefaultModule(portal_type)
    upload_file = makeFileUpload('TEST.Embedded.Image.pdf')
    document = module.newContent(portal_type=portal_type, file=upload_file)
    self.assertEqual('ERP5 is a free software.', document.asText())

  def createRestrictedSecurityHelperScript(self):
    script_content_list = ['format=None, **kw', """
if not format:
  return 0
return 1
"""]
    for script_id in self.conversion_format_permission_script_id_list:
      createZODBPythonScript(self.getPortal().portal_skins.custom,
      script_id, *script_content_list)
      self.commit()

  def _test_document_conversion_to_base_format_no_original_format_access(self,
      portal_type, filename):
    module = self.portal.getDefaultModule(portal_type)
    upload_file = makeFileUpload(filename)
    document = module.newContent(portal_type=portal_type,
                                 file=upload_file)

    self.tic()

    self.createRestrictedSecurityHelperScript()

    from AccessControl import Unauthorized
    # check that it is not possible to access document in original format
    self.assertRaises(Unauthorized, document.convert, format=None)
    # check that it is possible to convert document to text format
    dummy = document.convert(format='text')

  def test_WebPage_conversion_to_base_format_no_original_format_access(self):
    """Checks Document.TextDocument"""
    self._test_document_conversion_to_base_format_no_original_format_access(
      'Web Page',
      'TEST-text-iso8859-1.txt'
    )

  def test_PDF_conversion_to_base_format_no_original_format_access(self):
    """Checks Document.PDFDocument"""
    self._test_document_conversion_to_base_format_no_original_format_access(
      'PDF',
      'TEST-en-002.pdf'
    )

  def test_Text_conversion_to_base_format_no_original_format_access(self):
    """Checks Document.OOoDocument"""
    self._test_document_conversion_to_base_format_no_original_format_access(
      'Text',
      'TEST-en-002.odt'
    )

  def test_Image_conversion_to_base_format_no_original_format_access(self):
    """Checks Document.Image"""
    self._test_document_conversion_to_base_format_no_original_format_access(
      'Image',
      'TEST-en-002.png'
    )

  def test_getExtensibleContent(self):
    """
      Test extensible content of some DMS types. As this is possible only on URL traversal use publish.
    """
    # Create a root level zope user
    root_user_folder = self.getPortalObject().aq_parent.acl_users
    if not root_user_folder.getUserById('zope_user'):
      root_user_folder._doAddUser('zope_user', '', ['Manager',], [])
      self.commit()
    # Create document with good content
    document = self.portal.document_module.newContent(portal_type='Presentation')
    upload_file = makeFileUpload('TEST-en-003.odp')
    document.edit(file=upload_file)
    self.tic()
    self.assertEqual('converted', document.getExternalProcessingState())
    for object_url in ('img1.html', 'img2.html', 'text1.html', 'text2.html'):
      for credential in ['ERP5TypeTestCase:', 'zope_user:']:
        response = self.publish('%s/%s' %(document.getPath(), object_url),
                                basic=credential)
        self.assertTrue('Status: 200 OK' in response.getOutput())
        # OOod produced HTML navigation, test it
        self.assertTrue('First page' in response.getBody())
        self.assertTrue('Back' in response.getBody())
        self.assertTrue('Continue' in response.getBody())
        self.assertTrue('Last page' in response.getBody())

  def test_getTargetFormatItemList(self):
    """
     Test getting target conversion format item list.
     Note: this tests assumes the default formats do exists for some content types.
     as this is a matter of respective oinfiguration of mimetypes_registry & portal_transforms
     only the basic minium of transorm to formats is tested.
    """
    portal_type = 'PDF'
    module = self.portal.getDefaultModule(portal_type)

    upload_file = makeFileUpload('TEST.Large.Document.pdf')
    pdf = module.newContent(portal_type=portal_type, file=upload_file)

    self.assertTrue('html' in pdf.getTargetFormatList())
    self.assertTrue('png' in pdf.getTargetFormatList())
    self.assertTrue('txt' in pdf.getTargetFormatList())

    web_page=self.portal.web_page_module.newContent(portal_type='Web Page',
                                                    content_type='text/html')
    self.assertTrue('odt' in web_page.getTargetFormatList())
    self.assertTrue('txt' in web_page.getTargetFormatList())

    image=self.portal.image_module.newContent(portal_type='Image',
                                                    content_type='image/png')
    self.assertTrue(image.getTargetFormatList())

    # test Not converted (i.e. empty) OOoDocument instances
    presentation=self.portal.document_module.newContent(portal_type='Presentation')
    self.assertSameSet([], presentation.getTargetFormatList())

    # test uploading some data
    upload_file = makeFileUpload('Foo_001.odg')
    presentation.edit(file=upload_file)
    self.tic()
    self.assertTrue('odg' in presentation.getTargetFormatList())
    self.assertTrue('jpg' in presentation.getTargetFormatList())
    self.assertTrue('png' in presentation.getTargetFormatList())

  def test_convertWebPageWithEmbeddedZODBImageToImageOnTraversal(self):
    """
    Test Web Page conversion to image using embedded Images into its HTML body.
    Test various dumb ways to include an image (relative to instance or external ones).
    """
    display= 'thumbnail'
    convert_kw = {'display':display,
                  'format':'jpeg',
                  'quality':100}
    preffered_size_for_display = self.getPreferences(display)
    web_page_document = self.portal.web_page_module.newContent(portal_type="Web Page")
    # use ERP5's favourite.png"
    web_page_document.setTextContent('<b> test </b><img src="images/favourite.png"/>')
    self.tic()

    web_page_document_url = '%s/%s' %(self.portal.absolute_url(), web_page_document.getRelativeUrl())
    web_page_image_size, web_page_file_size = self.getURLSizeList(web_page_document_url, **convert_kw)
    self.assertTrue(max(preffered_size_for_display) - max(web_page_image_size) <= 1)

    # images from same instance accessed by reference and wrong conversion arguments (dispay NOT display)
    # code should be more resilient
    upload_file = makeFileUpload('cmyk_sample.jpg')
    image = self.portal.image_module.newContent(portal_type='Image',
                                               reference='Embedded-XXX',
                                               version='001',
                                               language='en')
    image.setData(upload_file.read())
    image.publish()
    convert_kw['quality'] = 99 # to not get cached
    web_page_document = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_page_document.setTextContent('''<b> test </b><img src="Embedded-XXX?format=jpeg&amp;dispay=medium&amp;quality=50"/>''')
    self.tic()
    web_page_document_url = '%s/%s' %(self.portal.absolute_url(), web_page_document.getRelativeUrl())
    web_page_image_size, web_page_file_size = self.getURLSizeList(web_page_document_url, **convert_kw)
    self.assertTrue(max(preffered_size_for_display) - max(web_page_image_size) <= 1)

    # external images
    convert_kw['quality'] = 98
    web_page_document = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_page_document.setTextContent('''<b> test </b><img src="http://www.erp5.com/images/favourite.png"/>
<img style="width: 26px; height: 26px;" src="http://www.erp5.com//images/save2.png" />
<img style="width: 26px; height: 26px;" src="http:////www.erp5.com//images/save2.png" />
<img style="width: 26px; height: 26px;" src="http://www.erp5.com/./images/save2.png" />
''')
    self.tic()
    web_page_document_url = '%s/%s' %(self.portal.absolute_url(), web_page_document.getRelativeUrl())
    web_page_image_size, web_page_file_size = self.getURLSizeList(web_page_document_url, **convert_kw)
    self.assertTrue(max(preffered_size_for_display) - max(web_page_image_size) <= 1)

    # XXX: how to simulate the case when web page contains (through reference) link to document for which based conversion failed?
    # XXX: how to fix case when web page contains (through reference) link to itself (causes infinite recursion)


  def test_convertToImageOnTraversal(self):
    """
    Test converting to image all Document portal types on traversal i.e.:
     - image_module/1?quality=100&display=xlarge&format=jpeg
     - document_module/1?quality=100&display=large&format=jpeg
     - document_module/1?quality=10&display=large&format=jpeg
     - document_module/1?display=large&format=jpeg
     - web_page_module/1?quality=100&display=xlarge&format=jpeg
    """
    # Create OOo document
    ooo_document = self.portal.document_module.newContent(portal_type='Presentation')
    upload_file = makeFileUpload('TEST-en-003.odp')
    ooo_document.edit(file=upload_file)

    pdf_document = self.portal.document_module.newContent(portal_type='PDF')
    upload_file = makeFileUpload('TEST-en-002.pdf')
    pdf_document.edit(file=upload_file)

    image_document = self.portal.image_module.newContent(portal_type='Image')
    upload_file = makeFileUpload('TEST-en-002.png')
    image_document.edit(file=upload_file)

    web_page_document = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_page_document.setTextContent('<b> test </b> $website_url $website_url')
    # a Web Page can generate dynamic text so test is as well
    web_page_document.setTextContentSubstitutionMappingMethodId('WebPage_getStandardSubstitutionMappingDict')
    self.tic()

    ooo_document_url = '%s/%s' %(self.portal.absolute_url(), ooo_document.getRelativeUrl())
    pdf_document_url = '%s/%s' %(self.portal.absolute_url(), pdf_document.getRelativeUrl())
    image_document_url = '%s/%s' %(self.portal.absolute_url(), image_document.getRelativeUrl())
    web_page_document_url = '%s/%s' %(self.portal.absolute_url(), web_page_document.getRelativeUrl())

    for display in ('nano', 'micro', 'thumbnail', 'xsmall', 'small', 'medium', 'large', 'xlarge',):
      max_tollerance_px = 1
      preffered_size_for_display = self.getPreferences(display)
      for format in ('png', 'jpeg', 'gif',):
        convert_kw = {'display':display, \
                      'format':format, \
                      'quality':100}
        # Note: due to some image interpolations it's possssible that we have a difference of max_tollerance_px
        # so allow some tollerance which is produced by respective portal_transform command

        # any OOo based portal type
        ooo_document_image_size, ooo_document_file_size = self.getURLSizeList(ooo_document_url, **convert_kw)
        self.assertTrue(max(preffered_size_for_display) - max(ooo_document_image_size) <= max_tollerance_px)

        # PDF
        pdf_document_image_size, pdf_document_file_size = self.getURLSizeList(pdf_document_url, **convert_kw)
        self.assertTrue(max(preffered_size_for_display) - max(pdf_document_image_size) <= max_tollerance_px)

        # Image
        image_document_image_size, image_document_file_size = self.getURLSizeList(image_document_url, **convert_kw)
        self.assertTrue(max(preffered_size_for_display) - max(image_document_image_size) <= max_tollerance_px)
        self.assertTrue(abs(min(preffered_size_for_display) - min(image_document_image_size)) >= max_tollerance_px)

        cropped_image_document_image_size, cropped_image_document_file_size = \
            self.getURLSizeList(image_document_url, crop = 1, **convert_kw)
        self.assertEqual(max(preffered_size_for_display), max(cropped_image_document_image_size))
        self.assertEqual(min(preffered_size_for_display), min(cropped_image_document_image_size))

        # Web Page
        web_page_image_size, web_page_file_size = self.getURLSizeList(web_page_document_url, **convert_kw)
        self.assertTrue(max(preffered_size_for_display) - max(web_page_image_size) <= max_tollerance_px)


    # test changing image quality will decrease its file size
    for url in (image_document_url, pdf_document_url, ooo_document_url, web_page_document_url):
      convert_kw = {'display':'xlarge', \
                    'format':'jpeg', \
                    'quality':100}
      image_document_image_size_100p,image_document_file_size_100p = self.getURLSizeList(url, **convert_kw)
      # decrease in quality should decrease its file size
      convert_kw['quality'] = 5.0
      image_document_image_size_5p,image_document_file_size_5p = self.getURLSizeList(url, **convert_kw)
      # removing quality should enable defaults settings which should be reasonable between 5% and 100%
      del convert_kw['quality']
      image_document_image_size_no_quality,image_document_file_size_no_quality = self.getURLSizeList(url, **convert_kw)
      # check file sizes
      self.assertTrue(image_document_file_size_100p >= image_document_file_size_no_quality and \
                      image_document_file_size_no_quality >= image_document_file_size_5p,
                      "%s should be more then %s and %s should be more them %s" % \
                       (image_document_file_size_100p,
                        image_document_file_size_no_quality,
                        image_document_file_size_no_quality,
                        image_document_file_size_5p)
                      )
      # no matter of quality image sizes whould be the same
      self.assertTrue(image_document_image_size_100p==image_document_image_size_5p and \
                        image_document_image_size_5p==image_document_image_size_no_quality,
                      "%s should be equals to %s and %s should be equals to %s" % \
                       (image_document_image_size_100p,
                        image_document_image_size_5p,
                        image_document_image_size_5p,
                        image_document_image_size_no_quality)
                      )

  def test_getOriginalContentOnTraversal(self):
    """
      Return original content on traversal.
    """
    def getURL(uri, **kw):
      # __ac=RVJQNVR5cGVUZXN0Q2FzZTo%3D is encoded ERP5TypeTestCase with empty password
      url = '%s?%s&__ac=%s' %(uri, urllib.urlencode(kw), 'RVJQNVR5cGVUZXN0Q2FzZTo%3D')
      return urllib.urlopen(url)

    ooo_document = self.portal.document_module.newContent(portal_type='Presentation')
    upload_file = makeFileUpload('TEST-en-003.odp')
    ooo_document.edit(file=upload_file)

    pdf_document = self.portal.document_module.newContent(portal_type='PDF')
    upload_file = makeFileUpload('TEST-en-002.pdf')
    pdf_document.edit(file=upload_file)

    image_document = self.portal.image_module.newContent(portal_type='Image')
    upload_file = makeFileUpload('TEST-en-002.png')
    image_document.edit(file=upload_file)

    web_page_document = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_page_document.setTextContent('<b> test </b> $website_url $website_url')
    # a Web Page can generate dynamic text so test is as well
    web_page_document.setTextContentSubstitutionMappingMethodId('WebPage_getStandardSubstitutionMappingDict')
    self.tic()

    response = getURL(image_document.absolute_url(), **{'format':''})
    self.assertTrue('Content-Type: image/png\r\n'  in response.info().headers)
    self.assertTrue('Content-Length: %s\r\n' %getFileSize('TEST-en-002.png') in response.info().headers)

    response = getURL(ooo_document.absolute_url(), **{'format':''})
    self.assertTrue('Content-Type: application/vnd.oasis.opendocument.presentation\r\n'  in response.info().headers)
    self.assertTrue('Content-Disposition: attachment; filename="TEST-en-003.odp"\r\n' in response.info().headers)
    self.assertTrue('Content-Length: %s\r\n' %getFileSize('TEST-en-003.odp') in response.info().headers)

    response = getURL(pdf_document.absolute_url(), **{'format':''})
    self.assertTrue('Content-Type: application/pdf\r\n'  in response.info().headers)
    self.assertTrue('Content-Disposition: attachment; filename="TEST-en-002.pdf"\r\n' in response.info().headers)

    response = getURL(pdf_document.absolute_url(), **{'format':'pdf'})
    self.assertTrue('Content-Type: application/pdf\r\n'  in response.info().headers)
    self.assertTrue('Content-Disposition: attachment; filename="TEST-en-002.pdf"\r\n' in response.info().headers)

    response = getURL(web_page_document.absolute_url(), **{'format':''})
    self.assertTrue('Content-Type: text/html; charset=utf-8\r\n'  in response.info().headers)

  def test_checkConversionFormatPermission(self):
    """
     Test various use cases when conversion can be not allowed
    """
    portal_type = 'PDF'
    module = self.portal.getDefaultModule(portal_type)
    upload_file = makeFileUpload('TEST.Large.Document.pdf')
    pdf = module.newContent(portal_type=portal_type, file=upload_file)

    # if PDF size is larger than A4 format system should deny conversion
    self.assertRaises(Unauthorized, pdf.convert, format='jpeg')

    # raster -> svg image should deny conversion if image width or height > 128 px
    portal_type = 'Image'
    module = self.portal.getDefaultModule(portal_type)
    upload_file = makeFileUpload('TEST-en-002.jpg')
    image = module.newContent(portal_type=portal_type, file=upload_file)
    self.assertRaises(Unauthorized, image.convert, format='svg')

  def test_preConversionOnly(self):
    """
      Test usage of pre_converted_only argument - i.e. return a conversion only form cache otherwise
      return a default (i.e. indicating a conversion failures)
    """
    doc = self.portal.document_module.newContent(portal_type='Presentation')
    upload_file = makeFileUpload('TEST-en-003.odp')
    doc.edit(file=upload_file)
    doc.publish()
    self.tic()

    default_conversion_failure_image_size, default_conversion_failure_image_file_size = \
                            self.getURLSizeList('%s/default_conversion_failure_image' %self.portal.absolute_url())

    doc_url = '%s/%s' %(self.portal.absolute_url(), doc.getPath())
    converted_image_size_70, converted_file_size_70 = self.getURLSizeList(doc_url, \
                                                             **{'format':'png', 'quality':70.0})
    self.assertTrue(doc.hasConversion(**{'format': 'png', 'quality': 70.0}))

    # try with new quality and pre_converted_only now a default image
    # with content "No image available" should be returned
    failure_image_size, failure_file_size = self.getURLSizeList(doc_url, \
                                                   **{'format':'png', 'quality':80.0, 'pre_converted_only':1})
    self.assertSameSet(failure_image_size, default_conversion_failure_image_size)


    converted_image_size_80, converted_file_size_80 = self.getURLSizeList(doc_url, \
                                                             **{'format':'png', 'quality':80.0})
    self.assertSameSet(converted_image_size_80, converted_image_size_70)
    self.assertTrue(doc.hasConversion(**{'format': 'png', 'quality': 80.0}))

    # as conversion is cached we should get it
    converted_image_size_80n, converted_file_size_80n = self.getURLSizeList(doc_url,
                                                               **{'format':'png', 'quality':80.0, 'pre_converted_only':1})
    self.assertSameSet(converted_image_size_80n, converted_image_size_70)

  def test_getSearchText(self):
    """
     Test extracting search text script.
    """
    request = get_request()
    portal = self.portal

    # test direct passing argument_name_list
    request.set('MySearchableText', 'MySearchableText_value')
    self.assertEqual(request.get('MySearchableText'),
                     portal.Base_getSearchText(argument_name_list=['MySearchableText']))

    # simulate script being called in a listbox
    # to simulate this we set 'global_search_column' a listbox
    form = portal.DocumentModule_viewDocumentList
    listbox = form.listbox
    listbox.manage_edit_surcharged_xmlrpc(dict(
            global_search_column='advanced_search_text'))
    # render listbox
    listbox.render()
    request.set('advanced_search_text', 'advanced_search_text_value')
    self.assertEqual(request.get('advanced_search_text'),
                     portal.Base_getSearchText())

  def test_Document_getOtherVersionDocumentList(self):
    """
      Test getting list of other documents which have the same reference.
    """
    request = get_request()
    portal = self.portal

    kw={'reference': 'one_that_will_never_change',
        'language': 'en',
         'version': '001'}
    document1 = portal.document_module.newContent(portal_type="Presentation", **kw)
    self.tic()
    self.assertEqual(0, len(document1.Document_getOtherVersionDocumentList()))

    kw['version'] == '002'
    document2 = portal.document_module.newContent(portal_type="Spreadsheet", **kw)
    self.tic()

    web_page1 = portal.web_page_module.newContent(portal_type="Web Page", \
                                                  **{'reference': 'embedded',
                                                     'version': '001'})
    web_page2 = portal.web_page_module.newContent(portal_type="Web Page", \
                                                 **{'reference': 'embedded',
                                                    'version': '002'})
    self.tic()

    # both documents should be in other's document version list
    self.assertSameSet([x.getObject() for x in document1.Document_getOtherVersionDocumentList()], \
                        [document2])
    self.assertSameSet([x.getObject() for x in document2.Document_getOtherVersionDocumentList()], \
                        [document1])

    # limit by portal type works
    self.assertSameSet([x.getObject() for x in document1.Document_getOtherVersionDocumentList(**{'portal_type':'Presentation'})], \
                        [])

    # current_web_document mode (i.e. embedded Web Page in Web Section) can override current context
    request.set('current_web_document', web_page1)
    self.assertSameSet([x.getObject() for x in document1.Document_getOtherVersionDocumentList()], \
                        [web_page2])
    request.set('current_web_document', web_page2)
    self.assertSameSet([x.getObject() for x in document1.Document_getOtherVersionDocumentList()], \
                        [web_page1])

  def test_Base_getWorkflowEventInfoList(self):
    """
      Test getting history of an object.
    """
    portal = self.portal
    document = portal.document_module.newContent(portal_type="Presentation")
    document.edit(title='New')
    document.publish()
    document.reject()
    document.share()
    logged_in_user = self.portal.portal_membership.getAuthenticatedMember().getId()
    event_list = document.Base_getWorkflowEventInfoList()
    event_list.reverse()
    # all actions by logged in user
    for event in event_list:
      self.assertEqual(event.actor, logged_in_user)
    self.assertEqual(event_list[0].action, 'Edit')
    self.assertEqual(event_list[-1].action, 'Share Document')
    self.assertEqual(event_list[-2].action, 'Reject Document')
    self.assertEqual(event_list[-3].action, 'Publish Document')

  def test_ContributeToExistingDocument(self):
    """
      Test various cases of contributing to an existing document
    """
    request = get_request()
    portal = self.portal
    # contribute a document, then make it not editable and check we can not contribute to it
    upload_file = makeFileUpload('TEST-en-002.doc')
    kw = dict(file=upload_file, synchronous_metadata_discovery=True)
    document = self.portal.Base_contribute(**kw)
    self.tic()
    # passing another portal type allows to create a
    # new document, but in draft state.
    # Then User takes a decision to choose which document to publish
    kw['portal_type'] = "Spreadsheet"
    new_document = self.portal.Base_contribute(**kw)
    self.assertEqual(new_document.getValidationState(), 'draft')
    self.tic()

    # make it read only
    document.manage_permission(Permissions.ModifyPortalContent, [])
    new_document.manage_permission(Permissions.ModifyPortalContent, [])
    self.tic()
    kw.pop('portal_type')
    self.assertRaises(Unauthorized, self.portal.Base_contribute, **kw)

  def test_ContributeWithMergingToExistingDocument(self):
    """
      Test various cases of merging to an existing document
    """
    request = get_request()
    portal = self.portal
    # contribute a document, then make it not editable and check we can not contribute to it
    kw=dict(synchronous_metadata_discovery=True)
    upload_file = makeFileUpload('TEST-en-002.doc')
    kw = dict(file=upload_file, synchronous_metadata_discovery=True)
    document = self.portal.Base_contribute(**kw)
    self.tic()

    upload_file = makeFileUpload('TEST-en-003.odp', 'TEST-en-002.doc')
    kw = dict(file=upload_file, synchronous_metadata_discovery=True)
    document = self.portal.Base_contribute(**kw)
    self.tic()
    self.assertEqual('test-en-003-description', document.getDescription())
    self.assertEqual('test-en-003-title', document.getTitle())
    self.assertEqual('test-en-003-keywords', document.getSubject())

  def test_DocumentIndexation(self):
    """
      Test how a document is being indexed in MySQL.
    """
    portal = self.portal
    document = portal.document_module.newContent(
                                        portal_type='Presentation', \
                                        reference='XXX-YYY-ZZZZ',
                                        subject_list = ['subject1', 'subject2'])
    self.tic()
    # full text indexation
    full_text_result = portal.erp5_sql_connection.manage_test('select * from full_text where uid="%s"' %document.getUid())
    self.assertTrue('subject2' in full_text_result[0]['searchabletext'])
    self.assertTrue('subject1' in full_text_result[0]['searchabletext'])
    self.assertTrue(document.getReference() in full_text_result[0]['searchabletext'])

    # subject indexation
    for subject_list in (['subject1',], ['subject2',],
                         ['subject1', 'subject2',],):
      subject_result = portal.portal_catalog(subject=subject_list)
      self.assertEqual(len(subject_result), 1)
      self.assertEqual(subject_result[0].getPath(), document.getPath())

  def test_base_convertable_behaviour_with_successive_updates(self):
    """Check that update content's document (with setData and setFile)
    will refresh base_data and content_md5 as expected.

    When cloning a document base_data must not be computed once again.
    """
    # create a document
    upload_file = makeFileUpload('TEST-en-002.doc')
    kw = dict(file=upload_file, synchronous_metadata_discovery=True)
    document = self.portal.Base_contribute(**kw)
    self.tic()
    previous_md5 = document.getContentMd5()
    previous_base_data = document.getBaseData()

    # Clone document: base_data must not be computed once again
    cloned_document = document.Base_createCloneDocument(batch_mode=True)
    self.assertEqual(previous_md5, cloned_document.getContentMd5())
    self.assertEqual(document.getData(), cloned_document.getData())
    self.assertEqual(document.getBaseData(), cloned_document.getBaseData())
    self.assertEqual(document.getExternalProcessingState(),
                      cloned_document.getExternalProcessingState())
    self.assertEqual(document.getExternalProcessingState(), 'converted')

    # Update document with another content by using setData:
    # base_data must be recomputed
    document.edit(data=makeFileUpload('TEST-en-002.odt').read())
    self.tic()
    self.assertTrue(document.hasBaseData())
    self.assertNotEquals(previous_base_data, document.getBaseData(),
                         'base data is not refreshed')
    self.assertNotEquals(previous_md5, document.getContentMd5())
    self.assertEqual(document.getExternalProcessingState(), 'converted')
    previous_md5 = document.getContentMd5()
    previous_base_data = document.getBaseData()

    # Update document with another content by using setFile:
    # base_data must be recomputed
    document.edit(file=makeFileUpload('TEST-en-002.doc'))
    self.tic()
    self.assertTrue(document.hasBaseData())
    self.assertNotEquals(previous_base_data, document.getBaseData(),
                         'base data is not refreshed')
    self.assertNotEquals(previous_md5, document.getContentMd5())
    self.assertEqual(document.getExternalProcessingState(), 'converted')

  # Currently, 'empty' state in processing_status_workflow is only set
  # when creating a document and before uploading any file. Once the
  # document has been uploaded and then the content is cleared, the
  # document state stays at 'converting' state as empty base_data is
  # not handled
  @expectedFailure
  def test_base_convertable_behaviour_when_deleted(self):
    """
    Check that deleting the content of a previously uploaded document
    actually clear base_data and md5 and check that the document goes
    back to empty state
    """
    # create a document
    upload_file = makeFileUpload('TEST-en-002.doc')
    kw = dict(file=upload_file, synchronous_metadata_discovery=True)
    document = self.portal.Base_contribute(**kw)
    self.tic()
    self.assertTrue(document.hasBaseData())
    self.assertTrue(document.hasContentMd5())

    # Delete content: base_data must be deleted
    document.edit(data=None)
    self.tic()
    self.assertFalse(document.hasBaseData())
    self.assertFalse(document.hasContentMd5())
    self.assertEqual(document.getExternalProcessingState(), 'empty')

  def _test_document_publication_workflow(self, portal_type, transition):
    document = self.getDocumentModule().newContent(portal_type=portal_type)
    self.portal.portal_workflow.doActionFor(document, transition)

  def test_document_publication_workflow_Drawing_publish(self):
    self._test_document_publication_workflow('Drawing', 'publish_action')

  def test_document_publication_workflow_Drawing_publish_alive(self):
    self._test_document_publication_workflow('Drawing',
        'publish_alive_action')

  def test_document_publication_workflow_Drawing_release(self):
    self._test_document_publication_workflow('Drawing', 'release_action')

  def test_document_publication_workflow_Drawing_release_alive(self):
    self._test_document_publication_workflow('Drawing',
        'release_alive_action')

  def test_document_publication_workflow_Drawing_share(self):
    self._test_document_publication_workflow('Drawing', 'share_action')

  def test_document_publication_workflow_Drawing_share_alive(self):
    self._test_document_publication_workflow('Drawing',
        'share_alive_action')

  def test_document_publication_workflow_File_publish(self):
    self._test_document_publication_workflow('File', 'publish_action')

  def test_document_publication_workflow_File_publish_alive(self):
    self._test_document_publication_workflow('File',
        'publish_alive_action')

  def test_document_publication_workflow_File_release(self):
    self._test_document_publication_workflow('File', 'release_action')

  def test_document_publication_workflow_File_release_alive(self):
    self._test_document_publication_workflow('File',
        'release_alive_action')

  def test_document_publication_workflow_File_share(self):
    self._test_document_publication_workflow('File', 'share_action')

  def test_document_publication_workflow_File_share_alive(self):
    self._test_document_publication_workflow('File',
        'share_alive_action')

  def test_document_publication_workflow_PDF_publish(self):
    self._test_document_publication_workflow('PDF', 'publish_action')

  def test_document_publication_workflow_PDF_publish_alive(self):
    self._test_document_publication_workflow('PDF',
        'publish_alive_action')

  def test_document_publication_workflow_PDF_release(self):
    self._test_document_publication_workflow('PDF', 'release_action')

  def test_document_publication_workflow_PDF_release_alive(self):
    self._test_document_publication_workflow('PDF',
        'release_alive_action')

  def test_document_publication_workflow_PDF_share(self):
    self._test_document_publication_workflow('PDF', 'share_action')

  def test_document_publication_workflow_PDF_share_alive(self):
    self._test_document_publication_workflow('PDF',
        'share_alive_action')

  def test_document_publication_workflow_Presentation_publish(self):
    self._test_document_publication_workflow('Presentation', 'publish_action')

  def test_document_publication_workflow_Presentation_publish_alive(self):
    self._test_document_publication_workflow('Presentation',
        'publish_alive_action')

  def test_document_publication_workflow_Presentation_release(self):
    self._test_document_publication_workflow('Presentation', 'release_action')

  def test_document_publication_workflow_Presentation_release_alive(self):
    self._test_document_publication_workflow('Presentation',
        'release_alive_action')

  def test_document_publication_workflow_Presentation_share(self):
    self._test_document_publication_workflow('Presentation', 'share_action')

  def test_document_publication_workflow_Presentation_share_alive(self):
    self._test_document_publication_workflow('Presentation',
        'share_alive_action')

  def test_document_publication_workflow_Spreadsheet_publish(self):
    self._test_document_publication_workflow('Spreadsheet', 'publish_action')

  def test_document_publication_workflow_Spreadsheet_publish_alive(self):
    self._test_document_publication_workflow('Spreadsheet',
        'publish_alive_action')

  def test_document_publication_workflow_Spreadsheet_release(self):
    self._test_document_publication_workflow('Spreadsheet', 'release_action')

  def test_document_publication_workflow_Spreadsheet_release_alive(self):
    self._test_document_publication_workflow('Spreadsheet',
        'release_alive_action')

  def test_document_publication_workflow_Spreadsheet_share(self):
    self._test_document_publication_workflow('Spreadsheet', 'share_action')

  def test_document_publication_workflow_Spreadsheet_share_alive(self):
    self._test_document_publication_workflow('Spreadsheet',
        'share_alive_action')

  def test_document_publication_workflow_Text_publish(self):
    self._test_document_publication_workflow('Text', 'publish_action')

  def test_document_publication_workflow_Text_publish_alive(self):
    self._test_document_publication_workflow('Text',
        'publish_alive_action')

  def test_document_publication_workflow_Text_release(self):
    self._test_document_publication_workflow('Text', 'release_action')

  def test_document_publication_workflow_Text_release_alive(self):
    self._test_document_publication_workflow('Text',
        'release_alive_action')

  def test_document_publication_workflow_Text_share(self):
    self._test_document_publication_workflow('Text', 'share_action')

  def test_document_publication_workflow_Text_share_alive(self):
    self._test_document_publication_workflow('Text',
        'share_alive_action')

  def test_document_publication_workflow_archiveVersion(self):
    """ Test "visible" instances of a doc are auto archived when a new
    instance is made "visible" except when they have a future effective date.
    """
    portal = self.portal

    upload_file = makeFileUpload('TEST-en-002.doc')
    kw = dict(file=upload_file, synchronous_metadata_discovery=True)
    document_002 = self.portal.Base_contribute(**kw)
    document_002.publish()
    self.tic()

    document_003 = document_002.Base_createCloneDocument(batch_mode=1)
    document_003.setEffectiveDate(DateTime() - 1)
    document_003.publish()
    document_future_003 = document_002.Base_createCloneDocument(batch_mode=1)
    document_future_003.setEffectiveDate(DateTime() + 10)
    document_future_003.publish()
    self.tic()
    self.assertEqual('published', document_003.getValidationState())
    self.assertEqual('archived', document_002.getValidationState())
    self.assertEqual('published', document_future_003.getValidationState())

    # check if in any case document doesn't archive itself
    # (i.e. shared_alive -> published or any other similar chain)
    document_004 = document_002.Base_createCloneDocument(batch_mode=1)
    document_004.shareAlive()
    self.tic()

    document_004.publish()
    self.tic()
    self.assertEqual('published', document_004.getValidationState())
    # document_future_003 must not have been archived, as its effective date is
    # in the future.
    self.assertEqual('published', document_future_003.getValidationState())

    document_005 = document_004.Base_createCloneDocument(batch_mode=1)
    document_005.setEffectiveDate(DateTime() + 5)
    document_005.publish()
    self.tic()
    # Also, document_004 must not have been archived, as document_005's
    # effective_date is in the future.
    self.assertEqual('published', document_004.getValidationState())

    # check case when no language is used
    document_nolang_005 = document_004.Base_createCloneDocument(batch_mode=1)
    document_nolang_005.setLanguage(None)
    document_nolang_005.publish()
    self.tic()
    self.assertEqual('published', document_nolang_005.getValidationState())

    document_nolang_006 = document_nolang_005.Base_createCloneDocument(batch_mode=1)
    document_nolang_006.shareAlive()
    self.tic()

    self.assertEqual('archived', document_nolang_005.getValidationState())
    self.assertEqual('shared_alive', document_nolang_006.getValidationState())

    # should ignore already archived document
    document_nolang_007 = document_nolang_006.Base_createCloneDocument(batch_mode=1)
    document_nolang_006.archive()
    document_nolang_007.shareAlive()
    self.tic()

  def testFileWithNotDefinedMimeType(self):
    upload_file = makeFileUpload('TEST-001-en.dummy')
    kw = dict(file=upload_file, synchronous_metadata_discovery=True,
              portal_type='File')
    document = self.portal.Base_contribute(**kw)
    document.setReference('TEST')
    request = self.app.REQUEST
    download_file = document.index_html(REQUEST=request, format=None)
    self.assertEqual(download_file, 'foo\n')
    document_format = None
    self.assertEqual('TEST-001-en.dummy', document.getStandardFilename(
                      document_format))

class TestDocumentWithSecurity(TestDocumentMixin):

  username = 'yusei'

  def getTitle(self):
    return "DMS with security"

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Auditor', 'Author'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)

  def test_ShowPreviewAfterSubmitted(self):
    """
    Make sure that uploader can preview document after submitted.
    """
    filename = 'REF-en-001.odt'
    upload_file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=upload_file)
    self.tic()

    document.submit()

    preview_html = document.Document_getPreviewAsHTML().replace('\n', ' ')

    self.tic()

    self.assert_('I use reference to look up TEST' in preview_html)

  def test_DownloadableDocumentSize(self):
    '''Check that once the document is converted and cached, its size is
    correctly set'''
    portal = self.getPortalObject()
    portal_type = 'Text'
    document_module = portal.getDefaultModule(portal_type)

    # create a text document in document module
    text_document = document_module.newContent(portal_type=portal_type,
                                               reference='Foo_001',
                                               title='Foo_OO1')
    f = makeFileUpload('Foo_001.odt')
    text_document.edit(file=f.read())
    f.close()
    self.tic()

    # the document should be automatically converted to html
    self.assertEqual(text_document.getExternalProcessingState(), 'converted')

    # check there is nothing in the cache for pdf conversion
    self.assertFalse(text_document.hasConversion(format='pdf'))

    # call pdf conversion, in this way, the result should be cached
    mime_type, pdf_data = text_document.convert(format='pdf')
    pdf_size = len(pdf_data)


    # check there is a cache entry for pdf conversion of this document
    self.assertTrue(text_document.hasConversion(format='pdf'))

    # check the size of the pdf conversion
    self.assertEqual(text_document.getConversionSize(format='pdf'), pdf_size)

  def test_ImageSizePreference(self):
    """
    Tests that when user defines image sizes are already defined in preferences
    those properties are taken into account when the user
    views an image
    """
    super(TestDocumentWithSecurity, self).login('yusei')
    preference_tool = self.portal.portal_preferences
    #get the thumbnail sizes defined by default on default site preference
    default_thumbnail_image_height = \
       preference_tool.default_site_preference.getPreferredThumbnailImageHeight()
    default_thumbnail_image_width = \
       preference_tool.default_site_preference.getPreferredThumbnailImageWidth()
    self.assertTrue(default_thumbnail_image_height > 0)
    self.assertTrue(default_thumbnail_image_width > 0)
    self.assertEqual(default_thumbnail_image_height,
                     preference_tool.getPreferredThumbnailImageHeight())
    self.assertEqual(default_thumbnail_image_width,
                     preference_tool.getPreferredThumbnailImageWidth())
    #create new user preference and set new sizes for image thumbnail display
    user_pref = preference_tool.newContent(
                          portal_type='Preference',
                          priority=Priority.USER)
    self.portal.portal_workflow.doActionFor(user_pref, 'enable_action')
    self.assertEqual(user_pref.getPreferenceState(), 'enabled')
    self.tic()
    user_pref.setPreferredThumbnailImageHeight(default_thumbnail_image_height + 10)
    user_pref.setPreferredThumbnailImageWidth(default_thumbnail_image_width + 10)
    #Verify that the new values defined are the ones used by default
    self.assertEqual(default_thumbnail_image_height + 10,
                     preference_tool.getPreferredThumbnailImageHeight())
    self.assertEqual(default_thumbnail_image_height + 10,
                     preference_tool.getPreferredThumbnailImageHeight(0))
    self.assertEqual(default_thumbnail_image_width + 10,
                     preference_tool.getPreferredThumbnailImageWidth())
    self.assertEqual(default_thumbnail_image_width + 10,
                     preference_tool.getPreferredThumbnailImageWidth(0))
    #Now lets check that when we try to view an image as thumbnail,
    #the sizes of that image are the ones defined in user preference
    image_portal_type = 'Image'
    image_module = self.portal.getDefaultModule(image_portal_type)
    image = image_module.newContent(portal_type=image_portal_type)
    self.assertEqual('thumbnail',
       image.Image_view._getOb('my_thumbnail', None).get_value('image_display'))
    self.assertEqual((user_pref.getPreferredThumbnailImageWidth(),
                    user_pref.getPreferredThumbnailImageHeight()),
                     image.getSizeFromImageDisplay('thumbnail'))

class TestDocumentPerformance(TestDocumentMixin):

  def test_01_LargeOOoDocumentToImageConversion(self):
    """
      Test large OOoDocument to image conversion
    """
    ooo_document = self.portal.document_module.newContent(portal_type='Spreadsheet')
    upload_file = makeFileUpload('import_big_spreadsheet.ods')
    ooo_document.edit(file=upload_file)
    self.tic()
    before = time.time()
    # converting any OOoDocument -> PDF -> Image
    # make sure that this can happen in less tan XXX seconds i.e. code doing convert
    # uses only first PDF frame (not entire PDF) to make an image - i.e.optimized enough to not kill
    # entire system performance by doing extensive calculations over entire PDF (see r37102-37103)
    ooo_document.convert(format='png')
    after = time.time()
    req_time = (after - before)
    # we should have image converted in less than Xs
    # the 100s value is estimated one, it's equal to time for cloudood conversion (around 52s) +
    # time for gs conversion. As normally test are executed in parallel some tollerance is needed.
    self.assertTrue(req_time < 100.0,
      "Conversion took %s seconds and it is not less them 100.0 seconds" % \
        req_time)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDocument))
  suite.addTest(unittest.makeSuite(TestDocumentWithSecurity))
  suite.addTest(unittest.makeSuite(TestDocumentPerformance))
  return suite


# vim: syntax=python shiftwidth=2
