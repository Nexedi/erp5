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

# XXX test_02 works only with oood on
# XXX test_03 and test_04 work only WITHOUT oood (because of a known bug in erp5_dms)

import unittest
import time

import transaction
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Type.tests.utils import DummyLocalizer
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
import os

QUIET = 0
RUN_ALL_TEST = 1

# Define the conversion server host
conversion_server_host = ('127.0.0.1', 8008)

TEST_FILES_HOME = os.path.join(os.path.dirname(__file__), 'test_document')
FILE_NAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})(-(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"


def printAndLog(msg):
  """
  A utility function to print a message
  to the standard output and to the LOG
  at the same time
  """
  if not QUIET:
    msg = str(msg)
    ZopeTestCase._print('\n ' + msg)
    LOG('Testing... ', 0, msg)



def makeFilePath(name):
  return os.getenv('INSTANCE_HOME') + '/../Products/ERP5OOo/tests/test_document/' + name

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)


class TestDocument(ERP5TypeTestCase, ZopeTestCase.Functional):
  """
    Test basic document - related operations
  """

  def getTitle(self):
    return "DMS"

  ## setup

  def afterSetUp(self):
    self.setSystemPreference()
    # set a dummy localizer (because normally it is cookie based)
    self.portal.Localizer = DummyLocalizer()
    # make sure every body can traverse document module
    self.portal.document_module.manage_permission('View', ['Anonymous'], 1)
    self.portal.document_module.manage_permission(
                           'Access contents information', ['Anonymous'], 1)

  def setSystemPreference(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(conversion_server_host[0])
    default_pref.setPreferredOoodocServerPortNumber(conversion_server_host[1])
    default_pref.setPreferredDocumentFileNameRegularExpression(FILE_NAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)
    if default_pref.getPreferenceState() != 'global':
      default_pref.enable()

  def getDocumentModule(self):
    return getattr(self.getPortal(),'document_module')

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_ingestion', 'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web', 'erp5_dms')

  def getNeededCategoryList(self):
    return ()

  def beforeTearDown(self):
    """
      Do some stuff after each test:
      - clear document module
    """
    self.clearDocumentModule()

  def clearDocumentModule(self):
    """
      Remove everything after each run
    """
    transaction.abort()
    self.tic()
    doc_module = self.getDocumentModule()
    ids = [i for i in doc_module.objectIds()]
    doc_module.manage_delObjects(ids)
    transaction.commit()
    self.tic()

  ## helper methods

  def createTestDocument(self, file_name=None, portal_type='Text', reference='TEST', version='002', language='en'):
    """
      Creates a text document
    """
    dm=self.getPortal().document_module
    doctext=dm.newContent(portal_type=portal_type)
    if file_name is not None:
      f = open(makeFilePath(file_name), 'rb')
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

  def clearCache(self):
    self.portal.portal_caches.clearAllCache()

  ## steps
  
  def stepTic(self, sequence=None, sequence_list=None, **kw):
    self.tic()

  ## tests

  def test_01_HasEverything(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Standard test to make sure we have everything we need - all the tools etc
    """
    if not run: return
    printAndLog('\nTest Has Everything ')
    self.failUnless(self.getCategoryTool()!=None)
    self.failUnless(self.getSimulationTool()!=None)
    self.failUnless(self.getTypeTool()!=None)
    self.failUnless(self.getSQLConnection()!=None)
    self.failUnless(self.getCatalogTool()!=None)
    self.failUnless(self.getWorkflowTool()!=None)

  def test_02_RevisionSystem(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
      Test revision mechanism
    """
    if not run: return
    printAndLog('\nTest Revision System')
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
    document.immediateReindexObject()
    transaction.commit()
    self.tic()
    document_url = document.getRelativeUrl()
    def getTestDocument():
      return self.portal.restrictedTraverse(document_url)
    self.assertEqual(getTestDocument().getRevision(), '1')
    getTestDocument().edit(file=file)
    transaction.commit()
    self.tic()
    self.assertEqual(getTestDocument().getRevision(), '2')
    getTestDocument().edit(title='Hey Joe')
    transaction.commit()
    self.tic()
    self.assertEqual(getTestDocument().getRevision(), '3')
    another_document = self.portal.portal_contributions.newContent(file=file)
    transaction.commit()
    self.tic()
    self.assertEqual(getTestDocument().getRevision(), '4')
    self.assertEqual(getTestDocument().getRevisionList(), ['1', '2', '3', '4'])

  def test_03_Versioning(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
      Test versioning
    """
    if not run: return
    printAndLog('\nTest Versioning System')
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
    transaction.commit()
    self.tic()
    self.failIf(docs[1].isVersionUnique())
    self.failIf(docs[2].isVersionUnique())
    self.failUnless(docs[3].isVersionUnique())
    docs[2].setVersion('003')
    transaction.commit()
    self.tic()
    self.failUnless(docs[1].isVersionUnique())
    self.failUnless(docs[2].isVersionUnique())
    self.failUnless(docs[3].isVersionUnique())
    self.failUnless(docs[1].getLatestVersionValue() == docs[3])
    self.failUnless(docs[2].getLatestVersionValue() == docs[3])
    self.failUnless(docs[3].getLatestVersionValue() == docs[3])
    version_list = [br.getRelativeUrl() for br in docs[2].getVersionValueList()]
    self.failUnless(version_list == [docs[3].getRelativeUrl(), docs[2].getRelativeUrl(), docs[1].getRelativeUrl()])

  def test_04_VersioningWithLanguage(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
      Test versioning with multi-language support
    """
    if not run: return
    printAndLog('\nTest Versioning With Language')
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
    transaction.commit()
    self.tic()
    doc = docs[2] # can be any
    self.failUnless(doc.getOriginalLanguage() == 'en')
    self.failUnless(doc.getLanguageList() == ['en', 'fr', 'pl', 'sp'])
    self.failUnless(doc.getLatestVersionValue() == docs[4]) # there are two latest - it chooses the one in user language
    self.failUnless(doc.getLatestVersionValue('en') == docs[4])
    self.failUnless(doc.getLatestVersionValue('fr') == docs[2])
    self.failUnless(doc.getLatestVersionValue('pl') == docs[3])
    self.failUnless(doc.getLatestVersionValue('ru') == None)
    localizer.changeLanguage('sp') # change user language
    self.failUnless(doc.getLatestVersionValue() == docs[5]) # there are two latest - it chooses the one in user language
    docs[6] = document_module.newContent(reference='TEST', version='004', language='pl')
    docs[7] = document_module.newContent(reference='TEST', version='004', language='en')
    transaction.commit()
    self.tic()
    self.failUnless(doc.getLatestVersionValue() == docs[7]) # there are two latest, neither in user language - it chooses the one in original language

  def test_06_testExplicitRelations(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
      Test explicit relations.
      Explicit relations are just like any other relation, so no need to test them here
      except for similarity cloud which we test.
    """
    if not run: return
    
    printAndLog('\nTest Explicit Relations')
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

    transaction.commit()
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

    transaction.commit()
    
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
    
    transaction.commit()
    
    # if user language is "bg"
    self.portal.Localizer.changeLanguage('bg')
    self.assertSameSet([document8, document13], 
                       document6.getSimilarCloudValueList())

  def test_07_testImplicitRelations(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
      Test implicit (wiki-like) relations.
    """
    # XXX this test should be extended to check more elaborate language selection
    if not run: return

    def sqlresult_to_document_list(result):
      return [i.getObject() for i in result]

    printAndLog('\nTest Implicit Relations')
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

    transaction.commit()
    self.tic()
    printAndLog('\nTesting Implicit Predecessors')
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
    transaction.commit()

    printAndLog('\nTesting Implicit Successors')
    # the implicit successors should be return document with appropriate
    # language.

    # if user language is 'en'.
    self.portal.Localizer.changeLanguage('en')

    self.assertSameSet(
      [document3],
      sqlresult_to_document_list(document5.getImplicitSuccessorValueList()))

    # clear transactional variable cache
    transaction.commit()

    # if user language is 'fr'.
    self.portal.Localizer.changeLanguage('fr')
    self.assertSameSet(
      [document2],
      sqlresult_to_document_list(document5.getImplicitSuccessorValueList()))

    # clear transactional variable cache
    transaction.commit()

    # if user language is 'ja'.
    self.portal.Localizer.changeLanguage('ja')
    self.assertSameSet(
      [document3],
      sqlresult_to_document_list(document5.getImplicitSuccessorValueList()))

  def testOOoDocument_get_size(self):
    # test get_size on OOoDocument
    doc = self.portal.document_module.newContent(portal_type='Spreadsheet')
    doc.edit(file=makeFileUpload('import_data_list.ods'))
    self.assertEquals(len(makeFileUpload('import_data_list.ods').read()),
                      doc.get_size())

  def testTempOOoDocument_get_size(self):
    # test get_size on temporary OOoDocument
    from Products.ERP5Type.Document import newTempOOoDocument
    doc = newTempOOoDocument(self.portal, 'tmp')
    doc.edit(base_data='OOo')
    self.assertEquals(len('OOo'), doc.get_size())

  def testOOoDocument_hasData(self):
    # test hasData on OOoDocument
    doc = self.portal.document_module.newContent(portal_type='Spreadsheet')
    self.failIf(doc.hasData())
    doc.edit(file=makeFileUpload('import_data_list.ods'))
    self.failUnless(doc.hasData())

  def testTempOOoDocument_hasData(self):
    # test hasData on TempOOoDocument
    from Products.ERP5Type.Document import newTempOOoDocument
    doc = newTempOOoDocument(self.portal, 'tmp')
    self.failIf(doc.hasData())
    doc.edit(file=makeFileUpload('import_data_list.ods'))
    self.failUnless(doc.hasData())

  def test_Owner_Base_download(self):
    # tests that owners can download OOo documents, and all headers (including
    # filenames) are set correctly
    doc = self.portal.document_module.newContent(
                                  source_reference='test.ods',
                                  portal_type='Spreadsheet')
    doc.edit(file=makeFileUpload('import_data_list.ods'))

    uf = self.portal.acl_users
    uf._doAddUser('member_user1', 'secret', ['Member', 'Owner'], [])
    user = uf.getUserById('member_user1').__of__(uf)
    newSecurityManager(None, user)

    response = self.publish('%s/Base_download' % doc.getPath(),
                            basic='member_user1:secret')
    self.assertEquals(makeFileUpload('import_data_list.ods').read(),
                      response.body)
    self.assertEquals('application/vnd.oasis.opendocument.spreadsheet',
                      response.headers['content-type'])
    self.assertEquals('attachment; filename="import_data_list.ods"',
                      response.headers['content-disposition'])

  def test_Member_download_pdf_format(self):
    # tests that members can download OOo documents in pdf format (at least in
    # published state), and all headers (including filenames) are set correctly
    doc = self.portal.document_module.newContent(
                                  source_reference='test.ods',
                                  portal_type='Spreadsheet')
    doc.edit(file=makeFileUpload('import_data_list.ods'))
    doc.publish()
    transaction.commit()
    self.tic()
    transaction.commit()

    uf = self.portal.acl_users
    uf._doAddUser('member_user2', 'secret', ['Member'], [])
    user = uf.getUserById('member_user2').__of__(uf)
    newSecurityManager(None, user)

    response = self.publish('%s/Document_convert?format=pdf' % doc.getPath(),
                            basic='member_user2:secret')
    self.assertEquals('application/pdf', response.headers['content-type'])
    self.assertEquals('attachment; filename="import_data_list.pdf"',
                      response.headers['content-disposition'])

  def test_05_getCreationDate(self):
    """
    Check getCreationDate on all document type, as those documents 
    are not associated to edit_workflow.
    """
    portal = self.getPortalObject()
    for document_type in portal.getPortalDocumentTypeList():
      module = portal.getDefaultModule(document_type)
      obj = module.newContent(portal_type=document_type)
      self.assertNotEquals(obj.getCreationDate(),
                           module.getCreationDate())
      self.assertNotEquals(obj.getCreationDate(),
                           portal.CreationDate())

  def test_Base_getConversionFormatItemList(self):
    # tests Base_getConversionFormatItemList script (requires oood)
    self.assertTrue(('Microsoft Excel 97/2000/XP', 'xls') in
        self.portal.Base_getConversionFormatItemList(base_content_type=
                  'application/vnd.oasis.opendocument.spreadsheet'))
    self.assertTrue(('DocBook', 'docbook.xml') in
        self.portal.Base_getConversionFormatItemList(base_content_type=
                  'application/vnd.oasis.opendocument.text'))

  def test_06_ProcessingStateOfAClonedDocument(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
    Check that the processing state of a cloned document
    is not draft
    """
    if not run: return
    printAndLog('\nProcessing State of a Cloned Document')
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)

    self.assertEquals('converting', document.getExternalProcessingState())
    transaction.commit()
    self.assertEquals('converting', document.getExternalProcessingState())

    # Clone a uploaded document
    container = document.getParentValue()
    clipboard = container.manage_copyObjects(ids=[document.getId()])
    paste_result = container.manage_pasteObjects(cb_copy_data=clipboard)
    new_document = container[paste_result[0]['new_id']]

    self.assertEquals('converting', new_document.getExternalProcessingState())
    transaction.commit()
    self.assertEquals('converting', new_document.getExternalProcessingState())

    # Change workflow state to converted
    self.tic()
    self.assertEquals('converted', document.getExternalProcessingState())
    self.assertEquals('converted', new_document.getExternalProcessingState())

    # Clone a converted document
    container = document.getParentValue()
    clipboard = container.manage_copyObjects(ids=[document.getId()])
    paste_result = container.manage_pasteObjects(cb_copy_data=clipboard)
    new_document = container[paste_result[0]['new_id']]

    self.assertEquals('converted', new_document.getExternalProcessingState())
    transaction.commit()
    self.assertEquals('converted', new_document.getExternalProcessingState())
    self.tic()
    self.assertEquals('converted', new_document.getExternalProcessingState())

  def test_07_EmbeddedDocumentOfAClonedDocument(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
    Check the validation state of embedded document when its container is
    cloned
    """
    if not run: return
    printAndLog('\nValidation State of a Cloned Document')
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)

    sub_document = document.newContent(portal_type='Image')
    self.assertEquals('embedded', sub_document.getValidationState())
    transaction.commit()
    self.tic()
    self.assertEquals('embedded', sub_document.getValidationState())

    # Clone document
    container = document.getParentValue()
    clipboard = container.manage_copyObjects(ids=[document.getId()])

    paste_result = container.manage_pasteObjects(cb_copy_data=clipboard)
    new_document = container[paste_result[0]['new_id']]

    new_sub_document_list = new_document.contentValues(portal_type='Image')
    self.assertEquals(1, len(new_sub_document_list))
    new_sub_document = new_sub_document_list[0]
    self.assertEquals('embedded', new_sub_document.getValidationState())
    transaction.commit()
    self.tic()
    self.assertEquals('embedded', new_sub_document.getValidationState())

  def test_08_EmbeddedDocumentState(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
    Check the validation state of an embedded document
    """
    if not run: return
    printAndLog('\nValidation State of an Embedded Document')
    filename = 'EmbeddedImage-en-002.odt'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)

    transaction.commit()
    self.tic()

    self.assertEquals(0, len(document.contentValues(portal_type='Image')))
    document.convert(format='html')
    image_list = document.contentValues(portal_type='Image')
    self.assertEquals(0, len(image_list))
#     image = image_list[0]
#     self.assertEquals('embedded', image.getValidationState())

  def test_09_ScriptableKeys(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Check the default DMS scriptale keys
    """
    if not run: return
    printAndLog('\nScriptable Keys')
    # Check that SQL generated is valid
    self.portal.portal_catalog(advanced_search_text='')
    self.portal.portal_catalog(advanced_search_text='a search text')
    self.portal.portal_catalog(portal_search_text='')
    self.portal.portal_catalog(portal_search_text='a search text')

    # Create a document.
    document_1 = self.portal.document_module.newContent(portal_type='File')
    document_1.setDescription('Hello. ScriptableKey is very useful if you want to make your own search syntax.')
    document_2 = self.portal.document_module.newContent(portal_type='File')
    document_2.setDescription('This test make sure that scriptable key feature on ZSQLCatalog works.')

    transaction.commit()
    self.tic()

    # Use scriptable key to search above documents.
    self.assertEqual(len(self.portal.portal_catalog(advanced_search_text='ScriptableKey')), 1)
    self.assertEqual(len(self.portal.portal_catalog(advanced_search_text='RelatedKey')), 0)
    self.assertEqual(len(self.portal.portal_catalog(advanced_search_text='make')), 2)

  def test_PDFTextContent(self):
    upload_file = makeFileUpload('REF-en-001.pdf')
    document = self.portal.portal_contributions.newContent(file=upload_file)
    self.assertEquals('PDF', document.getPortalType())
    self.assertEquals('I use reference to look up TEST\n',
                      document._convertToText())
    self.assert_('I use reference to look up TEST' in
                 document._convertToHTML().replace('&nbsp;', ' '))
    self.assert_('I use reference to look up TEST' in
                 document.SearchableText())


class TestDocumentWithSecurity(ERP5TypeTestCase):

  username = 'yusei'

  def getTitle(self):
    return "DMS with security"

  def afterSetUp(self):
    self.setSystemPreference()
    # set a dummy localizer (because normally it is cookie based)
    self.portal.Localizer = DummyLocalizer()
    # make sure every body can traverse document module
    self.portal.document_module.manage_permission('View', ['Anonymous'], 1)
    self.portal.document_module.manage_permission(
                           'Access contents information', ['Anonymous'], 1)
    self.login()

  def setSystemPreference(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(conversion_server_host[0])
    default_pref.setPreferredOoodocServerPortNumber(conversion_server_host[1])
    default_pref.setPreferredDocumentFileNameRegularExpression(FILE_NAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)
    if default_pref.getPreferenceState() != 'global':
      default_pref.enable()
    transaction.commit()
    self.tic()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Auditor', 'Author'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)

  def getDocumentModule(self):
    return getattr(self.getPortal(),'document_module')

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_ingestion', 'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web', 'erp5_dms')

  def test_ShowPreviewAfterSubmitted(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Make sure that uploader can preview document after submitted.
    """
    if not run: return
    filename = 'REF-en-001.odt'
    upload_file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=upload_file)

    transaction.commit()
    self.tic()

    document.submit()

    preview_html = document.Document_getPreviewAsHTML().replace('\n', ' ')

    transaction.commit()
    self.tic()

    self.assert_('I use reference to look up TEST' in preview_html)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDocument))
  suite.addTest(unittest.makeSuite(TestDocumentWithSecurity))
  return suite


# vim: syntax=python shiftwidth=2 
