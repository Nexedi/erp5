##############################################################################
#
# Copyright (c) 2005-2009 Nexedi SA and Contributors. All Rights Reserved.
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

from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, Query
from AccessControl import getSecurityManager
from Products.ERP5Type.tests.utils import updateCellList

class TestBudget(ERP5TypeTestCase):

  def afterSetUp(self):
    self.validateRules()
    product_line = self.portal.portal_categories.product_line
    if '1' not in product_line.objectIds():
      category = product_line.newContent(portal_type='Category', id='1')
      category.newContent(portal_type='Category', id='1.1')
      category.newContent(portal_type='Category', id='1.2')
    if '2' not in product_line.objectIds():
      category = product_line.newContent(portal_type='Category', id='2')
      category.newContent(portal_type='Category', id='2.1')
      category.newContent(portal_type='Category', id='2.2')

  def beforeTearDown(self):
    self.abort()
    self.portal.accounting_module.manage_delObjects(
       list(self.portal.accounting_module.objectIds()))
    self.tic()

  def getBusinessTemplateList(self):
    """Return the list of required business templates.
    We'll use erp5_accounting_ui_test to have some content
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_simplified_invoicing',
            'erp5_accounting_ui_test', 'erp5_budget',
            'erp5_configurator_standard_solver',
            'erp5_configurator_standard_trade_template',
            'erp5_configurator_standard_accounting_template',
            'erp5_configurator_standard_invoicing_template',
            'erp5_simulation_test')

  # creation and basic functionalities
  def test_simple_create_budget_model(self):
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='node_category',
                    variation_base_category='site',
                    )
    self.assertEqual([], budget_model.checkConsistency())

  def test_simple_create_budget(self):
    budget = self.portal.budget_module.newContent(
                            portal_type='Budget')
    budget_line = budget.newContent(portal_type='Budget Line')
    budget_line.newContent(portal_type='Budget Cell')
    self.assertEqual([], budget.checkConsistency())

  def test_budget_cell_node_variation_with_aggregate(self):
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    specialise_value=budget_model)
    budget_line = budget.newContent(portal_type='Budget Line')
    self.assertEqual(['source'],
                      budget_line.getVariationBaseCategoryList())
    self.assertEqual(
        [('Goods Purchase', 'source/account_module/goods_purchase'),
         ('Fixed Assets', 'source/account_module/fixed_assets')],
        budget_line.BudgetLine_getVariationRangeCategoryList())

    budget_line.setVariationCategoryList(
         ('source/account_module/goods_purchase',))
    self.assertEqual(
        ['source/account_module/goods_purchase'],
        budget_line.getVariationCategoryList())

    # This was a budget cell variation, so no criterion is set on budget line
    self.assertEqual(budget_line.getMembershipCriterionCategoryList(), [])
    self.assertEqual(
        budget_line.getMembershipCriterionBaseCategoryList(), [])


    # simuate a request and call Base_edit, which does all the work of creating
    # cell and setting cell properties.
    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="5",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'source/account_module/goods_purchase'],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))
    budget_cell = budget_line.getCell('source/account_module/goods_purchase')
    self.assertNotEqual(None, budget_cell)

    self.assertEqual(['source/account_module/goods_purchase'],
        budget_cell.getMembershipCriterionCategoryList())
    self.assertEqual(5, budget_cell.getQuantity())

    # there is no budget consumption
    self.assertEqual(0, budget_cell.getConsumedBudget())
    self.assertEqual(0, budget_cell.getEngagedBudget())
    self.assertEqual(5, budget_cell.getAvailableBudget())
    # there is no budget transfer
    self.assertEqual(5, budget_cell.getCurrentBalance())

  def test_budget_cell_node_variation_with_aggregate_using_category(self):
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='node_category',
                    variation_base_category='account_type',
                    aggregate_value_list=(
                      self.portal.portal_categories.account_type.expense,
                      self.portal.portal_categories.account_type.income,
                    ))
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    specialise_value=budget_model)
    budget_line = budget.newContent(portal_type='Budget Line')
    self.assertEqual(['account_type'],
                      budget_line.getVariationBaseCategoryList())
    self.assertEqual(
        [('Expense', 'account_type/expense'),
         ('Income', 'account_type/income')],
        budget_line.BudgetLine_getVariationRangeCategoryList())

    budget_line.setVariationCategoryList(
         ('account_type/expense',))
    self.assertEqual(
        ['account_type/expense'],
        budget_line.getVariationCategoryList())

    # This was a budget cell variation, so no criterion is set on budget line
    self.assertEqual(budget_line.getMembershipCriterionCategoryList(), [])
    self.assertEqual(
        budget_line.getMembershipCriterionBaseCategoryList(), [])

    # simuate a request and call Base_edit, which does all the work of creating
    # cell and setting cell properties.
    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="5",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'account_type/expense'],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))
    budget_cell = budget_line.getCell('account_type/expense')
    self.assertNotEqual(None, budget_cell)

    self.assertEqual(['account_type/expense'],
        budget_cell.getMembershipCriterionCategoryList())
    self.assertEqual(5, budget_cell.getQuantity())

    # there is no budget consumption
    self.assertEqual(0, budget_cell.getConsumedBudget())
    self.assertEqual(0, budget_cell.getEngagedBudget())
    self.assertEqual(5, budget_cell.getAvailableBudget())
    # there is no budget transfer
    self.assertEqual(5, budget_cell.getCurrentBalance())

  def test_category_budget_cell_variation(self):
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='node_category',
                    variation_base_category='account_type',)
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    specialise_value=budget_model)
    budget_line = budget.newContent(portal_type='Budget Line')
    self.assertEqual(['account_type'],
                      budget_line.getVariationBaseCategoryList())

    variation_range_category_list = \
       budget_line.BudgetLine_getVariationRangeCategoryList()
    self.assertIn(['', ''], variation_range_category_list)
    self.assertIn(['Expense', 'account_type/expense'], variation_range_category_list)

  def test_category_budget_line_variation(self):
    # test that using a variation on budget line level sets membership
    # criterion on budget line
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_line',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    specialise_value=budget_model)
    budget_line = budget.newContent(portal_type='Budget Line')

    self.assertEqual(['group'],
                      budget_line.getVariationBaseCategoryList())

    variation_range_category_list = \
       budget_line.BudgetLine_getVariationRangeCategoryList()

    self.assertIn(['', ''], variation_range_category_list)
    self.assertIn(['Demo Group', 'group/demo_group'], variation_range_category_list)

    budget_line.edit(variation_category_list=['group/demo_group'])
    self.assertEqual(['group'],
        budget_line.getMembershipCriterionBaseCategoryList())
    self.assertEqual(['group/demo_group'],
        budget_line.getMembershipCriterionCategoryList())

  def test_category_budget_line_and_budget_cell_variation(self):
    # test that using a variation on budget line level sets membership
    # criterion on budget line, but not on budget cell
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_line',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node_category',
                    variation_base_category='account_type',)
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    specialise_value=budget_model)
    budget_line = budget.newContent(portal_type='Budget Line')

    self.assertEqual(['group', 'account_type'],
                      budget_line.getVariationBaseCategoryList())

    budget_line.edit(variation_category_list=['group/demo_group',
                                              'account_type/expense'])
    self.assertEqual(['group'],
        budget_line.getMembershipCriterionBaseCategoryList())
    self.assertEqual(['group/demo_group'],
        budget_line.getMembershipCriterionCategoryList())

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="1",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'account_type/expense'],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))
    budget_cell = budget_line.getCell('account_type/expense')
    self.assertEqual(['account_type'],
                       budget_cell.getMembershipCriterionBaseCategoryList())
    self.assertEqual(['account_type/expense'],
                       budget_cell.getMembershipCriterionCategoryList())


  def test_category_budget_variation(self):
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    specialise_value=budget_model)

    self.assertEqual(['group'],
                      budget.getVariationBaseCategoryList())

    variation_range_category_list = \
       budget.Budget_getVariationRangeCategoryList()

    self.assertIn(['', ''], variation_range_category_list)
    self.assertIn(['Demo Group', 'group/demo_group'], variation_range_category_list)

    # setting this variation on the budget also sets membership
    budget.edit(variation_category_list=['group/demo_group'])
    self.assertEqual('demo_group', budget.getGroup())
    self.assertEqual('Demo Group', budget.getGroupTitle())

  # consumptions
  def test_simple_consumption(self):
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='node_category',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget.edit(variation_category_list=['group/demo_group'])
    budget_line = budget.newContent(portal_type='Budget Line')

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'source/account_module/goods_purchase',
          'source/account_module/fixed_assets',
          'account_type/expense',
          'account_type/asset', ))

    # simuate a request and call Base_edit, which does all the work of creating
    # cell and setting cell properties.
    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[],
             field_matrixbox_quantity_cell_1_0_0="2",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[
               'source/account_module/fixed_assets',
               'account_type/asset'],
             field_matrixbox_quantity_cell_0_1_0="1",
             field_matrixbox_membership_criterion_category_list_cell_0_1_0=[
               'source/account_module/goods_purchase',
               'account_type/expense'],
             field_matrixbox_quantity_cell_1_1_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_1_0=[],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(2, len(budget_line.contentValues()))
    budget_cell = budget_line.getCell('source/account_module/goods_purchase',
                                      'account_type/expense')
    self.assertNotEqual(None, budget_cell)
    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category=['account_type/expense'],
             node_uid=[self.portal.account_module.goods_purchase.getUid()],
             section_category=['group/demo_group'],),
        budget_model.getInventoryQueryDict(budget_cell))

    budget_cell = budget_line.getCell('source/account_module/fixed_assets',
                                      'account_type/asset')
    self.assertNotEqual(None, budget_cell)
    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category=['account_type/asset'],
             node_uid=[self.portal.account_module.fixed_assets.getUid()],
             section_category=['group/demo_group'],),
        budget_model.getInventoryQueryDict(budget_cell))

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category=['account_type/expense', 'account_type/asset'],
             node_uid=[self.portal.account_module.goods_purchase.getUid(),
                       self.portal.account_module.fixed_assets.getUid()],
             section_category=['group/demo_group'],
             group_by_node_category=True,
             group_by_node=True,
             group_by_section_category=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))


    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_debit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  source_credit=100)
    atransaction.confirm()

    # a confirmed transaction engages budget
    self.tic()

    self.assertEqual({}, budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getEngagedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): 102.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): -99.0},
        budget_line.getAvailableBudgetDict())

    atransaction.stop()
    # a stopped transaction consumes budget
    self.tic()

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getEngagedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): 102.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): -99.0},
        budget_line.getAvailableBudgetDict())

    # we can view the forms without error
    budget_line.BudgetLine_viewEngagedBudget()
    budget_line.BudgetLine_viewConsumedBudget()
    budget_line.BudgetLine_viewAvailableBudget()

  def test_all_other_and_strict_consumption(self):
    # tests consumptions, by using "all other" virtual node on a node budget
    # variation, and strict membership on category budget variation
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget',
                    inventory_axis='section_category_strict_membership',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,),
                    include_virtual_other_node=True)
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='node_category_strict_membership',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget.edit(variation_category_list=['group/demo_group/sub1'])
    budget_line = budget.newContent(portal_type='Budget Line')

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'source/account_module/goods_purchase',
          'source/budget_special_node/all_other', # this is 'all others'
          'account_type/expense',
          'account_type/asset', ))

    # simuate a request and call Base_edit, which does all the work of creating
    # cell and setting cell properties.
    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[],
             field_matrixbox_quantity_cell_1_0_0="2",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[
               'source/budget_special_node/all_other',
               'account_type/asset'],
             field_matrixbox_quantity_cell_0_1_0="1",
             field_matrixbox_membership_criterion_category_list_cell_0_1_0=[
               'source/account_module/goods_purchase',
               'account_type/expense'],
             field_matrixbox_quantity_cell_1_1_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_1_0=[],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(2, len(budget_line.contentValues()))

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category_strict_membership=['account_type/expense',
                                              'account_type/asset'],
             section_category_strict_membership=['group/demo_group/sub1'],
             group_by_node_category_strict_membership=True,
             group_by_node=True,
             group_by_section_category_strict_membership=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))


    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_debit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  source_credit=100)
    atransaction.stop()

    self.tic()

    self.assertEqual(
      {('source/budget_special_node/all_other', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source/budget_special_node/all_other', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getEngagedBudgetDict())

    self.assertEqual(
      {('source/budget_special_node/all_other', 'account_type/asset'): 102.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): -99.0},
        budget_line.getAvailableBudgetDict())

  def test_none_virtual_node(self):
    # tests consumptions, by using "none" virtual node on a node budget
    # variation
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    # this does not work for movement, node and section
                    # categories ...
                    inventory_axis='project',
                    variation_base_category='source_project',
                    aggregate_value_list=(
                      self.portal.organisation_module.my_organisation,),
                    include_virtual_none_node=True)
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=2,
                    budget_variation='budget_line',
                    inventory_axis='node_category_strict_membership',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget_line = budget.newContent(portal_type='Budget Line')

    budget_line.edit(
        variation_category_list=(
          'source_project/organisation_module/my_organisation',
          'source_project/budget_special_node/none', # this is 'none'
          'account_type/expense',))

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="100",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'source_project/organisation_module/my_organisation',],
             field_matrixbox_quantity_cell_1_0_0="200",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[
               'source_project/budget_special_node/none',],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(2, len(budget_line.contentValues()))

    test_class_self = self
    class ReferenceQuery:
      """Helper class to compare queries
      """
      def __eq__(self, query):
        test_class_self.assertTrue(isinstance(query, ComplexQuery))
        test_class_self.assertEqual(query.logical_operator, 'or')
        test_class_self.assertEqual(2, len(query.query_list))
        test_class_self.assertEqual(query.query_list[0].kw, {'project_uid': None})
        test_class_self.assertEqual(query.query_list[1].kw,
          {'project_uid':
            [test_class_self.portal.organisation_module.my_organisation.getUid()]})
        return True

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category_strict_membership=['account_type/expense',],
             project_uid=ReferenceQuery(),
             group_by_node_category_strict_membership=True,
             group_by_project=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))

    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  source_section_value=self.portal.organisation_module.my_organisation,
                  resource_value=self.portal.currency_module.euro,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_project_value=self.portal.organisation_module.my_organisation,
                  source_debit=200)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_credit=300)
    atransaction.stop()

    self.tic()

    self.assertEqual(
      {('source_project/organisation_module/my_organisation',): 200.0,
       ('source_project/budget_special_node/none',): -300.0
       }, budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source_project/organisation_module/my_organisation',): 200.0,
       ('source_project/budget_special_node/none',): -300.0
       }, budget_line.getEngagedBudgetDict())

  def test_only_none_virtual_node(self):
    # tests consumptions, by using only "none" virtual node on a node budget
    # variation
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    # this does not work for movement, node and section
                    # categories ...
                    inventory_axis='project',
                    variation_base_category='source_project',
                    aggregate_value_list=(
                      self.portal.organisation_module.my_organisation,),
                    include_virtual_none_node=True)
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=2,
                    budget_variation='budget_line',
                    inventory_axis='node_category_strict_membership',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget_line = budget.newContent(portal_type='Budget Line')

    budget_line.edit(
        variation_category_list=(
          'source_project/budget_special_node/none', # this is 'none'
          'account_type/expense',))

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="200",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'source_project/budget_special_node/none',],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))

    test_class_self = self
    class ReferenceQuery:
      """Helper class to compare queries
      """
      def __eq__(self, query):
        test_class_self.assertTrue(isinstance(query, Query))
        test_class_self.assertEqual(query.kw, {'project_uid': None})
        return True

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category_strict_membership=['account_type/expense',],
             project_uid=ReferenceQuery(),
             group_by_node_category_strict_membership=True,
             group_by_project=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))

    budget_cell = budget_line.contentValues()[0]
    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category_strict_membership=['account_type/expense',],
             project_uid=ReferenceQuery(),
             ),
        budget_model.getInventoryQueryDict(budget_cell))

    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  source_section_value=self.portal.organisation_module.my_organisation,
                  resource_value=self.portal.currency_module.euro,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_project_value=self.portal.organisation_module.my_organisation,
                  source_debit=200)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_credit=300)
    atransaction.stop()

    self.tic()

    self.assertEqual(
      {('source_project/budget_special_node/none',): -300.0
       }, budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source_project/budget_special_node/none',): -300.0
       }, budget_line.getEngagedBudgetDict())

    self.assertEqual(-300, budget_cell.getConsumedBudget())

  def test_none_and_all_others_virtual_nodes_together(self):
    # tests consumptions, by using "none" and "all other" virtual nodes
    # together on a node budget variation
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='project',
                    variation_base_category='source_project',
                    aggregate_value_list=(
                      self.portal.organisation_module.my_organisation,),
                    include_virtual_other_node=True,
                    include_virtual_none_node=True)
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=2,
                    budget_variation='budget_line',
                    inventory_axis='node_category_strict_membership',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget_line = budget.newContent(portal_type='Budget Line')

    budget_line.edit(
        variation_category_list=(
          'source_project/organisation_module/my_organisation',
          'source_project/budget_special_node/none', # this is 'none'
          'source_project/budget_special_node/all_other', # this is 'all_other'
          'account_type/expense',))

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="100",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'source_project/organisation_module/my_organisation',],
             field_matrixbox_quantity_cell_1_0_0="200",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[
               'source_project/budget_special_node/none',],
             field_matrixbox_quantity_cell_2_0_0="300",
             field_matrixbox_membership_criterion_category_list_cell_2_0_0=[
               'source_project/budget_special_node/all_other',],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(3, len(budget_line.contentValues()))

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category_strict_membership=['account_type/expense',],
             group_by_node_category_strict_membership=True,
             group_by_project=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))

    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  source_section_value=self.portal.organisation_module.my_organisation,
                  resource_value=self.portal.currency_module.euro,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_project_value=self.portal.organisation_module.my_organisation,
                  source_debit=200)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  # this will count for all other
                  source_project_value=self.portal.organisation_module.client_1,
                  source_credit=80)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  # this will count for none
                  source_credit=120)
    atransaction.stop()

    self.tic()

    self.assertEqual(
      {('source_project/organisation_module/my_organisation',): 200.0,
       ('source_project/budget_special_node/all_other',): -80.0,
       ('source_project/budget_special_node/none',): -120.0
       }, budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source_project/organisation_module/my_organisation',): 200.0,
       ('source_project/budget_special_node/all_other',): -80.0,
       ('source_project/budget_special_node/none',): -120.0
       }, budget_line.getEngagedBudgetDict())

  def test_full_consumption_detail_node_variation(self):
    # tests consumptions, by using "full consumption detail" on a node budget
    # variation
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget',
                    inventory_axis='section_category_strict_membership',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ),
                    full_consumption_detail=True)
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='node_category_strict_membership',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget.edit(variation_category_list=['group/demo_group/sub1'])
    budget_line = budget.newContent(portal_type='Budget Line')

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'source/account_module/goods_purchase',
            # Fixed assets is in the cell range, but is not selected
          'account_type/expense',
          'account_type/asset', ))

    # simuate a request and call Base_edit, which does all the work of creating
    # cell and setting cell properties.
    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[],
             field_matrixbox_quantity_cell_0_1_0="1",
             field_matrixbox_membership_criterion_category_list_cell_0_1_0=[
               'source/account_module/goods_purchase',
               'account_type/expense'],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))

    # At this time there are no consumption, so consumption and definition cell
    # ranges are all the same.
    default_cell_range = [['source/account_module/goods_purchase'],
                           ['account_type/asset', 'account_type/expense']]

    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('cell'))
    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('consumed'))
    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('engaged'))
    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('available'))

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_category_strict_membership=['account_type/expense',
                                              'account_type/asset'],
             section_category_strict_membership=['group/demo_group/sub1'],
             group_by_node_category_strict_membership=True,
             group_by_node=True,
             node_uid=[self.portal.account_module.goods_purchase.getUid(),
                       self.portal.account_module.fixed_assets.getUid()],
             group_by_section_category_strict_membership=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))


    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_debit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  source_credit=100)
    atransaction.stop()

    self.tic()

    # Now that we have consumptions, consumption cell ranges are updated
    consumption_cell_range = [['source/account_module/goods_purchase',
                               'source/account_module/fixed_assets'],
                           ['account_type/asset', 'account_type/expense']]
    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('cell'))
    self.assertEqual(consumption_cell_range,
        budget_line.BudgetLine_asCellRange('consumed'))
    self.assertEqual(consumption_cell_range,
        budget_line.BudgetLine_asCellRange('engaged'))
    self.assertEqual(consumption_cell_range,
        budget_line.BudgetLine_asCellRange('available'))

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getEngagedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): 100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): -99.0},
        budget_line.getAvailableBudgetDict())

    cell = budget_line.getCell('source/account_module/goods_purchase',
        'account_type/expense')
    self.assertEqual(100, cell.getConsumedBudget())
    self.assertEqual(100, cell.getEngagedBudget())

  def test_full_consumption_detail_category_variation(self):
    # tests consumptions, by using "full consumption detail" on a category
    # budget variation
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget',
                    inventory_axis='section_category_strict_membership',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='node_category_strict_membership',
                    variation_base_category='account_type',
                    full_consumption_detail=True)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget.edit(variation_category_list=['group/demo_group/sub1'])
    budget_line = budget.newContent(portal_type='Budget Line')

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'source/account_module/goods_purchase',
          'source/account_module/fixed_assets',
          'account_type/expense',
            # account type asset is in the cell range, but is not selected
          ))

    # simuate a request and call Base_edit, which does all the work of creating
    # cell and setting cell properties.
    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="1",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'source/account_module/goods_purchase',
               'account_type/expense'],
             field_matrixbox_quantity_cell_1_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))

    # At this time there are no consumption, so consumption and definition cell
    # ranges are all the same.
    default_cell_range = [['source/account_module/goods_purchase',
                            'source/account_module/fixed_assets'],
                           ['account_type/expense']]

    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('cell'))
    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('consumed'))
    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('engaged'))
    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('available'))

    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_debit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  source_credit=100)
    atransaction.stop()

    self.tic()

    # Now that we have consumptions, consumption cell ranges are updated
    consumption_cell_range = [['source/account_module/goods_purchase',
                               'source/account_module/fixed_assets'],
                           ['account_type/asset', 'account_type/expense']]
    self.assertEqual(default_cell_range,
        budget_line.BudgetLine_asCellRange('cell'))
    self.assertEqual(consumption_cell_range,
        budget_line.BudgetLine_asCellRange('consumed'))
    self.assertEqual(consumption_cell_range,
        budget_line.BudgetLine_asCellRange('engaged'))
    self.assertEqual(consumption_cell_range,
        budget_line.BudgetLine_asCellRange('available'))


    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): -100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): 100.0},
        budget_line.getEngagedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'account_type/asset'): 100.0,
       ('source/account_module/goods_purchase', 'account_type/expense'): -99.0},
        budget_line.getAvailableBudgetDict())

    cell = budget_line.getCell('source/account_module/goods_purchase',
        'account_type/expense')
    self.assertEqual(100, cell.getConsumedBudget())
    self.assertEqual(100, cell.getEngagedBudget())

  def test_consumption_movement_category(self):
    # test for budget consumption using movement category
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='movement',
                    variation_base_category='product_line',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget.edit(variation_category_list=['group/demo_group'])
    budget_line = budget.newContent(portal_type='Budget Line')

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'source/account_module/goods_purchase',
          'source/account_module/fixed_assets',
          'product_line/1',
          'product_line/1/1.1',
          'product_line/1/1.2', ))

    # simuate a request and call Base_edit, which does all the work of creating
    # cell and setting cell properties.
    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

            # this cell will be a summary cell
             field_matrixbox_quantity_cell_0_0_0="2",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'source/account_module/goods_purchase',
               'product_line/1'],
             field_matrixbox_quantity_cell_1_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[],
             field_matrixbox_quantity_cell_0_1_0="2",
             field_matrixbox_membership_criterion_category_list_cell_0_1_0=[
               'source/account_module/goods_purchase',
               'product_line/1/1.1'],
             field_matrixbox_quantity_cell_1_1_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_1_0=[],
             field_matrixbox_quantity_cell_0_2_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_2_0=[],
             field_matrixbox_quantity_cell_1_2_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_2_0=[],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(2, len(budget_line.contentValues()))

    product_line_1 = self.portal.portal_categories.product_line['1']
    product_line_1_11 = product_line_1['1.1']
    product_line_1_12 = product_line_1['1.2']

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_uid=[self.portal.account_module.goods_purchase.getUid(),
                       self.portal.account_module.fixed_assets.getUid(),],
             default_product_line_uid=[product_line_1.getUid(),
                                       product_line_1_11.getUid(),
                                       product_line_1_12.getUid(),],
             section_category=['group/demo_group'],
             group_by=['default_product_line_uid'],
             # select list is passed, because getInventoryList does not add
             # group by related keys to select
             select_list=['default_product_line_uid'],
             group_by_node=True,
             group_by_section_category=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))


    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  product_line_value=product_line_1_11,
                  source_debit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  product_line_value=product_line_1_12,
                  source_credit=100)
    atransaction.stop()

    self.tic()

    self.assertEqual(
      {('source/account_module/fixed_assets', 'product_line/1/1.2'): -100.0,
       ('source/account_module/goods_purchase', 'product_line/1/1.1'): 100.0,
       # summary lines are automatically added
       ('source/account_module/fixed_assets', 'product_line/1'): -100.0,
       ('source/account_module/goods_purchase', 'product_line/1'): 100.0
       },
        budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'product_line/1/1.2'): -100.0,
       ('source/account_module/goods_purchase', 'product_line/1/1.1'): 100.0,
       ('source/account_module/fixed_assets', 'product_line/1'): -100.0,
       ('source/account_module/goods_purchase', 'product_line/1'): 100.0
       },
        budget_line.getEngagedBudgetDict())

    self.assertEqual(
      {('source/account_module/fixed_assets', 'product_line/1/1.2'): 100.0,
       ('source/account_module/goods_purchase', 'product_line/1/1.1'): -98.0,
       ('source/account_module/fixed_assets', 'product_line/1'): 100.0,
       ('source/account_module/goods_purchase', 'product_line/1'): -98,
       },
        budget_line.getAvailableBudgetDict())

  def test_consumption_category_variation_summary(self):
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget_line = budget.newContent(portal_type='Budget Line',)

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'source/account_module/goods_purchase',
          'group/demo_group',
          'group/demo_group/sub1',
          ))

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[],
             field_matrixbox_quantity_cell_1_0_0="500",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[
               'group/demo_group/sub1',
               'source/account_module/goods_purchase', ],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_uid=[self.portal.account_module.goods_purchase.getUid(),],
             section_category=['group/demo_group',
                               'group/demo_group/sub1'],
             group_by_node=True,
             group_by_section_category=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))


    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_debit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  source_credit=100)
    atransaction.stop()

    self.tic()

    self.assertEqual(
      {('group/demo_group/sub1', 'source/account_module/goods_purchase'): 100.0,
       ('group/demo_group', 'source/account_module/goods_purchase'): 100.0,},
       budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('group/demo_group/sub1', 'source/account_module/goods_purchase'): 100.0,
       ('group/demo_group', 'source/account_module/goods_purchase'): 100.0,},
       budget_line.getEngagedBudgetDict())

  def test_consumption_node_budget_variation_not_set(self):
    # test consumption calculation when a node budget variation is used, but
    # this variation category is not set
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget_line = budget.newContent(portal_type='Budget Line',)

    # we don't set
    budget_line.edit(
        variation_category_list=(
          'group/demo_group/sub1',
          ))

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="500",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'group/demo_group/sub1', ],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             section_category=['group/demo_group/sub1',],
             group_by_section_category=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))


    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_debit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  source_credit=100)
    atransaction.stop()

    self.tic()

    self.assertEqual(
      {('group/demo_group/sub1', ): 0.0, },
       budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('group/demo_group/sub1', ): 0.0, },
       budget_line.getEngagedBudgetDict())

  def test_consumption_category_budget_variation_not_set(self):
    # test consumption calculation when a category budget variation is used, but
    # this variation category is not set
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget_line = budget.newContent(portal_type='Budget Line',)

    # we don't set
    budget_line.edit(
        variation_category_list=(
          'source/account_module/goods_purchase',
          ))

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="500",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[
               'source/account_module/goods_purchase', ],
        ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))

    self.assertEqual(
        dict(from_date=DateTime(2000, 1, 1),
             at_date=DateTime(2000, 12, 31).latestTime(),
             node_uid=[self.portal.account_module.goods_purchase.getUid(),],
             group_by_node=True,
             ),
        budget_model.getInventoryListQueryDict(budget_line))


    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_debit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  source_credit=100)
    atransaction.stop()

    self.tic()

    self.assertEqual(
      {('source/account_module/goods_purchase', ): 100.0, },
       budget_line.getConsumedBudgetDict())

    self.assertEqual(
      {('source/account_module/goods_purchase', ): 100.0, },
       budget_line.getEngagedBudgetDict())

  def test_multiple_variation_line_level(self):
    # tests the behaviour of getInventoryListQueryDict and
    # getInventoryQueryDict when we are using budget line level variation with
    # multiple variation set. It should be a 'OR' between all the selected
    # variations.
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=1,
                    budget_variation='budget_line',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=2,
                    budget_variation='budget_line',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    # this variation will be needed to create cells
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='node_category_strict_membership',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    specialise_value=budget_model)
    budget_line = budget.newContent(portal_type='Budget Line')

    budget_line.edit(
        variation_category_list=['group/demo_group/sub1',
                                 'group/demo_group/sub2',
                                 'source/account_module/goods_purchase',
                                 'source/account_module/fixed_assets',
                                 ])
    self.assertEqual({
      'from_date': None,
      'group_by_node': True,
      'group_by_section_category': True,
      'section_category': ['group/demo_group/sub1',
                           'group/demo_group/sub2'],
      'node_uid': [self.portal.account_module.goods_purchase.getUid(),
                   self.portal.account_module.fixed_assets.getUid()], },
      budget_model.getInventoryListQueryDict(budget_line))

    self.assertEqual({
      'from_date': None,
      'simulation_state': ('delivered', 'stopped', 'started'),
      'transit_simulation_state': ('started', ),
      'omit_transit': False,
      # XXX order is reversed for some reason ...
      'section_category': ['group/demo_group/sub2',
                           'group/demo_group/sub1'],
      'node_uid': [self.portal.account_module.fixed_assets.getUid(),
                   self.portal.account_module.goods_purchase.getUid()],
      'node_category_strict_membership': ['account_type/expense']},

      # BudgetLine_getInventoryQueryDictForCellIndex uses getInventoryQueryDict
      # but does not require the cell to be physically present
      budget_line.BudgetLine_getInventoryQueryDictForCellIndex(
        cell_index=('account_type/expense')))


  # Report
  def test_budget_consumption_report(self):
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget',
                    inventory_axis='section_category',
                    variation_base_category='group',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='node_category',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    title='Budget Title',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget.edit(variation_category_list=['group/demo_group'])
    budget_line = budget.newContent(portal_type='Budget Line',
                                    title='Budget Line Title',)

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'source/account_module/goods_purchase',
          'source/account_module/fixed_assets',
          'account_type/asset', ))

    # simuate a request and call Base_edit, which does all the work of creating
    # cell and setting cell properties.
    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             field_matrixbox_quantity_cell_0_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[],
             field_matrixbox_quantity_cell_1_0_0="200",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[
               'source/account_module/fixed_assets',
               'account_type/asset'],
        ))
    budget_line.Base_edit(form_id=form.getId())

    atransaction = self.portal.accounting_module.newContent(
                  portal_type='Accounting Transaction',
                  resource_value=self.portal.currency_module.euro,
                  source_section_value=self.portal.organisation_module.my_organisation,
                  start_date=DateTime(2000, 1, 2))
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.goods_purchase,
                  source_credit=100)
    atransaction.newContent(
                  portal_type='Accounting Transaction Line',
                  source_value=self.portal.account_module.fixed_assets,
                  source_debit=100)
    atransaction.stop()

    self.tic()

    # Budget_getBudgetConsumptionReportData returns all the data for the report
    line_list, line_count = budget.Budget_getBudgetConsumptionReportData()
    # the number of lines, which will be used in the report to set the print
    # range
    self.assertEqual(6, line_count)
    # number of line can be different from the length of the line list, because
    # line list is a recursive structure.
    self.assertEqual(4, len(line_list))

    # first line is for the title of the budget
    self.assertEqual('Budget Title', line_list[0]['title'])
    self.assertTrue(line_list[0]['is_budget'])

    # then we have a first level for budget lines
    self.assertEqual('Budget Line Title', line_list[1]['title'])
    self.assertTrue(line_list[1]['is_level_1'])
    # we can see global consumptions for the budget
    self.assertEqual(200, line_list[2]['initial_budget'])
    self.assertEqual(200, line_list[2]['current_budget'])
    self.assertEqual(100, line_list[2]['consumed_budget'])
    self.assertEqual(100, line_list[2]['engaged_budget'])
    self.assertEqual(.5, line_list[2]['consumed_ratio'])

    # the dimensions are reversed in the budget report, so on level 2 we have
    # the last dimension from cell range, here "account type"
    self.assertEqual('Asset', line_list[2]['title'])
    # we can see global consumptions for that summary line
    self.assertEqual(200, line_list[2]['initial_budget'])
    self.assertEqual(200, line_list[2]['current_budget'])
    self.assertEqual(100, line_list[2]['consumed_budget'])
    self.assertEqual(100, line_list[2]['engaged_budget'])
    self.assertEqual(.5, line_list[2]['consumed_ratio'])

    # no we have a recursive list, for the next dimension: node.
    self.assertTrue(isinstance(line_list[3], list))
    self.assertEqual(3, len(line_list[3]))

    # first is again a title XXX why ??
    self.assertEqual('Asset', line_list[3][0]['title'])
    # then we have two level 3 cells
    self.assertTrue(line_list[3][1]['is_level_3'])
    self.assertEqual('Goods Purchase', line_list[3][1]['title'])
    self.assertEqual(0, line_list[3][1]['initial_budget'])
    self.assertEqual(0, line_list[3][1]['current_budget'])
    self.assertEqual(0, line_list[3][1]['consumed_budget'])
    self.assertEqual(0, line_list[3][1]['engaged_budget'])
    self.assertEqual(0, line_list[3][1]['consumed_ratio'])

    self.assertEqual('Fixed Assets', line_list[3][2]['title'])
    self.assertEqual(200, line_list[3][2]['initial_budget'])
    self.assertEqual(200, line_list[3][2]['current_budget'])
    self.assertEqual(100, line_list[3][2]['consumed_budget'])
    self.assertEqual(100, line_list[3][2]['engaged_budget'])
    self.assertEqual(.5, line_list[3][2]['consumed_ratio'])

    # validate report ODF
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    odf = budget.Budget_viewBudgetConsumptionReport()
    err_list = odf_validator.validate(odf)
    if err_list:
      self.fail(''.join(err_list))

  # "update summary cells" feature
  def test_update_summary_cell_simple(self):
    # test the action to create or update quantity on summary cells
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='movement',
                    variation_base_category='product_line',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='section_category',
                    variation_base_category='group',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget_line = budget.newContent(portal_type='Budget Line')

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'group/demo_group',
          'group/demo_group/sub1',
          'group/demo_group/sub2',
          'source/account_module/goods_purchase',
          'source/account_module/fixed_assets',
          'product_line/1',
          'product_line/1/1.1',
          'product_line/1/1.2', ))

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),

             # group/demo_group
             field_matrixbox_quantity_cell_0_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[],
             field_matrixbox_quantity_cell_1_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[],
             field_matrixbox_quantity_cell_2_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_2_0_0=[],
             field_matrixbox_quantity_cell_0_1_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_1_0=[],
             field_matrixbox_quantity_cell_1_1_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_1_0=[],
             # This is a summary cell, but we set a manual value.
             field_matrixbox_quantity_cell_2_1_0="100",
             field_matrixbox_membership_criterion_category_list_cell_2_1_0=[
                'product_line/1/1.2',
                'source/account_module/fixed_assets',
                'group/demo_group',
                ],

             # group/demo_group/sub1
             field_matrixbox_quantity_cell_0_0_1="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_1=[],
             field_matrixbox_quantity_cell_1_0_1="1",
             field_matrixbox_membership_criterion_category_list_cell_1_0_1=[
                'product_line/1/1.1',
                'source/account_module/goods_purchase',
                'group/demo_group/sub1',
                ],
             field_matrixbox_quantity_cell_2_0_1="2",
             field_matrixbox_membership_criterion_category_list_cell_2_0_1=[
                'product_line/1/1.2',
                'source/account_module/goods_purchase',
                'group/demo_group/sub1',
                ],
             field_matrixbox_quantity_cell_0_1_1="",
             field_matrixbox_membership_criterion_category_list_cell_0_1_1=[],
             field_matrixbox_quantity_cell_1_1_1="3",
             field_matrixbox_membership_criterion_category_list_cell_1_1_1=[
                'product_line/1/1.1',
                'source/account_module/fixed_assets',
                'group/demo_group/sub1',
               ],
             field_matrixbox_quantity_cell_2_1_1="4",
             field_matrixbox_membership_criterion_category_list_cell_2_1_1=[
                'product_line/1/1.2',
                'source/account_module/fixed_assets',
                'group/demo_group/sub1',
               ],

             # group/demo_group/sub2
             field_matrixbox_quantity_cell_0_0_2="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_2=[],
             # we only have 1 cell here
             field_matrixbox_quantity_cell_1_0_2="5",
             field_matrixbox_membership_criterion_category_list_cell_1_0_2=[
                  'product_line/1/1.1',
                  'source/account_module/goods_purchase',
                  'group/demo_group/sub2',
                 ],
             field_matrixbox_quantity_cell_2_0_2="",
             field_matrixbox_membership_criterion_category_list_cell_2_0_2=[],
             # we have no cells here
             field_matrixbox_quantity_cell_0_1_2="",
             field_matrixbox_membership_criterion_category_list_cell_0_1_2=[],
             field_matrixbox_quantity_cell_1_1_2="",
             field_matrixbox_membership_criterion_category_list_cell_1_1_2=[],
             field_matrixbox_quantity_cell_2_1_2="",
             field_matrixbox_membership_criterion_category_list_cell_2_1_2=[],
        ))

    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(6, len(budget_line.contentValues()))

    budget_line.BudgetLine_setQuantityOnSummaryCellList()

    # summary cells have been created:
    self.assertEqual(14, len(budget_line.contentValues()))

    # those cells are aggregating
    self.assertEqual(1+2, budget_line.getCell(
                              'product_line/1',
                              'source/account_module/goods_purchase',
                              'group/demo_group/sub1',).getQuantity())
    self.assertEqual(4+3, budget_line.getCell(
                              'product_line/1',
                              'source/account_module/fixed_assets',
                              'group/demo_group/sub1',).getQuantity())
    self.assertEqual(1+5, budget_line.getCell(
                              'product_line/1/1.1',
                              'source/account_module/goods_purchase',
                              'group/demo_group',).getQuantity())
    self.assertEqual(1+2+5, budget_line.getCell(
                              'product_line/1',
                              'source/account_module/goods_purchase',
                              'group/demo_group',).getQuantity())

    # the cell that we have modified is erased
    self.assertEqual(4, budget_line.getCell(
                              'product_line/1/1.2',
                              'source/account_module/fixed_assets',
                              'group/demo_group',).getQuantity())

    # test all cells for complete coverage
    self.assertEqual(6, budget_line.getCell(
                              'product_line/1/1.1',
                              'source/account_module/goods_purchase',
                              'group/demo_group',).getQuantity())
    self.assertEqual(2, budget_line.getCell(
                              'product_line/1/1.2',
                              'source/account_module/goods_purchase',
                              'group/demo_group',).getQuantity())
    self.assertEqual(3+4, budget_line.getCell(
                              'product_line/1',
                              'source/account_module/fixed_assets',
                              'group/demo_group',).getQuantity())
    self.assertEqual(3, budget_line.getCell(
                              'product_line/1/1.1',
                              'source/account_module/fixed_assets',
                              'group/demo_group',).getQuantity())
    self.assertEqual(4, budget_line.getCell(
                              'product_line/1/1.2',
                              'source/account_module/fixed_assets',
                              'group/demo_group',).getQuantity())
    self.assertEqual(5, budget_line.getCell(
                              'product_line/1',
                              'source/account_module/goods_purchase',
                              'group/demo_group/sub2',).getQuantity())

    # change a cell quantity and call again
    budget_cell = budget_line.getCell(
        'product_line/1/1.2',
        'source/account_module/goods_purchase',
        'group/demo_group/sub1')
    self.assertNotEqual(None, budget_cell)
    self.assertEqual(2, budget_cell.getQuantity())
    budget_cell.setQuantity(6)

    budget_line.BudgetLine_setQuantityOnSummaryCellList()
    self.assertEqual(14, len(budget_line.contentValues()))

    self.assertEqual(1+6, budget_line.getCell(
                              'product_line/1',
                              'source/account_module/goods_purchase',
                              'group/demo_group/sub1',).getQuantity())
    self.assertEqual(4+3, budget_line.getCell(
                              'product_line/1',
                              'source/account_module/fixed_assets',
                              'group/demo_group/sub1',).getQuantity())
    self.assertEqual(1+5, budget_line.getCell(
                              'product_line/1/1.1',
                              'source/account_module/goods_purchase',
                              'group/demo_group',).getQuantity())
    self.assertEqual(1+6+5, budget_line.getCell(
                              'product_line/1',
                              'source/account_module/goods_purchase',
                              'group/demo_group',).getQuantity())


  def test_update_summary_cell_non_strict_and_second_summary(self):
    # test the action to create or update quantity on summary cells, variation
    # which are strict are not updated, and multiple level summary does not
    # aggregate again intermediate summaries
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='movement_strict_membership',
                    variation_base_category='product_line',)
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='node',
                    variation_base_category='source',
                    aggregate_value_list=(
                      self.portal.account_module.goods_purchase,
                      self.portal.account_module.fixed_assets,
                    ))
    budget_model.newContent(
                    portal_type='Category Budget Variation',
                    int_index=3,
                    budget_variation='budget_cell',
                    inventory_axis='node_category',
                    variation_base_category='account_type',)

    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2000, 1, 1),
                    start_date_range_max=DateTime(2000, 12, 31),
                    specialise_value=budget_model)

    budget_line = budget.newContent(portal_type='Budget Line')

    # set the range, this will adjust the matrix
    budget_line.edit(
        variation_category_list=(
          'account_type/asset',
          'account_type/asset/cash',
          'account_type/asset/cash/bank',
          'source/account_module/goods_purchase',
          'product_line/1',
          'product_line/1/1.1', ))

    form = budget_line.BudgetLine_view
    self.portal.REQUEST.other.update(
        dict(AUTHENTICATED_USER=getSecurityManager().getUser(),

             field_membership_criterion_base_category_list=
        form.membership_criterion_base_category_list.get_value('default'),
             field_mapped_value_property_list=
        form.mapped_value_property_list.get_value('default'),
             field_matrixbox_quantity_cell_0_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_0=[],
             field_matrixbox_quantity_cell_1_0_0="",
             field_matrixbox_membership_criterion_category_list_cell_1_0_0=[],
             field_matrixbox_quantity_cell_0_0_1="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_1=[],
             field_matrixbox_quantity_cell_1_0_1="",
             field_matrixbox_membership_criterion_category_list_cell_1_0_1=[],
             field_matrixbox_quantity_cell_0_0_2="",
             field_matrixbox_membership_criterion_category_list_cell_0_0_2=[],
             field_matrixbox_quantity_cell_1_0_2="1",
             field_matrixbox_membership_criterion_category_list_cell_1_0_2=[
                 'product_line/1/1.1',
                 'source/account_module/goods_purchase',
                 'account_type/asset/cash/bank',
               ],
          ))
    budget_line.Base_edit(form_id=form.getId())

    self.assertEqual(1, len(budget_line.contentValues()))

    budget_line.BudgetLine_setQuantityOnSummaryCellList()
    self.assertEqual(3, len(budget_line.contentValues()))

    budget_cell = budget_line.getCell(
        'product_line/1/1.1',
        'source/account_module/goods_purchase',
        'account_type/asset/cash')
    self.assertNotEqual(None, budget_cell)
    self.assertEqual(1, budget_cell.getQuantity())

    budget_cell = budget_line.getCell(
        'product_line/1/1.1',
        'source/account_module/goods_purchase',
        'account_type/asset',)
    self.assertNotEqual(None, budget_cell)
    self.assertEqual(1, budget_cell.getQuantity())

  def updateBudgetCellList(self, budget_line, table_list):
    updateCellList(self.portal,
                   budget_line,
                   'Budget Cell',
                   'BudgetLine_asCellRange',
                   table_list)

  def makeTableList(self, base_id, cell_range_kw,
                    mapped_value_argument_list, table):
    return [{'base_id':base_id,
            'cell_range_kw':cell_range_kw,
            'mapped_value_argument_list':mapped_value_argument_list,
            'table':table
            }]

  def makeQuantityTable(self, table):
    #two_dimension = (
    #  (        column,         column,),
    #  (line,   mapped_value,   mapped_value,),
    #  (line,   mapped_value,   mapped_value,),
    #  )
    return self.makeTableList(
              base_id='cell',
              cell_range_kw={},
              mapped_value_argument_list=('quantity',),
              table=table)

  def testNodeVariationWithMovemetAxisPackingList(self):
    """
     Budgets are normally used with accounting transactions, however it can be
     used with packing lists and other Movement. This is an experimental usage.
    """
    self.portal.product_module.newContent(portal_type='Product',
                                          id='test_product',
                                          title='Test Product')
    self.portal.product_module.newContent(portal_type='Product',
                                          id='demo_product',
                                          title='Demo Prduct')
    self.commit()
    budget_model = self.portal.budget_model_module.newContent(
                            portal_type='Budget Model')
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=1,
                    budget_variation='budget_cell',
                    inventory_axis='movement',
                    variation_base_category='resource',
                    aggregate_value_list=(
                      self.portal.product_module.test_product,
                      self.portal.product_module.demo_product,
                    ))
    budget_model.newContent(
                    portal_type='Node Budget Variation',
                    int_index=2,
                    budget_variation='budget_cell',
                    inventory_axis='mirror_section',
                    variation_base_category='source_section',
                    aggregate_value_list=(
                      self.portal.organisation_module.my_organisation,
                      self.portal.organisation_module.main_organisation
                    ))
    budget = self.portal.budget_module.newContent(
                    portal_type='Budget',
                    start_date_range_min=DateTime(2011, 1, 1),
                    start_date_range_max=DateTime(2011, 12, 31),
                    specialise_value=budget_model)
    budget_line = budget.newContent(portal_type='Budget Line')
    budget_line.edit(
        variation_category_list=(
          'resource/product_module/test_product',
          'resource/product_module/demo_product',
          'source_section/organisation_module/my_organisation',
          'source_section/organisation_module/main_organisation', ))
    self.updateBudgetCellList(
      budget_line,
      self.makeQuantityTable(
        table=[
           ('source_section/organisation_module/my_organisation',
            'source_section/organisation_module/main_organisation'),
           ('resource/product_module/test_product', 12000, 11000),
           ('resource/product_module/demo_product', 17000, 15000),
        ])
    )

    def createPackingList(organisation_id, product_id, quantity, price):
      spl = self.portal.sale_packing_list_module.newContent(
              portal_type='Sale Packing List')
      spl.setSpecialise(
        'business_process_module/erp5_default_business_process')
      spl.setStartDate('2011/08/01')
      spl.setStopDate('2011/08/05')
      spl.setDestinationSection('organisation_module/client_1')
      spl.setDestination('organisation_module/client_1')
      organisation = 'organisation_module/%s' % organisation_id
      spl.setSourceSection(organisation)
      spl.setSource(organisation)
      spll = spl.newContent(portal_type='Sale Packing List Line')
      spll.setQuantity(quantity)
      spll.setPrice(price)
      spll.setResource('product_module/%s' % product_id)
      self.commit()
      spl.confirm()
      self.tic()
      spl.start()
      self.tic()
      spl.stop()
      self.tic()
      return spl

    createPackingList('my_organisation', 'test_product', 100, 5)
    createPackingList('main_organisation', 'demo_product', 200, 6)
    self.tic()
    # Budget Line only support total price. It is considerable to support
    # total_quantity.
    total_price = budget_line.getConsumedBudgetDict().get(
      ('resource/product_module/test_product',
       'source_section/organisation_module/my_organisation'),
      None)
    self.assertNotEqual(None, total_price)
    self.assertEqual(500.0, total_price)
    total_price = budget_line.getEngagedBudgetDict().get(
      ('resource/product_module/demo_product',
       'source_section/organisation_module/main_organisation'),
      None)
    self.assertNotEqual(None, total_price)
    self.assertEqual(1200.0, total_price)


  # Other TODOs:

  # budget level variation and budget cell level variation for same inventory
  # axis

  # resource/price currency on budget ?

  # test virtual all others when cloning an existing budget

  # predicates


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBudget))
  return suite
