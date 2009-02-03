##############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
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
"""
  Tests paysheet creation using paysheet model.

TODO:
  - review naming of new methods
  - in the test test_04_paySheetCalculation, add sub_object (annotation_line,
  ratio_line and payment conditioni), and verify that before the script
  'PaySheetTransaction_applyModel' is called, subobjects are not in the
  paysheet, and after that there are copied in.
  - use ratio settings and test it (there is a method getRatioQuantityList, see
  the file Document/PaySheetTransaction.py)
  - test with bonus which participate on the base_salary and see if the
  contribution are applied on the real base_salary or on the base_salary + bonus
  (it should).

WARNING:
  - current API naming may change although model should be stable.

"""

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5ReportTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from DateTime import DateTime

class TestPayrollMixin(ERP5ReportTestCase):

  paysheet_model_portal_type        = 'Pay Sheet Model'
  paysheet_model_line_portal_type   = 'Pay Sheet Model Line'
  paysheet_transaction_portal_type  = 'Pay Sheet Transaction'
  paysheet_line_portal_type         = 'Pay Sheet Line'
  payroll_service_portal_type       = 'Payroll Service'
  currency_portal_type              = 'Currency'
  person_portal_type                = 'Person'
  organisation_portal_type          = 'Organisation'


  default_region                    = 'europe/west/france'
  france_settings_forfait           = 'france/forfait'
  france_settings_slice_a           = 'france/tranche_a'
  france_settings_slice_b           = 'france/tranche_b'
  france_settings_slice_c           = 'france/tranche_c'
  tax_category_employer_share       = 'employer_share'
  tax_category_employee_share       = 'employee_share'
  base_amount_deductible_tax        = 'deductible_tax'
  base_amount_non_deductible_tax    = 'deductible_tax'
  base_amount_bonus                 = 'bonus'
  base_amount_base_salary           = 'base_salary'
  grade_worker                      = 'worker'
  grade_engineer                    = 'engineer'

  plafond = 2682.0

  model = None
  model_id                          = 'model_one'
  model_title                       = 'Model One'
  person_id                         = 'one'
  person_title                      = 'One'
  person_career_grade               = 'worker'
  organisation_id                   = 'company_one'
  organisation_title                = 'Company One'
  variation_settings_category_list  = ['salary_range/france',]
  price_currency                    = 'currency_module/EUR'

  def getTitle(self):
    return "Payroll"

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

    self.model = self.createModel(self.model_id, self.model_title,
        self.person_id, self.person_title, self.person_career_grade,
        self.organisation_id, self.organisation_title,
        self.variation_settings_category_list, self.price_currency)

    self.login()

    # creation of payroll services
    self.urssaf_id = 'sickness_insurance'
    self.labour_id = 'labour'

    self.urssaf_slice_list = ['salary_range/'+self.france_settings_slice_a,
                              'salary_range/'+self.france_settings_slice_b,
                              'salary_range/'+self.france_settings_slice_c]

    self.urssaf_share_list = ['tax_category/'+self.tax_category_employee_share,
                              'tax_category/'+self.tax_category_employer_share]

    self.salary_slice_list = ['salary_range/'+self.france_settings_forfait,]
    self.salary_share_list = ['tax_category/'+self.tax_category_employee_share,]


    self.payroll_service_organisation = self.createOrganisation(
                                          id='urssaf', title='URSSAF')
    self.urssaf = self.createPayrollService(id=self.urssaf_id,
        title='State Insurance',
        product_line='state_insurance',
        variation_base_category_list=['tax_category', 'salary_range'],
        variation_category_list=self.urssaf_slice_list + \
                                self.urssaf_share_list)

    self.labour = self.createPayrollService(id=self.labour_id,
        title='Labour',
        product_line='labour',
        variation_base_category_list=['tax_category', 'salary_range'],
        variation_category_list=self.salary_slice_list +\
                                self.salary_share_list)

  def _safeTic(self):
    """Like tic, but swallowing errors, usefull for teardown"""
    try:
      get_transaction().commit()
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
    get_transaction().commit()

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
        get_transaction().commit()
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
    get_transaction().commit()
    self.tic()
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ('region/%s' % self.default_region,
            'salary_range/%s' % self.france_settings_forfait,
            'salary_range/%s' % self.france_settings_slice_a,
            'salary_range/%s' % self.france_settings_slice_b,
            'salary_range/%s' % self.france_settings_slice_c,
            'tax_category/%s' % self.tax_category_employer_share,
            'tax_category/%s' % self.tax_category_employee_share,
            'base_amount/%s' % self.base_amount_deductible_tax,
            'base_amount/%s' % self.base_amount_non_deductible_tax,
            'base_amount/%s' % self.base_amount_bonus,
            'base_amount/%s' % self.base_amount_base_salary,
            'base_amount/net_salary',
            'grade/%s' % self.grade_worker,
            'grade/%s' % self.grade_engineer,
            'quantity_unit/time/month',
            'group/demo_group',
            'product_line/base_salary',
            'product_line/payroll_tax_1',
            'product_line/payroll_tax_2',
           )

  def createCurrencies(self):
    """Create some currencies.
    This script will reuse existing currencies, because we want currency ids
    to be stable, as we use them as categories.
    """
    currency_module = self.getCurrencyModule()
    if not hasattr(currency_module, 'EUR'):
      self.EUR = currency_module.newContent(
          portal_type = self.currency_portal_type,
          reference = "EUR", id = "EUR", base_unit_quantity=0.001 )
      self.USD = currency_module.newContent(
          portal_type = self.currency_portal_type,
          reference = "USD", id = "USD" )
      self.YEN = currency_module.newContent(
          portal_type = self.currency_portal_type,
          reference = "YEN", id = "YEN" )
      get_transaction().commit()
      self.tic()
    else:
      self.EUR = currency_module.EUR
      self.USD = currency_module.USD
      self.YEN = currency_module.YEN

  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_payroll', )

  def createPerson(self, id='one', title='One',
      career_subordination_value=None, career_grade=None, **kw):
    """
      Create some Pesons so that we have something to feed.
    """
    person_module = self.portal.getDefaultModule(portal_type=\
                                                 self.person_portal_type)
    if hasattr(person_module, id):
      person_module.manage_delObjects([id])
    person = person_module.newContent(portal_type=self.person_portal_type,
                                      id=id)
    person.edit(
        title=title,
        career_subordination_value=career_subordination_value,
        career_grade=career_grade,
               )
    get_transaction().commit()
    self.tic()
    return person

  def createOrganisation(self, id='company_one', title='Company One', **kw):
    if hasattr(self.organisation_module, id):
      self.organisation_module.manage_delObjects([id])
    organisation = self.organisation_module.newContent( \
                                   portal_type=self.organisation_portal_type,
                                   id=id,
                                   title=title)
    get_transaction().commit()
    self.tic()
    return organisation

  def createPayrollService(self, id='', title='',
      variation_base_category_list=None,
      variation_category_list=None, product_line=None, **kw):

    payroll_service_portal_type = 'Payroll Service'
    payroll_service_module = self.portal.getDefaultModule(\
                                    portal_type=payroll_service_portal_type)

    if variation_category_list == None:
      variation_category_list=[]
    if variation_base_category_list == None:
      variation_category_list=[]
    if hasattr(payroll_service_module, id):
      payroll_service_module.manage_delObjects([id])

    payroll_service = payroll_service_module.newContent(
                            title=title,
                            portal_type=self.payroll_service_portal_type,
                            id=id,
                            quantity_unit='time/month',
                            product_line=product_line)
    payroll_service.setVariationBaseCategoryList(variation_base_category_list)
    payroll_service.setVariationCategoryList(variation_category_list)
    get_transaction().commit()
    self.tic()
    return payroll_service

  def createModel(self, id, title='', person_id='',
      person_title='', person_career_grade='',
      organisation_id='', organisation_title='',
      variation_settings_category_list=None,
      price_currency=''):
    """
      Create a model
    """
    if variation_settings_category_list == None:
      variation_settings_category_list = []

    organisation = self.createOrganisation(organisation_id, organisation_title)
    person = self.createPerson(id=person_id, title=person_title,
                               career_subordination_value=organisation,
                               career_grade=person_career_grade)

    if hasattr(self.paysheet_model_module, id):
      self.paysheet_model_module.manage_delObjects([id])
    paysheet_model = self.paysheet_model_module.newContent( \
                                portal_type=self.paysheet_model_portal_type,
                                id=id)
    paysheet_model.edit(\
        title=title,
        variation_settings_category_list=variation_settings_category_list,
        destination_section_value=organisation,
        source_section_value=person,)
    paysheet_model.setPriceCurrency(price_currency)
    get_transaction().commit()
    self.tic()

    return paysheet_model

  def addSlice(self, model, slice, min_value, max_value, base_id='cell'):
    '''
      add a new slice in the model
    '''
    slice_value = model.newCell(slice, portal_type='Pay Sheet Model Slice',
        base_id=base_id)
    slice_value.setQuantityRangeMax(max_value)
    slice_value.setQuantityRangeMin(min_value)
    get_transaction().commit()
    self.tic()
    return slice_value

  def addAllSlices(self, model):
    '''
      create all usefull slices with min and max values
    '''
    slice_list = []
    slice_list.append(self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_forfait, 0, 9999999999999))
    slice_list.append(self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_a, 0, self.plafond))
    slice_list.append(self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_b, self.plafond, self.plafond*4))
    slice_list.append(self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_c, self.plafond*4, self.plafond*8))
    return slice_list

  def createModelLine(self,
                      model,
                      id,
                      variation_category_list,
                      resource,
                      slice_list,
                      share_list,
                      values,
                      editable=False,
                      source_value=None,
                      base_application_list=[],
                      base_contribution_list=[]):
    '''
      test the function addModelLine and test if the model line has been
      well created.
      explaination for values :
      if slice_list is ('slice_a', 'slice_b') and share list is ('employer',
      'employee') and if you want to put 100 % of 1000 for slice_a for the
      employee and employer, and 50% of the base_application for slice_b
      employer and and 2000 for slice_b employee, the value list will look
      like this :
      values = [[[1000, 1], [1000, 1]], [[2000, None], [None, 0.5]]]

      next, two representations to well understand :

       'employee_share', 'employer_share'
      [[  1470, None  ], [  2100, None  ]]
       'salary_range/france/forfait'

    'employee_share',  'employer_share'   'employee_share',  'employer_share'
[ [   None, 0.01   ], [   None, 0.02   ],[   None, 0.01  ], [   None, 0.02  ] ]
'salary_range/france/tranche_a''salary_range/france/tranche_b'
    '''

    # verify if category used in this model line are selected in the resource
    resource_list = resource.getVariationCategoryList(base=1)
    msg='%r != %r' % (resource_list, variation_category_list)
    for i in variation_category_list:
      self.failUnless(i in resource_list, msg)

    if hasattr(model, id):
      model.manage_delObjects([id])
    model_line = model.newContent(
                        portal_type=self.paysheet_model_line_portal_type,
                        id=id,
                        resource_value=resource,
                        source_value=source_value,
                        editable=editable,
                        base_application_list=base_application_list,
                        base_contribution_list=base_contribution_list,
                        variation_category_list=variation_category_list,)
    get_transaction().commit()
    self.tic()

    # put values in Model Line cells
    model_line.updateCellRange(base_id='movement')
    for slice in slice_list:
      for share in share_list:
        cell = model_line.newCell(\
            share, slice, portal_type='Pay Sheet Cell', base_id='movement')
        cell.setMappedValuePropertyList(['quantity', 'price'])
        amount = values[share_list.index(share)][slice_list.index(slice)][0]
        percent = values[share_list.index(share)][slice_list.index(slice)][1]
        if amount != None:
          cell.setQuantity(amount)
        if percent != None:
          cell.setPrice(percent)
        get_transaction().commit()
        self.tic()

    return model_line

  def createPaySheet(self, model, id='my_paysheet'):
    '''
      create a Pay Sheet with the model specialisation
    '''
    paysheet_module = self.portal.getDefaultModule(\
                            portal_type=self.paysheet_transaction_portal_type)
    if hasattr(paysheet_module, id):
      paysheet_module.manage_delObjects([id])
    paysheet = paysheet_module.newContent(\
        portal_type               = self.paysheet_transaction_portal_type,
        id                        = id,
        title                     = id,
        specialise_value          = model,
        source_section_value      = model.getSourceSectionValue(),
        destination_section_value = model.getDestinationSectionValue(),
        start_date                = DateTime(2008, 1, 1),
        stop_date                 = DateTime(2008, 1, 31),)
    paysheet.setPriceCurrency('currency_module/EUR')
    get_transaction().commit()
    self.tic()
    return paysheet

  def calculatePaySheet(self, paysheet):
    '''
      Calcul the given paysheet like if you have click on the 'Calculation of
      the Pay Sheet Transaction' action button.
      XXX Editable line are not yet take into account
      XXX this method should not exist ! use the standard method
    '''
    paysheet_line_list = \
        paysheet.createPaySheetLineList()
    portal_type_list = ['Annotation Line', 'Payment Condition',
                        'Pay Sheet Model Ratio Line']
    paysheet.PaySheetTransaction_copySubObject(portal_type_list)
    get_transaction().commit()
    self.tic()
    return paysheet_line_list

  def assertEqualAmounts(self, pay_sheet_line, correct_value_slice_list,
      base_salary, i):
    slice_list = pay_sheet_line.getVariationCategoryList(\
        base_category_list='base_salary')
    share_list = pay_sheet_line.getVariationCategoryList(\
        base_category_list='tax_category')
    for slice in slice_list:
      for share in share_list:
        cell = pay_sheet_line.getCell(share, slice)
        value = cell.getQuantity()
        min_slice = correct_value_slice_list[i-1]
        max_slice = correct_value_slice_list[i]

        if base_salary <= max_slice:
          correct_value = base_salary - min_slice
        else:
          correct_value = max_slice - min_slice
        self.assertEqual(correct_value, value)
      i += 1


