# -*- coding: utf-8 -*-
##############################################################################
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

from collections import Counter
import unittest
import os

from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5OOo.OOoUtils import OOoParser
from DateTime import DateTime
import six


def makeFilePath(name):
  return os.path.join(os.path.dirname(__file__), 'test_document', name)


class TestOOoImportMixin(ERP5TypeTestCase):
  gender_base_cat_id    = 'gender'
  function_base_cat_id  = 'function'

  def makeFileUpload(self, name):
    path = makeFilePath(name)
    fu = FileUpload(path, name)
    self.addCleanup(fu.close)
    return fu

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()
    # create browser_id_manager
    if not "browser_id_manager" in self.portal.objectIds():
      self.portal.manage_addProduct['Sessions'].constructBrowserIdManager()

    # We create categories needed
    # For testing file whith column corresponding to category
    portal_categories = self.getCategoryTool()

    gender_bc = self.gender_base_cat_id
    if gender_bc not in portal_categories.objectIds():
      portal_categories.newContent(portal_type='Base Category', id=gender_bc)
    if 'male' not in portal_categories[gender_bc]:
      portal_categories[gender_bc].newContent(id='male', portal_type='Category', title='Male')
    if 'female' not in portal_categories[gender_bc]:
      portal_categories[gender_bc].newContent(id='female', portal_type='Category', title='Female')

    function_bc = self.function_base_cat_id
    if function_bc not in portal_categories.objectIds():
      portal_categories.newContent(portal_type='Base Category', id=function_bc)
    if 'director' not in portal_categories[function_bc]:
      portal_categories[function_bc].newContent(id='director', portal_type='Category', title='Director')
    if 'manager' not in portal_categories[function_bc]:
      portal_categories[function_bc].newContent(id='manager', portal_type='Category', title='Manager')

    self.portal.portal_caches.clearCache()
    self.tic()

  def beforeTearDown(self):
    self.tic()
    for parent in [
        self.portal.currency_module,
        self.portal.organisation_module,
        self.portal.person_module,
        self.portal.portal_categories.function,
        self.portal.portal_categories.gender,
        self.portal.portal_categories.region,
        ]:
      parent.setLastId('0')
      parent.deleteContent(list(parent.objectIds()))
    self.tic()

