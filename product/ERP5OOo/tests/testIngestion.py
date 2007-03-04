##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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
from cgi import FieldStorage
from zLOG import LOG
from zExceptions import BadRequest
from Testing import ZopeTestCase
from ZPublisher.HTTPRequest import FileUpload
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from AccessControl.SecurityManagement import newSecurityManager


if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

ooodoc_coordinates = ('127.0.0.1', 8008)

def shout(msg):
  msg = str(msg)
  ZopeTestCase._print('\n ' + msg)
  LOG('Testing... ', 0, msg)


def makeFileUpload(name):
  path = os.getenv('INSTANCE_HOME') + '/../Products/ERP5OOo/tests/' + name
  headers = {'content-disposition': 'form-data; name="field_my_file"; filename="%s"' % name}
  fs = FieldStorage(fp=open(path), headers=headers)
  fup = FileUpload(fs)
  return fup

class TestIngestion(ERP5TypeTestCase):
  """
    ERP5 Document Management System - test file ingestion mechanism
  """

  # pseudo constants
  RUN_ALL_TEST = 1
  QUIET = 0

  ##################################
  ##  ZopeTestCase Skeleton
  ##################################

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 DMS - ingestion"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base', 'erp5_trade', 'erp5_project', 'erp5_dms')

  def afterSetUp(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.datetime          = DateTime()
    self.portal            = self.getPortal()
    self.portal_categories = self.getCategoryTool()
    self.portal_catalog    = self.getCatalogTool()
    self.createCategories()
    self.createPreferences()
    self.createTools()

  def createTools(self):
    """
      Set up contribution tool and content type registry
    """
    # XXX portal_contributions is not created in bootstrap
    # so we have to create it here
    try:
      self.portal._delObject('portal_contributions')
    except AttributeError:
      pass
    addTool = self.portal.manage_addProduct['ERP5'].manage_addTool
    addTool('ERP5 Contribution Tool', None)
    # XXX  content_type_registry is not services by business templating mechanism
    # so it has to be exported and placed in ../../../unit_test/import/ director
    # we import it here
    try:
      self.portal._delObject('content_type_registry')
    except AttributeError:
      pass
    self.portal.manage_importObject(file='content_type_registry.zexp')

  def createPreferences(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(ooodoc_coordinates[0])
    default_pref.setPreferredOoodocServerPortNumber(ooodoc_coordinates[1])
    default_pref.setPreferredDocumentFileNameRegularExpression("(?P<reference>[A-Z]{3,6})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})")
    default_pref.enable()


  ##################################
  ##  Useful methods
  ##################################

  def login(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a new manager user and login.
    """
    user_name = 'bartek'
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)


  def createCategories(self):
    """
      Create some categories for testing.
    """
    self.category_list = [
                         # Role categories
                          {'path' : 'role/internal'
                           ,'title': 'Internal'
                           }

                         ]

    # Create categories
    # Note : this code was taken from the CategoryTool_importCategoryFile python
    #        script (packaged in erp5_core).
    for category in self.category_list:
      keys = category.keys()
      if 'path' in keys:
        base_path_obj = self.portal_categories
        is_base_category = True
        for category_id in category['path'].split('/'):
          # The current category is not existing
          if category_id not in base_path_obj.contentIds():
            # Create the category
            if is_base_category:
              category_type = 'Base Category'
            else:
              category_type = 'Category'
            base_path_obj.newContent( portal_type       = category_type
                                    , id                = category_id
                                    , immediate_reindex = 1
                                    )
          base_path_obj = base_path_obj[category_id]
          is_base_category = False
        new_category = base_path_obj

        # Set the category properties
        for key in keys:
          if key != 'path':
            method_id = "set" + convertToUpperCase(key)
            value = category[key]
            if value not in ('', None):
              if hasattr(new_category, method_id):
                method = getattr(new_category, method_id)
                method(value.encode('UTF-8'))

  def getCategoryList(self, base_category=None):
    """
      Get a list of categories with same base categories.
    """
    categories = []
    if base_category != None:
      for category in self.category_list:
        if category["path"].split('/')[0] == base_category:
          categories.append(category)
    return categories

  def checkObjectCatalogged(self, portal_type, reference):
    """
      make sure this object is already in the catalog
    """
    res = self.portal_catalog(portal_type=portal_type, reference=reference)
    self.assertEquals(len(res), 1)
    self.assertEquals(res[0].getReference(), reference)

  def createDocument(self, portal_type, id):
    """
      create an empty document of given portal type
      it has id as given and reference like document_[id]
      immediately catalogged and verified in two ways
    """
    dm = self.getPortal().document_module
    reference =  'document_' + id
    doc = dm.newContent(portal_type=portal_type, id=id, reference=reference)
    #doctext._getServerCoordinate = getOoodCoordinate()
    doc.reindexObject(); get_transaction().commit(); self.tic()
    self.checkObjectCatalogged('Text', reference)
    self.assert_(hasattr(dm, id))


  ##################################
  ##  Basic steps
  ##################################

  def stepCheckPreferences(self, sequence=None, sequence_list=None, **kw):
    """
      make sure preferences are set up properly and accessible
    """
    self.assertEquals(self.portal.portal_preferences.getPreferredOoodocServerAddress(), ooodoc_coordinates[0])
    self.assertEquals(self.portal.portal_preferences.getPreferredOoodocServerPortNumber(), ooodoc_coordinates[1])
    self.assertEquals(self.portal.portal_preferences.default_site_preference.getPreferredDocumentFileNameRegularExpression(), "(?P<reference>[A-Z]{3,6})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})")

  def stepCheckContentTypeRegistry(self, sequence=None, sequence_list=None, **kw):
    """
      check if we successfully imported registry
      and that it has all the entries we need
    """
    reg = self.portal.content_type_registry
    correct_type_mapping = {
            'doc' : 'Text',
            'txt' : 'Text',
            'odt' : 'Text',
            'sxw' : 'Text',
            'rtf' : 'Text',
            'gif' : 'Image',
            'jpg' : 'Image',
            'png' : 'Image',
            'bmp' : 'Image',
            'pdf' : 'PDF',
            'xls' : 'Spreadsheet',
            'ods' : 'Spreadsheet',
            'sdc' : 'Spreadsheet',
            'ppt' : 'Presentation',
            'odp' : 'Presentation',
            'sxi' : 'Presentation',
            'xxx' : 'File',
          }
    for type, portal_type in correct_type_mapping.items():
      file_name = 'aaa.' + type
      self.assertEquals(reg.findTypeName(file_name, None, None), portal_type)

  def stepCreatePerson(self, sequence=None, sequence_list=None, **kw):
    """
      Create a person.
    """
    portal_type = 'Person'
    reference = 'john_doe'
    person_module = self.portal.getDefaultModule(portal_type)
    person = person_module.newContent( portal_type=portal_type
                                     , id='john'
                                     ,  reference = reference
                                     )
    person.reindexObject(); get_transaction().commit(); self.tic()

  def stepCreateTextDocument(self, sequence=None, sequence_list=None, **kw):
    """
      create an empty document 'one'
      for further testing
    """
    self.createDocument('Text', 'one')

  def stepStraightUpload(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file directly from the form
      check if it has the data and source_reference
    """
    dm = self.getPortal().document_module
    doc = getattr(dm, 'one')
    f = makeFileUpload('TEST-en-002.doc')
    doc.edit(file=f)
    self.assert_(doc.hasFile())
    self.assertEquals(doc.getSourceReference(), 'TEST-en-002.doc')
    self.assertEquals(doc.getRevision(), '')

  def stepDialogUpload(self, sequence=None, sequence_list=None, **kw):
    """
      upload a file using dialog
      should increase revision
    """
    dm = self.getPortal().document_module
    context = getattr(dm, 'one')
    f = makeFileUpload('TEST-en-002.doc')
    file_name = f.filename
    context.Document_uploadFile(file=f)
    self.assertEquals(context.getRevision(), '001')

  def stepDiscoverFromFilename(self, sequence=None, sequence_list=None, **kw):
    """
      upload file using dialog
      this should trigger metadata discovery and we should have
      basic coordinates immediately, from first stage
    """
    dm = self.getPortal().document_module
    context = getattr(dm, 'one')
    f = makeFileUpload('TEST-en-002.doc')
    file_name = f.filename
    context.Document_uploadFile(file=f)
    self.assertEquals(context.getReference(), 'TEST')
    self.assertEquals(context.getLanguage(), 'en')
    self.assertEquals(context.getVersion(), '002')


  ##################################
  ##  Tests
  ##################################

  def test_01_checkBasics(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run: return
    if not quiet: shout('test_01_checkBasics')
    sequence_list = SequenceList()
    step_list = [ 'stepCheckPreferences'
                 ,'stepCheckContentTypeRegistry'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_02_TextDoc(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test basic behaviour of Text document
    """
    if not run: return
    if not quiet: shout('test_02_TextDoc')
    sequence_list = SequenceList()
    step_list = [ 'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepDialogUpload'
                 ,'stepDiscoverFromFilename'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIngestion))
    return suite


# vim: filetype=python syntax=python shiftwidth=2 
