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

import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestBudget(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    """Return the list of required business templates.
    We'll use erp5_accounting_ui_test to have some content
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_simplified_invoicing',
            'erp5_accounting_ui_test', 'erp5_budget')

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
    self.assertEquals([], budget_model.checkConsistency())

  def test_simple_create_budget(self):
    budget = self.portal.budget_module.newContent(
                            portal_type='Budget')
    budget_line = budget.newContent(portal_type='Budget Line')
    budget_cell = budget_line.newContent(portal_type='Budget Cell')
    self.assertEquals([], budget.checkConsistency())

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
    self.assertEquals(['source'],
                      budget_line.getVariationBaseCategoryList())
    self.assertEquals(
        [('Goods Purchase', 'source/account_module/goods_purchase'),
         ('Fixed Assets', 'source/account_module/fixed_assets')],
        budget_line.BudgetLine_getVariationRangeCategoryList())

    budget_line.setVariationCategoryList(
         ('source/account_module/goods_purchase',))
    self.assertEquals(
        ['source/account_module/goods_purchase'],
        budget_line.getVariationCategoryList())
  
    # This was a budget cell variation, so no criterion is set on budget line
    self.assertEquals(budget_line.getMembershipCriterionCategoryList(), [])
    self.assertEquals(
        budget_line.getMembershipCriterionBaseCategoryList(), [])

    # TODO: create cells and test variation on cell
  
  # Other TODOs
  # test simple category variation in getInventory
   
  # test that using a category variation on budget level sets membership
  # criterion on budget

  # test that using a variation on budget line level sets membership
  # criterion on budget line (and budget cell or not ?)


  # test that using a category variation on budget level is used in inventory
  # calculation 


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBudget))
  return suite
