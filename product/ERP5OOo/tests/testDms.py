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


#
# Skeleton ZopeTestCase
#

from random import randint

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
RUN_ALL_TEST = 0

# Define the conversion server host
conversion_server_host = ('127.0.0.1', 8008)


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


class TestDocument(ERP5TypeTestCase):
  """
  """

  # Different variables used for this test

  def getTitle(self):
    return "DMS"

  ## setup

  def afterSetUp(self, quiet=QUIET, run=1):
    self.createCategoryList()
    self.createObjectList()
    self.setSystemPreference()
    self.login()
    portal = self.getPortal()

  def getDocumentModule(self):
    return getattr(self.getPortal(),'document_module')

  def getBusinessTemplateList(self):
    return ('erp5_base','erp5_trade','erp5_project','erp5_dms')

  def getNeededCategoryList(self):
    return ('function/publication/reviewer','function/project/director','function/hq')

  def createCategoryList(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList():
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:]:
        if not cat in path.objectIds():
          path = path.newContent(
            portal_type='Category',
            id=cat,
            title=cat,
            immediate_reindex=1)
        else:
          path = path[cat]

  def setSystemPreference(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(conversion_server_host[0])
    default_pref.setPreferredOoodocServerPortNumber(conversion_server_host[1])
    default_pref.setPreferredDocumentFileNameRegularExpression(
           "(?P<reference>[A-Z]{3,6})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})")
    default_pref.setPreferredReferenceLookupRegularExpression(
           "(?P<reference>[A-Z]{3,6})(-(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?")
    default_pref.enable()

  ## helper methods

  def getUserFolder(self):
    return self.getPortal().acl_users

  def login(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a new manager user and login.
    """
    user_name = 'dms_user'
    user_folder = self.portal.acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

  def createTestDocument(self, file_name=None, reference='TEST', version='002', language='en'):
    """
      Creates a text document
    """
    dm=self.getPortal().document_module
    doctext=dm.newContent(portal_type='Text Document')
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
    # there should still be only one document, with revision 4 (because it should have done mergeRevision)
    # getRevisionList should return (1, 2, 3, 4)

  def test_03_Versioning(self,quiet=QUIET,run=RUN_ALL_TEST):
    """
      Test versioning
    """
    if not run: return
    printAndLog('\nTest Versioning System')
    # create a test document, set coordinates (reference=TEST, version=002, language=en)
    # create a second test document, set coordinates (reference=TEST, version=002, language=en)
    # create a third test document, set its reference to ANOTHER
    # run isVersionUnique on all three (should return False, False, True)
    # change version of the second doc to 003
    # run isVersionUnique on all three (should return True)
    # run getLatestVersionValue on first and second (should return the second)
    # run getVersionValueList on first and second (should return the two)
    # run getVersionValueList on third (should return the third)

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
    # the following calls should produce the following output:
    # getOriginalLanguage() = 'en'
    # getLanguageList = ('en', 'fr', 'pl', 'sp')
    # getLatestVersionValue() = 4
    # getLatestVersionValue('en') = 4
    # getLatestVersionValue('fr') = 2
    # getLatestVersionValue('pl') = 3
    # getLatestVersionValue('ru') = None
    # Set user language with Localizer to 'sp'
    # getLatestVersionValue() = 5

  def test_05_UniqueReference(self,quiet=QUIET,run=RUN_ALL_TEST):
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
    # getSimilarCloudValueList on 4 should return 2, 3 and 5
    # getSimilarCloudValueList(depth=1) on 4 should return 3 and 5

  def test_07_testImplicitRelations(self,quiet=QUIET,run=RUN_ALL_TEST):
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