class TestPayroll(TestPayrollMixin):
  quiet = 0

  def test_01_modelCreation(self):
    '''
      test the function createModel and test if the model has been well created
    '''

    if hasattr(self.paysheet_model_module, self.model_id):
      self.paysheet_model_module.manage_delObjects([self.model_id])

    model_count_before_add = \
        len(self.paysheet_model_module.contentValues(portal_type=\
        self.paysheet_model_portal_type))

    self.model = self.createModel(self.model_id,
                                  self.model_title,
                                  self.person_id,
                                  self.person_title,
                                  self.person_career_grade,
                                  self.organisation_id,
                                  self.organisation_title,
                                  self.variation_settings_category_list,
                                  self.price_currency)

    model_count_after_add = \
        len(self.paysheet_model_module.contentValues(portal_type=\
        self.paysheet_model_portal_type))

    # check that the number of model_lines has been incremented
    self.assertEqual(model_count_before_add+1, model_count_after_add)

    #check model have been well created
    self.model = self.paysheet_model_module._getOb(self.model_id)
    self.assertEqual(self.model_id, self.model.getId())
    self.assertEqual(self.model_title, self.model.getTitle())
    self.assertEqual(self.organisation_title,
                     self.model.getDestinationSectionTitle())
    self.assertEqual(self.person_title, self.model.getSourceSectionTitle())
    self.assertEqual(self.variation_settings_category_list,
                     self.model.getVariationSettingsCategoryList(base=1))

  def test_02_addModelLine(self):
    '''
      create a Model Line and test if it has been well created
    '''
    #model = self.createModel()
    self.addAllSlices(self.model)

    payroll_service_portal_type = 'Payroll Service'
    payroll_service_module = self.portal.getDefaultModule(\
                                    portal_type=payroll_service_portal_type)

    model_line_id = 'URSSAF'

    variation_category_list = self.urssaf_share_list + self.urssaf_slice_list

    model_line_count_before_add = len(self.model.contentValues(portal_type=\
        self.paysheet_model_line_portal_type))

    returned_model_line = self.createModelLine(
        model=self.model,
        id=model_line_id,
        variation_category_list=variation_category_list,
        resource=self.urssaf,
        share_list=self.urssaf_share_list,
        slice_list=self.urssaf_slice_list,
        values=[[[None, 0.01], [None, 0.02],[None, 0.03]], [[None, 0.04],
                 [None, 0.05], [None, 0.06]]],
        base_application_list=['base_amount/base_salary',],
        base_contribution_list=['base_amount/deductible_tax',])

    model_line_count_after_add = len(self.model.contentValues(portal_type=\
        self.paysheet_model_line_portal_type))

    # check that the number of model_lines has been incremented
    self.assertEqual(model_line_count_before_add+1, model_line_count_after_add)

    model_line = self.model._getOb(model_line_id)
    self.assertEqual(returned_model_line, model_line)
    self.assertEqual(model_line_id, model_line.getId())
    payroll_service_portal_type = 'Payroll Service'
    payroll_service_module = self.portal.getDefaultModule(\
        portal_type=payroll_service_portal_type)
    resource = payroll_service_module._getOb(self.urssaf_id)
    self.assertEqual(resource, model_line.getResourceValue())
    self.assertEqual(variation_category_list,
        model_line.getVariationCategoryList())

  def test_03_createPaySheet(self):
    '''
      create a Pay Sheet with the model specialisation and verify it was well
      created
    '''
    paysheet_id = 'my_paysheet'
    paysheet_returned = self.createPaySheet(self.model, paysheet_id)
    paysheet_module = self.portal.getDefaultModule(\
                          portal_type=self.paysheet_transaction_portal_type)
    paysheet = paysheet_module._getOb(paysheet_id)
    self.assertEqual(paysheet_returned, paysheet)
    self.assertEqual(paysheet_id, paysheet.getId())
    self.assertEqual(paysheet.getDestinationSectionTitle(),
        self.model.getDestinationSectionTitle())
    self.assertEqual(paysheet.getSourceSectionTitle(),
        self.model.getSourceSectionTitle())
    self.assertEqual(paysheet.getSpecialiseValue(), self.model)

  def test_04_paySheetCalculation(self):
    '''
      test if the scripts called by the 'Calculation of the Pay Sheet
      Transaction' action create the paysheet lines
    '''
    self.addAllSlices(self.model)

    model_line_id1 = 'urssaf'
    model_line_id2 = 'salary'

    urssaf_slice_list = [ 'salary_range/'+self.france_settings_slice_a,
                          'salary_range/'+self.france_settings_slice_b,
                          'salary_range/'+self.france_settings_slice_c]

    urssaf_share_list = [ 'tax_category/'+self.tax_category_employee_share,
                          'tax_category/'+self.tax_category_employer_share]

    salary_slice_list = ['salary_range/'+self.france_settings_forfait,]
    salary_share_list = ['tax_category/'+self.tax_category_employee_share,]

    variation_category_list_urssaf = urssaf_share_list + urssaf_slice_list
    variation_category_list_salary = salary_share_list + salary_slice_list

    model_line1 = self.createModelLine(model=self.model,
        id=model_line_id1,
        variation_category_list=variation_category_list_urssaf,
        resource=self.urssaf,
        share_list=self.urssaf_share_list,
        slice_list=self.urssaf_slice_list,
        values=[[[None, 0.01], [None, 0.02], [None, 0.03]], [[None, 0.04],
               [None, 0.05], [None, 0.06]]],
        source_value=self.payroll_service_organisation,
        base_application_list=[ 'base_amount/base_salary'],
        base_contribution_list=['base_amount/deductible_tax',])

    model_line2 = self.createModelLine(model=self.model,
        id=model_line_id2,
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=self.salary_share_list,
        slice_list=self.salary_slice_list,
        values=[[[10000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary'])

    pay_sheet_line_count = len(self.model.contentValues(portal_type=\
        self.paysheet_line_portal_type)) + 2 # because in this test, 2 lines
                                             # are added

    paysheet = self.createPaySheet(self.model)

    paysheet_line_count_before_calculation = \
        len(paysheet.contentValues(portal_type= \
        self.paysheet_line_portal_type))

    # calculate the pay sheet
    pay_sheet_line_list = self.calculatePaySheet(paysheet=paysheet)

    paysheet_line_count_after_calculation = \
        len(paysheet.contentValues(portal_type= \
        self.paysheet_line_portal_type))
    self.assertEqual(paysheet_line_count_before_calculation, 0)
    self.assertEqual(paysheet_line_count_after_calculation,
        pay_sheet_line_count)

    # check the amount in the cells of the created paysheet lines
    for pay_sheet_line in pay_sheet_line_list:
      service = pay_sheet_line.getResourceId()
      if service == self.urssaf_id:
        i = 1
        correct_value_slice_list = [0, self.plafond, self.plafond*4,
                                    self.plafond*8]

        self.assertEqualAmounts(pay_sheet_line, correct_value_slice_list,
            10000, i)
        self.assertEquals(
            [self.payroll_service_organisation.getRelativeUrl()],
            pay_sheet_line._getCategoryMembershipList('source_section'))

        # check the base_contribution has been copied from the pay sheet model
        # to the pay sheet line
        self.assertEquals(model_line1.getBaseContributionList(),
                          pay_sheet_line.getBaseContributionList())

      elif service == self.labour_id:
        cell = pay_sheet_line.getCell(\
            'tax_category/'+ self.tax_category_employee_share,
            'salary_range/'+ self.france_settings_forfait)
        value = cell.getTotalPrice()
        self.assertEqual(10000, value)
        self.assertEquals([],
            pay_sheet_line._getCategoryMembershipList('source_section'))

        # check the base_contribution has been copied from the pay sheet model
        # to the pay sheet line
        self.assertEquals(model_line2.getBaseContributionList(),
                          pay_sheet_line.getBaseContributionList())

      else:
        self.fail("Unknown service for line %s" % pay_sheet_line)

  def test_05_caculationWithANonNullMinimumValueSlice(self):
    '''
      if the is only slice B (without previous slice A), test that
      the amount paid for this tax is correct
    '''
    self.addAllSlices(self.model)

    model_line_id1 = 'urssaf'
    model_line_id2 = 'salary'
    base_salary = 10000

    urssaf_slice_list = ['salary_range/'+self.france_settings_slice_b,]
    variation_category_list_urssaf = self.urssaf_share_list + urssaf_slice_list
    variation_category_list_salary = self.salary_share_list + \
        self.salary_slice_list

    model_line1 = self.createModelLine(model=self.model,
        id=model_line_id1,
        variation_category_list=variation_category_list_urssaf,
        resource=self.urssaf, share_list=self.urssaf_share_list,
        slice_list=urssaf_slice_list,
        values=[[[None, 0.03]], [[None, 0.04]],],
        base_application_list=[ 'base_amount/base_salary'],
        base_contribution_list=['base_amount/deductible_tax',])

    model_line2 = self.createModelLine(model=self.model,
        id=model_line_id2,
        variation_category_list=variation_category_list_salary,
        resource=self.labour, share_list=self.salary_share_list,
        slice_list=self.salary_slice_list,
        values=[[[base_salary, None]],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary',])

    pay_sheet_line_count = len(self.model.contentValues(portal_type=\
        self.paysheet_line_portal_type)) + 2 # because in this test, 2 lines
                                             # are added

    paysheet = self.createPaySheet(self.model)

    paysheet_line_count_before_calculation = \
        len(paysheet.contentValues(portal_type= \
        self.paysheet_line_portal_type))

    # calculate the pay sheet
    pay_sheet_line_list = self.calculatePaySheet(paysheet=paysheet)

    paysheet_line_count_after_calculation = \
        len(paysheet.contentValues(portal_type= \
        self.paysheet_line_portal_type))
    self.assertEqual(paysheet_line_count_before_calculation, 0)
    self.assertEqual(paysheet_line_count_after_calculation,
        pay_sheet_line_count)

    # check the amount in the cells of the created paysheet lines
    for pay_sheet_line in pay_sheet_line_list:
      service = pay_sheet_line.getResourceId()
      if service == self.urssaf_id:
        i = 2 # the begining max slice
        correct_value_slice_list = [0, self.plafond, self.plafond*4,
                                    self.plafond*8]

        self.assertEqualAmounts(pay_sheet_line, correct_value_slice_list,
            base_salary, i)

      elif service == self.labour_id:
        cell = pay_sheet_line.getCell('tax_category/'+\
            self.tax_category_employee_share,
            'salary_range/'+ self.france_settings_forfait)
        value = cell.getTotalPrice()
        self.assertEqual(base_salary, value)

      else:
        self.fail("Unknown service for line %s" % pay_sheet_line)

  def test_06_model_inheritance(self):
    '''
      check that a model can inherite some datas from another
      the ineritance rules are the following :
       - a DATA could be a model_line, annotation_line, ratio_line or
         payement_condition (XXX -> this last one haven't yet reference)
       - a model_line, annotation_line and a ratio_line have a REFERENCE
       - a model can have some DATA's
       - a model can inherite from another, that's mean :
         o At the calculation step, each DATA of the parent model will be
           checked : the DATA with a REFERENCE that's already in the child
           model will not entered in the calcul. The other will.
         o This will be repeated on each parent model and on each parent of
           the parent model,... until there is no parent model to inherite
           (or until a max loop number has been reached).
    '''
    # create 3 models
    model_employee = self.paysheet_model_module.newContent(id='model_employee',
        portal_type='Pay Sheet Model')

    model_company = self.paysheet_model_module.newContent(id='model_company',
        portal_type='Pay Sheet Model')

    model_country = self.paysheet_model_module.newContent(id='model_country',
        portal_type='Pay Sheet Model')

    # add some content in the models
    model_employee.newContent(id='over_time_duration',
                              title='over_time_duration',
                              portal_type='Annotation Line',
                              reference='over_time_duration',)

    model_company.newContent( id='worked_time_duration',
                              title='worked_time_duration',
                              portal_type='Annotation Line',
                              reference='worked_time_duration',)

    model_country.newContent( id='social_insurance',
                              title='social_insurance',
                              portal_type='Annotation Line',
                              reference='social_insurance',)

    # inherite from each other
    model_employee.setSpecialiseValue(model_company)
    model_company.setSpecialiseValue(model_country)

    # return a list of data that should contain data from all model
    portal_type_list = ['Annotation Line', ]
    model_reference_dict = model_employee.getInheritanceModelReferenceDict(\
        portal_type_list=portal_type_list)


    # check data's are corrected
    number_of_different_references = []
    for model in model_reference_dict.keys():
      number_of_different_references.extend(model_reference_dict[model])

    self.assertEqual(len(number_of_different_references), 3) # here, there is
                                                # 3 differents annotation line

    # check the model number
    self.assertEqual(len(model_reference_dict), 3)
    self.assertEqual(model_reference_dict[model_employee.getRelativeUrl()],
        ['over_time_duration',])
    self.assertEqual(model_reference_dict[model_company.getRelativeUrl()],
        ['worked_time_duration',])
    self.assertEqual(model_reference_dict[model_country.getRelativeUrl()],
        ['social_insurance',])

    # check with more values on each model
    # employee :
    model_employee.newContent(id='1',
                              portal_type='Annotation Line',
                              reference='1',)
    # company :
    model_company.newContent( id='1',
                              portal_type='Annotation Line',
                              reference='1',)
    model_company.newContent( id='2',
                              portal_type='Annotation Line',
                              reference='2',)
    # country :
    model_country.newContent( id='1',
                              portal_type='Annotation Line',
                              reference='1',)
    model_country.newContent( id='2',
                              portal_type='Annotation Line',
                              reference='2',)
    model_country.newContent( id='3',
                              portal_type='Annotation Line',
                              reference='3',)
    model_country.newContent( id='4',
                              portal_type='Annotation Line',
                              reference='4',)

    # return a list of data that should contain data from all model
    portal_type_list = ['Annotation Line', ]
    model_reference_dict = {}
    model_reference_dict = model_employee.getInheritanceModelReferenceDict(\
        portal_type_list=portal_type_list)

    # check that if a reference is already present in the model_employee,
    # and the model_company contain a data with the same one, the data used at
    # the calculation step is the model_employee data.
    number_of_different_references = []
    for model in model_reference_dict.keys():
      number_of_different_references.extend(model_reference_dict[model])

    self.assertEqual(len(number_of_different_references), 7) # here, there is
    # 4 differents annotation lines, and with the 3 ones have been had before
    # that's make 7 !



    # check the model number
    self.assertEqual(len(model_reference_dict), 3)
    self.assertEqual(set(model_reference_dict[model_employee.getRelativeUrl()]),
        set(['1', 'over_time_duration']))
    self.assertEqual(set(model_reference_dict[model_company.getRelativeUrl()]),
        set(['2', 'worked_time_duration']))
    self.assertEqual(set(model_reference_dict[model_country.getRelativeUrl()]),
        set(['3','4', 'social_insurance']))


    # same test with a multi model inheritance
    model_a = self.paysheet_model_module.newContent(id='model_a',
        title='model_a', portal_type='Pay Sheet Model')
    model_b = self.paysheet_model_module.newContent(id='model_b',
        title='model_b', portal_type='Pay Sheet Model')
    model_c = self.paysheet_model_module.newContent(id='model_c',
        title='model_c', portal_type='Pay Sheet Model')
    model_d = self.paysheet_model_module.newContent(id='model_d',
        title='model_d', portal_type='Pay Sheet Model')

    # check with more values on each model
    # a :
    model_a.newContent(id='5', portal_type='Annotation Line', reference='5')
    # b :
    model_b.newContent(id='5',portal_type='Annotation Line', reference='5')
    model_b.newContent(id='6',portal_type='Annotation Line', reference='6')
    # c :
    model_c.newContent(id='5', portal_type='Annotation Line', reference='5')
    model_c.newContent(id='6', portal_type='Annotation Line', reference='6')
    model_c.newContent(id='7', portal_type='Annotation Line', reference='7')
    model_c.newContent(id='8', portal_type='Annotation Line', reference='8')
    # d :
    model_d.newContent(id='5',portal_type='Annotation Line', reference='5')
    model_d.newContent(id='6',portal_type='Annotation Line', reference='6')


    # inherite from each other
    model_a.setSpecialiseValue(model_c)
    model_country.setSpecialiseValue(model_d)
    model_company.setSpecialiseValueList([model_country, model_a, model_b])
    model_employee.setSpecialiseValue(model_company)

    # get a list of data that should contain data from all model inheritance
    # dependances tree
    portal_type_list = ['Annotation Line', ]
    model_reference_dict = {}
    model_reference_dict = model_employee.getInheritanceModelReferenceDict(\
        portal_type_list=portal_type_list)


    # check data's are corrected
    number_of_different_references = []
    for model in model_reference_dict.keys():
      number_of_different_references.extend(model_reference_dict[model])

    self.assertEqual(len(number_of_different_references), 11) # here, there is
    # 8 differents annotation lines, and with the 3 ones have been had before
    # that's make 11 !

    # check the model number
    self.assertEqual(len(model_reference_dict), 6) # there is 7 model, but the
    # model_d is not take into account because it have no annotation line wich
    # are not already added by other models


    # the inheritance tree look like this :

#                                model_employee
#                           ('overtime_duration', '1')
#                                      |
#                                      |
#                                      |
#                                model_company
#                      ('worked_time_duration', '1', '2')
#                         /            |            \
#                        /             |             \
#                       /              |              \
#            model_country           model_a          model_b
#         ('social_insurance',       ('5',)          ('5', '6')
#          '1', '2', '3', '4')         |
#                  |                   |
#                  |                   |
#               model_d             model_c
#            ('5', '6')       ('5', '6', '7', '8')




    self.assertEqual(set(model_reference_dict[model_employee.getRelativeUrl()]),
        set(['1', 'over_time_duration']))
    self.assertEqual(set(model_reference_dict[model_company.getRelativeUrl()]),
        set(['2', 'worked_time_duration']))
    self.assertEqual(set(model_reference_dict[model_country.getRelativeUrl()]),
        set(['3','4', 'social_insurance']))
    self.assertEqual(model_reference_dict[model_a.getRelativeUrl()], ['5',])
    self.assertEqual(model_reference_dict[model_b.getRelativeUrl()], ['6',])
    self.assertEqual(set(model_reference_dict[model_c.getRelativeUrl()]),
        set(['7', '8']))


    # get all sub objects from a paysheet witch inherite of model_employee

    # create a paysheet
    id = 'inheritance_paysheet'
    paysheet_module = self.portal.getDefaultModule(\
                            portal_type=self.paysheet_transaction_portal_type)
    if hasattr(paysheet_module, id):
      paysheet_module.manage_delObjects([id])
    paysheet = paysheet_module.newContent(\
        portal_type               = self.paysheet_transaction_portal_type,
        id                        = id,
        title                     = id,
        specialise_value          = model_employee)

    # check heneritance works
    self.assertEqual(paysheet.getSpecialiseValue(), model_employee)

    # get a list of all this subObjects:
    sub_object_list = paysheet.getInheritedObjectValueList(portal_type_list)
    self.assertEqual(len(sub_object_list), 11)

  def test_07_model_getCell(self):
    '''
      Model objects have a overload method called getCell. This method first
      call the XMLMatrix.getCell and if the cell is not found, call
      getCell method in all it's inherited model until the cell is found or
      the cell have been searched on all inherited models.

      TODO : Currently, the method use a Depth-First Search algorithm, it will
      be better to use Breadth-First Search one.
      more about this on :
        - http://en.wikipedia.org/wiki/Breadth-first_search
        - http://en.wikipedia.org/wiki/Depth-first_search
    '''
    # create 3 models
    model_employee = self.paysheet_model_module.newContent(id='model_employee',
        portal_type='Pay Sheet Model')
    model_employee.edit(variation_settings_category_list=
        self.variation_settings_category_list)

    model_company = self.paysheet_model_module.newContent(id='model_company',
        portal_type='Pay Sheet Model')
    model_company.edit(variation_settings_category_list=
        self.variation_settings_category_list)

    model_company_alt = self.paysheet_model_module.newContent(
        id='model_company_alt',
        portal_type='Pay Sheet Model')
    model_company_alt.edit(variation_settings_category_list=
        self.variation_settings_category_list)

    model_country = self.paysheet_model_module.newContent(id='model_country',
        portal_type='Pay Sheet Model')
    model_country.edit(variation_settings_category_list=
        self.variation_settings_category_list)

    # add some cells in the models
    self.addSlice(model_employee, 'salary_range/%s' % \
        self.france_settings_slice_a, 0, 1)

    self.addSlice(model_company, 'salary_range/%s' % \
        self.france_settings_slice_b, 2, 3)

    self.addSlice(model_company_alt, 'salary_range/%s' % \
        self.france_settings_forfait, 20, 30)

    self.addSlice(model_country, 'salary_range/%s' % \
        self.france_settings_slice_c, 4, 5)

    # inherite from each other
    model_employee.setSpecialiseValueList((model_company, model_company_alt))
    model_company.setSpecialiseValue(model_country)


    # check getCell results

    # check model_employee could access all cells
    cell_a = model_employee.getCell('salary_range/%s' % \
                        self.france_settings_slice_a)
    self.assertNotEqual(cell_a, None)
    self.assertEqual(cell_a.getQuantityRangeMin(), 0)
    self.assertEqual(cell_a.getQuantityRangeMax(), 1)

    cell_b = model_employee.getCell('salary_range/%s' % \
                        self.france_settings_slice_b)
    self.assertNotEqual(cell_b, None)
    self.assertEqual(cell_b.getQuantityRangeMin(), 2)
    self.assertEqual(cell_b.getQuantityRangeMax(), 3)

    cell_forfait = model_employee.getCell('salary_range/%s' % \
                        self.france_settings_forfait)
    self.assertNotEqual(cell_forfait, None)
    self.assertEqual(cell_forfait.getQuantityRangeMin(), 20)
    self.assertEqual(cell_forfait.getQuantityRangeMax(), 30)

    cell_c = model_employee.getCell('salary_range/%s' % \
                        self.france_settings_slice_c)
    self.assertNotEqual(cell_c, None)
    self.assertEqual(cell_c.getQuantityRangeMin(), 4)
    self.assertEqual(cell_c.getQuantityRangeMax(), 5)

    # check model_company and model_company_alt could access just it's own cell
    # and this of the country model
    cell_a = model_company.getCell('salary_range/%s' % \
                        self.france_settings_slice_a)
    self.assertEqual(cell_a, None)

    cell_b = model_company.getCell('salary_range/%s' % \
                        self.france_settings_slice_b)
    self.assertNotEqual(cell_b, None)
    self.assertEqual(cell_b.getQuantityRangeMin(), 2)
    self.assertEqual(cell_b.getQuantityRangeMax(), 3)

    cell_forfait = model_company_alt.getCell('salary_range/%s' % \
                        self.france_settings_forfait)
    self.assertNotEqual(cell_forfait, None)
    self.assertEqual(cell_forfait.getQuantityRangeMin(), 20)
    self.assertEqual(cell_forfait.getQuantityRangeMax(), 30)

    cell_c = model_company.getCell('salary_range/%s' % \
                        self.france_settings_slice_c)
    self.assertNotEqual(cell_c, None)
    self.assertEqual(cell_c.getQuantityRangeMin(), 4)
    self.assertEqual(cell_c.getQuantityRangeMax(), 5)

    # check model_country could access just it's own cell
    # model
    cell_a = model_country.getCell('salary_range/%s' % \
                        self.france_settings_slice_a)
    self.assertEqual(cell_a, None)

    cell_b = model_country.getCell('salary_range/%s' % \
                        self.france_settings_slice_b)
    self.assertEqual(cell_b, None)

    cell_forfait = model_country.getCell('salary_range/%s' % \
                        self.france_settings_forfait)
    self.assertEqual(cell_forfait, None)

    cell_c = model_country.getCell('salary_range/%s' % \
                        self.france_settings_slice_c)
    self.assertNotEqual(cell_c, None)
    self.assertEqual(cell_c.getQuantityRangeMin(), 4)
    self.assertEqual(cell_c.getQuantityRangeMax(), 5)


  def test_model_slice_cell_range(self):
    base_id = 'cell'
    model_1 = self.paysheet_model_module.newContent(
                            portal_type='Pay Sheet Model',
                            variation_settings_category_list=
                                  ('salary_range/france',))

    model_2 = self.paysheet_model_module.newContent(
                            portal_type='Pay Sheet Model',
                            specialise_value=model_1,)

    cell = model_1.newCell('salary_range/france/tranche_a',
                    portal_type='Pay Sheet Model Slice',
                    base_id='cell')
    cell.setQuantityRangeMin(1)
    cell.setQuantityRangeMax(2)

    # model 2 gets cell values from model 1 (see test_07_model_getCell)
    self.assertEquals(1,
        model_2.getCell('salary_range/france/tranche_a').getQuantityRangeMin())
    self.assertEquals(2,
        model_2.getCell('salary_range/france/tranche_a').getQuantityRangeMax())

    # model 2 can override values
    model_2.edit(variation_settings_category_list=('salary_range/france',))
    cell = model_2.newCell('salary_range/france/tranche_a',
                    portal_type='Pay Sheet Model Slice',
                    base_id='cell')
    cell.setQuantityRangeMin(3)
    cell.setQuantityRangeMax(4)
    self.assertEquals(3,
        model_2.getCell('salary_range/france/tranche_a').getQuantityRangeMin())
    self.assertEquals(4,
        model_2.getCell('salary_range/france/tranche_a').getQuantityRangeMax())

    # when unsetting variation settings category on this model will acquire
    # again values from specialised model
    model_2.edit(variation_settings_category_list=())
    self.assertEquals(1,
        model_2.getCell('salary_range/france/tranche_a').getQuantityRangeMin())
    self.assertEquals(2,
        model_2.getCell('salary_range/france/tranche_a').getQuantityRangeMax())


  def test_PaySheetTransaction_getMovementList(self):
    # Tests PaySheetTransaction_getMovementList script
    pay_sheet = self.createPaySheet(self.model)
    # when pay sheet has no line, the script returns an empty list
    self.assertEquals(pay_sheet.PaySheetTransaction_getMovementList(), [])
    # we add a line, then it is returned in the list
    line = pay_sheet.newContent(portal_type='Pay Sheet Line')
    self.assertEquals(1, len(pay_sheet.PaySheetTransaction_getMovementList()))

    # if the line has cells with different tax categories, new properties are
    # added to this line.
    line.setResourceValue(self.urssaf)
    line.setVariationCategoryList(['tax_category/employee_share',
                                   'tax_category/employer_share'])
    line.updateCellRange(base_id='movement')
    cell0 = line.newCell('tax_category/employee_share',
                         portal_type='Pay Sheet Cell', base_id='movement')
    cell0.setMappedValuePropertyList(['quantity', 'price'])
    cell0.setVariationCategoryList(('tax_category/employee_share',))
    cell0.setPrice(2)
    cell0.setQuantity(3)
    cell1 = line.newCell('tax_category/employer_share',
                         portal_type='Pay Sheet Cell', base_id='movement')
    cell1.setMappedValuePropertyList(['quantity', 'price'])
    cell1.setVariationCategoryList(('tax_category/employer_share',))
    cell1.setPrice(4)
    cell1.setQuantity(5)

    movement_list = pay_sheet.PaySheetTransaction_getMovementList()
    self.assertEquals(1, len(movement_list))
    movement = movement_list[0]
    self.assertEquals(2, movement.employee_share_price)
    self.assertEquals(3, movement.employee_share_quantity)
    self.assertEquals(2*3, movement.employee_share_total_price)
    self.assertEquals(4, movement.employer_share_price)
    self.assertEquals(5, movement.employer_share_quantity)
    self.assertEquals(4*5, movement.employer_share_total_price)

  def test_createEditablePaySheetLine(self):
    # test the creation of lines with editable lines in the model
    line = self.model.newContent(
          id='line',
          portal_type='Pay Sheet Model Line',
          resource_value=self.labour,
          variation_category_list=['tax_category/employee_share'],
          editable=1)
    # Note that it is required that the editable line contains at least one
    # cell, to know which tax_category is used (employee share or employer
    # share).
    line.updateCellRange(base_id='movement')
    cell = line.newCell('tax_category/employee_share',
                        portal_type='Pay Sheet Cell',
                        base_id='movement')
    cell.setMappedValuePropertyList(('quantity', 'price'))
    cell.setVariationCategoryList(('tax_category/employee_share',))
    cell.setPrice(1)

    pay_sheet = self.createPaySheet(self.model)

    # PaySheetTransaction_getEditableObjectLineList is the script used as list
    # method to display editable lines in the dialog listbox
    editable_line_list = pay_sheet\
          .PaySheetTransaction_getEditableObjectLineList()
    self.assertEquals(1, len(editable_line_list))
    editable_line = editable_line_list[0]
    self.assertEquals(1, editable_line.employee_share_price)
    self.assertEquals(0, editable_line.employee_share_quantity)
    self.assertEquals('paysheet_model_module/model_one/line',
                      editable_line.model_line)
    self.assertEquals(None, editable_line.salary_range_relative_url)

    # PaySheetTransaction_createAllPaySheetLineList is the script used to create line and cells in the
    # paysheet using the listbox input
    pay_sheet.PaySheetTransaction_createAllPaySheetLineList(
      listbox=[dict(listbox_key='0',
                    employee_share_price=1,
                    employee_share_quantity=2,
                    model_line='paysheet_model_module/model_one/line',
                    salary_range_relative_url='',)])
    pay_sheet_line_list = pay_sheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(1, len(pay_sheet_line_list))
    pay_sheet_line = pay_sheet_line_list[0]
    self.assertEquals(self.labour, pay_sheet_line.getResourceValue())
    cell = pay_sheet_line.getCell('tax_category/employee_share',
                                  base_id='movement')
    self.assertNotEquals(None, cell)
    self.assertEquals(1, cell.getPrice())
    self.assertEquals(2, cell.getQuantity())

    # if the script is called again, previous content is erased.
    pay_sheet.PaySheetTransaction_createAllPaySheetLineList(
      listbox=[dict(listbox_key='0',
                    employee_share_price=0.5,
                    employee_share_quantity=10,
                    model_line='paysheet_model_module/model_one/line',
                    salary_range_relative_url='',)])
    pay_sheet_line_list = pay_sheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(1, len(pay_sheet_line_list))
    pay_sheet_line = pay_sheet_line_list[0]
    self.assertEquals(self.labour, pay_sheet_line.getResourceValue())
    cell = pay_sheet_line.getCell('tax_category/employee_share',
                                  base_id='movement')
    self.assertNotEquals(None, cell)
    self.assertEquals(0.5, cell.getPrice())
    self.assertEquals(10, cell.getQuantity())

    # If the user enters a null quantity, the line will not be created
    pay_sheet.PaySheetTransaction_createAllPaySheetLineList(
      listbox=[dict(listbox_key='0',
                    employee_share_price=1,
                    employee_share_quantity=0,
                    model_line='paysheet_model_module/model_one/line',
                    salary_range_relative_url='',)])
    pay_sheet_line_list = pay_sheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(0, len(pay_sheet_line_list))

  def test_createEditablePaySheetLineAppliedToBase(self):
    # test the creation of lines with editable lines in the model, when those
    # editable lines applies to a base
    # line1 will contribute to 'base_salary'
    line1 = self.model.newContent(
          id='line1',
          portal_type='Pay Sheet Model Line',
          resource_value=self.labour,
          variation_category_list=['tax_category/employee_share'],
          base_application_list= [],
          base_contribution_list=['base_amount/base_salary',
                                  'base_amount/gross_salary'],
          float_index=1,
          int_index=1)
    line1.updateCellRange(base_id='movement')
    cell = line1.newCell('tax_category/employee_share',
                        portal_type='Pay Sheet Cell',
                        base_id='movement')
    cell.setMappedValuePropertyList(('quantity', 'price'))
    cell.setVariationCategoryList(('tax_category/employee_share',))
    cell.setPrice(1)
    cell.setQuantity(100)
    # line2 will apply to 'base_salary', but we'll set 0 quantity in the dialog
    line2 = self.model.newContent(
          id='line2',
          portal_type='Pay Sheet Model Line',
          resource_value=self.labour,
          variation_category_list=['tax_category/employee_share'],
          base_application_list= [],
          base_contribution_list=['base_amount/base_salary',
                                  'base_amount/gross_salary'],
          #base_amount_list=['base_salary'],
          editable=1,
          float_index=2,
          int_index=2)
    line2.updateCellRange(base_id='movement')
    cell = line2.newCell('tax_category/employee_share',
                        portal_type='Pay Sheet Cell',
                        base_id='movement')
    cell.setMappedValuePropertyList(('quantity', 'price'))
    cell.setVariationCategoryList(('tax_category/employee_share',))
    cell.setPrice(1)

    pay_sheet = self.createPaySheet(self.model)

    # PaySheetTransaction_getEditableObjectLineList is the script used as list
    # method to display editable lines in the dialog listbox
    editable_line_list = pay_sheet\
          .PaySheetTransaction_getEditableObjectLineList()
    self.assertEquals(1, len(editable_line_list))
    editable_line = editable_line_list[0]
    self.assertEquals(1, editable_line.employee_share_price)
    self.assertEquals(0, editable_line.employee_share_quantity)
    self.assertEquals('paysheet_model_module/model_one/line2',
                      editable_line.model_line)
    self.assertEquals(None, editable_line.salary_range_relative_url)

    # PaySheetTransaction_createAllPaySheetLineList is the script used to create line and cells in the
    # paysheet using the listbox input
    pay_sheet.PaySheetTransaction_createAllPaySheetLineList(
      listbox=[dict(listbox_key='0',
                    employee_share_price=.5,
                    employee_share_quantity=4,
                    model_line='paysheet_model_module/model_one/line2',
                    salary_range_relative_url='',)])
    pay_sheet_line_list = pay_sheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(2, len(pay_sheet_line_list))
    pay_sheet_line1 = [l for l in pay_sheet_line_list
                         if l.getIntIndex() == 1][0]
    self.assertEquals(self.labour, pay_sheet_line1.getResourceValue())
    cell = pay_sheet_line1.getCell('tax_category/employee_share',
                                  base_id='movement')
    self.assertNotEquals(None, cell)
    self.assertEquals(1, cell.getPrice())
    self.assertEquals(100, cell.getQuantity())

    pay_sheet_line2 = [l for l in pay_sheet_line_list
                         if l.getIntIndex() == 2][0]
    self.assertEquals(self.labour, pay_sheet_line2.getResourceValue())
    cell = pay_sheet_line2.getCell('tax_category/employee_share',
                                  base_id='movement')
    self.assertNotEquals(None, cell)
    self.assertEquals(.5, cell.getPrice())
    self.assertEquals(4, cell.getQuantity())

    # if the script is called again, previous content is erased.
    pay_sheet.PaySheetTransaction_createAllPaySheetLineList(
      listbox=[dict(listbox_key='0',
                    employee_share_price=0.6,
                    employee_share_quantity=10,
                    model_line='paysheet_model_module/model_one/line2',
                    salary_range_relative_url='',)])
    pay_sheet_line_list = pay_sheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(2, len(pay_sheet_line_list))
    pay_sheet_line1 = [l for l in pay_sheet_line_list
                         if l.getIntIndex() == 1][0]
    self.assertEquals(self.labour, pay_sheet_line1.getResourceValue())
    cell = pay_sheet_line1.getCell('tax_category/employee_share',
                                  base_id='movement')
    self.assertNotEquals(None, cell)
    self.assertEquals(1, cell.getPrice())
    self.assertEquals(100, cell.getQuantity())

    pay_sheet_line2 = [l for l in pay_sheet_line_list
                         if l.getIntIndex() == 2][0]
    self.assertEquals(self.labour, pay_sheet_line2.getResourceValue())
    cell = pay_sheet_line2.getCell('tax_category/employee_share',
                                  base_id='movement')
    self.assertNotEquals(None, cell)
    self.assertEquals(0.6, cell.getPrice())
    self.assertEquals(10, cell.getQuantity())

    # If the user enters a null quantity, the line will not be created
    pay_sheet.PaySheetTransaction_createAllPaySheetLineList(
      listbox=[dict(listbox_key='0',
                    employee_share_price=1,
                    employee_share_quantity=0,
                    model_line='paysheet_model_module/model_one/line2',
                    salary_range_relative_url='',)])
    pay_sheet_line_list = pay_sheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(1, len(pay_sheet_line_list))
    pay_sheet_line1 = [l for l in pay_sheet_line_list
                         if l.getIntIndex() == 1][0]
    self.assertEquals(self.labour, pay_sheet_line1.getResourceValue())
    cell = pay_sheet_line1.getCell('tax_category/employee_share',
                                  base_id='movement')
    self.assertNotEquals(None, cell)
    self.assertEquals(1, cell.getPrice())
    self.assertEquals(100, cell.getQuantity())

  def test_createPaySheetLineNonePrice(self):
    # test the creation of lines when the price is not set, but only the
    # quantity. This means that no ratio is applied on this line.
    line = self.model.newContent(
          id='line',
          portal_type='Pay Sheet Model Line',
          resource_value=self.labour,
          variation_category_list=['tax_category/employee_share'],
          base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary'])
    line.updateCellRange(base_id='movement')
    cell = line.newCell('tax_category/employee_share',
                        portal_type='Pay Sheet Cell',
                        base_id='movement')
    cell.setMappedValuePropertyList(('quantity', 'price'))
    cell.setVariationCategoryList(('tax_category/employee_share',))
    cell.setQuantity(5)

    pay_sheet = self.createPaySheet(self.model)

    pay_sheet.PaySheetTransaction_createAllPaySheetLineList()
    pay_sheet_line_list = pay_sheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(1, len(pay_sheet_line_list))
    pay_sheet_line = pay_sheet_line_list[0]
    self.assertEquals(self.labour, pay_sheet_line.getResourceValue())
    cell = pay_sheet_line.getCell('tax_category/employee_share',
                                  base_id='movement')
    self.assertNotEquals(None, cell)
    self.assertEquals(1, cell.getPrice())
    self.assertEquals(5, cell.getQuantity())

  def test_createPaySheetLineZeroPrice(self):
    # test the creation of lines when the price is set to zero: the line should
    # not be created.
    line = self.model.newContent(
          id='line',
          portal_type='Pay Sheet Model Line',
          resource_value=self.labour,
          variation_category_list=['tax_category/employee_share'],
          base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary'])
    line.updateCellRange(base_id='movement')
    cell = line.newCell('tax_category/employee_share',
                        portal_type='Pay Sheet Cell',
                        base_id='movement')
    cell.setMappedValuePropertyList(('quantity', 'price'))
    cell.setVariationCategoryList(('tax_category/employee_share',))
    cell.setQuantity(5)
    cell.setPrice(0)

    pay_sheet = self.createPaySheet(self.model)

    pay_sheet.PaySheetTransaction_createAllPaySheetLineList()
    pay_sheet_line_list = pay_sheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(0, len(pay_sheet_line_list))

  def test_paysheet_consistency(self):
    # minimal test for checkConsistency on a Pay Sheet Transaction and its
    # subdocuments (may have to be updated when we'll add more constraints).
    paysheet = self.createPaySheet(self.model)
    paysheet.setResourceValue(self.portal.currency_module.EUR)
    paysheet.newContent(portal_type='Pay Sheet Line')
    paysheet.newContent(portal_type='Pay Sheet Transaction Line')
    paysheet.newContent(portal_type='Annotation Line')
    paysheet.newContent(portal_type='Pay Sheet Model Ratio Line')
    paysheet.newContent(portal_type='Payment Condition')
    self.assertEquals([], paysheet.checkConsistency())

  def test_paysheet_model_consistency(self):
    # minimal test for checkConsistency on a Pay Sheet Model and its
    # subdocuments (may have to be updated when we'll add more constraints).
    model = self.model
    model.newContent(portal_type='Pay Sheet Model Line') # XXX this one needs a
                                                         # resource
    model.newContent(portal_type='Annotation Line')
    model.newContent(portal_type='Pay Sheet Model Ratio Line')
    model.newContent(portal_type='Payment Condition')
    self.assertEquals([], model.checkConsistency())

  def test_payroll_service_consistency(self):
    # minimal test for checkConsistency on a Payroll Service
    service = self.portal.payroll_service_module.newContent(
                           portal_type='Payroll Service')
    service.setVariationBaseCategoryList(['tax_category'])
    service.setVariationCategoryList(['tax_category/employee_share'])
    self.assertEquals([], service.checkConsistency())

  def test_apply_model(self):
    eur = self.portal.currency_module.EUR
    employee = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee')
    employee_bank_account = employee.newContent(
                      portal_type='Bank Account')
    employer = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Employer')
    employer_bank_account = employee.newContent(
                      portal_type='Bank Account')
    model = self.portal.paysheet_model_module.newContent(
                      portal_type='Pay Sheet Model',
                      source_section_value=employee,
                      source_payment_value=employee_bank_account,
                      destination_section_value=employer,
                      destination_payment_value=employer_bank_account,
                      price_currency_value=eur,
                      payment_condition_payment_date=DateTime(2008, 1, 1),
                      work_time_annotation_line_quantity=10)
    paysheet = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      specialise_value=model)

    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(employee, paysheet.getSourceSectionValue())
    self.assertEquals(employer, paysheet.getDestinationSectionValue())
    self.assertEquals(employee_bank_account, paysheet.getSourcePaymentValue())
    self.assertEquals(employer_bank_account, paysheet.getDestinationPaymentValue())
    self.assertEquals(employee_bank_account,
                      paysheet.getPaymentConditionSourcePaymentValue())
    self.assertEquals(employer_bank_account,
                      paysheet.getPaymentConditionDestinationPaymentValue())
    self.assertEquals(eur, paysheet.getResourceValue())
    self.assertEquals(eur, paysheet.getPriceCurrencyValue())
    self.assertEquals(DateTime(2008, 1, 1),
                      paysheet.getPaymentConditionPaymentDate())
    self.assertEquals(10, paysheet.getWorkTimeAnnotationLineQuantity())

    # if not found on the first model, values are searched recursivly in the
    # model hierarchy
    other_model = self.portal.paysheet_model_module.newContent(
                      portal_type='Pay Sheet Model',
                      specialise_value=model)
    paysheet = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      specialise_value=other_model)

    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(employee, paysheet.getSourceSectionValue())
    self.assertEquals(employer, paysheet.getDestinationSectionValue())
    self.assertEquals(eur, paysheet.getResourceValue())
    self.assertEquals(eur, paysheet.getPriceCurrencyValue())
    self.assertEquals(DateTime(2008, 1, 1),
                      paysheet.getPaymentConditionPaymentDate())
    self.assertEquals(10, paysheet.getWorkTimeAnnotationLineQuantity())

    # applying twice does not copy subdocument twice
    self.assertEquals(2, len(paysheet.contentValues()))
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(2, len(paysheet.contentValues()))

  def test_apply_model_empty_line(self):
    # apply a model with some empty lines
    eur = self.portal.currency_module.EUR
    employee = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee')
    employer = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Employer')
    model = self.portal.paysheet_model_module.newContent(
                      portal_type='Pay Sheet Model',
                      source_section_value=employee,
                      destination_section_value=employer,
                      price_currency_value=eur,
                      payment_condition_payment_date=DateTime(2008, 1, 1),
                      work_time_annotation_line_quantity=10)
    employee_model = self.portal.paysheet_model_module.newContent(
                      portal_type='Pay Sheet Model',
                      specialise_value=model,
                      work_time_annotation_line_quantity=20)
    employee_model.setWorkTimeAnnotationLineQuantity(None)
    paysheet = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      specialise_value=employee_model)

    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(employee, paysheet.getSourceSectionValue())
    self.assertEquals(employer, paysheet.getDestinationSectionValue())
    self.assertEquals(eur, paysheet.getResourceValue())
    self.assertEquals(eur, paysheet.getPriceCurrencyValue())
    self.assertEquals(DateTime(2008, 1, 1),
                      paysheet.getPaymentConditionPaymentDate())
    # WorkTimeAnnotationLine is not taken on employee_model, because the line
    # is "empty", it is taken on model.
    self.assertEquals(10, paysheet.getWorkTimeAnnotationLineQuantity())

    # applying twice does not copy subdocument twice
    self.assertEquals(2, len(paysheet.contentValues()))
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(2, len(paysheet.contentValues()))

  def test_calculate_paysheet_source_annotation_line_reference(self):
    # the payroll service provider can be specified using the reference of an
    # annotation line.
    eur = self.portal.currency_module.EUR
    employee = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee')
    employer = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Employer')
    provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Payroll Service Provider')
    model = self.portal.paysheet_model_module.newContent(
                      portal_type='Pay Sheet Model',
                      source_section_value=employee,
                      destination_section_value=employer,
                      price_currency_value=eur,)
    model_line = model.newContent(
                    portal_type='Pay Sheet Model Line',
                    resource_value=self.urssaf,
                    variation_category_list=['tax_category/employee_share'],
                    source_annotation_line_reference='tax1',
                    base_contribution_list = ['base_amount/deductible_tax',],)
    model_line.updateCellRange(base_id='movement')
    cell = model_line.newCell('tax_category/employee_share',
                              portal_type='Pay Sheet Cell',
                              base_id='movement')
    cell.setMappedValuePropertyList(('quantity', 'price'))
    cell.setPrice(10)
    cell.setQuantity(10)

    annotation = model.newContent(
                        portal_type='Annotation Line',
                        reference='tax1',
                        source_value=provider)

    paysheet = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      specialise_value=model)

    paysheet.PaySheetTransaction_applyModel()
    paysheet.createPaySheetLineList()
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEquals(1, len(paysheet_line_list))
    paysheet_line = paysheet_line_list[0]

    self.assertEquals([provider.getRelativeUrl()],
                      paysheet_line._getCategoryMembershipList('source_section'))
    self.assertEquals(self.urssaf, paysheet_line.getResourceValue())
    self.assertEquals(100, paysheet_line.getTotalPrice())
    self.assertEquals(['tax_category/employee_share'],
                      paysheet_line.getVariationCategoryList())


  def test_PayrollTaxesReport(self):
    eur = self.portal.currency_module.EUR
    payroll_service = self.portal.payroll_service_module.newContent(
                      portal_type='Payroll Service',
                      title='PS1',
                      variation_base_category_list=('tax_category',),
                      variation_category_list=('tax_category/employee_share',
                                               'tax_category/employer_share'))
    employer = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Employer',
                      price_currency_value=eur,
                      group_value=self.portal.portal_categories.group.demo_group)
    employee1 = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee One',
                      career_reference='E1',
                      career_subordination_value=employer)
    employee2 = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee Two',
                      career_reference='E2',
                      career_subordination_value=employer)
    provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Payroll Service Provider')
    other_provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Another Payroll Service Provider')
    ps1 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 1',
                      destination_section_value=employer,
                      source_section_value=employee1,
                      start_date=DateTime(2006, 1, 1),)
    line = ps1.newContent(portal_type='Pay Sheet Line',
                   resource_value=payroll_service,
                   source_section_value=provider,
                # (destination is set by PaySheetTransaction.createPaySheetLine)
                   destination_value=employee1,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.50, quantity=2000, tax_category='employee_share')
    cell_employer = line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.40, quantity=2000, tax_category='employer_share')
    ps1.plan()

    ps2 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 2',
                      destination_section_value=employer,
                      source_section_value=employee2,
                      start_date=DateTime(2006, 1, 1),)
    line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=payroll_service,
                   source_section_value=provider,
                   destination_value=employee2,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.50, quantity=3000, tax_category='employee_share')
    cell_employer = line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.40, quantity=3000, tax_category='employer_share')

    other_line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=payroll_service,
                   destination_value=employee2,
                   source_section_value=other_provider,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    other_line.updateCellRange(base_id='movement')
    cell_employee = other_line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.46, quantity=2998, tax_category='employee_share')
    cell_employer = other_line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.42, quantity=2998, tax_category='employer_share')

    get_transaction().commit()
    self.tic()

    # AccountingTransactionModule_getPaySheetMovementMirrorSectionItemList is
    # used in the report dialog to display possible organisations.
    self.assertEquals(
        [('', ''),
         (other_provider.getTitle(), other_provider.getRelativeUrl()),
         (provider.getTitle(), provider.getRelativeUrl())],
        self.portal.accounting_module\
    .AccountingTransactionModule_getPaySheetMovementMirrorSectionItemList())

    # set request variables and render
    request_form = self.portal.REQUEST
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['draft', 'planned']
    request_form['resource'] = payroll_service.getRelativeUrl()
    request_form['mirror_section'] = provider.getRelativeUrl()

    report_section_list = self.getReportSectionList(
                             self.portal.accounting_module,
                             'AccountingTransactionModule_viewPaySheetLineReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(2, len(data_line_list))

    # base_unit_quantity for EUR is set to 0.001 in createCurrencies, so the
    # precision is 3
    precision = self.portal.REQUEST.get('precision')
    self.assertEquals(3, precision)

    self.checkLineProperties(data_line_list[0],
                            id=1,
                            employee_career_reference='E1',
                            employee_title='Employee One',
                            base=2000,
                            employee_share=2000 * .50,
                            employer_share=2000 * .40,
                            total=(2000 * .50 + 2000 * .40))
    self.checkLineProperties(data_line_list[1],
                            id=2,
                            employee_career_reference='E2',
                            employee_title='Employee Two',
                            base=3000,
                            employee_share=3000 * .50,
                            employer_share=3000 * .40,
                            total=(3000 * .50 + 3000 * .40))
    # stat line
    self.checkLineProperties(line_list[-1],
                            base=3000 + 2000,
                            employee_share=(3000 + 2000) * .50,
                            employer_share=(3000 + 2000) * .40,
                            total=((3000 + 2000) * .50 + (3000 + 2000) * .40))


  def test_PayrollTaxesReportDifferentSalaryRange(self):
    eur = self.portal.currency_module.EUR
    payroll_service = self.portal.payroll_service_module.newContent(
                      portal_type='Payroll Service',
                      title='PS1',
                      variation_base_category_list=('tax_category',
                                                    'salary_range'),
                      variation_category_list=('tax_category/employee_share',
                                               'tax_category/employer_share',
                                               'salary_range/france/tranche_a',
                                               'salary_range/france/tranche_b'))
    employer = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Employer',
                      price_currency_value=eur,
                      group_value=self.portal.portal_categories.group.demo_group)
    employee1 = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee One',
                      career_reference='E1',
                      career_subordination_value=employer)
    employee2 = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee Two',
                      career_reference='E2',
                      career_subordination_value=employer)
    provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Payroll Service Provider')
    other_provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Another Payroll Service Provider')
    ps1 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 1',
                      destination_section_value=employer,
                      source_section_value=employee1,
                      start_date=DateTime(2006, 1, 1),)
    line = ps1.newContent(portal_type='Pay Sheet Line',
                   resource_value=payroll_service,
                   source_section_value=provider,
                # (destination is set by PaySheetTransaction.createPaySheetLine)
                   destination_value=employee1,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share',
                                            'salary_range/france/tranche_a',
                                            'salary_range/france/tranche_b'))
    line.updateCellRange(base_id='movement')
    cell_employee_a = line.newCell('tax_category/employee_share',
                                   'salary_range/france/tranche_a',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employee_a.edit(price=-.50, quantity=1000,
                         tax_category='employee_share',
                         salary_range='france/tranche_a')
    cell_employee_b = line.newCell('tax_category/employee_share',
                                   'salary_range/france/tranche_b',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employee_b.edit(price=-.20, quantity=500,
                         tax_category='employee_share',
                         salary_range='france/tranche_b')

    cell_employer_a = line.newCell('tax_category/employer_share',
                                   'salary_range/france/tranche_a',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employer_a.edit(price=-.40, quantity=1000,
                         tax_category='employer_share',
                         salary_range='france/tranche_a')
    cell_employer_b = line.newCell('tax_category/employer_share',
                                   'salary_range/france/tranche_b',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employer_b.edit(price=-.32, quantity=500,
                         tax_category='employer_share',
                         salary_range='france/tranche_b')

    ps1.plan()

    ps2 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 2',
                      destination_section_value=employer,
                      source_section_value=employee2,
                      start_date=DateTime(2006, 1, 1),)
    line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=payroll_service,
                   source_section_value=provider,
                   destination_value=employee2,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share',
                                            'salary_range/france/tranche_a',
                                            'salary_range/france/tranche_b'))
    line.updateCellRange(base_id='movement')
    cell_employee_a = line.newCell('tax_category/employee_share',
                                   'salary_range/france/tranche_a',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employee_a.edit(price=-.50, quantity=1000,
                         salary_range='france/tranche_a',
                         tax_category='employee_share')
    cell_employee_b = line.newCell('tax_category/employee_share',
                                   'salary_range/france/tranche_b',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employee_b.edit(price=-.20, quantity=3000,
                         salary_range='france/tranche_b',
                         tax_category='employee_share')

    cell_employer_a = line.newCell('tax_category/employer_share',
                                   'salary_range/france/tranche_a',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employer_a.edit(price=-.40, quantity=1000,
                         salary_range='france/tranche_a',
                         tax_category='employer_share')
    cell_employer_b = line.newCell('tax_category/employer_share',
                                   'salary_range/france/tranche_b',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employer_b.edit(price=-.32, quantity=3000,
                         salary_range='france/tranche_b',
                         tax_category='employer_share')
    get_transaction().commit()
    self.tic()

    # set request variables and render
    request_form = self.portal.REQUEST
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['draft', 'planned']
    request_form['resource'] = payroll_service.getRelativeUrl()
    request_form['mirror_section'] = provider.getRelativeUrl()

    report_section_list = self.getReportSectionList(
                             self.portal.accounting_module,
                             'AccountingTransactionModule_viewPaySheetLineReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(6, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                            id=1,
                            employee_career_reference='E1',
                            employee_title='Employee One',
                            base=1000,
                            employee_share=1000 * .50,
                            employer_share=1000 * .40,
                            total=(1000 * .50 + 1000 * .40))
    self.checkLineProperties(data_line_list[1],
                            id=2,
                            employee_career_reference='E2',
                            employee_title='Employee Two',
                            base=1000,
                            employee_share=1000 * .50,
                            employer_share=1000 * .40,
                            total=(1000 * .50 + 1000 * .40))
    self.checkLineProperties(data_line_list[2],
                            employee_title='Total Tranche A',
                            base=2000,
                            employee_share=2000 * .50,
                            employer_share=2000 * .40,
                            #total=(2000 * .50 + 2000 * .40)
                            )

    self.checkLineProperties(data_line_list[3],
                            id=3,
                            employee_career_reference='E1',
                            employee_title='Employee One',
                            base=500,
                            employee_share=500 * .20,
                            employer_share=500 * .32,
                            total=(500 * .20 + 500 * .32))
    self.checkLineProperties(data_line_list[4],
                            id=4,
                            employee_career_reference='E2',
                            employee_title='Employee Two',
                            base=3000,
                            employee_share=3000 * .20,
                            employer_share=3000 * .32,
                            total=(3000 * .20 + 3000 * .32))
    self.checkLineProperties(data_line_list[5],
                            employee_title='Total Tranche B',
                            base=3500,
                            employee_share=3500 * .20,
                            employer_share=3500 * .32,
                            #total=(3500 * .20 + 3500 * .32),
                            )

    # stat line
    self.checkLineProperties(line_list[-1],
                            base=2000 + 3500,
                            employee_share=(2000 * .50 + 3500 * .20),
                            employer_share=(2000 * .40 + 3500 * .32),
                            total=((2000 * .50 + 3500 * .20) +
                                   (2000 * .40 + 3500 * .32)))

  def test_NetSalaryReport(self):
    eur = self.portal.currency_module.EUR
    salary_service = self.portal.payroll_service_module.newContent(
                      portal_type='Payroll Service',
                      title='Gross Salary',
                      variation_base_category_list=('tax_category',),
                      variation_category_list=('tax_category/employee_share',
                                               'tax_category/employer_share'))
    payroll_service = self.portal.payroll_service_module.newContent(
                      portal_type='Payroll Service',
                      title='PS1',
                      variation_base_category_list=('tax_category',),
                      variation_category_list=('tax_category/employee_share',
                                               'tax_category/employer_share'))
    employer = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Employer',
                      price_currency_value=eur,
                      group_value=self.portal.portal_categories.group.demo_group)
    employee1 = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee One',
                      career_reference='E1',
                      career_subordination_value=employer)
    employee1_ba = employee1.newContent(portal_type='Bank Account',
                                        title='Bank 1')
    employee2 = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee Two',
                      career_reference='E2',
                      career_subordination_value=employer)
    employee2_ba = employee2.newContent(portal_type='Bank Account',
                                        title='Bank 2')
    provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Payroll Service Provider')
    other_provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Another Payroll Service Provider')
    ps1 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 1',
                      destination_section_value=employer,
                      source_section_value=employee1,
                      payment_condition_source_payment_value=employee1_ba,
                      start_date=DateTime(2006, 1, 1),)
    line = ps1.newContent(portal_type='Pay Sheet Line',
                   resource_value=salary_service,
                   destination_value=employee1,
                   base_contribution_list=['base_amount/net_salary',],
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=1, quantity=2000, tax_category='employee_share')
    line = ps1.newContent(portal_type='Pay Sheet Line',
                   resource_value=payroll_service,
                   source_section_value=provider,
                   destination_value=employee1,
                   base_contribution_list=['base_amount/net_salary',],
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.50, quantity=2000, tax_category='employee_share')
    cell_employer = line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.40, quantity=2000, tax_category='employer_share')
    ps1.plan()

    ps2 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 2',
                      destination_section_value=employer,
                      source_section_value=employee2,
                      payment_condition_source_payment_value=employee2_ba,
                      start_date=DateTime(2006, 1, 1),)
    line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=salary_service,
                   destination_value=employee2,
                   base_contribution_list=['base_amount/net_salary',],
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=1, quantity=3000, tax_category='employee_share')
    line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=payroll_service,
                   source_section_value=provider,
                   destination_value=employee2,
                   base_contribution_list=['base_amount/net_salary',],
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.50, quantity=3000, tax_category='employee_share')
    cell_employer = line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.40, quantity=3000, tax_category='employer_share')

    get_transaction().commit()
    self.tic()

    # set request variables and render
    request_form = self.portal.REQUEST
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['draft', 'planned']

    report_section_list = self.getReportSectionList(
                             self.portal.accounting_module,
                             'AccountingTransactionModule_viewNetSalaryReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(2, len(data_line_list))

    # base_unit_quantity for EUR is set to 0.001 in createCurrencies, so the
    # precision is 3
    precision = self.portal.REQUEST.get('precision')
    self.assertEquals(3, precision)

    self.checkLineProperties(data_line_list[0],
                            employee_career_reference='E1',
                            employee_title='Employee One',
                            employee_bank_account='Bank 1',
                            total_price=2000 - (2000 * .5),)
    self.checkLineProperties(data_line_list[1],
                            employee_career_reference='E2',
                            employee_title='Employee Two',
                            employee_bank_account='Bank 2',
                            total_price=3000 - (3000 * .5),)
    # stat line
    self.checkLineProperties(
            line_list[-1],
            total_price=3000 + 2000 - (2000 * .5) - (3000 * .5))

  def test_AccountingLineGeneration(self):
    # create payroll services
    base_salary = self.portal.payroll_service_module.newContent(
                          portal_type='Payroll Service',
                          title='Base Salary',
                          product_line='base_salary',
                          variation_base_category_list=('tax_category',),
                          variation_category_list=('tax_category/employee_share',
                                                   'tax_category/employer_share'))
    bonus = self.portal.payroll_service_module.newContent(
                          portal_type='Payroll Service',
                          title='Bonus',
                          product_line='base_salary',
                          variation_base_category_list=('tax_category',),
                          variation_category_list=('tax_category/employee_share',
                                                   'tax_category/employer_share'))
    deductions = self.portal.payroll_service_module.newContent(
                          portal_type='Payroll Service',
                          title='Deductions',
                          product_line='base_salary',
                          variation_base_category_list=('tax_category',),
                          variation_category_list=('tax_category/employee_share',
                                                   'tax_category/employer_share'))
    tax1 = self.portal.payroll_service_module.newContent(
                          portal_type='Payroll Service',
                          title='Tax1',
                          product_line='payroll_tax_1',
                          variation_base_category_list=('tax_category',),
                          variation_category_list=('tax_category/employee_share',
                                                   'tax_category/employer_share'))

    # create accounts
    account_payroll_wages_expense = self.portal.account_module.newContent(
                          portal_type='Account',
                          title='Payroll Wages (expense)',
                          account_type='expense',)
    account_payroll_taxes_expense = self.portal.account_module.newContent(
                          portal_type='Account',
                          title='Payroll Taxes (expense)',
                          account_type='expense',)
    account_net_wages = self.portal.account_module.newContent(
                          portal_type='Account',
                          title='Net Wages',
                          account_type='liability/payable',)
    account_payroll_taxes = self.portal.account_module.newContent(
                          portal_type='Account',
                          title='Payroll Taxes',
                          account_type='liability/payable',)

    # create an invoice transaction rule for pay sheets.
    rule = self.portal.portal_rules.newContent(
                          portal_type='Invoice Transaction Rule',
                          title='Rule for PaySheet Accounting',
                          reference='paysheet_transaction_rule',
                          test_method_id=
                              'SimulationMovement_testInvoiceTransactionRule')
    rule.newContent(portal_type='Predicate',
                    title='Employee Share',
                    string_index='tax_category',
                    int_index=1,
                    membership_criterion_base_category_list=('tax_category',),
                    membership_criterion_category_list=('tax_category/employee_share',))
    rule.newContent(portal_type='Predicate',
                    title='Employer Share',
                    string_index='tax_category',
                    int_index=2,
                    membership_criterion_base_category_list=('tax_category',),
                    membership_criterion_category_list=('tax_category/employer_share',))

    rule.newContent(portal_type='Predicate',
                    title='Base Salary',
                    string_index='payroll_service',
                    int_index=1,
                    membership_criterion_base_category_list=('product_line',),
                    membership_criterion_category_list=('product_line/base_salary',))
    rule.newContent(portal_type='Predicate',
                    title='Payroll Tax 1',
                    string_index='payroll_service',
                    int_index=2,
                    membership_criterion_base_category_list=('product_line',),
                    membership_criterion_category_list=('product_line/payroll_tax_1',))

    get_transaction().commit()
    self.tic()

    cell_list = rule.contentValues(portal_type='Accounting Rule Cell')
    self.assertEquals(4, len(cell_list))

    employee_base_salary = rule._getOb('movement_0_0')
    self.assertEquals('Employee Share * Base Salary',
                      employee_base_salary.getTitle())
    employee_base_salary.newContent(
                      portal_type='Accounting Rule Cell Line',
                      destination_debit=1,
                      destination_value=account_payroll_wages_expense)
    employee_base_salary.newContent(
                      portal_type='Accounting Rule Cell Line',
                      destination_credit=1,
                      destination_value=account_net_wages)

    employer_tax = rule._getOb('movement_1_1')
    self.assertEquals('Employer Share * Payroll Tax 1',
                      employer_tax.getTitle())
    employer_tax.newContent(
                      portal_type='Accounting Rule Cell Line',
                      destination_debit=1,
                      destination_value=account_payroll_taxes)
    employer_tax.newContent(
                      portal_type='Accounting Rule Cell Line',
                      destination_credit=1,
                      destination_value=account_payroll_taxes_expense)

    employee_tax = rule._getOb('movement_0_1')
    self.assertEquals('Employee Share * Payroll Tax 1',
                      employee_tax.getTitle())
    employee_tax.newContent(
                      portal_type='Accounting Rule Cell Line',
                      destination_debit=1,
                      destination_value=account_payroll_taxes)
    employee_tax.newContent(
                      portal_type='Accounting Rule Cell Line',
                      destination_credit=1,
                      generate_prevision_script_id=\
      'SimulationMovement_generatePrevisionForEmployeeSharePaySheetMovement',
                      destination_value=account_net_wages)
    rule.validate()

    # create a pay sheet
    eur = self.portal.currency_module.EUR
    employer = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Employer',
                      price_currency_value=eur,
                      group_value=self.portal.portal_categories.group.demo_group)
    employee = self.portal.person_module.newContent(
                      portal_type='Person',
                      title='Employee',
                      career_reference='E1',
                      career_subordination_value=employer)
    provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Payroll Service Provider')

    ps = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      price_currency_value=eur,
                      resource_value=eur,
                      title='Employee 1',
                      destination_section_value=employer,
                      source_section_value=employee,
                      start_date=DateTime(2006, 1, 1),)

    # base salary = 2000
    line = ps.newContent(portal_type='Pay Sheet Line',
                   title='Base salary',
                   resource_value=base_salary,
                   destination_value=employee,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=1, quantity=2000, tax_category='employee_share')
    cell_employer = line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=1, quantity=2000, tax_category='employer_share')

    # base_salary += 100 (bonus)
    line = ps.newContent(portal_type='Pay Sheet Line',
                   title='Bonus',
                   resource_value=bonus,
                   destination_value=employee,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=1, quantity=100, tax_category='employee_share')
    cell_employer = line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=1, quantity=100, tax_category='employer_share')

    # base_salary -= 50 (deductions)   => base_salary == 2050
    line = ps.newContent(portal_type='Pay Sheet Line',
                   title='Deduction',
                   resource_value=deductions,
                   destination_value=employee,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-1, quantity=50, tax_category='employee_share')
    cell_employer = line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-1, quantity=50, tax_category='employer_share')

    # tax1 = 10% for employee ( 205 )
    #        20% for employer ( 410 )
    line = ps.newContent(portal_type='Pay Sheet Line',
                   title='Tax 1',
                   resource_value=tax1,
                   source_section_value=provider,
                   destination_value=employee,
                   variation_category_list=('tax_category/employee_share',
                                            'tax_category/employer_share'))
    line.updateCellRange(base_id='movement')
    cell_employee = line.newCell('tax_category/employee_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.1, quantity=2050, tax_category='employee_share')
    cell_employer = line.newCell('tax_category/employer_share',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.2, quantity=2050, tax_category='employer_share')

    ps.plan()

    get_transaction().commit()
    self.tic()

    related_applied_rule = ps.getCausalityRelatedValue(
                                portal_type='Applied Rule')
    self.assertNotEquals(related_applied_rule, None)

    # build accounting lines
    ps.confirm()
    ps.start()
    get_transaction().commit()
    self.tic()

    accounting_line_list = ps.contentValues(
        portal_type='Pay Sheet Transaction Line')
    self.assertEquals(len(accounting_line_list), 4)

    line = [l for l in accounting_line_list
            if l.getDestinationValue() == account_payroll_wages_expense][0]
    self.assertEquals(2050, line.getDestinationDebit())
    self.assertEquals(employer, line.getDestinationSectionValue())

    line = [l for l in accounting_line_list
            if l.getDestinationValue() == account_net_wages][0]
    self.assertEquals(2050 - 205, line.getDestinationCredit())
    self.assertEquals(employer, line.getDestinationSectionValue())
    self.assertEquals(employee, line.getSourceSectionValue())

    line = [l for l in accounting_line_list
            if l.getDestinationValue() == account_payroll_taxes_expense][0]
    self.assertEquals(410, line.getDestinationDebit())
    self.assertEquals(employer, line.getDestinationSectionValue())

    line = [l for l in accounting_line_list
            if l.getDestinationValue() == account_payroll_taxes][0]
    self.assertEquals(410 + 205, line.getDestinationCredit())
    self.assertEquals(employer, line.getDestinationSectionValue())
    self.assertEquals(provider, line.getSourceSectionValue())

  def test_intermediateLinesAreNotCreatedOnPaysheet(self):
    '''
      Intermediate lines are paysheet model lines usefull to calcul, but we
      don't want to have on paysheet. So a checkbox on paysheet model lines
      permit to create it or not (created by default)
    '''
    eur = self.portal.currency_module.EUR
    model = self.paysheet_model_module.newContent( \
                              portal_type='Pay Sheet Model',
                              variation_settings_category_list=self.variation_settings_category_list)
    model.setPriceCurrencyValue(eur)

    
    self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_a, 0, 1000)
    self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_b, 1000, 2000)
    self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_c, 2000, 10000000)
    self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_forfait, 0, 10000000)

    urssaf_slice_list = [ 'salary_range/'+self.france_settings_slice_a,]
    urssaf_share_list = [ 'tax_category/'+self.tax_category_employee_share,]
    salary_slice_list = ['salary_range/'+self.france_settings_forfait,]
    salary_share_list = ['tax_category/'+self.tax_category_employee_share,]
    variation_category_list_urssaf = urssaf_share_list + urssaf_slice_list
    variation_category_list_salary = salary_share_list + salary_slice_list

    model_line_1 = self.createModelLine(model=model,
        id='model_line_1',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[10000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary'])
    model_line_1.setIntIndex(1)

    model_line_2 = self.createModelLine(model=model,
        id='model_line_2',
        variation_category_list=variation_category_list_urssaf,
        resource=self.urssaf,
        share_list=urssaf_share_list,
        slice_list=urssaf_slice_list,
        values=[[[None, 0.8]],],
        source_value=self.payroll_service_organisation,
        base_application_list=[ 'base_amount/base_salary',],
        base_contribution_list=['base_amount/net_salary',])
    model_line_2.setIntIndex(2)
    
    model_line_3 = self.createModelLine(model=model,
        id='model_line_3',
        variation_category_list=variation_category_list_urssaf,
        resource=self.urssaf,
        share_list=urssaf_share_list,
        slice_list=urssaf_slice_list,
        values=[[[None, -0.1]],],
        source_value=self.payroll_service_organisation,
        base_application_list=[ 'base_amount/net_salary',],
        base_contribution_list=['base_amount/deductible_tax',])
    model_line_3.setIntIndex(3)

    # create a paysheet with two lines
    paysheet = self.portal.accounting_module.newContent(
                              portal_type='Pay Sheet Transaction',
                              specialise_value=model)
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(len(paysheet.contentValues(portal_type='Pay Sheet Line')), 0)
    # calculate the pay sheet
    pay_sheet_line_list = self.calculatePaySheet(paysheet=paysheet)
    self.assertEquals(len(paysheet.contentValues(portal_type='Pay Sheet Line')), 3)
    # check values on the paysheet
    self.assertEquals(paysheet.contentValues()[0].contentValues()[0].getTotalPrice(), 10000)
    self.assertEquals(paysheet.contentValues()[1].contentValues()[0].getTotalPrice(), 8000)
    self.assertEquals(paysheet.contentValues()[2].contentValues()[0].getTotalPrice(), -800)

    # create a paysheet with one normal line and an intermediate line
    model_line_2.setCreatePaysheetLine(False)
    paysheet = self.portal.accounting_module.newContent(
                              portal_type='Pay Sheet Transaction',
                              specialise_value=model)
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(len(paysheet.contentValues(portal_type='Pay Sheet Line')), 0)
    # calculate the pay sheet
    pay_sheet_line_list = self.calculatePaySheet(paysheet=paysheet)
    # now only one line should be created 
    self.assertEquals(len(paysheet.contentValues(portal_type='Pay Sheet Line')), 2)

    # check values on the paysheet
    self.assertEquals(paysheet.contentValues()[0].contentValues()[0].getTotalPrice(), 10000)
    self.assertEquals(paysheet.contentValues()[1].contentValues()[0].getTotalPrice(), -800)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPayroll))
  return suite
