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
import transaction


class TestPayrollMixin(ERP5ReportTestCase):

  paysheet_model_portal_type        = 'Pay Sheet Model'
  paysheet_model_line_portal_type   = 'Pay Sheet Model Line'
  paysheet_transaction_portal_type  = 'Pay Sheet Transaction'
  paysheet_line_portal_type         = 'Pay Sheet Line'
  service_portal_type       = 'Service'
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
    self.service_module = self.portal.service_module
    self.paysheet_model_module = self.portal.paysheet_model_module
    self.validateRules()
    self.createCategories()
    self.createCurrencies()

    self.model = self.createModel(self.model_id, self.model_title,
        self.person_id, self.person_title, self.person_career_grade,
        self.organisation_id, self.organisation_title,
        self.variation_settings_category_list, self.price_currency)

    self.login()

    # creation of services
    self.urssaf_id = 'sickness_insurance'
    self.labour_id = 'labour'

    self.urssaf_slice_list = ['salary_range/'+self.france_settings_slice_a,
                              'salary_range/'+self.france_settings_slice_b,
                              'salary_range/'+self.france_settings_slice_c]

    self.urssaf_share_list = ['tax_category/'+self.tax_category_employee_share,
                              'tax_category/'+self.tax_category_employer_share]

    self.salary_slice_list = ['salary_range/'+self.france_settings_forfait,]
    self.salary_share_list = ['tax_category/'+self.tax_category_employee_share,]


    self.service_organisation = self.createOrganisation(
                                          id='urssaf', title='URSSAF')
    self.urssaf = self.createService(id=self.urssaf_id,
        title='State Insurance',
        product_line='state_insurance',
        variation_base_category_list=['tax_category', 'salary_range'],
        variation_category_list=self.urssaf_slice_list + \
                                self.urssaf_share_list)

    self.labour = self.createService(id=self.labour_id,
        title='Labour',
        product_line='labour',
        variation_base_category_list=['tax_category', 'salary_range'],
        variation_category_list=self.salary_slice_list +\
                                self.salary_share_list)

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
                    'service_module',
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
      transaction.commit()
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
    transaction.commit()
    self.tic()
    return person

  def createOrganisation(self, id='company_one', title='Company One', **kw):
    if hasattr(self.organisation_module, id):
      self.organisation_module.manage_delObjects([id])
    organisation = self.organisation_module.newContent( \
                                   portal_type=self.organisation_portal_type,
                                   id=id,
                                   title=title)
    transaction.commit()
    self.tic()
    return organisation

  def createService(self, id='', title='',
      variation_base_category_list=None,
      variation_category_list=None, product_line=None, **kw):

    service_portal_type = 'Service'
    service_module = self.portal.getDefaultModule(\
                                    portal_type=service_portal_type)

    if variation_category_list == None:
      variation_category_list=[]
    if variation_base_category_list == None:
      variation_category_list=[]
    if hasattr(service_module, id):
      service_module.manage_delObjects([id])

    service = service_module.newContent(
                            title=title,
                            portal_type=self.service_portal_type,
                            id=id,
                            quantity_unit='time/month',
                            product_line=product_line)
    service.setVariationBaseCategoryList(variation_base_category_list)
    service.setVariationCategoryList(variation_category_list)
    transaction.commit()
    self.tic()
    return service

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
    transaction.commit()
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
    transaction.commit()
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
    transaction.commit()
    self.tic()

    # put values in Model Line cells
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
        transaction.commit()
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
    transaction.commit()
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
    transaction.commit()
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

  def test_createPaySheetLineZeroPrice(self):
    # test the creation of lines when the price is set to zero: the line should
    # not be created.
    line = self.model.newContent(
          id='line',
          portal_type='Pay Sheet Model Line',
          resource_value=self.labour,
          variation_category_list=['tax_category/employee_share'],
          base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary'])
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

  def testComplexModelInheritanceScheme(self):
    '''
    check inheritance and effective model with a more complexe inheritance tree
    '''

    # the inheritance tree look like this :
#                                        model_employee
#   (model_1, 01/01/09, 28/02/09) ; (model_2, 01/07/09, 31/12/09) ; (model_2, 01/07/09, 31/12/09)
#                                              |
#                                              |
#                                              |
#                                        model_company
#                (model_4, 01/07/09, 31/12/09), (model_5, 01/07/09, 31/12/09)
#                                              |
#                                              |
#                                              |
#                                        model_company
#                (model_6, 01/07/09, 31/12/09), (model_7, 01/07/09, 31/12/09)


    eur = self.portal.currency_module.EUR
    urssaf_slice_list = [ 'salary_range/'+self.france_settings_slice_a,]
    urssaf_share_list = [ 'tax_category/'+self.tax_category_employee_share,]
    salary_slice_list = ['salary_range/'+self.france_settings_forfait,]
    salary_share_list = ['tax_category/'+self.tax_category_employee_share,]
    variation_category_list_urssaf = urssaf_share_list + urssaf_slice_list
    variation_category_list_salary = salary_share_list + salary_slice_list

    # define a non effective model
    model_1 = self.paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=self.variation_settings_category_list,
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 01, 1),
        expiration_date=DateTime(2009, 02, 28))
    model_line_1 = self.createModelLine(model=model_1,
        id='model_line_1',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[10000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary'])

    # define two models with same references and same dates
    # but different version number
    model_2 = self.paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=self.variation_settings_category_list,
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='002')
    model_line_2 = self.createModelLine(model=model_2,
        id='model_line_2',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[20000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary'])

    model_3 = self.paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=self.variation_settings_category_list,
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='001')
    model_line_3 = self.createModelLine(model=model_3,
        id='model_line_3',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[30000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary', 'base_amount/gross_salary'])

    # define two models with same references and same dates
    # but different version number
    model_4 = self.paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=self.variation_settings_category_list,
        reference='fabien_model_level_2_2009',
        effective_date=DateTime(2009, 01, 1),
        expiration_date=DateTime(2009, 06, 30),
        version='002')
    model_line_4 = self.createModelLine(model=model_4,
        id='model_line_4',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[40000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'])

    model_5 = self.paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=self.variation_settings_category_list,
        reference='fabien_model_level_2_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='001')
    model_line_5 = self.createModelLine(model=model_5,
        id='model_line_5',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[50000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'])

    # third level : define two models with same references and same dates
    # but different version number
    model_6 = self.paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=self.variation_settings_category_list,
        reference='fabien_model_level_3_2009',
        effective_date=DateTime(2009, 01, 1),
        expiration_date=DateTime(2009, 06, 30),
        version='002')
    model_line_6 = self.createModelLine(model=model_6,
        id='model_line_6',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[60000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'])

    model_7 = self.paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=self.variation_settings_category_list,
        reference='fabien_model_level_3_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='001')
    model_line_7 = self.createModelLine(model=model_7,
        id='model_line_7',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[70000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'])

    transaction.commit()
    self.tic()

    # create the paysheet
    paysheet = self.portal.accounting_module.newContent(
                              portal_type='Pay Sheet Transaction',
                              specialise_value=model_1,
                              start_date=DateTime(2009, 07, 1),
                              stop_date=DateTime(2009, 07, 31),
                              price_currency_value=eur)
    specialise_value = paysheet.getSpecialiseValue()

    # design some heritance trees, and check them:
    model_1.setSpecialiseValue(model_4)
    model_4.setSpecialiseValue(model_6)
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(specialise_value.getInheritanceModelTreeAsList(),
        [model_1, model_4, model_6])
    self.assertEquals(specialise_value.getInheritanceEffectiveModelTreeAsList(paysheet),
        [model_2,])

    model_1.setSpecialiseValue(None)
    model_2.setSpecialiseValue(model_5)
    model_5.setSpecialiseValue(model_6)
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(specialise_value.getInheritanceModelTreeAsList(),
        [model_1,])
    self.assertEquals(specialise_value.getInheritanceEffectiveModelTreeAsList(paysheet),
        [model_2, model_5, model_7])

    paysheet.setSpecialiseValue(model_3)
    model_3.setSpecialiseValue(model_5)
    model_5.setSpecialiseValue(model_6)
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(specialise_value.getInheritanceModelTreeAsList(),
        [model_1,])
    self.assertEquals(specialise_value.getInheritanceEffectiveModelTreeAsList(paysheet),
        [model_2, model_5, model_7])

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPayroll))
  return suite
