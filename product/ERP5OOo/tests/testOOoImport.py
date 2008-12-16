##############################################################################
# -*- coding: utf8 -*-
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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
import os
import sys

from zLOG import LOG
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5OOo.OOoUtils import OOoParser

def unpackData(data):
  """
  Unpack Pdata into string
  """
  if isinstance(data, str):
    return data
  else:
    data_list = []
    while data is not None:
      data_list.append(data.data)
      data = data.next
    return ''.join(data_list)

class FileUploadTest(file):

  __allow_access_to_unprotected_subobjects__=1

  def __init__(self, path, name):
    self.filename = name
    file.__init__(self, path, 'rb')
    self.headers = {}

def makeFilePath(name):
  return os.path.join(os.path.dirname(__file__), 'test_document', name)

def makeFileUpload(name):
  path = makeFilePath(name)
  return FileUploadTest(path, name)

class TestOOoImport(ERP5TypeTestCase):
  """
    ERP5  test import object list from OOo Document
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
    return "ERP5 Site - importing"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base',)

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()

    # Enable oood on localhost:8008
    # This should probably become a test runner option
    self.pref = self.portal.portal_preferences.newContent(
                          portal_type='System Preference')
    self.pref.setPreferredOoodocServerAddress('localhost')
    self.pref.setPreferredOoodocServerPortNumber(8008)
    self.pref.enable()
    get_transaction().commit()
    self.tic()

  def beforeTearDown(self):
    region = self.portal.portal_categories.region
    region.manage_delObjects(list(region.objectIds()))
    self.portal.portal_preferences.manage_delObjects([self.pref.getId()])
    get_transaction().commit()
    self.tic()


  ##################################
  ##  Useful methods
  ##################################

  def login(self):
    """
      Create a new manager user and login.
    """
    user_name = 'bartek'
    user_folder = self.portal.acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

  ##################################
  ##  Basic steps
  ##################################

  def stepTic(self, sequence=None, sequence_list=None, **kw):
    self.tic()

  def stepImportRawDataFile(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_list.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    get_transaction().commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.last_name'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.default_email_text'}
    )
    person_module.ERP5Site_importObjectFromOOo(import_file=f, listbox=listbox)

  def stepCheckActivitiesCount(self, sequence=None, sequence_list=None, **kw):
    message_list = self.getPortal().portal_activities.getMessageList()
    self.assertEqual(1,len(message_list))
    method_id = message_list[0].method_id
    self.assertEqual('ERP5Site_importObjectFromOOoActivity',method_id)

  def stepCheckImportedPersonList(self, sequence=None, sequence_list=None, **kw):
    person_module = self.getPortal().person_module
    for i in range(101):
      object = person_module['%s' % (i+1)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('Doe %s' % (i), object.getLastName())
      self.assertEqual('john.doe%s@foo.com' % (i), object.getDefaultEmailText())

  ##################################
  ##  Tests
  ##################################

  def test_01_ImportObjectFromOOoInActivities(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Simulate import of OOo file true ERP5Site_importObjectFromOOoFastInput
      For Person Module.
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepImportRawDataFile'
                 ,'stepCheckActivitiesCount'
                 ,'Tic'
                 ,'stepCheckImportedPersonList'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_Base_getCategoriesSpreadSheetMapping(self):
    # test structure returned by Base_getCategoriesSpreadSheetMapping
    mapping = self.portal.Base_getCategoriesSpreadSheetMapping(
        import_file=makeFileUpload('import_region_category.sxc'))
    self.assertTrue(isinstance(mapping, dict))
    self.assertEquals(['region'], list(mapping.keys()))
    region = mapping['region']
    self.assertTrue(isinstance(region, list))
    self.assertEquals(6, len(region))
    # base category is contained in the list
    self.assertEquals(dict(path='region',
                           title='region'),
                      region[0])
    self.assertEquals(dict(path='region/europe',
                           title='Europe'),
                      region[1])
    self.assertEquals(dict(codification='FR',
                           description='A Country',
                           int_index='1',
                           path='region/europe/france',
                           title='France'),
                      region[2])
    # strings are encoded in UTF8
    self.assertTrue(isinstance(region[1]['title'], str))
    self.assertTrue(isinstance(region[1]['path'], str))
    for k in region[1].keys():
      self.assertTrue(isinstance(k, str), (k, type(k)))

  def test_CategoryTool_importCategoryFile(self):
    # tests simple use of CategoryTool_importCategoryFile script
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=makeFileUpload('import_region_category.sxc'))
    get_transaction().commit()
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(2, len(region))
    self.assertTrue('europe' in region.objectIds())
    self.assertTrue('germany' in region.europe.objectIds())
    self.assertTrue('france' in region.europe.objectIds())
    france = region.europe.france
    self.assertEquals('France', france.getTitle())
    self.assertEquals('A Country', france.getDescription())
    self.assertEquals('FR', france.getCodification())
    self.assertEquals(1, france.getIntIndex())

  def test_CategoryTool_importCategoryFileXLS(self):
    # tests that CategoryTool_importCategoryFile supports .xls files
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=makeFileUpload('import_region_category.xls'))
    get_transaction().commit()
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(2, len(region))
    self.assertTrue('europe' in region.objectIds())
    self.assertTrue('germany' in region.europe.objectIds())
    self.assertTrue('france' in region.europe.objectIds())
    france = region.europe.france
    self.assertEquals('France', france.getTitle())
    self.assertEquals('A Country', france.getDescription())
    self.assertEquals('FR', france.getCodification())
    self.assertEquals(1, france.getIntIndex())

  def test_CategoryTool_importCategoryFile_PathStars(self):
    # tests CategoryTool_importCategoryFile with * in the paths columns
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=makeFileUpload('import_region_category_path_stars.sxc'))
    get_transaction().commit()
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(2, len(region))
    self.assertTrue('europe' in region.objectIds())
    self.assertTrue('germany' in region.europe.objectIds())
    self.assertTrue('france' in region.europe.objectIds())
    france = region.europe.france
    self.assertEquals('France', france.getTitle())
    self.assertEquals('A Country', france.getDescription())
    self.assertEquals('FR', france.getCodification())
    self.assertEquals(1, france.getIntIndex())
    
  def test_CategoryTool_importCategoryFile_PathStars_noID(self):
    # tests CategoryTool_importCategoryFile with * in the paths columns, and no
    # ID column, and non ascii titles
    self.portal.portal_categories.CategoryTool_importCategoryFile(
            import_file=makeFileUpload(
              'import_region_category_path_stars_non_ascii.sxc'))
    get_transaction().commit()
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(2, len(region))
    self.assertTrue('europe' in region.objectIds())
    self.assertTrue('germany' in region.europe.objectIds())
    self.assertTrue('france' in region.europe.objectIds())
    france = region.europe.france
    self.assertEquals('Frànce', france.getTitle())
    self.assertEquals('A Country', france.getDescription())
    self.assertEquals('FR', france.getCodification())
    self.assertEquals(1, france.getIntIndex())
    
  def test_CategoryTool_importCategoryFile_DuplicateIds(self):
    # tests CategoryTool_importCategoryFile when a document contain same
    # categories ID at different level (a good candidate for an acquisition
    # bug)
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=makeFileUpload('import_region_category_duplicate_ids.sxc'))
    get_transaction().commit()
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(1, len(region))
    self.assertEquals(['europe'], list(region.objectIds()))
    self.assertEquals(['france'], list(region.europe.objectIds()))
    self.assertEquals(['europe'], list(region.europe.france.objectIds()))
    self.assertEquals(['france'], list(region.europe.france.europe.objectIds()))
    self.assertEquals([], list(region.europe.france.europe.france.objectIds()))

  def test_Base_getCategoriesSpreadSheetMapping_DuplicateIdsAtSameLevel(self):
    # tests Base_getCategoriesSpreadSheetMapping when a document contain same
    # categories ID at the same level, in that case, a ValueError is raised
    import_file = makeFileUpload(
        'import_region_category_duplicate_ids_same_level.sxc')
    try:
      self.portal.portal_categories.Base_getCategoriesSpreadSheetMapping(
             import_file=import_file)
    except ValueError, error:
      # 'france' is the duplicate ID in this spreadsheet
      self.assertTrue('france' in str(error), str(error))
    else:
      self.fail('ValueError not raised')
    
    # Base_getCategoriesSpreadSheetMapping performs checks on the spreadsheet,
    # an "invalid spreadsheet" error handler can be provided, to report errors
    # nicely.
    message_list = []
    def on_invalid_spreadsheet(message):
      message_list.append(message)

    import_file = makeFileUpload(
        'import_region_category_duplicate_ids_same_level.sxc')
    self.portal.portal_categories.Base_getCategoriesSpreadSheetMapping(import_file,
         invalid_spreadsheet_error_handler=on_invalid_spreadsheet)
    
    self.assertEquals(1, len(message_list))
    self.assertTrue('france' in str(message_list[0]))


  # simple OOoParser tests
  def test_getSpreadSheetMapping(self):
    parser = OOoParser()
    parser.openFile(open(makeFilePath('import_data_list.ods'), 'rb'))
    mapping = parser.getSpreadsheetsMapping()
    self.assertEquals(['Person'], mapping.keys())
    person_mapping = mapping['Person']
    self.assertTrue(isinstance(person_mapping, list))
    self.assertTrue(102, len(person_mapping))
    self.assertEquals(person_mapping[0],
       ['Title', 'First Name', 'Last Name', 'Default Email Text'])
    self.assertEquals(person_mapping[1],
       ['John Doe 0', 'John', 'Doe 0', 'john.doe0@foo.com'])
  
  def test_openFromString(self):
    parser = OOoParser()
    parser.openFromString(
        open(makeFilePath('import_data_list.ods'), 'rb').read())
    mapping = parser.getSpreadsheetsMapping()
    self.assertEquals(['Person'], mapping.keys())

  def test_getSpreadSheetMappingStyle(self):
    parser = OOoParser()
    parser.openFile(open(makeFilePath('import_data_list_with_style.ods'), 'rb'))
    mapping = parser.getSpreadsheetsMapping()
    self.assertEquals(['Feuille1'], mapping.keys())
    self.assertEquals(mapping['Feuille1'][1],
                      ['a line with style'])
    self.assertEquals(mapping['Feuille1'][2],
                      ['a line with multiple styles'])
    self.assertEquals(mapping['Feuille1'][3],
                      ['http://www.erp5.org'])
    self.assertEquals(mapping['Feuille1'][4],
                      ['john.doe@example.com'])

  def test_getSpreadSheetMappingDataTypes(self):
    parser = OOoParser()
    parser.openFile(open(makeFilePath('import_data_list_data_type.ods'), 'rb'))
    mapping = parser.getSpreadsheetsMapping()
    self.assertEquals(['Feuille1'], mapping.keys())
    self.assertEquals(mapping['Feuille1'][0],
                      ['1234.5678'])
    self.assertEquals(mapping['Feuille1'][1],
                      ['1234.5678'])
    self.assertEquals(mapping['Feuille1'][2],
                      ['0.1'])
    self.assertEquals(mapping['Feuille1'][3],
                      ['2008-11-14'])
    self.assertEquals(mapping['Feuille1'][4],
                      ['2008-11-14T10:20:30']) # supported by DateTime
    self.assertEquals(mapping['Feuille1'][5],
                      ['PT12H34M56S']) # maybe not good, this is raw format


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOOoImport))
  return suite
