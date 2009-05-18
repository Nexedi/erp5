##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
#          Fabien Morin <fabien.morin@gmail.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5ReportTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
import transaction
from Products.CMFCore.utils import getToolByName


class TestNewPayrollMixin(ERP5ReportTestCase):
  price_currency = 'currency_module/EUR'

  def getTitle(self):
    return "Payroll"

  def setSystemPreference(self):
    preference_tool = getToolByName(self.portal, 'portal_preferences')
    system_preference_list = preference_tool.contentValues(
        portal_type='System Preference')
    if len(system_preference_list) > 1:
      raise AttributeError('More than one System Preference, cannot test')
    if len(system_preference_list) == 0:
      system_preference = preference_tool.newContent(
          portal_type='System Preference')
    else:
      system_preference = system_preference_list[0]
    system_preference.edit(
      preferred_invoicing_resource_use_category_list = \
          ['payroll/tax'],
      preferred_normal_resource_use_category_list = \
          ['payroll/base_salary'],
      priority = 1)
    if system_preference.getPreferenceState() == 'disabled':
      system_preference.enable()

  def afterSetUp(self):
    """Prepare the test."""
    self.portal = self.getPortal()
    self.organisation_module = self.portal.organisation_module
    self.person_module = self.portal.person_module
    self.payroll_service_module = self.portal.payroll_service_module
    self.paysheet_model_module = self.portal.paysheet_model_module
    self.validateRules()
    self.createCategories()
    self.createCurrencies()

    self.login()

    # creation of payroll services
    self.urssaf_id = 'sickness_insurance'
    self.labour_id = 'labour'

    self.urssaf_slice_list = ['salary_range/france/slice_a',
                              'salary_range/france/slice_b',
                              'salary_range/france/slice_c']

    self.urssaf_share_list = ['tax_category/employee_share',
                              'tax_category/employer_share']

    self.payroll_service_organisation = self.createOrganisation(title='URSSAF')
    self.urssaf = self.createPayrollService(id=self.urssaf_id,
        title='State Insurance',
        product_line='state_insurance',
        variation_base_category_list=['tax_category', 'salary_range'],
        variation_category_list=self.urssaf_slice_list + \
                                self.urssaf_share_list,
        use='payroll/tax')

    self.labour = self.createPayrollService(id=self.labour_id,
        title='Labour',
        product_line='labour',
        use='payroll/base_salary')
    self.setSystemPreference()

  def _safeTic(self):
    """Like tic, but swallowing errors, usefull for teardown"""
    try:
      transaction.commit()
      self.tic()
    except RuntimeError:
      pass

  def beforeTearDown(self):
    """Clear everything for next test."""
    self._safeTic()
    for module in [ 'organisation_module',
                    'person_module',
                    'currency_module',
                    'payroll_service_module',
                    'paysheet_model_module',
                    'accounting_module']:
      folder = getattr(self.getPortal(), module, None)
      if folder:
        [x.unindexObject() for x in folder.objectValues()]
        self._safeTic()
        folder.manage_delObjects([x.getId() for x in folder.objectValues()])
    self._safeTic()
    # cancel remaining messages
    activity_tool = self.getPortal().portal_activities
    for message in activity_tool.getMessageList():
      activity_tool.manageCancel(message.object_path, message.method_id)
      ZopeTestCase._print('\nCancelling active message %s.%s()\n'
                          % (message.object_path, message.method_id) )
    transaction.commit()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('admin', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('admin').__of__(uf)
    newSecurityManager(None, user)

  def createCategories(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList() :
      base_cat = cat_string.split("/")[0]
      # if base_cat not exist, create it
      if getattr(self.getPortal().portal_categories, base_cat, None) == None:
        self.getPortal().portal_categories.newContent(\
                                          portal_type='Base Category',
                                          id=base_cat)
        transaction.commit()
        self.tic()
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in path.objectIds() :
          path = path.newContent(
                    portal_type='Category',
                    id=cat,
                    title=cat.replace('_', ' ').title(),)
        else:
          path = path[cat]
    transaction.commit()
    self.tic()
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ('region/europe/west/france',
            'salary_range/france/forfait',
            'salary_range/france/slice_a',
            'salary_range/france/slice_b',
            'salary_range/france/slice_c',
            'tax_category/employer_share',
            'tax_category/employee_share',
            'base_amount/deductible_tax',
            'base_amount/non_deductible_tax',
            'base_amount/bonus',
            'base_amount/base_salary',
            'base_amount/net_salary',
            'grade/worker',
            'grade/engineer',
            'quantity_unit/time/month',
            'group/demo_group',
            'product_line/base_salary',
            'product_line/payroll_tax_1',
            'product_line/payroll_tax_2',
            'use/payroll',
            'use/payroll/tax',
            'use/payroll/base_salary',
           )

  def createCurrencies(self):
    """Create some currencies.
    This script will reuse existing currencies, because we want currency ids
    to be stable, as we use them as categories.
    """
    currency_module = self.getCurrencyModule()
    if not hasattr(currency_module, 'EUR'):
      self.EUR = currency_module.newContent(
          portal_type = 'Currency',
          reference = "EUR", id = "EUR", base_unit_quantity=0.001 )
      self.USD = currency_module.newContent(
          portal_type = 'Currency',
          reference = "USD", id = "USD" )
      self.YEN = currency_module.newContent(
          portal_type = 'Currency',
          reference = "YEN", id = "YEN" )
      transaction.commit()
      self.tic()
    else:
      self.EUR = currency_module.EUR
      self.USD = currency_module.USD
      self.YEN = currency_module.YEN

  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_payroll', 'erp5_mrp', 'erp5_bpm')

  def createPerson(self, title,
      career_subordination_value=None, career_grade=None, **kw):
    """
      Create some Pesons so that we have something to feed.
    """
    person_module = self.portal.getDefaultModule(portal_type='Person')
    person = person_module.newContent(portal_type='Person')
    person.edit(
        title=title,
        career_subordination_value=career_subordination_value,
        career_grade=career_grade)
    transaction.commit()
    self.tic()
    return person

  def createOrganisation(self, title, **kw):
    organisation = self.organisation_module.newContent( \
                                   portal_type='Organisation',
                                   title=title)
    transaction.commit()
    self.tic()
    return organisation

  def createPayrollService(self, id='', title='',
      variation_base_category_list=None,
      variation_category_list=None, product_line=None, **kw):

    if variation_category_list == None:
      variation_category_list=[]
    if variation_base_category_list == None:
      variation_category_list=[]
    if hasattr(self.payroll_service_module, id):
      self.payroll_service_module.manage_delObjects([id])
    payroll_service = self.payroll_service_module.newContent(
                            title=title,
                            portal_type='Payroll Service',
                            id=id,
                            quantity_unit='time/month',
                            product_line=product_line,
                            **kw)
    payroll_service.setVariationBaseCategoryList(variation_base_category_list)
    payroll_service.setVariationCategoryList(variation_category_list)
    transaction.commit()
    self.tic()
    return payroll_service

  def createModel(self, title='',
      person_title='', person_career_grade='',
      organisation_title='',
      variation_settings_category_list=None,
      price_currency=''):
    """
      Create a model
    """
    if variation_settings_category_list == None:
      variation_settings_category_list = []
    organisation = self.createOrganisation(organisation_title)
    person = self.createPerson(title=person_title,
                               career_subordination_value=organisation,
                               career_grade=person_career_grade)
    paysheet_model = self.paysheet_model_module.newContent( \
                                portal_type='Pay Sheet Model')
    paysheet_model.edit(\
        title=title,
        variation_settings_category_list=['salary_range/france',],
        destination_section_value=organisation,
        source_section_value=person,)
    paysheet_model.setPriceCurrency(price_currency)
    transaction.commit()
    self.tic()
    return paysheet_model

class TestNewPayroll(TestNewPayrollMixin):

  def test_01_basicPaySheetCalculation(self):
    '''
      test applyTransformation method. It should create new movements
    '''
    model = self.createModel('Homer Model', 'Homer Simpson', 'worker',
        'Nexedi', [], self.price_currency)

    share_list = ['tax_category/employee_share',
                  'tax_category/employer_share']

    # add a model line
    model_line1 = model.newContent(portal_type='Pay Sheet Model Line',
                     title='Urssaf',
                     int_index=2,
                     resource_value=self.urssaf,
                     variation_category_list=share_list,
                     source_value=self.payroll_service_organisation,
                     base_application_list=[ 'base_amount/base_salary'],
                     base_contribution_list=['base_amount/deductible_tax'])
    # if the line has cells with different tax categories, new properties are
    # added to this line.
    model_line1.setResourceValue(self.urssaf)
    model_line1.setVariationCategoryList(['tax_category/employee_share',
                                          'tax_category/employer_share'])
    transaction.commit()
    self.tic()

    # create movement
    cell1 = model_line1.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'),)
    cell1.edit(price=0.1, tax_category='employee_share')

    cell2 = model_line1.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'),)
    cell2.edit(price=0.5, tax_category='employer_share')
    transaction.commit()
    self.tic()

    # create paysheet
    paysheet_module = self.portal.getDefaultModule(\
                            portal_type='Pay Sheet Transaction')
    paysheet = paysheet_module.newContent(\
        portal_type='Pay Sheet Transaction',
        title='test 1',
        specialise_value=model,
        source_section_value=model.getSourceSectionValue(),
        destination_section_value=model.getDestinationSectionValue())
    paysheet.setPriceCurrency('currency_module/EUR')
    transaction.commit()
    self.tic()

    # add an input line (the salary) in the paysheet
    labour_line = paysheet.newContent(portal_type='Pay Sheet Line',
            resource_value=self.labour,
            source_section_value=model.getSourceSectionValue(),
            destination_section_value=model.getDestinationSectionValue(),
            int_index=1,
            price=20,
            quantity=150,
            base_application_list=[],
            base_contribution_list=['base_amount/base_salary',
                                    'base_amount/gross_salary'])
    self.assertEqual(labour_line.getTotalPrice(), 3000.0)

    # check updateAggregatedMovement method return
    # XXX updateAggregatedMovement have to be tested in a generic way (not on
    # payroll but context independant). Currently, there is no test for that
    movement_dict = model.updateAggregatedAmountList(context=paysheet)
    movement_to_delete = movement_dict['movement_to_delete']
    movement_to_add = movement_dict['movement_to_add']
    self.assertEquals(len(movement_to_delete), 0)
    self.assertEquals(len(movement_to_add), 2)

    # calculate the pay sheet
    paysheet.applyTransformation()
    transaction.commit()
    self.tic()

    # check lines were created
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 2)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 2)

    # check the amount in the cells of the created paysheet lines
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceId()
      if service == self.urssaf_id:
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == self.labour_id:
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line)
    
    # check that after the line creation, updateAggregatedAmountList return
    # nothing
    movement_dict = model.updateAggregatedAmountList(context=paysheet)
    movement_to_delete = movement_dict['movement_to_delete']
    movement_to_add = movement_dict['movement_to_add']
    self.assertEquals(len(movement_to_delete), 0)
    self.assertEquals(len(movement_to_add), 0)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNewPayroll))
  return suite
