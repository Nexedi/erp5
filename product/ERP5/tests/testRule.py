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

import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5.tests.testOrder import TestOrderMixin

class TestRuleMixin(TestOrderMixin):
  """
  Test basic rule behaviours
  """

  def createRule(self, base_reference, version, **kw):
    rule = super(TestRuleMixin, self).getRule(reference=base_reference,
                                              version='<testRule.')
    assert rule.getValidationState() == 'draft'
    parent = rule.getParentValue()
    rule, = parent.manage_pasteObjects(
      parent.manage_copyObjects(ids=rule.getId()))
    rule = parent[rule['new_id']]
    rule._edit(version='testRule.' + version, **kw)
    return rule

  def getRule(self, reference):
    rule = super(TestRuleMixin, self).getRule(reference=reference)
    assert rule.getVersion().startswith('testRule.')
    return rule

  def _wipe(self, folder):
    folder.manage_delObjects(list(folder.objectIds()))

  def afterSetUp(self):
    # delete rules
    rule_tool = self.portal.portal_rules
    rule_tool.manage_delObjects(ids=[x.getId() for x in rule_tool.objectValues()
                                     if x.getVersion().startswith('testRule.')])
    # recreate rules
    self.createRule('default_order_rule', '1')
    self.createRule('default_delivery_rule', '1')
    transaction.commit()
    self.tic()
    # create packing list if necessary
    pl_module = self.portal.getDefaultModule(self.packing_list_portal_type)
    if pl_module.objectCount() == 0:
      # at least one default_delivery_rule should be validated here to
      # confirm Sale Packing List
      delivery_rule = self.getRule('default_delivery_rule')
      delivery_rule.validate()
      self.pl = self.createPackingList()
      delivery_rule.invalidate()
    else:
      self.pl = pl_module.objectValues()[0]
    #delete applied_rule
    simulation_tool = self.getSimulationTool()
    self._wipe(simulation_tool)
    # create one manual simulation movement for rule testing
    self.ar = simulation_tool.newContent(portal_type='Applied Rule')
    self.sm = self.ar.newContent(portal_type='Simulation Movement')
    self.sm.setStartDate("2007-07-01") # for the date based rule tests
    # commit
    transaction.commit()
    self.tic()


  def beforeTearDown(self):
    self._wipe(self.getSimulationTool())
    self._wipe(self.portal.portal_skins.custom)
    transaction.commit()
    self.tic()

  def getTitle(self):
    return "Rule"

  def getBusinessTemplateList(self):
    return TestOrderMixin.getBusinessTemplateList(self) + ('erp5_accounting',
                'erp5_invoicing',)

  def createPackingList(self):
    """
    create a packing list, to allow testing
    """
    self.getCategoryTool()['group'].newContent(portal_type='Category', id='a')
    self.getCategoryTool()['group'].newContent(portal_type='Category', id='b')
    pl_module = self.getPortal().getDefaultModule(
        self.packing_list_portal_type)
    pl = pl_module.newContent(portal_type=self.packing_list_portal_type,
        specialise=self.business_process,
        source_section='group/a', destination_section='group/b')
    pl.newContent(portal_type=self.packing_list_line_portal_type, id='line',
                  quantity=1)
    pl.setStartDate("2007-07-01")
    transaction.commit()
    self.tic()
    pl.confirm()
    transaction.commit()
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

    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.validate()
    transaction.commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.sm)), 0)

  def test_02_WrongTestMethod(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule's test method returns False, it will not apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'wrong_script', 'rule',
        'return False')
    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.setTestMethodId('wrong_script')
    delivery_rule.validate()
    transaction.commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.sm)), 0)

  def test_03_GoodTestMethod(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule's test method returns True, it will apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.validate()
    transaction.commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.sm)), 1)

  def test_04_NotValidatedRule(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule is not validated, it will not apply, even if it has
    a good script
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.validate()
    delivery_rule.invalidate()
    transaction.commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 0)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.sm)), 0)

  def test_06_WrongDateRange(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule is validated but does not have correct date range,
    it will not apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.setStartDateRangeMin('2007-06-01')
    delivery_rule.setStartDateRangeMax('2007-06-04')
    delivery_rule.validate()
    transaction.commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.sm)), 0)

  def test_07_GoodDateRange(self, quiet=quiet, run=run_all_test):
    """
    test that when a rule is validated and has a correct date range, it will
    apply
    """
    if not run: return

    skin_folder = self.getPortal().portal_skins.custom
    skin = createZODBPythonScript(skin_folder, 'good_script', 'rule',
        'return True')
    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.setStartDateRangeMin('2007-06-01')
    delivery_rule.setStartDateRangeMax('2007-08-01')
    delivery_rule.validate()
    transaction.commit()
    self.tic()

    self.assertEquals(self.getRuleTool().countFolder(
      validation_state="validated")[0][0], 1)
    self.assertEquals(len(self.getRuleTool().searchRuleList(self.sm)), 1)

  def test_070_direct_criteria_specification(self):
    """
    test that rule-specific scripts can specify identity and range criteria
    """
    skin_folder = self.getPortal().portal_skins.custom
    # add an always-matching predicate test script to the rule
    createZODBPythonScript(skin_folder, 'good_script', 'rule',
                           'return True')
    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.setTestMethodId('good_script')
    # but add a predicate building script that only matches on
    # Simulation Movements, to affect all rules
    createZODBPythonScript(skin_folder, 'RuleMixin_asPredicate', '',
        """
return context.generatePredicate(
  identity_criterion=dict(portal_type=(context.movement_type,)),
)
        """)
    # and validate it, which will indirectly reindex the predicate.
    delivery_rule.validate()
    transaction.commit()
    self.tic()
    # now rules don't match packing lists by default
    self.assertEqual(len(self.getRuleTool().searchRuleList(self.pl)), 0)
    # only simulation movements
    self.assertEqual(len(self.getRuleTool().searchRuleList(self.sm)), 1)
    # unless they have more specific predicate script telling them otherwise:
    predicate_script = createZODBPythonScript(
      skin_folder, 'DeliveryRootSimulationRule_asPredicate', '',
      """
return context.generatePredicate(
  identity_criterion=dict(portal_type=('Sale Packing List',)),
  range_criterion=dict(start_date=(%r, None)),
)
      """ % self.pl.getStartDate())
    delivery_rule.reindexObject()
    transaction.commit()
    self.tic()
    # now they match the packing list, but not the simulation movement
    self.assertEqual(len(self.getRuleTool().searchRuleList(self.pl)), 1)
    self.assertEqual(len(self.getRuleTool().searchRuleList(self.sm)), 0)
    # Note that we added a range criterion above, which means that if
    # the packing list no longer falls within the range...
    self.pl.setStartDate(self.pl.getStartDate() - 1)
    transaction.commit()
    self.tic()
    # ... then the rule no longer matches the packing list:
    self.assertEqual(len(self.getRuleTool().searchRuleList(self.pl)), 0)
    # But if we push back the date on the criterion...
    predicate_script.write("""
return context.generatePredicate(
  identity_criterion=dict(portal_type=('Sale Packing List',)),
  range_criterion=dict(start_date=(%r, None)),
)
      """ % self.pl.getStartDate())
    delivery_rule.reindexObject()
    transaction.commit()
    self.tic()
    # ... it will match again
    self.assertEqual(len(self.getRuleTool().searchRuleList(self.pl)), 1)

  def test_071_empty_rule_category_matching(self):
    """
    test that a category criteria on a rule that doesn't have that category
    allows the rule to match contexts with and without that category
    """
    skin_folder = self.getPortal().portal_skins.custom
    rule_tool = self.getRuleTool()
    # add an always-matching predicate test script to the rule
    createZODBPythonScript(skin_folder, 'good_script', 'rule',
                           'return True')
    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.setTestMethodId('good_script')
    # and  add  a  predicate  building  script that  only  matches  on
    # Simulation Movements, to affect all rules
    createZODBPythonScript(skin_folder, 'RuleMixin_asPredicate', '',
        """
return context.generatePredicate(
  identity_criterion=dict(portal_type=(context.movement_type,)),
  membership_criterion_base_category_list=('trade_phase',),
)
        """)
    # and validate it, which will indirectly reindex the predicate.
    delivery_rule.validate()
    transaction.commit()
    self.tic()
    # Now since the rule has a trade_phase
    self.assertEqual(delivery_rule.getTradePhase(), 'default/delivery')
    # ...then it won't match the Simulation Movement
    self.assertEqual(len(rule_tool.searchRuleList(self.sm)), 0)
    # unless it gets a trade_phase itself
    self.sm.setTradePhase('default/delivery')
    self.stepTic()
    self.assertEqual(len(rule_tool.searchRuleList(self.sm)), 1)
    # But if the rule itself has no trade_phase...
    delivery_rule.setTradePhase(None)
    self.stepTic()
    # then it should match the simulation movement with or without
    # trade_phase
    self.assertEqual(len(rule_tool.searchRuleList(self.sm)), 1)
    self.sm.setTradePhase(None)
    self.stepTic()
    self.assertEqual(len(rule_tool.searchRuleList(self.sm)), 1)

  def test_072_search_with_extra_catalog_keywords(self):
    """
    test that a category criteria on a rule that doesn't have that category
    allows the rule to match contexts with and without that category
    """
    skin_folder = self.getPortal().portal_skins.custom
    rule_tool = self.getRuleTool()
    # add an always-matching predicate test script to the rule
    createZODBPythonScript(skin_folder, 'good_script', 'rule',
                           'return True')
    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.setTestMethodId('good_script')
    delivery_rule.validate()
    transaction.commit()
    self.tic()
    # Now since the rule has a trade_phase
    self.assertEqual(delivery_rule.getTradePhaseList(), ['default/delivery'])
    # then it should be possible to find it by passing this trade_phase
    # as an additional catalog keyword
    kw = {'trade_phase_relative_url':
            ['trade_phase/' + path for path in delivery.getTradePhaseList()]}
    # XXX-Leo: Fugly catalog syntax for category search above.
    self.assertEqual(len(rule_tool.searchRuleList(self.sm, **kw)), 1)
    # and also not to match it if we pass a different trade_phase
    kw['trade_phase_relative_url'] = ['trade_phase/' + 'default/order']
    self.assertEqual(len(rule_tool.searchRuleList(self.sm, **kw)), 0)
    # but match it again if we pass an empty list for trade_phase
    # (with a warning in the log about discarding empty values)
    kw['trade_phase_relative_url'] = []
    self.assertEqual(len(rule_tool.searchRuleList(self.sm, **kw)), 1)

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
    order_rule = self.getRule('default_order_rule')
    order_rule.setTestMethodId('rule_script')
    order_rule.validate()

    delivery_rule_1 = self.getRule('default_delivery_rule')
    delivery_rule_1.setTestMethodId('rule_script')
    delivery_rule_1.validate()

    delivery_rule_2 = self.createRule('default_delivery_rule', '2',
                                      test_method_id='rule_script')
    delivery_rule_2.validate()
    transaction.commit()
    self.tic()

    # delivery_rule_2 should be applied
    self.pl.updateAppliedRule('default_delivery_rule')
    transaction.commit()
    self.tic()
    self.assertEquals(self.pl.getCausalityRelatedValue().getSpecialise(),
        delivery_rule_2.getRelativeUrl())

    self.getSimulationTool().manage_delObjects(
        ids=[self.pl.getCausalityRelatedId()])

    # increase version of delivery_rule_1
    delivery_rule_1.setVersion("testRule.3")
    transaction.commit()
    self.tic()

    # delivery_rule_1 should be applied
    self.pl.updateAppliedRule('default_delivery_rule')
    transaction.commit()
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

    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.validate()

    invoicing_rule_1 = self.createRule('default_invoicing_rule', '1',
                                       test_method_id='invoice_rule_script')
    invoicing_rule_1.validate()

    invoicing_rule_2 = self.createRule('default_invoicing_rule', '2',
                                       test_method_id='invoice_rule_script')
    invoicing_rule_2.validate()

    # clear simulation
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))
    transaction.commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    transaction.commit()
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
    invoicing_rule_1.setVersion('testRule.3')
    transaction.commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    transaction.commit()
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
    if no rule with the same reference is already applied.
    - test that it happens if no rule is already applied
    - test that nothing changes if a rule of same reference is already
      applied (no matter what the version is)
    """
    if not run: return

    skin_folder = self.portal.portal_skins.custom
    createZODBPythonScript(skin_folder, 'delivery_rule_script', 'rule',
        "return False")
    createZODBPythonScript(skin_folder, 'invoice_rule_script', 'rule',
        "return context.getParentValue().getSpecialiseReference() == 'default_delivery_rule'")

    # XXX-Leo: This script should become the default in erp5_simulation. Remove
    # it from here when no longer needed:
    createZODBPythonScript(skin_folder, 'RuleMixin_asPredicate', '',
        """
