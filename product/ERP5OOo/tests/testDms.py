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


#
# Skeleton ZopeTestCase
#

from random import randint
import time

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
import os
from Products.ERP5Type import product_path
from Products.ERP5OOo.Document.OOoDocument import ConversionError

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

QUIET = 0
RUN_ALL_TEST = 1

# Define the conversion server host
conversion_server_host = ('127.0.0.1', 8008)

TEST_FILES_HOME = os.path.join(os.getenv('INSTANCE_HOME'), 'Products', 'ERP5OOo', 'tests', 'test_document')
FILE_NAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,6})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,6})(-(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"


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


class FileUploadTest(file):

  __allow_access_to_unprotected_subobjects__=1

  def __init__(self, path, name):
    self.filename = name
    file.__init__(self, path)
    self.headers = {}


def makeFilePath(name):
  return os.getenv('INSTANCE_HOME') + '/../Products/ERP5OOo/tests/test_document/' + name


def makeFileUpload(name):
  path = makeFilePath(name)
  return FileUploadTest(path, name)

class DummyLocalizer:

  """
    A replacement for stock cookie - based localizer
  """

  lang = 'en'

  def get_selected_language(self):
    return self.lang

  def changeLanguage(self, lang):
    self.lang = lang

  def translate(self, dictionnary, word):
    return word

class TestDocument(ERP5TypeTestCase):
  """
    Test basic document - related operations
  """

  def getTitle(self):
    return "DMS"

  ## setup

  def afterSetUp(self, quiet=QUIET, run=0):
    self.portal = self.getPortal()
    self.setSystemPreference()
    # set a dummy localizer (because normally it is cookie based)
    self.portal.Localizer = DummyLocalizer()

  def setSystemPreference(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(conversion_server_host[0])
    default_pref.setPreferredOoodocServerPortNumber(conversion_server_host[1])
    default_pref.setPreferredDocumentFileNameRegularExpression(FILE_NAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)
    default_pref.enable()

  def getDocumentModule(self):
    return getattr(self.getPortal(),'document_module')

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_web', 'erp5_dms_mysql_innodb_catalog', 'erp5_dms')

  def getNeededCategoryList(self):
    return ()

  def tearDown(self):
    """
      Do some stuff after each test:
      - clear document module
    """
    # XXX Is it safe to overwrite tearDown?
    self.clearDocumentModule()

  def clearDocumentModule(self):
    """
      Remove everything after each run
    """
    printAndLog("clearing document module...")
    doc_module = self.getDocumentModule()
    ids = [i for i in doc_module.objectIds()]
    doc_module.manage_delObjects(ids)
    get_transaction().commit()
    self.tic()

  ## helper methods

  def createTestDocument(self, file_name=None, portal_type='Text', reference='TEST', version='002', language='en'):
    """
      Creates a text document
    """
    dm=self.getPortal().document_module
    doctext=dm.newContent(portal_type=portal_type)
    if file_name is not None:
      f = open(makeFilePath(file_name))
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
    # revision should be 0
    # upload file (can be the same) into it
    # revision should now be 1
    # edit the document with any value or no values
    # revision should now be 2
    # contribute the same file through portal_contributions
    # the same document should now have revision 3 (because it should have done mergeRevision)
    # getRevisionList should return (0, 1, 2, 3)
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)
    document.immediateReindexObject()
    get_transaction().commit()
    self.tic()
    document_url = document.getRelativeUrl()
    def getTestDocument():
      return self.portal.restrictedTraverse(document_url)
    self.failUnless(getTestDocument().getRevision() == '0')
    getTestDocument().edit(file=file)
    get_transaction().commit()
    self.tic()
    self.failUnless(getTestDocument().getRevision() == '1')
    getTestDocument().edit(title='Hey Joe')
    get_transaction().commit()
    self.tic()
    self.failUnless(getTestDocument().getRevision() == '2')
    another_document = self.portal.portal_contributions.newContent(file=file)
    get_transaction().commit()
    self.tic()
    self.failUnless(getTestDocument().getRevision() == '3')
    self.failUnless(getTestDocument().getRevisionList() == ['0', '1', '2'] )

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
    get_transaction().commit()
    self.tic()
    self.failIf(docs[1].isVersionUnique())
    self.failIf(docs[2].isVersionUnique())
    self.failUnless(docs[3].isVersionUnique())
    docs[2].setVersion('003')
    get_transaction().commit()
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
    get_transaction().commit()
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
    get_transaction().commit()
    self.tic()
    self.failUnless(doc.getLatestVersionValue() == docs[7]) # there are two latest, neither in user language - it chooses the one in original language

  def no_test_05_UniqueReference(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
      Test automatic setting of unique reference
    """
    if not run: return
    printAndLog('\nTest Automatic Setting Unique Reference')
    # create three empty test documents
    # run setUniqueReference on the second
    # reference of the second doc should now be TEST-auto-2
    # run setUniqueReference('uniq') on the third
    # reference of the third doc should now be TEST-uniq-1

  def no_test_06_testExplicitRelations(self,quiet=QUIET,run=RUN_ALL_TEST):
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
    # getSimilarCloudValueList on 4 should return 2, 3 and 5
    # getSimilarCloudValueList(depth=1) on 4 should return 3 and 5

  def no_test_07_testImplicitRelations(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
      Test implicit (wiki-like) relations.
    """
    # XXX this test should be extended to check more elaborate language selection
    if not run: return
    printAndLog('\nTest Implicit Relations')
    # create docs to be referenced:
    # (1) TEST, 002, en
    # (2) TEST, 002, fr
    # (3) TEST, 003, en
    # create docs to contain references in text_content:
    # REF, 001, en; "I use reference to look up TEST"
    # REF, 002, en; "I use reference to look up TEST"
    # REFLANG, 001, en: "I use reference and language to look up TEST-fr"
    # REFVER, 001, en: "I use reference and version to look up TEST-002"
    # REFVERLANG, 001, en: "I use reference, version and language to look up TEST-002-en"
    printAndLog('\nTesting Implicit Predecessors')
    # the implicit predecessors should be:
    # for (1): REF-002, REFVER, REFVERLANG
    # for (2): REF-002, REFLANG, REFVER
    # for (3): REF-002
    printAndLog('\nTesting Implicit Successors')
    # the implicit successors should be:
    # for REF: (3)
    # for REFLANG: (2)
    # for REFVER: (3)
    # for REFVERLANG: (3)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestDocument))
        return suite


# vim: syntax=python shiftwidth=2 
