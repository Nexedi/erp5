##############################################################################
# -*- coding: utf8 -*-
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Mohamadou Mbengue <mmbengue@gmail.com>
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

from zLOG import LOG
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5OOo.OOoUtils import OOoParser
from Products.ERP5.Document.Document import ConversionError
from DateTime import DateTime
import transaction

person_current_id = 1

def shout(msg):
  msg = str(msg)
  ZopeTestCase._print('\n ' + msg)
  LOG('Testing... ', 0, msg)

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
  gender_base_cat_id    = 'gender'
  function_base_cat_id  = 'function'

  ##################################
  ##  ZopeTestCase Skeleton
  ##################################

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 Site - OOo File importing"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base', 'erp5_ooo_import')

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()

    # Enable oood on localhost:8008
    # This should probably become a test runner option
    self.pref = self.portal.portal_preferences.newContent(
                          portal_type='Preference')
    self.pref.setPreferredOoodocServerAddress('localhost')
    self.pref.setPreferredOoodocServerPortNumber(8008)
    self.pref.enable()

    # create browser_id_manager
    ZopeTestCase.installProduct('Sessions')
    if not "browser_id_manager" in self.portal.objectIds():
      self.portal.manage_addProduct['Sessions'].constructBrowserIdManager()

    # We create categories needed
    # For testing file whith column corresponding to category
    portal_categories = self.getCategoryTool()

    gender_bc = self.gender_base_cat_id
    if gender_bc not in portal_categories.objectIds():
      portal_categories.newContent(portal_type='Base Category', id=gender_bc)
    if not portal_categories[gender_bc].has_key('male'):
      portal_categories[gender_bc].newContent(id='male', portal_type='Category', title='Male')
    if not portal_categories[gender_bc].has_key('female'):
      portal_categories[gender_bc].newContent(id='female', portal_type='Category', title='Female')

    function_bc = self.function_base_cat_id
    if function_bc not in portal_categories.objectIds():
      portal_categories.newContent(portal_type='Base Category', id=function_bc)
    if not portal_categories[function_bc].has_key('director'):
      portal_categories[function_bc].newContent(id='director', portal_type='Category', title='Director')
    if not portal_categories[function_bc].has_key('manager'):
      portal_categories[function_bc].newContent(id='manager', portal_type='Category', title='Manager')

    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    region = self.portal.portal_categories.region
    region.manage_delObjects(list(region.objectIds()))
    self.portal.portal_preferences.manage_delObjects([self.pref.getId()])
    gender = self.portal.portal_categories.gender
    function  = self.portal.portal_categories.function
    gender.manage_delObjects(list(gender.objectIds()))
    function.manage_delObjects(list(function.objectIds()))

    transaction.commit()
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
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor',
                               	           'Associate', 'Auditor', 'Author'], [])
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
    transaction.commit(); self.tic()
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
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepCheckActivitiesCount(self, sequence=None, sequence_list=None, **kw):
    message_list   = self.getPortal().portal_activities.getMessageList()
    self.assertEqual(102,len(message_list))
    '''for i in range(101):
      method_id = message_list[i].method_id
      self.assertEqual('Base_importFileLine',method_id)'''

  def stepCheckImportedPersonList(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(101):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('Doe %s' % (i), object.getLastName())
      self.assertEqual('john.doe%s@foo.com' % (i), object.getDefaultEmailText())
    person_current_id =  person_current_id+101

  def stepCheckImportedPersonListBlank(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(101):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('Doe %s' % (i), object.getLastName())
      self.assertEqual('john.doe%s@foo.com' % (i), object.getDefaultEmailText())
    person_current_id = person_current_id+101

  def stepCheckImportedPersonListCategory(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(10):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('male', object.getGender())
      self.assertEqual('director', object.getFunction())
    person_current_id = person_current_id+10

  def stepCheckAuthorImportedPersonList(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(10):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('male', object.getGender())
      self.assertEqual('director', object.getFunction())
    person_current_id=person_current_id+10

  def stepCheckImportedPersonListFreeText(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(10):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('male', object.getGenderFreeText())
      self.assertEqual('Director', object.getFunctionFreeText())
    person_current_id=person_current_id+10

  def stepCheckImportedPersonListAccentuated(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(10):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      title = 'John Doe é %s' % (i)
      #encode_title = title.encode('UTF-8')
      self.assertEqual(title, object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('male', object.getGender())
      self.assertEqual('director', object.getFunction())
    person_current_id = person_current_id+10

  def stepCheckXLSImportedPersonList(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(10):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('Doe %s' % (i), object.getLastName())
      self.assertEqual('john.doe%s@foo.com' % (i), object.getDefaultEmailText())
    person_current_id = person_current_id+10

  def stepCheckImportedPersonListWithDates(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(9):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('male', object.getGender())
      self.assertEqual(DateTime('2008/02/0%s %s' % (i+1, 'GMT')), object.getStartDate())
    object = person_module['%s' % (object_id+1)]
    self.assertEqual(DateTime('2008/02/%s %s' % (10, 'GMT')), object.getStartDate())
    person_current_id = person_current_id+10

  def stepCheckImportFloatsAndPercentage(self, sequence=None, sequence_list=None, **kw):
    currency_module = self.getPortal().currency_module
    for i in range(10):
      height_quantity = 1000.3 + i
      object = currency_module['%s' % (i + 1)]
      self.assertEqual('Currency %s' % (i), object.getTitle())
      self.assertEqual(height_quantity, object.getHeightQuantity())

  def stepCheckImportedPersonList_1(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(1000):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('Doe %s' % (i), object.getLastName())
      self.assertEqual('john.doe%s@foo.com' % (i), object.getDefaultEmailText())
    person_current_id =  person_current_id+1000

  def stepCheckImportedPersonList_2(self, sequence=None, sequence_list=None, **kw):
    global person_current_id
    person_module = self.getPortal().person_module
    for i in range(10000):
      object_id = i + person_current_id
      object = person_module['%s' % (object_id)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('Doe %s' % (i), object.getLastName())
      self.assertEqual('john.doe%s@foo.com' % (i), object.getDefaultEmailText())
    person_current_id =  person_current_id+10000

  def stepCheckImportedOrganisationList(self, sequence=None, sequence_list=None, **kw):
    organisation_module = self.getPortal().organisation_module
    for i in range(10):
      object_id = i + 1
      object = organisation_module['%s' % (object_id)]
      self.assertEqual('Foo Organisation %s' % (i), object.getTitle())
      self.assertEqual('Description organisation %s' % (i), object.getDescription())
      self.assert_('1234567%s' % (i) in object.getTelephoneText())
      self.assertEqual('org%s@foo.com' % (i), object.getEmailText())

  def stepImportFileNoMapping(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_list.ods')
    #self.logMessage("f : %s" % str(f))

    person_module = self.getPortal().person_module
    person_module.Base_importFile(import_file=f, listbox=())
    self.assertRaises(ConversionError, person_module.Base_importFile, import_file=f, listbox=())
    #self.logMessage("Validation failed : %s" % kw)

  def stepImportFileWithBlankLine(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_list_blank_line.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
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
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportFileWithCategory(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_with_categories.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.gender'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.function'}
    )
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportFileWithDates(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_with_dates.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.gender'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.start_date'}
    )
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportFloatsAndPercentage(self, sequence=None, sequence_list=None, **kw):
    """
      This test make sure that either floats (1000,9), sientific numbers (1,00E+003)
      or percentage (19%) are correctly imported .
    """
    f = makeFileUpload('import_float_and_percentage.ods')
    currency_module = self.getPortal().currency_module
    currency_module.manage_delObjects([id for id in currency_module.getObjectIds()])
    transaction.commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Currency.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Currency.height_quantity'}
    )
    currency_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportOrganisation(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_organisation_list.ods')
    organisation_module = self.getPortal().organisation_module
    #purge existing persons
    organisation_module.manage_delObjects([id for id in organisation_module.getObjectIds()])
    transaction.commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Organisation.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Organisation.description'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Organisation.telephone_text'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Organisation.email_text'}
    )
    organisation_module.Base_importFile(import_file=f, listbox=listbox)

  def stepAuthorImportFile(self, sequence=None, sequence_list=None, **kw):
    user_name = 'author'
    user_folder = self.portal.acl_users
    user_folder._doAddUser(user_name, '', ['Author', 'Member'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

    f = makeFileUpload('import_data_with_categories.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.gender'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.function'}
    )
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportFileWithFreeText(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_with_categories.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.gender_free_text'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.function_free_text'}
    )
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportFileWithAccentuatedText(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_accentuated_text.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.gender'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.function'}
    )
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportXLSFile(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_list.xls')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
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
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportBigFile_1(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_big_file_1.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
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
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportBigFile_2(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_big_file_2.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    transaction.commit(); self.tic()
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
    person_module.Base_importFile(import_file=f, listbox=listbox)

  ##  Tests
  ##################################
  def test_01_ImportFileLine(self, quiet=QUIET, run=RUN_ALL_TEST):
    # Simulate import of OOo file Base_importFile for Person Module.
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

  def test_02_ImportFileBlankLine(self, quiet=QUIET, run=RUN_ALL_TEST):
    #Simulate import of an OOo file with blank lines.
    #self.logMessage('Simulate import of an OOo file with blank lines')
    if not run: return
    sequence_list = SequenceList()
    step_list = [  'stepImportFileWithBlankLine'
                  ,'Tic'
                  ,'stepCheckImportedPersonListBlank'
                 ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_03_ImportNoMapping(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepImportFileNoMapping'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_04_ImportFileWithCategory(self, quiet=QUIET, run=RUN_ALL_TEST):
    #self.logMessage('Simulate import of an OOo file with blank lines')
    if not run: return
    sequence_list = SequenceList()
    step_list = [  'stepImportFileWithCategory'
                  ,'Tic'
                  ,'stepCheckImportedPersonListCategory'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_05_ImportOrganisation(self, quiet=QUIET, run=RUN_ALL_TEST):
   #self.logMessage('Simulate import of an OOo file with blank lines')
    if not run: return
    sequence_list = SequenceList()
    step_list = [  'stepImportOrganisation'
                  ,'Tic'
                  ,'stepCheckImportedOrganisationList'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_06_AuthorImportFile(self, quiet=QUIET, run=RUN_ALL_TEST):
    #self.logMessage('Simulate import of an OOo file with blank lines')
    if not run: return
    sequence_list = SequenceList()
    step_list = [  'stepAuthorImportFile'
                  ,'Tic'
                  ,'stepCheckAuthorImportedPersonList'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_07_ImportFileWithFreeText(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run: return
    sequence_list = SequenceList()
    step_list = [  'stepImportFileWithFreeText'
                  ,'Tic'
                  ,'stepCheckImportedPersonListFreeText'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_08_ImportFileWithAccentuatedText(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run: return
    sequence_list = SequenceList()
    step_list = [  'stepImportFileWithAccentuatedText'
                  ,'Tic'
                  ,'stepCheckImportedPersonListAccentuated'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_09_ImportXLSFile(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepImportXLSFile'
                 ,'Tic'
                 ,'stepCheckXLSImportedPersonList'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_10_ImportFileWithDates(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepImportFileWithDates'
                 ,'Tic'
                 ,'stepCheckImportedPersonListWithDates'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_11_ImportFloatAndPercentage(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepImportFloatsAndPercentage'
                 ,'Tic'
                 ,'stepCheckImportFloatsAndPercentage'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_12_ImportBigFile_1(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run: return
    sequence_list = SequenceList()
    step_list = [  'stepImportBigFile_1'
                  ,'Tic'
                  ,'stepCheckImportedPersonList_1'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  '''
  def test_12_ImportBigFile_2(self, quiet=QUIET, run=RUN_ALL_TEST):
    #self.logMessage('Simulate import of an OOo file with blank lines')
    if not run: return
    sequence_list = SequenceList()
    step_list = [  'stepImportBigFile_2'
                  ,'Tic'
                  ,'stepCheckImportedPersonList_2'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)
  '''

  def test_CategoryTool_importCategoryFile(self):
    # tests simple use of CategoryTool_importCategoryFile script
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=makeFileUpload('import_region_category.sxc'))
    transaction.commit()
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
    transaction.commit()
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOOoImport))
  return suite