kw = dict(criterion_property_list=("start_date",),
          membership_criterion_base_category_list=('trade_phase',),)
return context.generatePredicate(**kw)
        """.strip())

    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.validate()

    # create rule with a wrong script
    invoicing_rule_1 = self.createRule('default_invoicing_rule', '1',
                                       test_method_id='delivery_rule_script')
    invoicing_rule_1.validate()

    # clear simulation
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))
    transaction.commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    transaction.commit()
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
    transaction.commit()
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
    invoicing_rule_1_applied_rule = movement.objectValues()[0]
    self.assertEquals(invoicing_rule_1_applied_rule.getSpecialise(),
                      invoicing_rule_1.getRelativeUrl())

    # add more invoicing_rule and test that nothing is changed
    ## same reference, higher version
    invoicing_rule_n = self.createRule('default_invoicing_rule', '2',
                                       test_method_id='invoice_rule_script')
    invoicing_rule_n.validate()
    ## different reference, higher version (but version shouldn't matter here)
    invoicing_rule_2 = self.createRule('default_invoicing_rule', '2',
                                       reference='default_invoicing_rule_2',
                                       test_method_id='invoice_rule_script')
    invoicing_rule_2.validate()
    transaction.commit()
    self.tic()
    root_applied_rule.expand()
    transaction.commit()
    self.tic()

    self.assertEquals(root_applied_rule.getRelativeUrl(),
        self.pl.getCausalityRelated())
    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())

    self.assertEquals(root_applied_rule.getSpecialise(),
        delivery_rule.getRelativeUrl())
    self.assertEquals(root_applied_rule.objectCount(), 1)
    movement = root_applied_rule.objectValues()[0]
    self.assertEquals(movement.objectCount(), 2)
    applied_rule_list = sorted(movement.objectValues(),
                          key=lambda x: x.getSpecialiseValue().getReference())
    # check the 1st applied rule is an application of invoicing_rule_1
    self.assertEquals(applied_rule_list[0].getSpecialise(),
                      invoicing_rule_1.getRelativeUrl())
    # but also check it's the same applied rule as before instead of a new
    # one with the same specialization
    self.assertEqual(applied_rule_list[0],
                      invoicing_rule_1_applied_rule)
    self.assertEquals(applied_rule_list[1].getSpecialise(),
        invoicing_rule_2.getRelativeUrl())


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

    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.validate()

    invoicing_rule_1 = self.createRule('default_invoicing_rule', '1',
                                       test_method_id='invoice_rule_script')
    invoicing_rule_1.validate()

    # clear simulation
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))

    transaction.commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    transaction.commit()
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
    transaction.commit()
    self.tic()
    self.assertEquals(invoicing_rule_1.getValidationState(), 'invalidated')
    root_applied_rule.expand()
    transaction.commit()
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
    transaction.commit()
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
    transaction.commit()
    self.tic()
    self.assertEquals(invoicing_rule_1.getValidationState(), 'validated')
    root_applied_rule.expand()
    transaction.commit()
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
    transaction.commit()
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

    delivery_rule = self.getRule('default_delivery_rule')
    delivery_rule.validate()

    invoicing_rule_1 = self.createRule('default_invoicing_rule', '1',
                                       test_method_id='invoice_rule_script')
    invoicing_rule_1.validate()

    invoicing_rule_2 = self.createRule('default_invoicing_rule', '2',
                                       test_method_id='invoice_rule_script')
    invoicing_rule_2.validate()

    # clear simulation
    self.getSimulationTool().manage_delObjects(
        ids=list(self.getSimulationTool().objectIds()))

    transaction.commit()
    self.tic()

    self.pl.updateAppliedRule('default_delivery_rule')
    transaction.commit()
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
    transaction.commit()
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
    transaction.commit()
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
