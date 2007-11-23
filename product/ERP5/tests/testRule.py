##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from testOrder import TestOrderMixin

class TestRuleMixin(TestOrderMixin):
  """
  Test basic rule behaviours
  """

  def afterSetUp(self):
    self.test_data = []
    # delete rules
    self.getRuleTool().manage_delObjects(
        ids=list(list(self.getRuleTool().objectIds())))
    # recreate rules
    self.getRuleTool().newContent(portal_type="Order Rule",
        id='default_order_rule',
        reference='default_order_rule', version='1')
    self.getRuleTool().newContent(portal_type="Delivery Rule",
        id='default_delivery_rule',
        reference='default_delivery_rule', version='1')
    # create packing list if necessary
    pl_module = self.getPortal().getDefaultModule(
        self.packing_list_portal_type)
    if pl_module.objectCount() == 0:
      self.pl = self.createPackingList()
    else:
      self.pl = self.getPortal().getDefaultModule(
          self.packing_list_portal_type).objectValues()[0]
    #delete applied_rule
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))
    # commit
    get_transaction().commit()
    self.tic()


  def beforeTearDown(self):
    for container, id in self.test_data:
      container.manage_delObjects(ids=[id])
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))
    get_transaction().commit()
    self.tic()

  def getTitle(self):
    return "Rule"

  def getBusinessTemplateList(self):
    """
    Add erp5_dms_mysql_innodb_catalog, as for now, it's the one in charge of
    cataloging the version property.
    """
    return TestOrderMixin.getBusinessTemplateList(self) + ('erp5_accounting',
        'erp5_dms_mysql_innodb_catalog',)

  def createPackingList(self):
    """
    create a packing list, to allow testing
    """
    self.getCategoryTool()['group'].newContent(portal_type='Category', id='a')
    self.getCategoryTool()['group'].newContent(portal_type='Category', id='b')
    pl_module = self.getPortal().getDefaultModule(
        self.packing_list_portal_type)
    pl = pl_module.newContent(portal_type=self.packing_list_portal_type,
        source_section='group/a', destination_section='group/b')
    pl.newContent(portal_type=self.packing_list_line_portal_type, id='line')
    pl.setStartDate("2007-07-01")
    get_transaction().commit()
    self.tic()
    pl.confirm()
    get_transaction().commit()
    self.tic()
    return pl