class TestOOoImport(TestOOoImportMixin):
  """
    ERP5  test import object list from OOo Document
  """

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

  ##################################
  ##  Basic steps
  ##################################
  def stepImportRawDataFile(self, sequence=None, sequence_list=None, **kw):
    f = self.makeFileUpload('import_data_list.ods')
    person_module = self.getPortal().person_module
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
    activity_count_by_method_dict = Counter(
      x.method_id
      for x in self.getPortal().portal_activities.getMessageList()
    )
    self.assertEqual(
      101,
      activity_count_by_method_dict['Base_importFileLineDefaultScript'],
      activity_count_by_method_dict,
    )

  def stepCheckImportedPersonList(self, sequence=None, sequence_list=None,
                                  num=101, **kw):
    person_list = self.getPortal().person_module.objectValues()
    self.assertEqual(
      sorted(['John Doe %s' % (i) for i in range(num)]),
      sorted([person_list[i].getTitle() for i in range(num)]))
    self.assertEqual(
      sorted(['John' for i in range(num)]),
      sorted([person_list[i].getFirstName() for i in range(num)]))
    self.assertEqual(
      sorted(['Doe %s' % (i) for i in range(num)]),
      sorted([person_list[i].getLastName() for i in range(num)]))
    self.assertEqual(
      sorted(['john.doe%s@foo.com' % (i) for i in range(num)]),
      sorted([person_list[i].getDefaultEmailText() for i in range(num)]))

  def stepCheckImportedPersonListBlank(self, sequence=None, sequence_list=None, **kw):
    return self.stepCheckImportedPersonList(sequence=sequence,
                                            sequence_list=sequence_list, **kw)

  def stepCheckImportedPersonListCategory(self, sequence=None, sequence_list=None, **kw):
    num = 10
    person_list = self.getPortal().person_module.objectValues()
    self.assertEqual(
      ['John'] * num,
      sorted([person_list[i].getTitle() for i in range(num)]))
    self.assertEqual(
      sorted(['John' for i in range(num)]),
      sorted([person_list[i].getFirstName() for i in range(num)]))
    self.assertEqual(
      sorted(['male' for i in range(num)]),
      sorted([person_list[i].getGender() for i in range(num)]))
    self.assertEqual(
      sorted(['director' for i in range(num)]),
      sorted([person_list[i].getFunction() for i in range(num)]))
    self.assertEqual(
      sorted(['europe/france' for i in range(num)]),
      sorted([person_list[i].getRegion() for i in range(num)]))
    self.assertEqual(
      sorted(['France' for i in range(num)]),
      sorted([person_list[i].getRegionTitle() for i in range(num)]))

  def stepCheckAuthorImportedPersonList(self, sequence=None, sequence_list=None, **kw):
    return self.stepCheckImportedPersonListCategory(sequence=sequence,
                                                    sequence_list=sequence_list,
                                                    **kw)

  def stepCheckImportedPersonListFreeText(self, sequence=None, sequence_list=None, **kw):
    num = 10
    person_list = self.getPortal().person_module.objectValues()
    self.assertEqual(
      ['John'] * num,
      sorted([person_list[i].getTitle() for i in range(num)]))
    self.assertEqual(
      sorted(['John' for i in range(num)]),
      sorted([person_list[i].getFirstName() for i in range(num)]))
    self.assertEqual(
      sorted(['male' for i in range(num)]),
      sorted([person_list[i].getGenderFreeText() for i in range(num)]))
    self.assertEqual(
      sorted(['Director' for i in range(num)]),
      sorted([person_list[i].getFunctionFreeText() for i in range(num)]))

  def stepCheckImportedPersonListAccentuated(self, sequence=None, sequence_list=None, **kw):
    num = 10
    person_list = self.getPortal().person_module.objectValues()
    self.assertEqual(
      ['John'] * num,
      sorted([person_list[i].getTitle() for i in range(num)]))
    self.assertEqual(
      sorted(['John' for i in range(num)]),
      sorted([person_list[i].getFirstName() for i in range(num)]))
    self.assertEqual(
      sorted(['male' for i in range(num)]),
      sorted([person_list[i].getGender() for i in range(num)]))
    self.assertEqual(
      sorted(['director' for i in range(num)]),
      sorted([person_list[i].getFunction() for i in range(num)]))

  def stepCheckXLSImportedPersonList(self, sequence=None, sequence_list=None, **kw):
    return self.stepCheckImportedPersonList(sequence=sequence,
                                            sequence_list=sequence_list,
                                            num=10, **kw)

  def stepCheckImportedPersonListWithDates(self, sequence=None, sequence_list=None, **kw):
    num = 10
    person_list = self.getPortal().person_module.objectValues()
    self.assertEqual(
      ['John'] * num,
      sorted([person_list[i].getTitle() for i in range(num)]))
    self.assertEqual(
      sorted(['John' for i in range(num)]),
      sorted([person_list[i].getFirstName() for i in range(num)]))
    self.assertEqual(
      sorted(['male' for i in range(num)]),
      sorted([person_list[i].getGender() for i in range(num)]))
    self.assertEqual(
      sorted([DateTime('2008-02-%02d' % (i+1)) for i in range(num)]),
      sorted([person_list[i].getStartDate() for i in range(num)]))

  def stepCheckImportFloatsAndPercentage(self, sequence=None, sequence_list=None, **kw):
    num = 10
    currency_module = self.getPortal().currency_module
    currency_list = [currency_module[str(i + 1)] \
                   for i in range(num)]
    self.assertEqual(
      sorted(['Currency %s' % (i) for i in range(num)]),
      sorted([currency_list[i].getTitle() for i in range(num)]))
    self.assertEqual(
      sorted([1000.3 + i for i in range(num)]),
      sorted([currency_list[i].getHeightQuantity() for i in range(num)]))

  def stepCheckImportedPersonList_1(self, sequence=None, sequence_list=None, **kw):
    return self.stepCheckImportedPersonList(sequence=sequence,
                                            sequence_list=sequence_list,
                                            num=1000, **kw)

  def stepCheckImportedPersonList_2(self, sequence=None, sequence_list=None, **kw):
    return self.stepCheckImportedPersonList(sequence=sequence,
                                            sequence_list=sequence_list,
                                            num=10000, **kw)

  def stepCheckImportedOrganisationList(self, sequence=None, sequence_list=None, **kw):
    num = 10
    organisation_module = self.getPortal().organisation_module
    organisation_list = [organisation_module[str(i + 1)] \
                   for i in range(num)]
    self.assertEqual(
      sorted(['Foo Organisation %s' % (i) for i in range(num)]),
      sorted([organisation_list[i].getTitle() for i in range(num)]))
    self.assertEqual(
      sorted(['Description organisation %s' % (i) for i in range(num)]),
      sorted([organisation_list[i].getDescription() for i in range(num)]))
    self.assertEqual(
      sorted(['+(0)-1234567%s' % i for i in range(num)]),
      sorted([organisation_list[i].getTelephoneText() for i in range(num)]))
    self.assertEqual(
      sorted(['org%s@foo.com' % i for i in range(num)]),
      sorted([organisation_list[i].getEmailText() for i in range(num)]))

  def stepImportFileNoMapping(self, sequence=None, sequence_list=None, **kw):
    f = self.makeFileUpload('import_data_list.ods')

    person_module = self.getPortal().person_module
    listbox = (
    { 'listbox_key': '001',
      'portal_type_property_list': ''},
    { 'listbox_key': '002',
      'portal_type_property_list': ''},
    { 'listbox_key': '003',
      'portal_type_property_list': ''},
    { 'listbox_key': '004',
      'portal_type_property_list': ''},)
    redirect = person_module.Base_importFile(import_file=f, listbox=listbox)
    self.assertTrue(redirect.endswith(
      'portal_status_message=Please%20Define%20a%20mapping.'))

  def stepImportFileWithBlankLine(self, sequence=None, sequence_list=None, **kw):
    f = self.makeFileUpload('import_data_list_blank_line.ods')
    person_module = self.getPortal().person_module
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
    f = self.makeFileUpload('import_data_with_categories.ods')
    # create some regions
    region = self.portal.portal_categories.region
    europe = region.newContent(portal_type='Category',
                      title='Europe',
                      id='europe')
    europe.newContent(portal_type='Category',
                      title='France',
                      id='france')

    person_module = self.getPortal().person_module
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.gender'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.function'},
    { 'listbox_key': '005',
      'portal_type_property_list':'Person.region'}
    )
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportFileWithDates(self, sequence=None, sequence_list=None, **kw):
    f = self.makeFileUpload('import_data_with_dates.ods')
    person_module = self.getPortal().person_module
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
    f = self.makeFileUpload('import_float_and_percentage.ods')
    currency_module = self.getPortal().currency_module
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Currency.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Currency.height_quantity'}
    )
    currency_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportOrganisation(self, sequence=None, sequence_list=None, **kw):
    f = self.makeFileUpload('import_organisation_list.ods')
    organisation_module = self.getPortal().organisation_module
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
    # create some regions
    region = self.portal.portal_categories.region
    europe = region.newContent(portal_type='Category',
                      title='Europe',
                      id='europe')
    europe.newContent(portal_type='Category',
                      title='France',
                      id='france')

    user_name = 'author'
    user_folder = self.portal.acl_users
    user_folder._doAddUser(user_name, '', ['Author', 'Member'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

    f = self.makeFileUpload('import_data_with_categories.ods')
    person_module = self.getPortal().person_module
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.gender'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.function'},
    { 'listbox_key': '005',
      'portal_type_property_list':'Person.region'}
    )
    person_module.Base_importFile(import_file=f, listbox=listbox)

  def stepImportFileWithFreeText(self, sequence=None, sequence_list=None, **kw):
    f = self.makeFileUpload('import_data_with_categories.ods')
    person_module = self.getPortal().person_module
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
    f = self.makeFileUpload('import_data_accentuated_text.ods')
    person_module = self.getPortal().person_module
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
    f = self.makeFileUpload('import_data_list.xls')
    person_module = self.getPortal().person_module
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
    f = self.makeFileUpload('import_data_big_file_1.ods')
    person_module = self.getPortal().person_module
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
    f = self.makeFileUpload('import_data_big_file_2.ods')
    person_module = self.getPortal().person_module
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
  def test_01_ImportFileLine(self):
    # Simulate import of OOo file Base_importFile for Person Module.
    sequence_list = SequenceList()
    step_list = [ 'stepImportRawDataFile'
                 ,'stepCheckActivitiesCount'
                 ,'Tic'
                 ,'stepCheckImportedPersonList'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_ImportFileBlankLine(self):
    #Simulate import of an OOo file with blank lines.
    sequence_list = SequenceList()
    step_list = [  'stepImportFileWithBlankLine'
                  ,'Tic'
                  ,'stepCheckImportedPersonListBlank'
                 ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_03_ImportNoMapping(self):
    sequence_list = SequenceList()
    step_list = [ 'stepImportFileNoMapping'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_04_ImportFileWithCategory(self):
    sequence_list = SequenceList()
    step_list = [  'stepImportFileWithCategory'
                  ,'Tic'
                  ,'stepCheckImportedPersonListCategory'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_05_ImportOrganisation(self):
    sequence_list = SequenceList()
    step_list = [  'stepImportOrganisation'
                  ,'Tic'
                  ,'stepCheckImportedOrganisationList'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_06_AuthorImportFile(self):
    sequence_list = SequenceList()
    step_list = [  'stepAuthorImportFile'
                  ,'Tic'
                  ,'stepCheckAuthorImportedPersonList'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_07_ImportFileWithFreeText(self):
    sequence_list = SequenceList()
    step_list = [  'stepImportFileWithFreeText'
                  ,'Tic'
                  ,'stepCheckImportedPersonListFreeText'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_08_ImportFileWithAccentuatedText(self):
    sequence_list = SequenceList()
    step_list = [  'stepImportFileWithAccentuatedText'
                  ,'Tic'
                  ,'stepCheckImportedPersonListAccentuated'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_09_ImportXLSFile(self):
    sequence_list = SequenceList()
    step_list = [ 'stepImportXLSFile'
                 ,'Tic'
                 ,'stepCheckXLSImportedPersonList'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_10_ImportFileWithDates(self):
    sequence_list = SequenceList()
    step_list = [ 'stepImportFileWithDates'
                 ,'Tic'
                 ,'stepCheckImportedPersonListWithDates'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_11_ImportFloatAndPercentage(self):
    sequence_list = SequenceList()
    step_list = [ 'stepImportFloatsAndPercentage'
                 ,'Tic'
                 ,'stepCheckImportFloatsAndPercentage'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_12_ImportBigFile_1(self):
    sequence_list = SequenceList()
    step_list = [  'stepImportBigFile_1'
                  ,'Tic'
                  ,'stepCheckImportedPersonList_1'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

#  def test_12_ImportBigFile_2(self):
#    sequence_list = SequenceList()
#    step_list = [  'stepImportBigFile_2'
#                  ,'Tic'
#                  ,'stepCheckImportedPersonList_2'
#                ]
#    sequence_string = ' '.join(step_list)
#    sequence_list.addSequenceString(sequence_string)
#    sequence_list.play(self)

  # CategoryTool_importCategoryFile tests
  def test_CategoryTool_importCategoryFile(self):
    # tests simple use of CategoryTool_importCategoryFile script
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category.sxc'))
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(2, len(region))
    self.assertIn('europe', region.objectIds())
    self.assertIn('germany', region.europe.objectIds())
    self.assertIn('france', region.europe.objectIds())
    france = region.europe.france
    self.assertEqual('France', france.getTitle())
    self.assertTrue(france.hasProperty('title'))
    self.assertEqual('A Country', france.getDescription())
    self.assertEqual('FR', france.getCodification())
    self.assertEqual(1, france.getIntIndex())

  def test_CategoryTool_importCategoryFileDeletionSupport(self):
    # tests simple use of CategoryTool_importCategoryFile script
    region = self.portal.portal_categories.region
    region.newContent(id='dummy_region')
    self.tic()
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category.sxc'),
        existing_category_list='delete')
    self.tic()
    self.assertEqual(2, len(region))
    self.assertIn('europe', region.objectIds())
    self.assertIn('germany', region.europe.objectIds())
    self.assertIn('france', region.europe.objectIds())
    france = region.europe.france
    self.assertEqual('France', france.getTitle())
    self.assertTrue(france.hasProperty('title'))
    self.assertEqual('A Country', france.getDescription())
    self.assertEqual('FR', france.getCodification())
    self.assertEqual(1, france.getIntIndex())

  def test_CategoryTool_importCategoryFileDeletionSupportForCategoriesInUse(self):
    region = self.portal.portal_categories.region
    region.newContent(id='dummy_region')
    self.portal.person_module.newContent(
        portal_type='Person',
        region_value=region.dummy_region
    )
    self.tic()
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category.sxc'),
        existing_category_list='delete')
    self.tic()
    self.assertEqual(3, len(region))
    # dummy region is in used so it was not deleted
    self.assertIn('dummy_region', region.objectIds())

  def test_CategoryTool_importCategoryFileForcedDeletionSupportForCategoriesInUse(self):
    region = self.portal.portal_categories.region
    region.newContent(id='dummy_region')
    self.portal.person_module.newContent(
        portal_type='Person',
        region_value=region.dummy_region
    )
    self.tic()
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category.sxc'),
        existing_category_list='force_delete')
    self.tic()
    self.assertEqual(2, len(region))
    self.assertNotIn('dummy_region', region.objectIds())

  def test_CategoryTool_importCategoryFileExpirationSupport(self):
    # tests simple use of CategoryTool_importCategoryFile script
    region = self.portal.portal_categories.region
    region.newContent(id='dummy_region')
    self.tic()
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category.sxc'),
        existing_category_list='expire')
    self.tic()
    self.assertEqual(3, len(region))
    self.assertIn('dummy_region', region.objectIds())
    self.assertIn('europe', region.objectIds())
    self.assertIn('germany', region.europe.objectIds())
    self.assertIn('france', region.europe.objectIds())
    france = region.europe.france
    self.assertEqual('France', france.getTitle())
    self.assertTrue(france.hasProperty('title'))
    self.assertEqual('A Country', france.getDescription())
    self.assertEqual('FR', france.getCodification())
    self.assertEqual(1, france.getIntIndex())

  def test_CategoryTool_importCategoryFileXLS(self):
    # tests that CategoryTool_importCategoryFile supports .xls files
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category.xls'))
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(2, len(region))
    self.assertIn('europe', region.objectIds())
    self.assertIn('germany', region.europe.objectIds())
    self.assertIn('france', region.europe.objectIds())
    france = region.europe.france
    self.assertEqual('France', france.getTitle())
    self.assertEqual('A Country', france.getDescription())
    self.assertEqual('FR', france.getCodification())
    self.assertEqual(1, france.getIntIndex())

  def test_CategoryTool_importCategoryFile_PathStars(self):
    # tests CategoryTool_importCategoryFile with * in the paths columns
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category_path_stars.sxc'))
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(2, len(region))
    self.assertIn('europe', region.objectIds())
    self.assertIn('germany', region.europe.objectIds())
    self.assertIn('france', region.europe.objectIds())
    france = region.europe.france
    self.assertEqual('France', france.getTitle())
    self.assertEqual('A Country', france.getDescription())
    self.assertEqual('FR', france.getCodification())
    self.assertEqual(1, france.getIntIndex())

  def test_CategoryTool_importCategoryFile_PathStars_noID(self):
    # tests CategoryTool_importCategoryFile with * in the paths columns, and no
    # ID column, and non ascii titles
    self.portal.portal_categories.CategoryTool_importCategoryFile(
            import_file=self.makeFileUpload(
              'import_region_category_path_stars_non_ascii.sxc'))
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(2, len(region))
    self.assertIn('europe', region.objectIds())
    self.assertIn('germany', region.europe.objectIds())
    self.assertIn('france', region.europe.objectIds())
    france = region.europe.france
    self.assertEqual('Frànce', france.getTitle())
    self.assertEqual('A Country', france.getDescription())
    self.assertEqual('FR', france.getCodification())
    self.assertEqual(1, france.getIntIndex())

  def test_CategoryTool_importCategoryFile_DuplicateIds(self):
    # tests CategoryTool_importCategoryFile when a document contain same
    # categories ID at different level (a good candidate for an acquisition
    # bug)
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category_duplicate_ids.sxc'))
    self.tic()
    region = self.portal.portal_categories.region
    self.assertEqual(1, len(region))
    self.assertEqual(['europe'], list(region.objectIds()))
    self.assertEqual(['france'], list(region.europe.objectIds()))
    self.assertEqual(['europe'], list(region.europe.france.objectIds()))
    self.assertEqual(['france'], list(region.europe.france.europe.objectIds()))
    self.assertEqual([], list(region.europe.france.europe.france.objectIds()))

  # Base_getCategoriesSpreadSheetMapping tests
  def test_Base_getCategoriesSpreadSheetMapping(self):
    # test structure returned by Base_getCategoriesSpreadSheetMapping
    mapping = self.portal.Base_getCategoriesSpreadSheetMapping(
        import_file=self.makeFileUpload('import_region_category.sxc'))
    self.assertTrue(isinstance(mapping, dict))
    self.assertEqual(['region'], list(mapping.keys()))
    region = mapping['region']
    self.assertTrue(isinstance(region, list))
    self.assertEqual(6, len(region))
    # base category is contained in the list
    self.assertEqual(dict(path='region',
                           title='region'),
                      region[0])
    self.assertEqual(dict(path='region/europe',
                           short_title='Europe',
                           title='Europe'),
                      region[1])
    self.assertEqual(dict(codification='FR',
                           description='A Country',
                           int_index='1',
                           path='region/europe/france',
                           short_title='France',
                           title='France'),
                      region[2])
    # strings are encoded in UTF8
    self.assertTrue(isinstance(region[1]['title'], str))
    self.assertTrue(isinstance(region[1]['path'], str))
    for k in region[1].keys():
      self.assertTrue(isinstance(k, str), (k, type(k)))

  def test_Base_getCategoriesSpreadSheetMapping_DuplicateIdsAtSameLevel(self):
    # tests Base_getCategoriesSpreadSheetMapping when a document contain same
    # categories ID at the same level, in that case, a ValueError is raised
    import_file = self.makeFileUpload(
        'import_region_category_duplicate_ids_same_level.sxc')
    try:
      self.portal.portal_categories.Base_getCategoriesSpreadSheetMapping(
             import_file=import_file)
    except ValueError as error:
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

    import_file = self.makeFileUpload(
        'import_region_category_duplicate_ids_same_level.sxc')
    self.portal.portal_categories.Base_getCategoriesSpreadSheetMapping(import_file,
         invalid_spreadsheet_error_handler=on_invalid_spreadsheet)

    self.assertEqual(1, len(message_list))
    self.assertIn('france', str(message_list[0]))

  def test_Base_getCategoriesSpreadSheetMapping_WrongHierarchy(self):
    # tests Base_getCategoriesSpreadSheetMapping when the spreadsheet has an
    # invalid hierarchy (#788)
    import_file = self.makeFileUpload(
        'import_region_category_wrong_hierarchy.sxc')
    try:
      self.portal.portal_categories.Base_getCategoriesSpreadSheetMapping(
             import_file=import_file)
    except ValueError as error:
      # 'wrong_hierarchy' is the ID of the category where the problem happens
      self.assertTrue('wrong_hierarchy' in str(error), str(error))
    else:
      self.fail('ValueError not raised')

  def test_Base_getCategoriesSpreadSheetMapping_MultiplePaths(self):
    # If multiple paths is defined (for instance more than one * in paths
    # columns), then it should be an error and the error must be reported
    import_file = self.makeFileUpload(
        'import_region_category_multiple_paths.ods')
    try:
      self.portal.portal_categories.Base_getCategoriesSpreadSheetMapping(
             import_file=import_file)
    except ValueError as error:
      self.assertTrue('More that one path is defined' in str(error), str(error))
    else:
      self.fail('ValueError not raised')

  def test_Base_getCategoriesSpreadSheetMapping_Id_is_reserved_property_name(self):
    # tests Base_getCategoriesSpreadSheetMapping reserved property name are only test for path column, not all.
    import_file = self.makeFileUpload(
        'import_region_category_with_reserved_id_in_title.sxc')
    mapping = self.portal.portal_categories.Base_getCategoriesSpreadSheetMapping(
             import_file=import_file)
    self.assertTrue(isinstance(mapping, dict))
    self.assertEqual(['region'], list(mapping.keys()))
    region = mapping['region']
    self.assertTrue(isinstance(region, list))
    self.assertEqual(7, len(region))
    # Check that category can have a reserved property as title
    self.assertEqual(dict(codification='codification',
                           description='codification',
                           path='region/antartica',
                           short_title='codification',
                           title='codification'),
                      region[6])

    # Check that category cannot have a Base Category nor Category property
    # id/storage_id as their ID
    message_set = set()
    def on_invalid_spreadsheet(message):
      message_set.add(message.translate())
      # To continue processing and get all the errors
      return True

    self.portal.portal_categories.Base_getCategoriesSpreadSheetMapping(
      import_file=self.makeFileUpload('import_category_with_reserved_id_in_id.sxc'),
      invalid_spreadsheet_error_handler=on_invalid_spreadsheet)

    self.assertEqual(message_set, {
           "The ID source_title in region at line 2 is invalid, "
           "it's a reserved property name",
           "The ID source_title in region at line 4 is invalid, "
           "it's a reserved property name",
           "The ID fallback_base_category_list in region at line 5 is invalid, "
           "it's a reserved property name",
           "The ID fallback_base_category_list in region at line 6 is invalid, "
           "it's a reserved property name",
           "The ID default_source_reference in region at line 7 is invalid, "
           "it's a reserved property name"})

  def test_BigSpreadSheet_can_be_parsed(self,):
    """Test than OOoimport can parse a file with more than 40000 lines
    """
    parser = OOoParser()
    with open(makeFilePath('import_big_spreadsheet.ods'), 'rb') as f:
      parser.openFile(f)
    mapping = parser.getSpreadsheetsMapping()
    not_ok = 1
    for spread, values in six.iteritems(mapping):
      self.assertEqual(len(values), 41001)
      not_ok = 0
    if not_ok:
      self.fail('Spreadsheet not read!')

class TestOOoImportWeb(TestOOoImportMixin):
  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 Site - OOo File importing (with web)"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base', 'erp5_web', 'erp5_ooo_import')

  def test_CategoryTool_importCategoryFileExpirationSupport(self):
    """Import category file with expiration request, and do it again to be
    sure that expired categories will not be expired again."""
    region = self.portal.portal_categories.region
    region.newContent(id='dummy_region')
    dummy_expired_region = region.newContent(id='dummy_expired_region')
    dummy_expired_region.expire()
    self.tic()
    self.portal.portal_categories.CategoryTool_importCategoryFile(
        import_file=self.makeFileUpload('import_region_category.sxc'),
        existing_category_list='expire')
    self.tic()
    self.assertEqual(4, len(region))
    self.assertIn('dummy_region', region.objectIds())
    self.assertEqual(region.dummy_region.getValidationState(), 'expired')
    self.assertIn('dummy_expired_region', region.objectIds())
    self.assertEqual(region.dummy_expired_region.getValidationState(), 'expired')
    self.assertIn('europe', region.objectIds())
    self.assertIn('germany', region.europe.objectIds())
    self.assertIn('france', region.europe.objectIds())
    france = region.europe.france
    self.assertEqual('France', france.getTitle())
    self.assertTrue(france.hasProperty('title'))
    self.assertEqual('A Country', france.getDescription())
    self.assertEqual('FR', france.getCodification())
    self.assertEqual(1, france.getIntIndex())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOOoImport))
  suite.addTest(unittest.makeSuite(TestOOoImportWeb))
  return suite
