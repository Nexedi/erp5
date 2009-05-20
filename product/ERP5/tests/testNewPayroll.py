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

class TestNewPayrollMixin(ERP5ReportTestCase, TestBPMMixin):
  price_currency = 'currency_module/EUR'
  normal_resource_use_category_list = ['payroll/base_salary']
  invoicing_resource_use_category_list = ['payroll/tax']

  def getTitle(self):
    return "Payroll"

  def afterSetUp(self):
    """Prepare the test."""
    self.createCategories()
    self.setSystemPreference()

  def beforeTearDown(self):
    pass

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
            'grade/worker',
            'grade/engineer',
            'quantity_unit/time/month',
            'product_line/labour',
            'product_line/state_insurance',
            'use/payroll/tax',
            'use/payroll/base_salary',
            'trade_phase/payroll/france/urssaf',
           )

  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_payroll', 'erp5_mrp', 'erp5_bpm')

  def createPayrollService(self):
    module = self.portal.getDefaultModule(portal_type='Payroll Service')
    return module.newContent(portal_type='Payroll Service')

  def stepCreateUrssafPayrollService(self, sequence=None, **kw):
    node = self.createPayrollService()
    node.edit(title='Urssaf',
        product_line='state_insurance', quantity_unit='time/month',
        variation_base_category_list=['tax_category', 'salary_range'],
        use='payroll/tax')
    sequence.edit(urssaf_payroll_service = node)

  def stepCreateLabourPayrollService(self, sequence=None, **kw):
    node = self.createPayrollService()
    node.edit(title='Labour', quantity_unit='time/month',
        product_line='labour', use='payroll/base_salary')
    sequence.edit(labour_payroll_service = node)

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

  def createModelLine(self, document, **kw):
    return document.newContent(portal_type='Pay Sheet Model Line', **kw)

  def stepModelCreateUrssafModelLine(self, sequence=None, **kw):
    model = sequence.get('model')
    model_line = self.createModelLine(model)
    model_line.edit(title='Urssaf',
                    int_index=2,
                    trade_phase='trade_phase/payroll/france/urssaf',
                    resource_value=sequence.get('urssaf_payroll_service'),
                    variation_category_list=['tax_category/employee_share',
                                             'tax_category/employer_share'],
                    base_application_list=[ 'base_amount/base_salary'],
                    base_contribution_list=['base_amount/deductible_tax'])
    sequence.edit(urssaf_model_line = model_line)

  def stepCreateMovementOnUrssafModelLine(self, sequence=None, **kw):
    model_line = sequence.get('urssaf_model_line')
    cell1 = model_line.newCell('tax_category/employee_share',
        portal_type='Pay Sheet Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell1.edit(price=0.1, tax_category='employee_share')
    cell2 = model_line.newCell('tax_category/employer_share',
        portal_type='Pay Sheet Cell',
        base_id='movement',
        mapped_value_property_list=('quantity', 'price'))
    cell2.edit(price=0.5, tax_category='employer_share')
    sequence.edit(urssaf_model_line_cell1 = cell1)
    sequence.edit(urssaf_model_line_cell2 = cell2)

  def createPaysheet(self, sequence=None, **kw):
    module = self.portal.getDefaultModule(portal_type='Pay Sheet Transaction')
    return module.newContent(portal_type='Pay Sheet Transaction')

  def stepCreateBasicPaysheet(self, sequence=None, **kw):
    paysheet = self.createPaysheet()
    paysheet.edit(title='test 1',
                  specialise_value=sequence.get('model'),
                  source_section_value=sequence.get('employee'),
                  destination_section_value=sequence.get('employer'))
    sequence.edit(paysheet = paysheet)

  def createPaysheetLine(self, document, **kw):
    return document.newContent(portal_type='Pay Sheet Line', **kw)

  def stepPaysheetCreateLabourPaySheetLine(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line = self.createPaysheetLine(paysheet)
    paysheet_line.edit(title='Labour',
                    int_index=1,
                    price=20,
                    quantity=150,
                    resource_value=sequence.get('labour_payroll_service'),
                    base_contribution_list=[ 'base_amount/base_salary'])
    sequence.edit(labour_paysheet_line = paysheet_line)

  def stepCheckUpdateAggregatedMovementReturn(self, sequence=None, **kw):
    model = sequence.get('model')
    paysheet = sequence.get('paysheet')
    movement_dict = model.updateAggregatedAmountList(context=paysheet)
    movement_to_delete = movement_dict['movement_to_delete_list']
    movement_to_add = movement_dict['movement_to_add_list']
    self.assertEquals(len(movement_to_delete), 0)
    self.assertEquals(len(movement_to_add), 2)

  def stepPaysheetApplyTransformation(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet.applyTransformation()

  def stepCheckPaysheetLineAreCreated(self, sequence=None, **kw):
    paysheet = sequence.get('paysheet')
    paysheet_line_list = paysheet.contentValues(portal_type='Pay Sheet Line')
    self.assertEqual(len(paysheet_line_list), 2)
    self.assertEqual(len(paysheet.getMovementList(portal_type=\
        'Pay Sheet Cell')), 2)

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
        self.fail("Unknown service for line %s" % paysheet_line)

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
    sequence.edit(business_path=business_path)

  def stepSpecialiseBusinessProcessOnModel(self, sequence=None, **kw):
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
        self.fail("Unknown service for line %s" % paysheet_line)

class TestNewPayroll(TestNewPayrollMixin):
  COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING = """
               CreateUrssafPayrollService
               CreateLabourPayrollService
               CreateEmployer
               CreateEmployee
               CreateBasicModel
               ModelCreateUrssafModelLine
               CreateMovementOnUrssafModelLine
               CreateBasicPaysheet
               PaysheetCreateLabourPaySheetLine
               Tic
  """

  def test_01_basicPaySheetCalculation(self):
    '''
      test applyTransformation method. It should create new movements
    '''
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CheckUpdateAggregatedMovementReturn
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreated
               CheckPaysheetLineAmounts
               CheckUpdateAggregatedAmountListReturnNothing
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_setSourceOnMovementUsingBusinessProcess(self):
    sequence_list = SequenceList()
    sequence_string = self.COMMON_BASIC_DOCUMENT_CREATION_SEQUENCE_STRING + """
               CreateBusinessProcess
               CreateBusinessPath
               CreateUrssafRoubaixOrganisation
               ModifyBusinessPathTradePhase
               SpecialiseBusinessProcessOnModel
               Tic
               CheckUpdateAggregatedMovementReturn
               PaysheetApplyTransformation
               Tic
               CheckSourceSectionOnMovements
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNewPayroll))
  return suite