class TestRule(TestRuleMixin, ERP5TypeTestCase) :

  run_all_test = 1
  quiet = 0

  def test_01_ValidatedRuleWithNoScript(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule is validated, but has no script it will not apply
    """
    if not run: return

    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.validate()
    get_transaction().commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.pl)), 0)

  def test_02_WrongTestMethod(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule's test method returns False, it will not apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'wrong_script', 'rule',
        'return False')
    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.setTestMethodId('wrong_script')
    delivery_rule.validate()
    get_transaction().commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.pl)), 0)

  def test_03_GoodTestMethod(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule's test method returns True, it will apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.validate()
    get_transaction().commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.pl)), 1)

  def test_04_NotValidatedRule(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule is not validated, it will not apply, even if it has
    a good script
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.validate()
    delivery_rule.invalidate()
    get_transaction().commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 0)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.pl)), 0)

  def test_05_ValidatedRule(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule is validated, it will apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.validate()
    get_transaction().commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.pl)), 1)

  def test_06_WrongDateRange(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule is validated but does not have correct date range,
    it will not apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.setStartDateRangeMin('2007-06-01')
    delivery_rule.setStartDateRangeMax('2007-06-04')
    delivery_rule.validate()
    get_transaction().commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.pl)), 0)

  def test_07_GoodDateRange(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule is validated and has a correct date range, it will
    apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.setStartDateRangeMin('2007-06-01')
    delivery_rule.setStartDateRangeMax('2007-08-01')
    delivery_rule.validate()
    get_transaction().commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.pl)), 1)

  def test_08_updateAppliedRule(self, quiet=quiet, run=run_all_test):
    """
    test that when updateAppliedRule is called, the rule with the correct
    reference and higher version is used

    XXX as expand is triggered here, make sure rules won't be created forever
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'rule_script', 'rule',
        "return False")

    # wrong reference
    order_rule = self.getRuleTool().searchFolder(
        reference='default_order_rule')[0]
    order_rule.setTestMethodId('rule_script')
    order_rule.validate()
    
    delivery_rule_1 = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule_1.setTestMethodId('rule_script')
    delivery_rule_1.validate()
    
    delivery_rule_2 = self.getRuleTool().newContent(
        portal_type="Delivery Rule", reference='default_delivery_rule',
        version='2')
    delivery_rule_2.setTestMethodId('rule_script')
    delivery_rule_2.validate()
    get_transaction().commit()
    self.tic()

    # delivery_rule_2 should be applied
    self.pl.updateAppliedRule('default_delivery_rule')
    get_transaction().commit()
    self.tic()
    self.assertEquals(self.pl.getCausalityRelatedValue().getSpecialise(),
        delivery_rule_2.getRelativeUrl())

    self.getSimulationTool().manage_delObjects(
        ids=[self.pl.getCausalityRelatedId()])

    # increase version of delivery_rule_1
    delivery_rule_1.setVersion("3")
    get_transaction().commit()
    self.tic()

    # delivery_rule_1 should be applied
    self.pl.updateAppliedRule('default_delivery_rule')
    get_transaction().commit()
    self.tic()
    self.assertEquals(self.pl.getCausalityRelatedValue().getSpecialise(),
        delivery_rule_1.getRelativeUrl())

  def test_09_expandTwoRules(self, quiet=quiet, run=run_all_test):
    """
    test that when expand is called on a simulation movement, if two rules
    with the same reference are found, only the one with the higher version
    will be applied.

    XXX as expand is triggered here, make sure rules won't be created forever
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'delivery_rule_script', 'rule',
        "return False")

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'invoice_rule_script', 'rule',
        "return context.getParentValue().getSpecialiseReference() == 'default_delivery_rule'")

    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.validate()
    
    invoicing_rule_1 = self.getRuleTool().newContent(
        portal_type="Invoicing Rule", reference='default_invoicing_rule',
        version='1')
    invoicing_rule_1.setTestMethodId('invoice_rule_script')
    invoicing_rule_1.validate()

    invoicing_rule_2 = self.getRuleTool().newContent(
        portal_type="Invoicing Rule", reference='default_invoicing_rule',
        version='2')
    invoicing_rule_2.setTestMethodId('invoice_rule_script')
    invoicing_rule_2.validate()

    # clear simulation
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))
    get_transaction().commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    get_transaction().commit()
    self.tic()

    # check that only one invoicing rule (higher version) was applied
    root_applied_rule = self.pl.getCausalityRelatedValue()
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())

    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_2.getRelativeUrl())

    # increase version of other rule, clean simulation and check again
    self.getSimulationTool().manage_delObjects(
        ids=[self.pl.getCausalityRelatedId()])
    invoicing_rule_1.setVersion('3')
    get_transaction().commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    get_transaction().commit()
    self.tic()

    # check that only one invoicing rule (higher version) was applied
    root_applied_rule = self.pl.getCausalityRelatedValue()
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())

    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())

  def test_10_expandAddsRule(self, quiet=quiet, run=run_all_test):
    """
    test that if a rule didn't match previously, and does now, it should apply
    if no rule with the same type is already applied.
    - test that it happens if no rule is already applied
    - test that nothing changes if a rule of same type is already applied (no
      matter what the reference or version is)
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'delivery_rule_script', 'rule',
        "return False")

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'invoice_rule_script', 'rule',
        "return context.getParentValue().getSpecialiseReference() == 'default_delivery_rule'")

    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.validate()
    
    # create rule with a wrong script
    invoicing_rule_1 = self.getRuleTool().newContent(
        portal_type="Invoicing Rule", reference='default_invoicing_rule',
        version='1')
    invoicing_rule_1.setTestMethodId('delivery_rule_script')
    invoicing_rule_1.validate()

    # clear simulation
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))
    get_transaction().commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    get_transaction().commit()
    self.tic()
    root_applied_rule = self.pl.getCausalityRelatedValue()

    # check that no invoicing rule was applied
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 0)

    # change rule script so that it matches and test again
    invoicing_rule_1.setTestMethodId('invoice_rule_script')
    root_applied_rule.expand()
    get_transaction().commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())

    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())

    # add more invoicing_rule and test that nothing is changed
    ## same reference, higher version
    invoicing_rule_n = self.getRuleTool().newContent(
        portal_type="Invoicing Rule", reference='default_invoicing_rule',
        version='2', test_method_id='invoice_rule_script')
    invoicing_rule_n.validate()
    ## different reference, higher version (but version shouldn't matter here)
    invoicing_rule_n = self.getRuleTool().newContent(
        portal_type="Invoicing Rule", reference='default_invoicing_rule_2',
        version='2', test_method_id='invoice_rule_script')
    invoicing_rule_n.validate()
    get_transaction().commit()
    self.tic()
    root_applied_rule.expand()
    get_transaction().commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())

    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())


  def test_11_expandRemovesRule(self, quiet=quiet, run=run_all_test):
    """
    test that if a rule matched previously and does not anymore, it should be
    removed, if no child movement of this rule is delivered
    - test that it happens if no child is delivered
    - test that nothing is changed if at least one child is delivered
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'delivery_rule_script', 'rule',
        "return False")

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'invoice_rule_script', 'rule',
        "return context.getParentValue().getSpecialiseReference() == 'default_delivery_rule'")

    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.validate()
    
    invoicing_rule_1 = self.getRuleTool().newContent(
        portal_type="Invoicing Rule", reference='default_invoicing_rule',
        version='1')
    invoicing_rule_1.setTestMethodId('invoice_rule_script')
    invoicing_rule_1.validate()

    # clear simulation
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))

    get_transaction().commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    get_transaction().commit()
    self.tic()
    root_applied_rule = self.pl.getCausalityRelatedValue()

    # check that the invoicing rule was applied
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())

    # invalidate the rule and test that it is still there
    invoicing_rule_1.invalidate()
    get_transaction().commit()
    self.tic()
    self.assertEquals(invoicing_rule_1.getValidationState(), 'invalidated')
    root_applied_rule.expand()
    get_transaction().commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())

    # change the test method to one that fails, and test that the rule is
    # removed
    invoicing_rule_1.setTestMethodId('delivery_rule_script')
    root_applied_rule.expand()
    get_transaction().commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 0)

    # change the test to one that succeeds, revalidate, expand, add a delivery
    # relation, change the test method to one that fails, expand, and test
    # that the rule is still there
    invoicing_rule_1.setTestMethodId('invoice_rule_script')
    invoicing_rule_1.validate()
    get_transaction().commit()
    self.tic()
    self.assertEquals(invoicing_rule_1.getValidationState(), 'validated')
    root_applied_rule.expand()
    get_transaction().commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())
    self.assertEquals(applied_rule.objectCount(), 1)
    sub_movement = applied_rule.objectValues()[0]

    sub_movement.setDeliveryValue(self.pl.line)

    invoicing_rule_1.setTestMethodId('delivery_rule_script')
    root_applied_rule.expand()
    get_transaction().commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())
    self.assertEquals(applied_rule.objectCount(), 1)
    sub_movement = applied_rule.objectValues()[0]
    self.assertEquals(sub_movement.getDelivery(), self.pl.line.getRelativeUrl())

  def test_12_expandReplacesRule(self, quiet=quiet, run=run_all_test):
    """
    test that if a rule matched previously and does not anymore, and another
    rule matches now, the old rule should be replaced by the new one, if no
    child movement of this rule is delivered
    - test that it happens if no child is delivered
    - test that nothing is changed if at least one child is delivered
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'delivery_rule_script', 'rule',
        "return False")

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'invoice_rule_script', 'rule',
        "return context.getParentValue().getSpecialiseReference() == 'default_delivery_rule'")

    delivery_rule = self.getRuleTool().searchFolder(
        reference='default_delivery_rule')[0]
    delivery_rule.validate()
    
    invoicing_rule_1 = self.getRuleTool().newContent(
        portal_type="Invoicing Rule", reference='default_invoicing_rule',
        version='1')
    invoicing_rule_1.setTestMethodId('invoice_rule_script')
    invoicing_rule_1.validate()

    invoicing_rule_2 = self.getRuleTool().newContent(
        portal_type="Invoicing Rule", reference='default_invoicing_rule',
        version='2')
    invoicing_rule_2.setTestMethodId('invoice_rule_script')
    invoicing_rule_2.validate()

    # clear simulation
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))

    get_transaction().commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    get_transaction().commit()
    self.tic()
    root_applied_rule = self.pl.getCausalityRelatedValue()

    # check that the invoicing rule 2 was applied
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_2.getRelativeUrl())

    # change the test method to one that fails, and test that the rule is
    # replaced by invoicing rule 1
    invoicing_rule_2.setTestMethodId('delivery_rule_script')
    root_applied_rule.expand()
    get_transaction().commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())

    # change the test of invoicing rule 2 to one that succeeds, add a delivery
    # relation, expand, and test that the invoicing rule 1 is still there
    invoicing_rule_2.setTestMethodId('invoice_rule_script')
    sub_movement = applied_rule.objectValues()[0]
    sub_movement.setDeliveryValue(self.pl.line)
    root_applied_rule.expand()
    get_transaction().commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 1)
    applied_rule = movement.objectValues()[0]
    self.assertEquals(applied_rule.getSpecialise(),
        invoicing_rule_1.getRelativeUrl())
    self.assertEquals(applied_rule.objectCount(), 1)
    sub_movement = applied_rule.objectValues()[0]
    self.assertEquals(sub_movement.getDelivery(), self.pl.line.getRelativeUrl())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRule))
  return suite

