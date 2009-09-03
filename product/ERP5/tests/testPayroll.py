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
from Products.ERP5.tests.testTradeModelLine import TestTradeModelLineMixin
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import reindex
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
import transaction

class TestPayrollMixin(ERP5ReportTestCase, TestTradeModelLineMixin):
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
               Tic
               ModelCreateUrssafModelLine
               UrssafModelLineCreateMovements
               CreateBasicPaysheet
               PaysheetCreateLabourPaySheetLine
               Tic
  """ + BUSINESS_PATH_CREATION_SEQUENCE_STRING


  def getTitle(self):
    return "Payroll"

  def afterSetUp(self):
    """Prepare the test."""
    self.createCategories()

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
    return ('contribution_share/employer',
            'contribution_share/employee',
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
            'use/payroll/output',
            'trade_phase/payroll/france/urssaf',
            'trade_phase/payroll/france/labour',
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
            'group/demo_group',
           )

  def getBusinessTemplateList(self):
    return TestTradeModelLineMixin.getBusinessTemplateList(self) + ('erp5_payroll', )

  def createService(self):
    module = self.portal.getDefaultModule(portal_type='Service')
    return module.newContent(portal_type='Service')

  def stepCreateUrssafService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Urssaf',
        product_line='state_insurance', quantity_unit='time/month',
        variation_base_category_list=['contribution_share', 'salary_range'],
        use='payroll/tax')
    node.setVariationCategoryList(['contribution_share/employee',
                                   'contribution_share/employer',
                                    'salary_range/france/slice_0_to_200',
                                    'salary_range/france/slice_200_to_400',
                                    'salary_range/france/slice_400_to_5000',
                                    'salary_range/france/slice_600_to_800',
                                   ])
    sequence.edit(urssaf_service = node)

  def stepCreateLabourService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Labour', quantity_unit='time/month',
        product_line='labour', use='payroll/base_salary')
    sequence.edit(labour_service = node)

  def stepCreateLabourOutputService(self, sequence=None, **kw):
    '''In case we want to have the labour line in the model, the use category
    should not be base_salary (=input) because in this case the line will be
    added on each calculation'''
    node = self.createService()
    node.edit(title='Labour', quantity_unit='time/month',
        product_line='labour', use='payroll/output')
    sequence.edit(labour_service = node)

  def stepCreateBonusService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Bonus', quantity_unit='time/month',
        variation_base_category_list=['contribution_share'],
        product_line='labour', use='payroll/base_salary')
    node.setVariationCategoryList(['contribution_share/employee',
                                   'contribution_share/employer'])
    sequence.edit(bonus_service = node)

  def stepCreateOldAgeInsuranaceService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Old Age Insurance', quantity_unit='time/month',
        variation_base_category_list=['contribution_share', 'salary_range'],
        product_line='state_insurance', use='payroll/tax')
    node.setVariationCategoryList(['contribution_share/employee',
                                   'contribution_share/employer'])
    sequence.edit(old_age_insurance_service = node)

  def stepCreateSicknessInsuranceService(self, sequence=None, **kw):
    node = self.createService()
    node.edit(title='Sickness Insurance', quantity_unit='time/month',
        variation_base_category_list=['contribution_share', 'salary_range'],
        product_line='state_insurance', use='payroll/tax')
    node.setVariationCategoryList(['contribution_share/employee',
                                   'contribution_share/employer'])
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
        source_section_value=employee,
        effective_date=DateTime(2009,01,01),
        expiration_date=DateTime(2009,12,31),
        version='001',
        reference='basic_model',
    )
    sequence.edit(model = model)

  def addSlice(self, model, slice, min_value, max_value, base_id='cell'):
    '''add a new slice in the model'''
    slice_value = model.newCell(slice, portal_type='Pay Sheet Model Slice',
        base_id=base_id)
    slice_value.setQuantityRangeMax(max_value)
    slice_value.setQuantityRangeMin(min_value)
    return slice_value

  def stepSetCurrencyOnModel(self, sequence=None, **kw):
    model = sequence.get('model')
    currency = sequence.get('price_currency')
    model.setPriceCurrencyValue(currency)

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
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    variation_category_list=['contribution_share/employee',
                                             'contribution_share/employer'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(urssaf_model_line = model_line)

  def stepModelCreateUrssafModelLineWithSlices(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Urssaf',
                    reference='urssaf_model_line_2',
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    variation_category_list=['contribution_share/employee',
                                       'contribution_share/employer',
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
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    variation_category_list=['contribution_share/employee',
                                       'contribution_share/employer',
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
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    variation_category_list=['contribution_share/employee',
                                             'contribution_share/employer'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(urssaf_model_line = model_line)

  def stepUrssafModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    cell1 = model_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, contribution_share='employee')
    cell2 = model_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.5, contribution_share='employer')

  def stepUrssafModelLineCreateMovementsWithQuantityOnly(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    cell1 = model_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(quantity=-100, contribution_share='employee')
    cell2 = model_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(quantity=-200, contribution_share='employer')

  def stepUrssafModelLineWithSlicesCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line_with_slices')
    cell1 = model_line.newCell('contribution_share/employee',
        'salary_range/france/slice_0_to_200',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, contribution_share='employee',
        salary_range='france/slice_0_to_200')
    cell2 = model_line.newCell('contribution_share/employer',
        'salary_range/france/slice_0_to_200',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.2, contribution_share='employer',
        salary_range='france/slice_0_to_200')
    cell3 = model_line.newCell('contribution_share/employee',
        'salary_range/france/slice_200_to_400',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell3.edit(price=0.3, contribution_share='employee',
        salary_range='france/slice_200_to_400')
    cell4 = model_line.newCell('contribution_share/employer',
        'salary_range/france/slice_200_to_400',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell4.edit(price=0.4, contribution_share='employer',
        salary_range='france/slice_200_to_400')
    cell5 = model_line.newCell('contribution_share/employee',
        'salary_range/france/slice_400_to_5000',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell5.edit(price=0.5, contribution_share='employee',
        salary_range='france/slice_400_to_5000')
    cell6 = model_line.newCell('contribution_share/employer',
        'salary_range/france/slice_400_to_5000',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell6.edit(price=0.6, contribution_share='employer',
        salary_range='france/slice_400_to_5000')

  def stepUrssafModelLineWithComplexSlicesCreateMovements(self,
      sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line_with_slices')
    cell1 = model_line.newCell('contribution_share/employee',
        'salary_range/france/slice_200_to_400',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, contribution_share='employee',
        salary_range='france/slice_200_to_400')
    cell2 = model_line.newCell('contribution_share/employer',
        'salary_range/france/slice_200_to_400',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.2, contribution_share='employer',
        salary_range='france/slice_200_to_400')
    cell3 = model_line.newCell('contribution_share/employee',
        'salary_range/france/slice_600_to_800',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell3.edit(price=0.3, contribution_share='employee',
        salary_range='france/slice_600_to_800')
    cell4 = model_line.newCell('contribution_share/employer',
        'salary_range/france/slice_600_to_800',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell4.edit(price=0.4, contribution_share='employer',
        salary_range='france/slice_600_to_800')

  def stepPaysheetUrssafModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    cell1 = model_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.3, contribution_share='employee')
    cell2 = model_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.7, contribution_share='employer')

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
                  start_date=DateTime(2009,06,01),
                  stop_date=DateTime(2009,06,30))
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
                    base_contribution_list=['base_amount/base_salary',
                                            'base_amount/gross_salary'])
    sequence.edit(labour_paysheet_line = paysheet_line)

  def stepPaysheetCreateBonusPaySheetLine(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line = self.createPaysheetLine(paysheet)
    paysheet_line.edit(title='Bonus',
                    resource_value=sequence.get('bonus_service'),
                    variation_category_list=['contribution_share/employee',
                                             'contribution_share/employer'],
                    base_contribution_list=[ 'base_amount/base_salary'])
    sequence.edit(bonus_paysheet_line = paysheet_line)

  def stepPaysheetCreateBonusPaySheetLineMovements(self, sequence=None, **kw):
    paysheet_line = sequence.get('bonus_paysheet_line')
    cell1 = paysheet_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(quantity=1000, price=1, contribution_share='employee')
    cell2 = paysheet_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(quantity=1000, price=1, contribution_share='employer')

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

  def stepCheckNoPaysheetLineAreCreated(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 0)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 0) # 2 because labour line contain no movement

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
                               # because of the 3 slice and 2 contribution_shares

  def stepCheckPaysheetLineAreCreatedUsingComplexSlices(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 2)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 4) # 4 because labour line contain no movement and
                               # because of the 2 slice and 2 contribution_shares

  def stepCheckPaysheetLineAreCreatedUsingWith3Lines(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 3)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 4) # 4 because labour line contain no movement and
                               # because of the two lines and 2 contribution_shares
                               # (urssaf and sickness insurance. old age
                               # insurance does not match predicate)

  def stepCheckPaysheetLineAreCreatedAfterUpdateWithLinesWithSameResource(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 3)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 8) # 8 because labour line contain no movement and
                               # because of the 3 slice and 2 contribution_shares
                               # + the first model line with 2 contribution_shares

  def stepCheckPaysheetLineAmounts(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('contribution_share/employer')
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
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 4000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('contribution_share/employer')
        self.assertEquals(cell2.getQuantity(), 4000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      elif service == 'Bonus':
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getTotalPrice(), 1000)
        cell2 = paysheet_line.getCell('contribution_share/employer')
        self.assertEquals(cell2.getTotalPrice(), 1000)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineAmountsWithQuantityOnly(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), -100)
        self.assertEquals(cell1.getPrice(), 1)
        cell2 = paysheet_line.getCell('contribution_share/employer')
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
        cell1 = paysheet_line.getCell('contribution_share/employee',
            'salary_range/france/slice_0_to_200')
        self.assertEquals(cell1.getQuantity(), 200)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('contribution_share/employer',
            'salary_range/france/slice_0_to_200')
        self.assertEquals(cell2.getQuantity(), 200)
        self.assertEquals(cell2.getPrice(), 0.2)
        cell3 = paysheet_line.getCell('contribution_share/employee',
            'salary_range/france/slice_200_to_400')
        self.assertEquals(cell3.getQuantity(), 200)
        self.assertEquals(cell3.getPrice(), 0.3)
        cell4 = paysheet_line.getCell('contribution_share/employer',
            'salary_range/france/slice_200_to_400')
        self.assertEquals(cell4.getQuantity(), 200)
        self.assertEquals(cell4.getPrice(), 0.4)
        cell5 = paysheet_line.getCell('contribution_share/employee',
            'salary_range/france/slice_400_to_5000')
        self.assertEquals(cell5.getQuantity(), 2600)
        self.assertEquals(cell5.getPrice(), 0.5)
        cell6 = paysheet_line.getCell('contribution_share/employer',
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
        cell1 = paysheet_line.getCell('contribution_share/employee',
            'salary_range/france/slice_200_to_400')
        self.assertEquals(cell1.getQuantity(), 200)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('contribution_share/employer',
            'salary_range/france/slice_200_to_400')
        self.assertEquals(cell2.getQuantity(), 200)
        self.assertEquals(cell2.getPrice(), 0.2)
        cell3 = paysheet_line.getCell('contribution_share/employee',
            'salary_range/france/slice_600_to_800')
        self.assertEquals(cell3.getQuantity(), 200)
        self.assertEquals(cell3.getPrice(), 0.3)
        cell4 = paysheet_line.getCell('contribution_share/employer',
            'salary_range/france/slice_600_to_800')
        self.assertEquals(cell4.getQuantity(), 200)
        self.assertEquals(cell4.getPrice(), 0.4)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepCheckPaysheetLineAmountsAfterUpdateWithLinesWithSameResource(self,
      sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    for paysheet_line in paysheet_line_list:
      service = paysheet_line.getResourceTitle()
      if service == 'Urssaf':
        if len(paysheet_line.contentValues(portal_type='Pay Sheet Cell')) == 6:
          # there is two lines with the same resource, one with slice and one
          # without
          cell1 = paysheet_line.getCell('contribution_share/employee',
              'salary_range/france/slice_0_to_200')
          self.assertEquals(cell1.getQuantity(), 200)
          self.assertEquals(cell1.getPrice(), 0.1)
          cell2 = paysheet_line.getCell('contribution_share/employer',
              'salary_range/france/slice_0_to_200')
          self.assertEquals(cell2.getQuantity(), 200)
          self.assertEquals(cell2.getPrice(), 0.2)
          cell3 = paysheet_line.getCell('contribution_share/employee',
              'salary_range/france/slice_200_to_400')
          self.assertEquals(cell3.getQuantity(), 200)
          self.assertEquals(cell3.getPrice(), 0.3)
          cell4 = paysheet_line.getCell('contribution_share/employer',
              'salary_range/france/slice_200_to_400')
          self.assertEquals(cell4.getQuantity(), 200)
          self.assertEquals(cell4.getPrice(), 0.4)
          cell5 = paysheet_line.getCell('contribution_share/employee',
              'salary_range/france/slice_400_to_5000')
          self.assertEquals(cell5.getQuantity(), 2600)
          self.assertEquals(cell5.getPrice(), 0.5)
          cell6 = paysheet_line.getCell('contribution_share/employer',
              'salary_range/france/slice_400_to_5000')
          self.assertEquals(cell6.getQuantity(), 2600)
          self.assertEquals(cell6.getPrice(), 0.6)
        else:
          cell1 = paysheet_line.getCell('contribution_share/employee')
          self.assertEquals(cell1.getQuantity(), 3000)
          self.assertEquals(cell1.getPrice(), 0.1)
          cell2 = paysheet_line.getCell('contribution_share/employer')
          self.assertEquals(cell2.getQuantity(), 3000)
          self.assertEquals(cell2.getPrice(), 0.5)
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
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('contribution_share/employer')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      elif service == 'Sickness Insurance':
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.4)
        cell2 = paysheet_line.getCell('contribution_share/employer')
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
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('contribution_share/employer')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      elif service == 'Old Age Insurance':
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.5)
        cell2 = paysheet_line.getCell('contribution_share/employer')
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
    business_path.setTradePhaseList(['payroll/france/urssaf',
                                     'payroll/france/labour'])
    business_path.setSourceValue(sequence.get('urssaf_roubaix'))
    business_path.setSourceSectionValue(sequence.get('urssaf_roubaix'))
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
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getSourceSectionValue(), urssaf_roubaix)
        cell2 = paysheet_line.getCell('contribution_share/employer')
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
        default_payment_condition_payment_date=DateTime(2009,05,25),
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
        DateTime(2009,05,25))
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
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    reference='intermediate_line',
                    variation_category_list=['contribution_share/employee',
                                             'contribution_share/employer'],
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
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_service'),
                    reference='line_applied_on_intermediate_line',
                    variation_category_list=['contribution_share/employee',
                                             'contribution_share/employer'],
                    base_contribution_list=['base_amount/net_salary'],
                    base_application_list=['base_amount/deductible_tax'])
    sequence.edit(model_line_applied_on_tax = model_line)

  def stepIntermediateModelLineCreateMovements(self, sequence=None,
      **kw):
    model_line = sequence.get('intermediate_model_line')
    cell1 = model_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.2, contribution_share='employee')
    cell2 = model_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.2, contribution_share='employer')

  def stepAppliedOnTaxModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('model_line_applied_on_tax')
    cell1 = model_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, contribution_share='employee')
    cell2 = model_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.5, contribution_share='employer')

  def stepModelCreateOldAgeInsuranceModelLine(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Old Age Insurance',
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('old_age_insurance_service'),
                    reference='old_age_insurance',
                    variation_category_list=['contribution_share/employee',
                                             'contribution_share/employer'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(old_age_insurance = model_line)

  def stepOldAgeInsuranceModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('old_age_insurance')
    cell1 = model_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.5, contribution_share='employee')
    cell2 = model_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.8, contribution_share='employer')

  def stepModelCreateSicknessInsuranceModelLine(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Sickness Insurance',
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('sickness_insurance_service'),
                    reference='sickness_insurance',
                    variation_category_list=['contribution_share/employee',
                                             'contribution_share/employer'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(sickness_insurance = model_line)

  def stepSicknessInsuranceModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('sickness_insurance')
    cell1 = model_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.4, contribution_share='employee')
    cell2 = model_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.3, contribution_share='employer')

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
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 600) # here it's 600 of tax
                                  # because of the intermediate line (3000*0.2)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('contribution_share/employer')
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
                    trade_phase='payroll/france/urssaf',
                    resource_value=sequence.get('old_age_insurance_service'),
                    reference='model_line_in_the_payesheet',
                    variation_category_list=['contribution_share/employee',
                                             'contribution_share/employer'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(model_line_on_paysheet = model_line)

  def stepPaysheetModelLineCreateMovements(self, sequence=None, **kw):
    model_line = sequence.get('model_line_on_paysheet')
    cell1 = model_line.newCell('contribution_share/employee',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.5, contribution_share='employee')
    cell2 = model_line.newCell('contribution_share/employer',
        portal_type='Pay Sheet Model Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.8, contribution_share='employer')

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
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.1)
        cell2 = paysheet_line.getCell('contribution_share/employer')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.5)
      elif service == 'Labour':
        self.assertEqual(paysheet_line.getTotalPrice(), 3000.0)
      elif service == 'Old Age Insurance':
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.5)
        cell2 = paysheet_line.getCell('contribution_share/employer')
        self.assertEquals(cell2.getQuantity(), 3000)
        self.assertEquals(cell2.getPrice(), 0.8)
      else:
        self.fail("Unknown service for line %s" % paysheet_line.getTitle())

  def stepModelModifyUrssafModelLine(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    # modify price on movements :
    cell_1 = model_line.getCell('contribution_share/employee',
        base_id='movement')
    self.assertNotEquals(cell_1, None)
    cell_1.edit(price=0.2)
    cell_2 = model_line.getCell('contribution_share/employer',
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
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.2)
        cell2 = paysheet_line.getCell('contribution_share/employer')
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
        cell1 = paysheet_line.getCell('contribution_share/employee')
        self.assertEquals(cell1.getQuantity(), 3000)
        self.assertEquals(cell1.getPrice(), 0.3)
        cell2 = paysheet_line.getCell('contribution_share/employer')
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

  def stepCheckPaySheetTransaction_getMovementListReturn(self,
      sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    # when pay sheet has no line, the script returns an empty list
    self.assertEquals(len(paysheet.PaySheetTransaction_getMovementList()), 0)

    # we add a line, then it is returned in the list
    line = self.createPaysheetLine(paysheet)
    self.assertEquals(len(paysheet.PaySheetTransaction_getMovementList()), 1)

    # if the line has cells with different tax categories, new properties are
    # added to this line.
    urssaf_service = sequence.get('urssaf_service')
    line.setResourceValue(urssaf_service)
    line.setVariationCategoryList(['contribution_share/employee',
                                   'contribution_share/employer'])
    cell0 = line.newCell('contribution_share/employee',
                         portal_type='Pay Sheet Cell', base_id='movement')
    cell0.setMappedValuePropertyList(['quantity', 'price'])
    cell0.setVariationCategoryList(('contribution_share/employee',))
    cell0.setPrice(2)
    cell0.setQuantity(3)
    cell1 = line.newCell('contribution_share/employer',
                         portal_type='Pay Sheet Cell', base_id='movement')
    cell1.setMappedValuePropertyList(['quantity', 'price'])
    cell1.setVariationCategoryList(('contribution_share/employer',))
    cell1.setPrice(4)
    cell1.setQuantity(5)

    movement_list = paysheet.PaySheetTransaction_getMovementList()
    self.assertEquals(1, len(movement_list))
    movement = movement_list[0]
    self.assertEquals(2, movement.employee_price)
    self.assertEquals(3, movement.employee_quantity)
    self.assertEquals(2*3, movement.employee_total_price)
    self.assertEquals(4, movement.employer_price)
    self.assertEquals(5, movement.employer_quantity)
    self.assertEquals(4*5, movement.employer_total_price)

  def stepCheckModelWithoutRefValidity(self, sequence=None, **kw):
    '''
    If no reference are defined on a model, the behavior is that this model is
    always valid. So check a Pay Sheet Transaction Line is created after
    calling the calculation script
    '''
    eur = sequence.get('currency')
    labour = sequence.get('labour_service_output')

    model_without_ref = self.getPortalObject().paysheet_model_module.newContent( \
        specialise_value=sequence.get('business_process'),
        portal_type='Pay Sheet Model',
        variation_settings_category_list=['salary_range/france',],
        effective_date=DateTime(2009, 1, 1),
        expiration_date=DateTime(2009, 12, 31))
    model_without_ref.setPriceCurrencyValue(eur)


    model_line_1 = self.createModelLine(model_without_ref)
    model_line_1.edit(
        trade_phase='payroll/france/labour',
        reference='model_without_ref',
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=10000)
    
    # create the paysheet
    paysheet = self.createPaysheet()
    paysheet.edit(specialise_value=model_without_ref,
                  start_date=DateTime(2009, 1, 1),
                  stop_date=DateTime(2009, 1, 31),
                  price_currency_value=eur)
    paysheet.PaySheetTransaction_applyModel()
    self.stepTic()

    portal_type_list = ['Pay Sheet Model Line',]

    # if no reference, we don't care about dates
    sub_object_list = paysheet.getInheritedObjectValueList(portal_type_list)
    
    self.assertEquals(len(paysheet.contentValues(\
        portal_type='Pay Sheet Line')), 0)
    # calculate the pay sheet
    paysheet.applyTransformation()
    self.stepTic()
    self.assertEquals(len(paysheet.contentValues(
        portal_type='Pay Sheet Line')), 1)
    # check values on the paysheet
    self.assertEquals(paysheet.contentValues()[0].getTotalPrice(), 10000)

  def stepCheckModelWithoutDateValidity(self, sequence=None, **kw):
    '''
    If no date are defined on a model, the behavior is that this model
    is always valid.
    '''
    eur = sequence.get('currency')
    labour = sequence.get('labour_service_output')

    model_without_date = self.getPortalObject().paysheet_model_module.newContent( \
        specialise_value=sequence.get('business_process'),
        portal_type='Pay Sheet Model',
        variation_settings_category_list=['salary_range/france',],
        reference='fabien_model_without_date')

    model_line_2 = self.createModelLine(model_without_date)
    model_line_2.edit(
        trade_phase='payroll/france/labour',
        reference='model_without_date',
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=10000)

    # create a paysheet without date
    paysheet_without_date = self.createPaysheet()
    paysheet_without_date.edit(specialise_value=model_without_date,
                  price_currency_value=eur)
    paysheet_without_date.PaySheetTransaction_applyModel()
    self.stepTic()

    portal_type_list = ['Pay Sheet Model Line',]

    # check the paysheet contail no lines before calculation
    self.assertEquals(len(paysheet_without_date.contentValues(\
        portal_type='Pay Sheet Line')), 0)
    # calculate the pay sheet
    paysheet_without_date.applyTransformation()
    self.stepTic()
    self.assertEquals(len(paysheet_without_date.contentValues(\
        portal_type='Pay Sheet Line')), 1)
    # check values on the paysheet_without_date
    self.assertEquals(paysheet_without_date.contentValues()[0].getTotalPrice(),
        10000)

    # create a paysheet with dates
    paysheet_with_date = self.createPaysheet()
    paysheet_with_date.edit(specialise_value=model_without_date,
                  start_date=DateTime(2009, 1, 1),
                  stop_date=DateTime(2009, 1, 31),
                  price_currency_value=eur)
    paysheet_with_date.PaySheetTransaction_applyModel()
    self.stepTic()

    portal_type_list = ['Pay Sheet Model Line',]

    # check the paysheet contains no lines before calculation
    self.assertEquals(len(paysheet_with_date.contentValues(\
        portal_type='Pay Sheet Line')), 0)
    # calculate the pay sheet
    paysheet_with_date.applyTransformation()
    self.stepTic()
    # after calculation, paysheet contains one line, because the model applies.
    self.assertEquals(len(paysheet_with_date.contentValues(\
        portal_type='Pay Sheet Line')), 1)
    self.assertEquals(paysheet_without_date.contentValues()[0].getTotalPrice(),
        10000)

  def stepCheckModelDateValidity(self, sequence=None, **kw):
    '''
    check that model effective_date and expiration_date are take into account.
    '''
    eur = sequence.get('currency')
    labour = sequence.get('labour_service_output')

    model_1 = self.getPortalObject().paysheet_model_module.newContent( \
        specialise_value=sequence.get('business_process'),
        portal_type='Pay Sheet Model',
        variation_settings_category_list=['salary_range/france',],
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 1, 1),
        expiration_date=DateTime(2009, 06, 30))
    
    model_2 = self.getPortalObject().paysheet_model_module.newContent( \
        specialise_value=sequence.get('business_process'),
        portal_type='Pay Sheet Model',
        variation_settings_category_list=['salary_range/france',],
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31))

    model_line_3 = self.createModelLine(model_1)
    model_line_3.edit(
        trade_phase='payroll/france/labour',
        reference='check_model_date_validity_1',
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=20000,
        price=1)

    model_line_4 = self.createModelLine(model_2)
    model_line_4.edit(
        trade_phase='payroll/france/labour',
        reference='check_model_date_validity_2',
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=30000,
        price=1)
    self.stepTic()

    # create the paysheet
    paysheet = self.portal.accounting_module.newContent(
                              portal_type='Pay Sheet Transaction',
                              specialise_value=model_1,
                              start_date=DateTime(2009, 07, 1),
                              stop_date=DateTime(2009, 07, 31),
                              price_currency_value=eur)
    paysheet.PaySheetTransaction_applyModel()
    self.stepTic()

    self.assertEquals(len(paysheet.contentValues(\
        portal_type='Pay Sheet Line')), 0)
    # calculate the pay sheet
    paysheet.applyTransformation()
    self.stepTic()
    self.assertEquals(len(paysheet.contentValues(\
        portal_type='Pay Sheet Line')), 1)
    # check values on the paysheet, if it's model_2, the total_price 
    # should be 30000.
    self.assertEquals(paysheet.contentValues()[0].getTotalPrice(), 30000)

  def stepCheckModelVersioning(self, sequence=None, **kw):
    '''
    check that latest version is used in case of more thant one model is matching
    using dates
    '''
    eur = sequence.get('currency')

    # define a non effective model
    model_1 = self.getPortalObject().paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=['salary_range/france',],
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 01, 1),
        expiration_date=DateTime(2009, 02, 28),
        specialise_value=sequence.get('business_process'))

    # define two models with same references and same dates
    # but different version number
    model_2 = self.getPortalObject().paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=['salary_range/france',],
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='002',
        specialise_value=sequence.get('business_process'))

    model_3 = self.getPortalObject().paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        variation_settings_category_list=['salary_range/france',],
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='001',
        specialise_value=sequence.get('business_process'))
    self.stepTic()

    # create the paysheet
    paysheet = self.portal.accounting_module.newContent(
                              portal_type='Pay Sheet Transaction',
                              specialise_value=model_1,
                              start_date=DateTime(2009, 07, 1),
                              stop_date=DateTime(2009, 07, 31),
                              price_currency_value=eur)
    paysheet.PaySheetTransaction_applyModel()
    self.stepTic()

    # the effective model should be model_2 because of the effective date and
    # version number
    specialise_value = paysheet.getSpecialiseValue()
    effective_model = specialise_value.getEffectiveModel(\
        start_date=paysheet.getStartDate(),
        stop_date=paysheet.getStopDate())
    self.assertEquals(effective_model, model_2)

    # check the effective model tree list
    effective_value_list = specialise_value.findEffectiveSpecialiseValueList(\
        context=specialise_value,
        start_date=paysheet.getStartDate(),
        stop_date=paysheet.getStopDate())
    self.assertEquals(effective_value_list, [model_2])

  def stepCreateModelLineZeroPrice(self, sequence=None, **kw):
    '''Test the creation of lines when the price is set to zero: the line should
    not be created.'''
    model = sequence.get('model')
    labour = sequence.get('labour_service_output')
    line = model.newContent(
          id='line',
          portal_type='Pay Sheet Model Line',
          resource_value=labour,
          base_contribution_list=['base_amount/base_salary',
            'base_amount/gross_salary'],
          quantity=5,
          price=0)

  def stepComplexModelInheritanceScheme(self, sequence=None, **kw):
    '''
    check inheritance and effective model with a more complex inheritance tree

    # the inheritance tree look like this :

                                    model_employee
(model_1, 01/01/09, 28/02/09) ; (model_2, 01/07/09, 31/12/09) ; (model_3, 01/07/09, 31/12/09)
                                           |
                                           |
                                           |
                                     model_company
             (model_4, 01/07/09, 31/12/09), (model_5, 01/07/09, 31/12/09)
                                           |
                                           |
                                           |
                                     model_company
             (model_6, 01/07/09, 31/12/09), (model_7, 01/07/09, 31/12/09)
    '''

    eur = sequence.get('currency')
    labour = sequence.get('labour_service_output')
    paysheet_model_module = self.getPortalObject().paysheet_model_module

    # define a non effective model
    model_1 = paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        specialise_value=sequence.get('business_process'),
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 01, 1),
        expiration_date=DateTime(2009, 02, 28))
    model_line_1 = self.createModelLine(model_1)
    model_line_1.edit(
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=10000)

    # define two models with same references and same dates
    # but different version number
    model_2 = paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        specialise_value=sequence.get('business_process'),
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='002')
    model_line_2 = self.createModelLine(model_2)
    model_line_2.edit(
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=20000)

    model_3 = paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        specialise_value=sequence.get('business_process'),
        reference='fabien_model_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='001')
    model_line_3 = self.createModelLine(model_3)
    model_line_3.edit(
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=30000)

    # define two models with same references and same dates
    # but different version number
    model_4 = paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        specialise_value=sequence.get('business_process'),
        reference='fabien_model_level_2_2009',
        effective_date=DateTime(2009, 01, 1),
        expiration_date=DateTime(2009, 06, 30),
        version='002')
    model_line_4 = self.createModelLine(model_4)
    model_line_4.edit(
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=40000)

    model_5 = paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        specialise_value=sequence.get('business_process'),
        reference='fabien_model_level_2_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='001')
    model_line_5 = self.createModelLine(model_5)
    model_line_5.edit(
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=50000)

    # third level : define two models with same references and same dates
    # but different version number
    model_6 = paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        specialise_value=sequence.get('business_process'),
        reference='fabien_model_level_3_2009',
        effective_date=DateTime(2009, 01, 1),
        expiration_date=DateTime(2009, 06, 30),
        version='002')
    model_line_6 = self.createModelLine(model_6)
    model_line_6.edit(
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=60000)

    model_7 = paysheet_model_module.newContent( \
        portal_type='Pay Sheet Model',
        specialise_value=sequence.get('business_process'),
        reference='fabien_model_level_3_2009',
        effective_date=DateTime(2009, 07, 1),
        expiration_date=DateTime(2009, 12, 31),
        version='001')
    model_line_7 = self.createModelLine(model_7)
    model_line_7.edit(
        resource_value=labour,
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'],
        quantity=70000)

    self.stepTic()

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
    self.assertEquals(specialise_value.findSpecialiseValueList(context=paysheet),
        [model_1, model_4, model_6])
    self.assertEquals(specialise_value.findEffectiveSpecialiseValueList(\
        context=paysheet, start_date=paysheet.getStartDate(),
        stop_date=paysheet.getStopDate()), [model_2,])

    model_1.setSpecialiseValue(None)
    model_2.setSpecialiseValue(model_5)
    model_5.setSpecialiseValue(model_6)
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(specialise_value.findSpecialiseValueList(context=paysheet),
        [model_1,])
    self.assertEquals(specialise_value.findEffectiveSpecialiseValueList(\
        context=paysheet, start_date=paysheet.getStartDate(),
        stop_date=paysheet.getStopDate()), [model_2, model_5, model_7])

    model_3.setSpecialiseValue(model_5)
    model_5.setSpecialiseValue(model_6)
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(specialise_value.findSpecialiseValueList(context=paysheet),
        [model_1,])
    self.assertEquals(specialise_value.findEffectiveSpecialiseValueList(\
        context=paysheet, start_date=paysheet.getStartDate(),
        stop_date=paysheet.getStopDate()), [model_2, model_5, model_7])

  def stepCheckPropertiesAreCopiedFromModelLineToPaySheetLine(self,
      sequence=None, **kw):
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    property_list = ('title', 'description', 'int_index')
    for model_line in model.contentValues(portal_type='Pay Sheet Model Line'):
      model_line_resource = model_line.getResource()
      line_found = False
      for paysheet_line in paysheet.contentValues(portal_type='Pay Sheet Line'):
        if paysheet_line.getResource() == model_line_resource:
          line_found = True
          for prop in property_list:
            prop_from_model_line = getattr(model_line, prop, None)
            # check a value is set on the model line
            self.assertNotEquals(prop_from_model_line, None)
            prop_from_paysheet_line = getattr(paysheet_line, prop, None)
            # check the property is the same on model_line and paysheet_line
            self.assertEquals(prop_from_model_line, prop_from_paysheet_line)
          break

      # check that for each model line, we foud a corresponding paysheet_line
      self.assertEquals(line_found, True)

  def stepSetProperiesOnModelLines(self, sequence=None, **kw):
    model = sequence.get('model')
    index = 0
    for model_line in model.contentValues(portal_type='Pay Sheet Model Line'):
      model_line.setTitle('Model line title %s' % index)
      model_line.setDescription('Model line description %s' % index)
      model_line.setIntIndex(index)
      index += 1

  def checkPrecisionOfListBox(self, report_section, precision):
    here = report_section.getObject(self.portal)
    report_section.pushReport(self.portal)
    form = getattr(here, report_section.getFormId())
    self.portal.REQUEST['here'] = here
    if form.has_field('listbox'):
      result = form.listbox.get_value('default',
                                      render_format='list',
                                      REQUEST=self.portal.REQUEST)
      self.assertEquals(precision, self.portal.REQUEST.get('precision'))
    report_section.popReport(self.portal)

class TestPayroll(TestPayrollMixin):

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
               Tic
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
               Tic
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
               Tic
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
               Tic
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
               Tic
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

  def test_modelLineWithZeroPrice(self):
    '''Test the creation of lines when the price is set to zero: the line should
    not be created.'''
    sequence_list = SequenceList()
    sequence_string = """
               CreateLabourOutputService
               CreateEmployer
               CreateEmployee
               CreatePriceCurrency
               CreateBasicModel
               Tic
               CreateModelLineZeroPrice
               CreateBasicPaysheet
  """ + self.BUSINESS_PATH_CREATION_SEQUENCE_STRING + """
               PaysheetApplyTransformation
               Tic
               CheckNoPaysheetLineAreCreated
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

  def test_PaySheetTransaction_getMovementList(self):
    '''
      PaySheetTransaction_getMovementList is a script used by the listbox to
      display information about lines in the Paysheet. Just test the return of
      it.
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreateUrssafService
               CreateBasicPaysheet
               CheckPaySheetTransaction_getMovementListReturn
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_PayrollTaxesReport(self):
    currency_module = self.getCurrencyModule()
    if not hasattr(currency_module, 'EUR'):
      currency_module.newContent(
          portal_type = 'Currency',
          reference = "EUR", id = "EUR", base_unit_quantity=0.001 )
    eur = self.portal.currency_module.EUR
    service = self.portal.service_module.newContent(
                      portal_type='Service',
                      title='PS1',
                      variation_base_category_list=('contribution_share',),
                      variation_category_list=('contribution_share/employee',
                                               'contribution_share/employer'))
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
                      title='Service Provider')
    other_provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Another Service Provider')
    ps1 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 1',
                      destination_section_value=employer,
                      source_section_value=employee1,
                      start_date=DateTime(2006, 1, 1),)
    line = ps1.newContent(portal_type='Pay Sheet Line',
                   resource_value=service,
                   source_section_value=provider,
                # (destination is set by PaySheetTransaction.createPaySheetLine)
                   destination_value=employee1,
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.50, quantity=2000, contribution_share='employee')
    cell_employer = line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.40, quantity=2000, contribution_share='employer')
    ps1.plan()

    ps2 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 2',
                      destination_section_value=employer,
                      source_section_value=employee2,
                      start_date=DateTime(2006, 1, 1),)
    line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=service,
                   source_section_value=provider,
                   destination_value=employee2,
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.50, quantity=3000, contribution_share='employee')
    cell_employer = line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.40, quantity=3000, contribution_share='employer')

    other_line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=service,
                   destination_value=employee2,
                   source_section_value=other_provider,
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = other_line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.46, quantity=2998, contribution_share='employee')
    cell_employer = other_line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.42, quantity=2998, contribution_share='employer')
    self.stepTic()

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
    request_form['resource'] = service.getRelativeUrl()
    request_form['mirror_section'] = provider.getRelativeUrl()

    report_section_list = self.getReportSectionList(
                             self.portal.accounting_module,
                             'AccountingTransactionModule_viewPaySheetLineReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(2, len(data_line_list))

    # base_unit_quantity for EUR is set to 0.001 in the created currencies, so the
    # precision is 3. Editable Fields will reuse this precision.
    self.checkPrecisionOfListBox(report_section_list[0], 3)

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
    currency_module = self.getCurrencyModule()
    if not hasattr(currency_module, 'EUR'):
      currency_module.newContent(
          portal_type = 'Currency',
          reference = "EUR", id = "EUR", base_unit_quantity=0.001 )
    eur = self.portal.currency_module.EUR
    service = self.portal.service_module.newContent(
                      portal_type='Service',
                      title='PS1',
                      variation_base_category_list=('contribution_share',
                                                    'salary_range'),
                      variation_category_list=('contribution_share/employee',
                                               'contribution_share/employer',
                                               'salary_range/france/slice_a',
                                               'salary_range/france/slice_b'))
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
                      title='Service Provider')
    other_provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Another Service Provider')
    ps1 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 1',
                      destination_section_value=employer,
                      source_section_value=employee1,
                      start_date=DateTime(2006, 1, 1),)
    line = ps1.newContent(portal_type='Pay Sheet Line',
                   resource_value=service,
                   source_section_value=provider,
                # (destination is set by PaySheetTransaction.createPaySheetLine)
                   destination_value=employee1,
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer',
                                            'salary_range/france/slice_a',
                                            'salary_range/france/slice_b'))
    cell_employee_a = line.newCell('contribution_share/employee',
                                   'salary_range/france/slice_a',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employee_a.edit(price=-.50, quantity=1000,
                         contribution_share='employee',
                         salary_range='france/slice_a')
    cell_employee_b = line.newCell('contribution_share/employee',
                                   'salary_range/france/slice_b',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employee_b.edit(price=-.20, quantity=500,
                         contribution_share='employee',
                         salary_range='france/slice_b')

    cell_employer_a = line.newCell('contribution_share/employer',
                                   'salary_range/france/slice_a',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employer_a.edit(price=-.40, quantity=1000,
                         contribution_share='employer',
                         salary_range='france/slice_a')
    cell_employer_b = line.newCell('contribution_share/employer',
                                   'salary_range/france/slice_b',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employer_b.edit(price=-.32, quantity=500,
                         contribution_share='employer',
                         salary_range='france/slice_b')

    ps1.plan()

    ps2 = self.portal.accounting_module.newContent(
                      portal_type='Pay Sheet Transaction',
                      title='Employee 2',
                      destination_section_value=employer,
                      source_section_value=employee2,
                      start_date=DateTime(2006, 1, 1),)
    line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=service,
                   source_section_value=provider,
                   destination_value=employee2,
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer',
                                            'salary_range/france/slice_a',
                                            'salary_range/france/slice_b'))
    cell_employee_a = line.newCell('contribution_share/employee',
                                   'salary_range/france/slice_a',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employee_a.edit(price=-.50, quantity=1000,
                         salary_range='france/slice_a',
                         contribution_share='employee')
    cell_employee_b = line.newCell('contribution_share/employee',
                                   'salary_range/france/slice_b',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employee_b.edit(price=-.20, quantity=3000,
                         salary_range='france/slice_b',
                         contribution_share='employee')

    cell_employer_a = line.newCell('contribution_share/employer',
                                   'salary_range/france/slice_a',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employer_a.edit(price=-.40, quantity=1000,
                         salary_range='france/slice_a',
                         contribution_share='employer')
    cell_employer_b = line.newCell('contribution_share/employer',
                                   'salary_range/france/slice_b',
                                   portal_type='Pay Sheet Cell',
                                   base_id='movement',
                                   mapped_value_property_list=('price',
                                                               'quantity'),)
    cell_employer_b.edit(price=-.32, quantity=3000,
                         salary_range='france/slice_b',
                         contribution_share='employer')
    self.stepTic()

    # set request variables and render
    request_form = self.portal.REQUEST
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['draft', 'planned']
    request_form['resource'] = service.getRelativeUrl()
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
                            employee_title='Total Slice A',
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
                            employee_title='Total Slice B',
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
    currency_module = self.getCurrencyModule()
    if not hasattr(currency_module, 'EUR'):
      currency_module.newContent(
          portal_type = 'Currency',
          reference = "EUR", id = "EUR", base_unit_quantity=0.001 )
    eur = self.portal.currency_module.EUR
    salary_service = self.portal.service_module.newContent(
                      portal_type='Service',
                      title='Gross Salary',
                      variation_base_category_list=('contribution_share',),
                      variation_category_list=('contribution_share/employee',
                                               'contribution_share/employer'))
    service = self.portal.service_module.newContent(
                      portal_type='Service',
                      title='PS1',
                      variation_base_category_list=('contribution_share',),
                      variation_category_list=('contribution_share/employee',
                                               'contribution_share/employer'))
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
                      title='Service Provider')
    other_provider = self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      title='Another Service Provider')
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
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=1, quantity=2000, contribution_share='employee')
    line = ps1.newContent(portal_type='Pay Sheet Line',
                   resource_value=service,
                   source_section_value=provider,
                   destination_value=employee1,
                   base_contribution_list=['base_amount/net_salary',],
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.50, quantity=2000, contribution_share='employee')
    cell_employer = line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.40, quantity=2000, contribution_share='employer')
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
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=1, quantity=3000, contribution_share='employee')
    line = ps2.newContent(portal_type='Pay Sheet Line',
                   resource_value=service,
                   source_section_value=provider,
                   destination_value=employee2,
                   base_contribution_list=['base_amount/net_salary',],
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.50, quantity=3000, contribution_share='employee')
    cell_employer = line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.40, quantity=3000, contribution_share='employer')
    self.stepTic()

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

    # base_unit_quantity for EUR is set to 0.001 in the created currencies, so the
    # precision is 3. Editable Fields will reuse this precision.
    self.checkPrecisionOfListBox(report_section_list[0], 3)

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
    currency_module = self.getCurrencyModule()
    if not hasattr(currency_module, 'EUR'):
      currency_module.newContent(
          portal_type = 'Currency',
          reference = "EUR", id = "EUR", base_unit_quantity=0.001 )
    # create services
    base_salary = self.portal.service_module.newContent(
      portal_type='Service',
      title='Base Salary',
      product_line='base_salary',
      variation_base_category_list=('contribution_share',),
      variation_category_list=('contribution_share/employee',
                               'contribution_share/employer'))
    bonus = self.portal.service_module.newContent(
      portal_type='Service',
      title='Bonus',
      product_line='base_salary',
      variation_base_category_list=('contribution_share',),
      variation_category_list=('contribution_share/employee',
                               'contribution_share/employer'))
    deductions = self.portal.service_module.newContent(
      portal_type='Service',
      title='Deductions',
      product_line='base_salary',
      variation_base_category_list=('contribution_share',),
      variation_category_list=('contribution_share/employee',
                               'contribution_share/employer'))
    tax1 = self.portal.service_module.newContent(
      portal_type='Service',
      title='Tax1',
      product_line='payroll_tax_1',
      variation_base_category_list=('contribution_share',),
      variation_category_list=('contribution_share/employee',
                               'contribution_share/employer'))

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
      test_method_id='SimulationMovement_testInvoiceTransactionRule')
    rule.newContent(portal_type='Predicate',
      title='Employee Share',
      string_index='contribution_share',
      int_index=1,
      membership_criterion_base_category_list=('contribution_share',),
      membership_criterion_category_list=('contribution_share/employee',))
    rule.newContent(portal_type='Predicate',
      title='Employer Share',
      string_index='contribution_share',
      int_index=2,
      membership_criterion_base_category_list=('contribution_share',),
      membership_criterion_category_list=('contribution_share/employer',))

    rule.newContent(portal_type='Predicate',
      title='Base Salary',
      string_index='service',
      int_index=1,
      membership_criterion_base_category_list=('product_line',),
      membership_criterion_category_list=('product_line/base_salary',))
    rule.newContent(portal_type='Predicate',
      title='Payroll Tax 1',
      string_index='service',
      int_index=2,
      membership_criterion_base_category_list=('product_line',),
      membership_criterion_category_list=('product_line/payroll_tax_1',))
    self.stepTic()

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
                      title='Service Provider')

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
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=1, quantity=2000, contribution_share='employee')
    cell_employer = line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=1, quantity=2000, contribution_share='employer')

    # base_salary += 100 (bonus)
    line = ps.newContent(portal_type='Pay Sheet Line',
                   title='Bonus',
                   resource_value=bonus,
                   destination_value=employee,
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=1, quantity=100, contribution_share='employee')
    cell_employer = line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=1, quantity=100, contribution_share='employer')

    # base_salary -= 50 (deductions)   => base_salary == 2050
    line = ps.newContent(portal_type='Pay Sheet Line',
                   title='Deduction',
                   resource_value=deductions,
                   destination_value=employee,
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-1, quantity=50, contribution_share='employee')
    cell_employer = line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-1, quantity=50, contribution_share='employer')

    # tax1 = 10% for employee ( 205 )
    #        20% for employer ( 410 )
    line = ps.newContent(portal_type='Pay Sheet Line',
                   title='Tax 1',
                   resource_value=tax1,
                   source_section_value=provider,
                   destination_value=employee,
                   variation_category_list=('contribution_share/employee',
                                            'contribution_share/employer'))
    cell_employee = line.newCell('contribution_share/employee',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employee.edit(price=-.1, quantity=2050, contribution_share='employee')
    cell_employer = line.newCell('contribution_share/employer',
                                portal_type='Pay Sheet Cell',
                                base_id='movement',
                                mapped_value_property_list=('price',
                                                            'quantity'),)
    cell_employer.edit(price=-.2, quantity=2050, contribution_share='employer')
    ps.plan()
    self.stepTic()

    related_applied_rule = ps.getCausalityRelatedValue(
                                portal_type='Applied Rule')
    self.assertNotEquals(related_applied_rule, None)

    # build accounting lines
    ps.confirm()
    ps.start()
    self.stepTic()
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

  def test_modelWithoutReferenceValidity(self):
    ''' Check that if no REFERENCE are defined on a model, the behavior is
    that this model is always valid. So check a Pay Sheet Transaction Line 
    is created after calling the calculation script
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreatePriceCurrency
               CreateLabourOutputService
               CreateBusinessProcess
               CreateBusinessPath
               CreateUrssafRoubaixOrganisation
               ModifyBusinessPathTradePhase
               Tic
               CheckModelWithoutRefValidity
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_modelWithoutDateValidity(self):
    ''' Check that if no DATE are defined on a model, the behavior is that 
    this model is always valid. (XXX check if it's what we want)
    So check that a line is created after calling calculation script, even if
    there is no start_date or stop_date
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreatePriceCurrency
               CreateLabourOutputService
               CreateBusinessProcess
               CreateBusinessPath
               CreateUrssafRoubaixOrganisation
               ModifyBusinessPathTradePhase
               Tic
               CheckModelWithoutDateValidity
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_modelDateValidity(self):
    ''' check that model effective_date and expiration_date are take into
    account.
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreatePriceCurrency
               CreateLabourOutputService
               CreateBusinessProcess
               CreateBusinessPath
               CreateUrssafRoubaixOrganisation
               ModifyBusinessPathTradePhase
               Tic
               CheckModelDateValidity
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_modelVersioning(self):
    '''check that latest version is used in case of more thant one model is
    matching using dates 
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreatePriceCurrency
               CreateBusinessProcess
               CreateBusinessPath
               CreateUrssafRoubaixOrganisation
               ModifyBusinessPathTradePhase
               Tic
               CheckModelVersioning
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_modelSliceInheritance(self):
    '''Check the slice inheritance'''
    base_id = 'cell'
    paysheet_model_module = self.getPortalObject().paysheet_model_module
    model_1 = paysheet_model_module.newContent(
        portal_type='Pay Sheet Model',
        variation_settings_category_list=
              ('salary_range/france',))

    model_2 = paysheet_model_module.newContent(
        portal_type='Pay Sheet Model',
        specialise_value=model_1,)

    cell = model_1.newCell('salary_range/france/slice_a',
        portal_type='Pay Sheet Model Slice',
        base_id='cell')
    cell.setQuantityRangeMin(1)
    cell.setQuantityRangeMax(2)

    # model 2 gets cell values from model 1 (see test_07_model_getCell)
    self.assertEquals(1,
        model_2.getCell('salary_range/france/slice_a').getQuantityRangeMin())
    self.assertEquals(2,
        model_2.getCell('salary_range/france/slice_a').getQuantityRangeMax())

    # model 2 can override values
    model_2.edit(variation_settings_category_list=('salary_range/france',))
    cell = model_2.newCell('salary_range/france/slice_a',
                    portal_type='Pay Sheet Model Slice',
                    base_id='cell')
    cell.setQuantityRangeMin(3)
    cell.setQuantityRangeMax(4)
    self.assertEquals(3,
        model_2.getCell('salary_range/france/slice_a').getQuantityRangeMin())
    self.assertEquals(4,
        model_2.getCell('salary_range/france/slice_a').getQuantityRangeMax())

    # when unsetting variation settings category on this model will acquire
    # again values from specialised model
    model_2.edit(variation_settings_category_list=())
    self.assertEquals(1,
        model_2.getCell('salary_range/france/slice_a').getQuantityRangeMin())
    self.assertEquals(2,
        model_2.getCell('salary_range/france/slice_a').getQuantityRangeMax())

  def test_complexModelInheritanceScheme(self):
    '''check inheritance and effective model with a more complex
    inheritance tree'''
    sequence_list = SequenceList()
    sequence_string = """
               CreatePriceCurrency
               CreateLabourOutputService
               Tic
               ComplexModelInheritanceScheme
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_updatePaysheetAfterModelModification(self):
    '''generate a paysheet using a model, modify the model by adding a new
    model line with the same resource as the first one and update the
    paysheet. Check the paysheet values have been updated (new line created)
    '''
    sequence_list = SequenceList()
    sequence_string = '''
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreatePriceCurrency
               CreateModelWithSlices
               Tic
               ModelCreateUrssafModelLine
               UrssafModelLineCreateMovements
               CreateBasicPaysheet
               PaysheetCreateLabourPaySheetLine
               Tic
  ''' + self.BUSINESS_PATH_CREATION_SEQUENCE_STRING +'''
               CheckUpdateAggregatedAmountListReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineAmounts
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmounts
               ModelCreateUrssafModelLineWithSlices
               Tic
               UrssafModelLineWithSlicesCreateMovements
               Tic
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedAfterUpdateWithLinesWithSameResource
               CheckPaysheetLineAmountsAfterUpdateWithLinesWithSameResource
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmountsAfterUpdateWithLinesWithSameResource
    '''
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_propertiesAreSetOnPaysheetLines(self):
    '''check porperties from model line (like description, int_index,
    title, ...) are copied on the paysheet lines'''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               SetProperiesOnModelLines
               Tic
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineAmounts
               CheckPropertiesAreCopiedFromModelLineToPaySheetLine
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPayroll))
  return suite
