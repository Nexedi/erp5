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
from Products.ERP5.tests.testBPMCore import TestBPMMixin
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import reindex
from DateTime import DateTime
import transaction

class TestNewPayrollMixin(ERP5ReportTestCase, TestBPMMixin):
  normal_resource_use_category_list = ['payroll/base_salary']
  invoicing_resource_use_category_list = ['payroll/tax']

  def getTitle(self):
    return "Payroll"

  def afterSetUp(self):
    """Prepare the test."""
    self.createCategories()
    self.setSystemPreference()

  @reindex
  def beforeTearDown(self):
    transaction.abort()
    for module in (
      self.portal.organisation_module,
      self.portal.person_module,
      self.portal.paysheet_model_module,
      self.portal.accounting_module,
      self.portal.business_process_module,
      self.portal.service_module,
      self.portal.portal_simulation,):
      module.manage_delObjects(list(module.objectIds()))


  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('admin', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('admin').__of__(uf)
    newSecurityManager(None, user)

  @reindex
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
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in path.objectIds() :
          path = path.newContent(
                    portal_type='Category',
                    id=cat,
                    title=cat.replace('_', ' ').title(),)
        else:
          path = path[cat]
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ('tax_category/employer_share',
            'tax_category/employee_share',
            'base_amount/deductible_tax',
            'base_amount/base_salary',
            'base_amount/net_salary',
            'grade/worker',
            'grade/engineer',
            'quantity_unit/time/month',
            'product_line/labour',
            'product_line/state_insurance',
            'use/payroll/tax',
            'use/payroll/base_salary',
            'trade_phase/payroll/france/urssaf',
            'time/hours',
            'salary_range/france',
            'salary_range/france/slice_a',
            'salary_range/france/slice_b',
            'salary_range/france/slice_c',
            'salary_range/france/forfait',
            'salary_range/france/slice_0_to_200',
            'salary_range/france/slice_200_to_400',
            'salary_range/france/slice_400_to_5000',
            'salary_range/france/slice_600_to_800',
            'marital_status/married',
            'marital_status/single',
           )

  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_mrp', 'erp5_bpm', 'erp5_payroll')

  def createService(self):
    module = self.portal.getDefaultModule(portal_type='Service')
    return module.newContent(portal_type='Service')

  def stepCreateUrssafService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Urssaf',
        product_line='state_insurance', quantity_unit='time/month',
        variation_base_category_list=['tax_category', 'salary_range'],
        use='payroll/tax')
    node.setVariationCategoryList(['tax_category/employee_share',
                                   'tax_category/employer_share'])
    sequence.edit(urssaf_service = node)

  def stepCreateLabourService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Labour', quantity_unit='time/month',
        product_line='labour', use='payroll/base_salary')
    sequence.edit(labour_service = node)

  def stepCreateBonusService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Bonus', quantity_unit='time/month',
        variation_base_category_list=['tax_category'],
        product_line='labour', use='payroll/base_salary')
    node.setVariationCategoryList(['tax_category/employee_share',
                                   'tax_category/employer_share'])
    sequence.edit(bonus_service = node)

  def stepCreateOldAgeInsuranaceService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Old Age Insurance', quantity_unit='time/month',
        variation_base_category_list=['tax_category', 'salary_range'],
        product_line='state_insurance', use='payroll/tax')
    node.setVariationCategoryList(['tax_category/employee_share',
                                   'tax_category/employer_share'])
    sequence.edit(old_age_insurance_service = node)

  def stepCreateSicknessInsuranceService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Sickness Insurance', quantity_unit='time/month',
        variation_base_category_list=['tax_category', 'salary_range'],
        product_line='state_insurance', use='payroll/tax')
    node.setVariationCategoryList(['tax_category/employee_share',
                                   'tax_category/employer_share'])
    sequence.edit(sickness_insurance_service = node)

  def createModel(self):
    module = self.portal.getDefaultModule(portal_type='Pay Sheet Model')
    return module.newContent(portal_type='Pay Sheet Model')

  def createPerson(self):
    module = self.portal.getDefaultModule(portal_type='Person')
    return module.newContent(portal_type='Person')

  def createOrganisation(self):
    module = self.portal.getDefaultModule(portal_type='Organisation')
    return module.newContent(portal_type='Organisation')

  def stepCreateEmployee(self, sequence=None, **kw):
    employer = sequence.get('employer')
    node = self.createPerson()
    node.edit(title='Employee',
              career_subordination_value=employer)
    sequence.edit(employee = node)

  def stepCreateEmployer(self, sequence=None, **kw):
    node = self.createOrganisation()
    node.edit(title='Employer')
    sequence.edit(employer = node)

  def stepCreateBasicModel(self, sequence=None, **kw):
    model = self.createModel()
    employer = sequence.get('employer')
    employee = sequence.get('employee')
    model.edit(destination_section_value=employer,
        source_section_value=employee)
    sequence.edit(model = model)

  def addSlice(self, model, slice, min_value, max_value, base_id='cell'):
    '''add a new slice in the model'''
    slice_value = model.newCell(slice, portal_type='Pay Sheet Model Slice',
        base_id=base_id)
    slice_value.setQuantityRangeMax(max_value)
    slice_value.setQuantityRangeMin(min_value)
    return slice_value

  def stepCreateModelWithSlices(self, sequence=None, **kw):
    model = self.createModel()
    employer = sequence.get('employer')
    employee = sequence.get('employee')
    model.edit(destination_section_value=employer,
        source_section_value=employee)
    model.setVariationSettingsCategoryList(\
        ['salary_range/france'])
    self.addSlice(model, 'salary_range/france/slice_0_to_200', 0, 200)
    self.addSlice(model, 'salary_range/france/slice_200_to_400', 200, 400)
    self.addSlice(model, 'salary_range/france/slice_400_to_5000', 400, 5000)
    self.addSlice(model, 'salary_range/france/slice_600_to_800', 600, 800)
    sequence.edit(model = model)

  def createModelLine(self, document, **kw):
    return document.newContent(portal_type='Pay Sheet Model Line', **kw)

  def stepModelCreateUrssafModelLine(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Urssaf',
                    reference='urssaf_model_line',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(urssaf_model_line = model_line)

  def stepModelCreateUrssafModelLineWithSlices(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Urssaf',
                    reference='urssaf_model_line_2',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    variation_category_list=['tax_category/employee_share',
                                       'tax_category/employer_share',
                                       'salary_range/france/slice_0_to_200',
                                       'salary_range/france/slice_200_to_400',
                                       'salary_range/france/slice_400_to_5000'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(urssaf_model_line_with_slices = model_line)

  def stepModelCreateUrssafModelLineWithComplexSlices(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Urssaf',
                    reference='urssaf_model_line_3',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    variation_category_list=['tax_category/employee_share',
                                       'tax_category/employer_share',
                                       'salary_range/france/slice_200_to_400',
                                       'salary_range/france/slice_600_to_800'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(urssaf_model_line_with_slices = model_line)

  def stepPaysheetCreateUrssafModelLine(self, sequence=None, **kw):
    '''The model line created here have the same reference than the model line
    created in stepModelCreateUrssafModelLine. This is used for line
    overloading tests'''
    paysheet = sequence.get('paysheet')
    model_line = self.createModelLine(paysheet)
    model_line.edit(title='Urssaf',
                    reference='urssaf_model_line',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(urssaf_model_line = model_line)

  def stepUrssafModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.5, tax_category='employer_share')

  def stepUrssafModelLineCreateMovementsWithQuantityOnly(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(quantity=-100, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(quantity=-200, tax_category='employer_share')

  def stepUrssafModelLineWithSlicesCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line_with_slices')
    cell1 = model_line.newCell('tax_category/employee_share',
        'salary_range/france/slice_0_to_200',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, tax_category='employee_share',
        salary_range='france/slice_0_to_200')
    cell2 = model_line.newCell('tax_category/employer_share',
        'salary_range/france/slice_0_to_200',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.2, tax_category='employer_share',
        salary_range='france/slice_0_to_200')
    cell3 = model_line.newCell('tax_category/employee_share',
        'salary_range/france/slice_200_to_400',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell3.edit(price=0.3, tax_category='employee_share',
        salary_range='france/slice_200_to_400')
    cell4 = model_line.newCell('tax_category/employer_share',
        'salary_range/france/slice_200_to_400',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell4.edit(price=0.4, tax_category='employer_share',
        salary_range='france/slice_200_to_400')
    cell5 = model_line.newCell('tax_category/employee_share',
        'salary_range/france/slice_400_to_5000',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell5.edit(price=0.5, tax_category='employee_share',
        salary_range='france/slice_400_to_5000')
    cell6 = model_line.newCell('tax_category/employer_share',
        'salary_range/france/slice_400_to_5000',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell6.edit(price=0.6, tax_category='employer_share',
        salary_range='france/slice_400_to_5000')

  def stepUrssafModelLineWithComplexSlicesCreateMovements(self,
      sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line_with_slices')
    cell1 = model_line.newCell('tax_category/employee_share',
        'salary_range/france/slice_200_to_400',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, tax_category='employee_share',
        salary_range='france/slice_200_to_400')
    cell2 = model_line.newCell('tax_category/employer_share',
        'salary_range/france/slice_200_to_400',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.2, tax_category='employer_share',
        salary_range='france/slice_200_to_400')
    cell3 = model_line.newCell('tax_category/employee_share',
        'salary_range/france/slice_600_to_800',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell3.edit(price=0.3, tax_category='employee_share',
        salary_range='france/slice_600_to_800')
    cell4 = model_line.newCell('tax_category/employer_share',
        'salary_range/france/slice_600_to_800',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell4.edit(price=0.4, tax_category='employer_share',
        salary_range='france/slice_600_to_800')

  def stepPaysheetUrssafModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.3, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.7, tax_category='employer_share')

  def createPaysheet(self, sequence=None, **kw):
    module = self.portal.getDefaultModule(portal_type='Pay Sheet Transaction')
    return module.newContent(portal_type='Pay Sheet Transaction')

  def stepCreateBasicPaysheet(self, sequence=None, **kw):
    paysheet = self.createPaysheet()
    paysheet.edit(title='test 1',
                  specialise_value=sequence.get('model'),
                  source_section_value=sequence.get('employee'),
                  destination_section_value=sequence.get('employer'),
                  resource_value=sequence.get('price_currency'),
                  start_date=DateTime(),
                  stop_date=DateTime()+1)
    sequence.edit(paysheet = paysheet)

  def createPaysheetLine(self, document, **kw):
    return document.newContent(portal_type='Pay Sheet Line', **kw)

  def stepPaysheetCreateLabourPaySheetLine(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line = self.createPaysheetLine(paysheet)
    paysheet_line.edit(title='Labour',
                    price=20,
                    quantity=150,
                    resource_value=sequence.get('labour_service'),
                    base_contribution_list=[ 'base_amount/base_salary'])
    sequence.edit(labour_paysheet_line = paysheet_line)

  def stepPaysheetCreateBonusPaySheetLine(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line = self.createPaysheetLine(paysheet)
    paysheet_line.edit(title='Bonus',
                    resource_value=sequence.get('bonus_service'),
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_contribution_list=[ 'base_amount/base_salary'])
    sequence.edit(bonus_paysheet_line = paysheet_line)

  def stepPaysheetCreateBonusPaySheetLineMovements(self, sequence=None, **kw):
    paysheet_line = sequence.get('bonus_paysheet_line')
    cell1 = paysheet_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(quantity=1000, price=1, tax_category='employee_share')
    cell2 = paysheet_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(quantity=1000, price=1, tax_category='employer_share')

  def checkUpdateAggregatedAmountListReturn(self, model, paysheet,
      expected_movement_to_delete_count, expected_movement_to_add_count):
    movement_dict = model.updateAggregatedAmountList(context=paysheet)
    movement_to_delete = movement_dict['movement_to_delete_list']
    movement_to_add = movement_dict['movement_to_add_list']
    self.assertEquals(len(movement_to_delete),
        expected_movement_to_delete_count)
    self.assertEquals(len(movement_to_add), expected_movement_to_add_count)

  def stepCheckUpdateAggregatedAmountListReturn(self, sequence=None, **kw):
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    self.checkUpdateAggregatedAmountListReturn(model, paysheet, 0, 2)

  def stepCheckUpdateAggregatedAmountListReturnUsingSlices(self,
      sequence=None, **kw):
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    self.checkUpdateAggregatedAmountListReturn(model, paysheet, 0, 6)

  def stepCheckUpdateAggregatedAmountListReturnUsingComplexSlices(self,
      sequence=None, **kw):
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    self.checkUpdateAggregatedAmountListReturn(model, paysheet, 0, 4)

  def stepCheckUpdateAggregatedAmountListReturnUsingPredicate(self,
      sequence=None, **kw):
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    self.checkUpdateAggregatedAmountListReturn(model, paysheet, 0, 4)

  def stepCheckUpdateAggregatedAmountListReturnAfterChangePredicate(self,
      sequence=None, **kw):
    # the marital status of the employe is change in the way that sickness
    # insurance model_line will not be applied but old age insurance yes.
    # So two movements will be deleted (from sickness insurance) and two should
    # be added (from old age insurance)
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    self.checkUpdateAggregatedAmountListReturn(model, paysheet, 2, 2)

  def stepCheckUpdateAggregatedAmountListReturnAfterRemoveLine(self,
      sequence=None, **kw):
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    self.checkUpdateAggregatedAmountListReturn(model, paysheet, 2, 0)

  def stepPaysheetApplyTransformation(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet.applyTransformation()

  def stepCheckPaysheetLineAreCreated(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 2)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 2) # 2 because labour line contain no movement

  def stepCheckPaysheetLineAreCreatedUsingBonus(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 3)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 4) # 4 because labour line contain no movement
                               # 2 for bonus, and 2 for urssaf

  def stepCheckThereIsOnlyOnePaysheetLine(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 1)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 0) # 0 because labour line contain no movement

  def stepCheckPaysheetLineAreCreatedUsingSlices(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 2)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 6) # 6 because labour line contain no movement and
                               # because of the 3 slice and 2 tax_categories

  def stepCheckPaysheetLineAreCreatedUsingComplexSlices(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 2)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 4) # 4 because labour line contain no movement and
                               # because of the 2 slice and 2 tax_categories

  def stepCheckPaysheetLineAreCreatedUsingWith3Lines(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 3)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 4) # 4 because labour line contain no movement and
                               # because of the two lines and 2 tax_categories
                               # (urssaf and sickness insurance. old age
                               # insurance does not match predicate)

  def stepCheckPaysheetLineAmounts(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineWithBonusAmounts(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 4000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 4000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      elif service == 'Bonus':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getTotalPrice(), 1000)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getTotalPrice(), 1000)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineAmountsWithQuantityOnly(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), -100)
        self.assertEquals(cell1.getPrice(), 1)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), -200)
        self.assertEquals(cell2.getPrice(), 1)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineAmountsUsingSlices(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share',
            'salary_range/france/slice_0_to_200')
        self.assertEquals(cell1.getQuantity(), 200)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share',
            'salary_range/france/slice_0_to_200')
        self.assertEquals(cell2.getQuantity(), 200)
        self.assertEquals(cell2.getPrice(), 0.2)
        cell3 = paysheet_line.getCell('tax_category/employee_share',
            'salary_range/france/slice_200_to_400')
        self.assertEquals(cell3.getQuantity(), 200)
        self.assertEquals(cell3.getPrice(), 0.3)
        cell4 = paysheet_line.getCell('tax_category/employer_share',
            'salary_range/france/slice_200_to_400')
        self.assertEquals(cell4.getQuantity(), 200)
        self.assertEquals(cell4.getPrice(), 0.4)
        cell5 = paysheet_line.getCell('tax_category/employee_share',
            'salary_range/france/slice_400_to_5000')
        self.assertEquals(cell5.getQuantity(), 2600)
        self.assertEquals(cell5.getPrice(), 0.5)
        cell6 = paysheet_line.getCell('tax_category/employer_share',
            'salary_range/france/slice_400_to_5000')
        self.assertEquals(cell6.getQuantity(), 2600)
        self.assertEquals(cell6.getPrice(), 0.6)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineAmountsUsingComplexSlices(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share',
            'salary_range/france/slice_200_to_400')
        self.assertEquals(cell1.getQuantity(), 200)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share',
            'salary_range/france/slice_200_to_400')
        self.assertEquals(cell2.getQuantity(), 200)
        self.assertEquals(cell2.getPrice(), 0.2)
        cell3 = paysheet_line.getCell('tax_category/employee_share',
            'salary_range/france/slice_600_to_800')
        self.assertEquals(cell3.getQuantity(), 200)
        self.assertEquals(cell3.getPrice(), 0.3)
        cell4 = paysheet_line.getCell('tax_category/employer_share',
            'salary_range/france/slice_600_to_800')
        self.assertEquals(cell4.getQuantity(), 200)
        self.assertEquals(cell4.getPrice(), 0.4)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineAmountsWithSicknessInsuranceAndUrssaf(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      elif service == 'Sickness Insurance':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.4)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.3)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineAmountsWithOldAgeInsuranceAndUrssaf(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      elif service == 'Old Age Insurance':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.5)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.8)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckUpdateAggregatedAmountListReturnNothing(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    model = sequence.get('model')
    movement_dict = model.updateAggregatedAmountList(context=paysheet)
    movement_to_delete = movement_dict['movement_to_delete_list']
    movement_to_add = movement_dict['movement_to_add_list']
    self.assertEquals(len(movement_to_delete), 0)
    self.assertEquals(len(movement_to_add), 0)

  def stepCreateUrssafRoubaixOrganisation(self, sequence=None, **kw):
    node = self.createOrganisation()
    node.edit(title='Urssaf de Roubaix Tourcoing')
    sequence.edit(urssaf_roubaix = node)

  def stepModifyBusinessPathTradePhase(self, sequence=None, **kw):
    business_path = sequence.get('business_path')
    business_path.setTradePhaseList(['trade_phase/payroll/france/urssaf'])
    business_path.setSourceDecisionValue(sequence.get('urssaf_roubaix'))
    business_path.setDeliveryBuilderList(('portal_deliveries/pay_sheet_builder',))
    sequence.edit(business_path=business_path)

  def stepModelSpecialiseBusinessProcess(self, sequence=None, **kw):
    model = sequence.get('model')
    business_process = sequence.get('business_process')
    model.setSpecialiseValueList(business_process)

  def stepCheckSourceSectionOnMovements(self, sequence=None, **kw):
    '''Check that the cell contain urssaf_roubaix as source section. This should
    be the case if getAggregatedAmountList from PaySheetModelLine is able to
    use Business Process to find the good source_section'''
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    urssaf_roubaix = sequence.get('urssaf_roubaix')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getSourceSectionValue(), urssaf_roubaix)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getSourceSectionValue(), urssaf_roubaix)
      elif service == 'Labour':
        pass
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepModelSetCategories(self, sequence=None, **kw):
    model = sequence.get('model')
    currency = sequence.get('price_currency')
    employer = sequence.get('employer')
    employee = sequence.get('employee')
    model.edit(\
        price_currency_value=currency,
        default_payment_condition_trade_date='custom',
        default_payment_condition_payment_date=DateTime(2009/05/25),
        work_time_annotation_line_quantity=151.67,
        work_time_annotation_line_quantity_unit='time/hours',
        )

  def stepPaysheetSetModelAndApplyIt(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    model = sequence.get('model')
    paysheet.setSpecialiseValue(model)
    paysheet.PaySheetTransaction_applyModel(force=1)
   
  def stepCheckCategoriesOnPaySheet(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    employer = sequence.get('employer')
    employee = sequence.get('employee')
    currency = sequence.get('price_currency')
    self.assertEquals(paysheet.getSourceSectionValue(), employee)
    self.assertEquals(paysheet.getDestinationSectionValue(), employer)
    self.assertEquals(paysheet.getPriceCurrencyValue(), currency)
    self.assertEquals(paysheet.getDefaultPaymentConditionTradeDate(), 'custom')
    self.assertEquals(paysheet.getDefaultPaymentConditionPaymentDate(),
        DateTime(2009/05/25))
    self.assertEquals(paysheet.getWorkTimeAnnotationLineQuantity(), 151.67)
    self.assertEquals(paysheet.getWorkTimeAnnotationLineQuantityUnit(),
      'time/hours')

  def stepCheckPaysheetContainNoAnnotationLine(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    self.assertEquals(len(paysheet.contentValues(portal_type=\
        'Annotation Line')), 0)

  def stepCheckPaysheetContainOneAnnotationLine(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    self.assertEquals(len(paysheet.contentValues(portal_type=\
        'Annotation Line')), 1)

  def stepCheckPaysheetContainNoPaymentCondition(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    self.assertEquals(len(paysheet.contentValues(portal_type=\
        'Payment Condition')), 0)

  def stepCheckPaysheetContainOnePaymentCondition(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    self.assertEquals(len(paysheet.contentValues(portal_type=\
        'Payment Condition')), 1)

  def stepCreateModelTree(self, sequence=None, **kw):
    '''
      Create three models inheriting from each other. Set slices values on a
      model.

      the inheritance tree look like this :

                                Employee Model
                                 /        \
                                /          \
                               /            \
                    Company Model         Second Company Alt
                         /
                        /
                       /
                Country Model
    '''
    model_employee = self.createModel()
    model_employee.edit(title='Employee Model', reference='model_employee',
        variation_settings_category_list='salary_range/france')
    model_company = self.createModel()
    model_company.edit(title='Company Model', reference='model_company',
        variation_settings_category_list='salary_range/france')
    model_company_alt = self.createModel()
    model_company_alt.edit(title='Second Company Model',
        reference='model_company_alt',
        variation_settings_category_list='salary_range/france')
    model_country = self.createModel()
    model_country.edit(title='Country Model', reference='model_country',
        variation_settings_category_list='salary_range/france')
    # add some cells in the models
    slice1 = model_employee.newCell('salary_range/france/slice_a',
                            portal_type='Pay Sheet Model Slice',
                            base_id='cell')
    slice1.setQuantityRangeMin(0)
    slice1.setQuantityRangeMax(1)

    slice2 = model_company.newCell('salary_range/france/slice_b',
                            portal_type='Pay Sheet Model Slice',
                            base_id='cell')
    slice2.setQuantityRangeMin(2)
    slice2.setQuantityRangeMax(3)

    slice3 = model_company_alt.newCell('salary_range/france/forfait',
                            portal_type='Pay Sheet Model Slice',
                            base_id='cell')
    slice3.setQuantityRangeMin(20)
    slice3.setQuantityRangeMax(30)

    slice4 = model_country.newCell('salary_range/france/slice_c',
                            portal_type='Pay Sheet Model Slice',
                            base_id='cell')
    slice4.setQuantityRangeMin(4)
    slice4.setQuantityRangeMax(5)

    # inherite from each other
    model_employee.setSpecialiseValueList((model_company, model_company_alt))
    model_company.setSpecialiseValue(model_country)

    sequence.edit(model_employee = model_employee,
                  model_company = model_company,
                  model_company_alt = model_company_alt,
                  model_country = model_country)

  def assertCell(self, model, salary_range, range_min, range_max):
    cell = model.getCell(salary_range)
    self.assertNotEqual(cell, None)
    self.assertEqual(cell.getQuantityRangeMin(), range_min)
    self.assertEqual(cell.getQuantityRangeMax(), range_max)

  def assertCellIsNone(self, model, salary_range):
    cell = model.getCell(salary_range)
    self.assertEqual(cell, None)

  def stepCheckgetCellResults(self, sequence=None, **kw):
    model_employee = sequence.get('model_employee')
    model_company = sequence.get('model_company')
    model_company_alt = sequence.get('model_company_alt')
    model_country = sequence.get('model_country')

    # check model_employee could access all cells
    self.assertCell(model_employee, 'salary_range/france/slice_a', 0, 1)
    self.assertCell(model_employee, 'salary_range/france/slice_b', 2, 3)
    self.assertCell(model_employee, 'salary_range/france/forfait', 20, 30)
    self.assertCell(model_employee, 'salary_range/france/slice_c', 4, 5)

    # check model_company could access just it's own cell
    # and this of the country model
    self.assertCellIsNone(model_company, 'salary_range/france/slice_a')
    self.assertCell(model_company, 'salary_range/france/slice_b', 2, 3)
    self.assertCellIsNone(model_company, 'salary_range/france/forfait')
    self.assertCell(model_company, 'salary_range/france/slice_c', 4, 5)

    # model_company_alt could access just it's own cell
    self.assertCellIsNone(model_company_alt, 'salary_range/france/slice_a')
    self.assertCellIsNone(model_company_alt, 'salary_range/france/slice_b')
    self.assertCell(model_company_alt, 'salary_range/france/forfait', 20, 30)
    self.assertCellIsNone(model_company_alt, 'salary_range/france/slice_c')

    # check model_country could access just it's own cell
    self.assertCellIsNone(model_country, 'salary_range/france/slice_a')
    self.assertCellIsNone(model_country, 'salary_range/france/slice_b')
    self.assertCellIsNone(model_country, 'salary_range/france/forfait')
    self.assertCell(model_country, 'salary_range/france/slice_c', 4, 5)

  def stepModelCreateIntermediateModelLine(self, sequence=None, **kw):
    '''
      create an intermediate_line wich contribute to tax and applied to
      base_salary
    '''
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='intermediate line',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    reference='intermediate_line',
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_contribution_list=['base_amount/deductible_tax'],
                    base_application_list=['base_amount/base_salary'],
                    create_line=False,)
    sequence.edit(intermediate_model_line = model_line)

  def stepModelCreateAppliedOnTaxModelLine(self, sequence=None, **kw):
    '''
      create a model line applied on tax
    '''
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='line applied on intermediate line',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    reference='line_applied_on_intermediate_line',
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_contribution_list=['base_amount/net_salary'],
                    base_application_list=['base_amount/deductible_tax'])
    sequence.edit(model_line_applied_on_tax = model_line)

  def stepIntermediateModelLineCreateMovements(self, sequence=None,
      **kw):
    model_line = sequence.get('intermediate_model_line')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.2, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.2, tax_category='employer_share')

  def stepAppliedOnTaxModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('model_line_applied_on_tax')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.5, tax_category='employer_share')

  def stepModelCreateOldAgeInsuranceModelLine(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Old Age Insurance',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('old_age_insurance_service'),
                    reference='old_age_insurance',
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(old_age_insurance = model_line)

  def stepOldAgeInsuranceModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('old_age_insurance')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.5, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.8, tax_category='employer_share')

  def stepModelCreateSicknessInsuranceModelLine(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Sickness Insurance',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('sickness_insurance_service'),
                    reference='sickness_insurance',
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(sickness_insurance = model_line)

  def stepSicknessInsuranceModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('sickness_insurance')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.4, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.3, tax_category='employer_share')

  def stepCheckPaysheetIntermediateLines(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')

    # paysheet should contain only two lines (labour and urssaf, but not
    # intermediate urssaf
    self.assertEquals(len(paysheet.contentValues(portal_type=\
        'Pay Sheet Line')), 2)

    # check amounts
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 600) # here it's 600 of tax
                                  # because of the intermediate line (3000*0.2)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 600) # here it's 600 of tax
                                  # because of the intermediate line (3000*0.2)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepPaysheetCreateModelLine(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    model_line = self.createModelLine(paysheet)
    model_line.edit(title='model line in the paysheet',
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('old_age_insurance_service'),
                    reference='model_line_in_the_payesheet',
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(model_line_on_paysheet = model_line)

  def stepPaysheetModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('model_line_on_paysheet')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.5, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.8, tax_category='employer_share')

  def stepCheckUpdateAggregatedAmountListReturnWithModelLineOnPaysheet(self,
      sequence=None, **kw):
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    self.checkUpdateAggregatedAmountListReturn(model, paysheet, 0, 4)

  def stepCheckPaysheetLineAreCreatedWithModelLineOnPaysheet(self,
      sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 3)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 4) # 2 from the urssaf paysheet line
                               # 2 from the line create with the paysheet model
                               # line
    self.assertEqual(len(paysheet.contentValues(portal_type=\
        'Pay Sheet Model Line')), 1)

  def stepCheckPaysheetLineFromModelLineAmounts(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      elif service == 'Old Age Insurance':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.5)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.8)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepModelModifyUrssafModelLine(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    # modify price on movements :
    cell_1 = model_line.getCell('tax_category/employee_share',
        base_id='movement')
    self.assertNotEquals(cell_1, None)
    cell_1.edit(price=0.2)
    cell_2 = model_line.getCell('tax_category/employer_share',
        base_id='movement')
    self.assertNotEquals(cell_2, None)
    cell_2.edit(price=0.6)

  def stepModelDelUrssafModelLine(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    model = sequence.get('model')
    model.manage_delObjects(model_line.getId())

  def stepCheckPaysheetLineNewAmountsAfterUpdate(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.2)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.6)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineLabourAmountOnly(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetModelLineOverLoadAmounts(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('tax_category/employee_share')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.3)
        cell2 = paysheet_line.getCell('tax_category/employer_share')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.7)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetConsistency(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    self.assertEquals([], paysheet.checkConsistency())

  def stepCheckModelConsistency(self, sequence=None, **kw):
    model = sequence.get('model')
    self.assertEquals([], model.checkConsistency())

  def stepCheckServiceConsistency(self, sequence=None, **kw):
    service = sequence.get('urssaf_service')
    self.assertEquals([], service.checkConsistency())

  def stepAddPredicateOnOldAgeInsuranceModelLineForSinglePerson(self,
      sequence=None, **kw):
    model_line = sequence.get('old_age_insurance')
    model_line.setMembershipCriterionBaseCategoryList(\
        ['source_marital_status'])
    model_line.setMembershipCriterionCategoryList(\
        ['source_marital_status/marital_status/single'])

  def stepAddPredicateOnSicknessInsuranceModelLineForMarriedPerson(self,
      sequence=None, **kw):
    model_line = sequence.get('sickness_insurance')
    model_line.setMembershipCriterionBaseCategoryList(\
        ['source_marital_status'])
    model_line.setMembershipCriterionCategoryList(\
        ['source_marital_status/marital_status/married'])

  def stepSetMaritalStatusMarriedOnEmployee(self, sequence=None, **kw):
    employee = sequence.get('employee')
    employee.setMaritalStatus('married')

  def stepSetMaritalStatusSingleOnEmployee(self, sequence=None, **kw):
    employee = sequence.get('employee')
    employee.setMaritalStatus('single')

  def stepModelTreeAddAnnotationLines(self, sequence=None, **kw):
    model_employee = sequence.get('model_employee')
    model_employee.newContent(id='over_time_duration',
                              title='Over time duration',
                              portal_type='Annotation Line',
                              reference='over_time_duration',
                              quantity=1)
    model_company = sequence.get('model_company')
    model_company.newContent(id='worked_time_duration',
                             title='Worked time duration',
                             portal_type='Annotation Line',
                             reference='worked_time_duration',
                             quantity=2)
    model_company_alt = sequence.get('model_company_alt')
    model_company_alt.newContent(id='social_insurance',
                                 title='Social insurance',
                                 portal_type='Annotation Line',
                                 reference='social_insurance',
                                 quantity=3)
    model_country = sequence.get('model_country')
    model_country.newContent(id='social_insurance',
                             title='Social insurance',
                             portal_type='Annotation Line',
                             reference='social_insurance',
                             quantity=4)

  def stepCheckInheritanceModelReferenceDict(self, sequence=None, **kw):
    model_employee = sequence.get('model_employee')
    model_employee_url = model_employee.getRelativeUrl()
    model_company_url = sequence.get('model_company').getRelativeUrl()
    model_company_alt_url = sequence.get('model_company_alt').getRelativeUrl()
    model_country_url = sequence.get('model_country').getRelativeUrl()
    
    model_reference_dict = model_employee.getInheritanceReferenceDict(\
        portal_type_list=('Annotation Line',))
    self.assertEquals(len(model_reference_dict), 3) # there is 4 model but two
                                                    # models have the same
                                                    # reference.
    self.assertEquals(model_reference_dict.has_key(model_employee_url), True)
    self.assertEquals(model_reference_dict[model_employee_url],
        ['over_time_duration'])
    self.assertEquals(model_reference_dict.has_key(model_company_url), True)
    self.assertEquals(model_reference_dict[model_company_url],
        ['worked_time_duration'])
    self.assertEquals(model_reference_dict.has_key(model_company_alt_url), True)
    self.assertEquals(model_reference_dict[model_company_alt_url],
        ['social_insurance'])
    self.assertNotEquals(model_reference_dict.has_key(model_country_url), True)
    
    # check the object list :
    paysheet = self.createPaysheet()
    paysheet.setSpecialiseValue(model_employee)
    object_list = paysheet.getInheritedObjectValueList(portal_type_list=\
        ('Annotation Line',))
    self.assertEquals(len(object_list), 3) # one line have the same reference
                                           # than another, so each reference
                                           # should be prensent only one time
                                           # in the list
    over_time_duration = paysheet.getAnnotationLineFromReference(\
        'over_time_duration')
    self.assertNotEquals(over_time_duration, None)
    over_time_duration.getQuantity(1)
    worked_time_duration = paysheet.getAnnotationLineFromReference(\
        'worked_time_duration')
    self.assertNotEquals(worked_time_duration, None)
    worked_time_duration.getQuantity(2)
    social_insurance = paysheet.getAnnotationLineFromReference(\
        'social_insurance')
    self.assertNotEquals(social_insurance, None)
    social_insurance.getQuantity(3)

class TestNewPayroll(TestNewPayrollMixin):

  BUSINESS_PATH_CREATION_SEQUENCE_STRING = """
               CreateBusinessProcess
               CreateBusinessPath
               CreateUrssafRoubaixOrganisation
               ModifyBusinessPathTradePhase
               ModelSpecialiseBusinessProcess
               Tic
  """
  COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING = """
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreatePriceCurrency
               CreateBasicModel
               ModelCreateUrssafModelLine
               UrssafModelLineCreateMovements
               CreateBasicPaysheet
               PaysheetCreateLabourPaySheetLine
               Tic
  """ + BUSINESS_PATH_CREATION_SEQUENCE_STRING

  def test_modelGetCell(self):
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
    sequence_list = SequenceList()
    sequence_string = """
               CreateModelTree
               CheckgetCellResults
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_applyModelSetCategories(self):
    '''
      check that when the model is set on the Pay Sheet Transaction, properties
      like source, destination, currency, ... and sub-object like
      annotation_line are copied from the model to the Pay Sheet Transaction
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreateBasicModel
               CreatePriceCurrency
               ModelSetCategories
               CreateBasicPaysheet
               PaysheetSetModelAndApplyIt
               CheckCategoriesOnPaySheet
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_applyModelTwice(self):
    '''
      apply model twice does not copy subdocument twice
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreateBasicModel
               CreatePriceCurrency
               ModelSetCategories
               CreateBasicPaysheet
               CheckPaysheetContainNoAnnotationLine
               CheckPaysheetContainNoPaymentCondition
               PaysheetSetModelAndApplyIt
               CheckPaysheetContainOneAnnotationLine
               CheckPaysheetContainOnePaymentCondition
               PaysheetSetModelAndApplyIt
               CheckPaysheetContainOneAnnotationLine
               CheckPaysheetContainOnePaymentCondition
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_checkConsistency(self):
    '''
      minimal test for checkConsistency on a Pay Sheet Transaction and it's
      subdocuments (may have to be updated when we'll add more constraints).
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CheckPaysheetConsistency
               CheckModelConsistency
               CheckServiceConsistency
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_basicPaySheetCalculation(self):
    '''
      test applyTransformation method. It should create new movements
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineAmounts
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmounts
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_intermediateLines(self):
    '''
      Intermediate lines are paysheet model lines usefull to calcul, but we
      don't want to have on paysheet. So a checkbox on paysheet model lines
      permit to create it or not (created by default)
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreateBasicModel
               ModelCreateIntermediateModelLine
               ModelCreateAppliedOnTaxModelLine
               IntermediateModelLineCreateMovements
               AppliedOnTaxModelLineCreateMovements
               CreateBasicPaysheet
               PaysheetCreateLabourPaySheetLine
  """ + self.BUSINESS_PATH_CREATION_SEQUENCE_STRING + """
               PaysheetApplyTransformation
               Tic
               CheckPaysheetIntermediateLines
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_modelLineInPaysheet(self):
    '''
      Put a Pay Sheet Model Line in Pay Sheet Transaction. This line will
      be like editable line
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CreateOldAgeInsuranaceService
               PaysheetCreateModelLine
               PaysheetModelLineCreateMovements
               CheckUpdateAggregatedAmountListReturnWithModelLineOnPaysheet
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedWithModelLineOnPaysheet
               CheckPaysheetLineFromModelLineAmounts
               CheckUpdateAggregatedAmountListReturnNothing
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_updateModifyMovements(self):
    '''
      Calculate the paySheet using a model, modify one value in the model and
      check that updateAggregatedAmount return nothing but modifed movements
      that need to be modified
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineAmounts
               CheckUpdateAggregatedAmountListReturnNothing
               ModelModifyUrssafModelLine
               CheckUpdateAggregatedAmountListReturnNothing
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineNewAmountsAfterUpdate
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineNewAmountsAfterUpdate
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_updateAddMovements(self):
    '''
      Calculate the paySheet using a model, add a model line in the model 
      and check that updateAggregatedAmount add the movements corresponding
      to this model_line
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineAmounts
               CheckUpdateAggregatedAmountListReturnNothing
               CreateSicknessInsuranceService
               ModelCreateSicknessInsuranceModelLine
               SicknessInsuranceModelLineCreateMovements
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedUsingWith3Lines
               CheckPaysheetLineAmountsWithSicknessInsuranceAndUrssaf
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmountsWithSicknessInsuranceAndUrssaf
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_updateRemoveMovements(self):
    '''
      Calculate the paySheet using a model, delete a model line in the model 
      and check that updateAggregatedAmount remove the movements corresponding
      to this model_line
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineAmounts
               CheckUpdateAggregatedAmountListReturnNothing
               ModelDelUrssafModelLine
               CheckUpdateAggregatedAmountListReturnAfterRemoveLine
               PaysheetApplyTransformation
               Tic
               CheckThereIsOnlyOnePaysheetLine
               CheckPaysheetLineLabourAmountOnly
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineLabourAmountOnly
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_modelLineOverLoad(self):
    '''
      Check it's possible to overload a model line from the model tree by
      having a model line with the same reference in the paysheet.
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               PaysheetCreateUrssafModelLine
               PaysheetUrssafModelLineCreateMovements
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetModelLineOverLoadAmounts
               CheckUpdateAggregatedAmountListReturnNothing
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_sourceSectionIsSetOnMovements(self):
    '''
      check that after apply transformation, source section is set on movment
      (using Business Process)
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               PaysheetApplyTransformation
               Tic
               CheckSourceSectionOnMovements
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_sliceOnModelLine(self):
    '''
      It's possible to define some slices on model, and use it on model lines.
      Check that works and that after appy transformation, amounts are goods
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreateModelWithSlices
               Tic
               ModelCreateUrssafModelLineWithSlices
               Tic
               UrssafModelLineWithSlicesCreateMovements
               CreateBasicPaysheet
               PaysheetCreateLabourPaySheetLine
  """ + self.BUSINESS_PATH_CREATION_SEQUENCE_STRING + """
               CheckUpdateAggregatedAmountListReturnUsingSlices
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedUsingSlices
               CheckPaysheetLineAmountsUsingSlices
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmountsUsingSlices
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_complexSliceOnModelLine(self):
    '''
      Check if there is only slice_200_to_400 (without previous
      slice_0_to_200), amount paid for this tax are correct.
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreateModelWithSlices
               Tic
               ModelCreateUrssafModelLineWithComplexSlices
               Tic
               UrssafModelLineWithComplexSlicesCreateMovements
               CreateBasicPaysheet
               PaysheetCreateLabourPaySheetLine
  """ + self.BUSINESS_PATH_CREATION_SEQUENCE_STRING + """
               CheckUpdateAggregatedAmountListReturnUsingComplexSlices
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedUsingComplexSlices
               CheckPaysheetLineAmountsUsingComplexSlices
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmountsUsingComplexSlices
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_modelLineWithNonePrice(self):
    '''
      test the creation of lines when the price is not set, but only the
      quantity. This means that no ratio is applied on this line.
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreatePriceCurrency
               CreateBasicModel
               ModelCreateUrssafModelLine
               UrssafModelLineCreateMovementsWithQuantityOnly
               CreateBasicPaysheet
               PaysheetCreateLabourPaySheetLine
  """ + self.BUSINESS_PATH_CREATION_SEQUENCE_STRING + """
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineAmountsWithQuantityOnly
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmountsWithQuantityOnly
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_predicateOnModelLine(self):
    '''
      Check predicates can be used on model lines to select a line or not.
      1 - employee have married marital status so Sickness Insurance tax
          should be applied, and Old age insurance should not be
      2 - employee marital status is changed to single. So after re-apply 
          the transformation, Sickness Insurance tax sould not be
          applied (and it's movements should be removed) but Old age insurance
          should be applied (and two movements should be created).
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CreateOldAgeInsuranaceService
               ModelCreateOldAgeInsuranceModelLine
               OldAgeInsuranceModelLineCreateMovements
               AddPredicateOnOldAgeInsuranceModelLineForSinglePerson
               CreateSicknessInsuranceService
               ModelCreateSicknessInsuranceModelLine
               SicknessInsuranceModelLineCreateMovements
               AddPredicateOnSicknessInsuranceModelLineForMarriedPerson
               SetMaritalStatusMarriedOnEmployee
               CheckUpdateAggregatedAmountListReturnUsingPredicate
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedUsingWith3Lines
               CheckPaysheetLineAmountsWithSicknessInsuranceAndUrssaf
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmountsWithSicknessInsuranceAndUrssaf
               SetMaritalStatusSingleOnEmployee
               CheckUpdateAggregatedAmountListReturnAfterChangePredicate
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedUsingWith3Lines
               CheckPaysheetLineAmountsWithOldAgeInsuranceAndUrssaf
               CheckUpdateAggregatedAmountListReturnNothing
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_paySheetCalculationWithBonus(self):
    '''
      add one more line in the paysheet that will not be hour count and rate
      (like the salary) but just a normal amount. Check applyTransformation 
      method result. It should create new movements applied on the slary + the
      bonnus
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CreateBonusService
               PaysheetCreateBonusPaySheetLine
               PaysheetCreateBonusPaySheetLineMovements
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedUsingBonus
               CheckPaysheetLineWithBonusAmounts
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineWithBonusAmounts
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_modelSubObjectInheritance(self):
    '''
      check that a model can inherite some datas from another
      the ineritance rules are the following :
       - a DATA could be a model_line, annotation_line, ratio_line
       - a model_line, annotation_line and a ratio_line have a REFERENCE
       - a model can have some DATA's
       - a model can inherite from another, that's mean :
         o At the calculation step, each DATA of the parent model will be
           checked : the DATA with a REFERENCE that's already in the child
           model will not entered in the calcul. The other will.
         o This will be repeated on each parent model and on each parent of
           the parent model,... until there is no parent model to inherite
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreateModelTree
               ModelTreeAddAnnotationLines
               CheckInheritanceModelReferenceDict
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNewPayroll))
  return suite
