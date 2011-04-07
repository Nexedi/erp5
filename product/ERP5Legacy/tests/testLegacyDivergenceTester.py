# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest
import transaction

from Products.ERP5Legacy.tests import testLegacySimulationPackingList
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import Sequence

class TestDivergenceTester(testLegacySimulationPackingList.TestPackingListMixin,
                           ERP5TypeTestCase):
  """
  Check isDivergent method on movement, delivery
  """
  run_all_test = 1
  quiet = 0

  def getTitle(self):
    return "Divergence Tester"

  def getDeliveringRule(self):
    return self.getRule(reference='default_delivering_rule',
                        validation_state="validated")

  def afterSetUp(self):
    """
    Remove all divergence testers from order_rule.
    """
    rule = self.getDeliveringRule()
    tester_list = rule.contentValues(
             portal_type=rule.getPortalDivergenceTesterTypeList())
    rule.deleteContent([x.getId() for x in tester_list])
    transaction.commit()
    self.tic()

  def bootstrapSite(self):
    """
    Manager has to create an administrator user first.
    """
    self.logMessage("Bootstrap the site by creating required " \
                    "order, simulation, ...")
    # These next calls were originally in TestOrderMixin.afterSetUp(), but we need
    # them here for the bootstrap Sequence to work correctly
    self.createCategories()
    self.validateRules()
    self.setUpPreferences()
    # Create a clean packing list
    sequence_string = ' \
          stepCreateOrganisation1 \
          stepCreateOrganisation2 \
          stepCreateOrganisation3 \
          stepCreateOrder \
          stepSetOrderProfile \
          stepCreateNotVariatedResource \
          stepTic \
          stepCreateOrderLine \
          stepSetOrderLineResource \
          stepSetOrderLineDefaultValues \
          stepOrderOrder \
          stepTic \
          stepConfirmOrder \
          stepTic \
    '
    sequence = Sequence(self)
    sequence(sequence_string, quiet=self.quiet)
    self.logMessage("Bootstrap finished")

  def setUpOnce(self, quiet=1, run=run_all_test):
    """
    Create an order and generate a packing list from it.
    This has to be called only once.
    """
    self.validateRules()
    transaction.commit()
    self.tic(verbose=1)
    self.bootstrapSite()

  def stepGetPackingList(self, sequence=None, sequence_list=None, **kw):
    """
    Set the packing list in the sequence
    """
    sql_result = self.getPortal().portal_catalog(
                         portal_type=self.packing_list_portal_type)
    self.assertEquals(1, len(sql_result))
    packing_list = sql_result[0].getObject()
    # XXX Hardcoded id
    movement=packing_list['1']
    rule = self.getDeliveringRule()
    sequence.edit(
        packing_list=packing_list,
        movement=movement,
        rule=rule,
        sim_mvt=movement.getDeliveryRelatedValueList()[0])

  def stepCheckPackingListIsDivergent(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertTrue(packing_list.isDivergent())

  def stepSetNewQuantity(self, sequence=None, 
                         sequence_list=None, **kw):
    """
    Modify the quantity of the delivery movement
    """
    packing_list = sequence.get('packing_list')
    movement = sequence.get('movement')
    movement.setQuantity(movement.getQuantity()+1234)

  def stepSetPreviousQuantity(self, sequence=None, 
                              sequence_list=None, **kw):
    """
    Reset the quantity of the delivery movement
    """
    sim_mvt = sequence.get('sim_mvt')
    movement = sequence.get('movement')
    movement.setQuantity(sim_mvt.getQuantity())

  def stepSetPreviousQuantityWithEpsilon(self, sequence=None, 
                                         sequence_list=None, **kw):
    sim_mvt = sequence.get('sim_mvt')
    movement = sequence.get('movement')
    prevision = sim_mvt.getQuantity()
    decision = prevision * (1 + 1e-15)
    self.assertNotEqual(prevision, decision)
    movement.setQuantity(decision)

  def stepAddQuantityDivergenceTester(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Add a quantity divergence tester in the rule
    """
    rule = sequence.get('rule')
    rule.newContent(portal_type='Quantity Divergence Tester')

  def test_01_QuantityDivergenceTester(self, quiet=quiet, run=run_all_test):
    """
    Test the quantity divergence tester
    """
    if not run: return
    sequence_string = """
          GetPackingList
          CheckPackingListIsNotDivergent
          SetNewQuantity
          CheckPackingListIsNotDivergent
          AddQuantityDivergenceTester
          CheckPackingListIsDivergent
          SetPreviousQuantity
          CheckPackingListIsNotDivergent
          SetPreviousQuantityWithEpsilon
          CheckPackingListIsNotDivergent
          Tic
    """
    sequence = Sequence(self)
    sequence(sequence_string, quiet=self.quiet)

  def stepSetNewSource(self, sequence=None, 
                       sequence_list=None, **kw):
    """
    Modify the source of the delivery
    """
    packing_list = sequence.get('packing_list')
    packing_list.setSource(None)

  def stepAddCategoryDivergenceTester(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Add a category divergence tester in the rule
    """
    rule = sequence.get('rule')
    tester = rule.newContent(portal_type='Category Divergence Tester')
    sequence.edit(tester=tester)

  def stepConfigureCategoryDivergenceTesterForSource(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Add a category divergence tester in the rule
    """
    tester = sequence.get('tester')
    tester.setTestedPropertyList(['source | Source'])

  def stepSetPreviousSource(self, sequence=None, 
                            sequence_list=None, **kw):
    """
    Reset the quantity of the delivery
    """
    sim_mvt = sequence.get('sim_mvt')
    packing_list = sequence.get('packing_list')
    packing_list.setSource(sim_mvt.getSource())

  def test_02_CategoryDivergenceTester(self, quiet=quiet, run=run_all_test):
    """
    Test the category divergence tester
    """
    if not run: return
    sequence_string = """
          GetPackingList
          CheckPackingListIsNotDivergent
          SetNewSource
          CheckPackingListIsNotDivergent
          AddCategoryDivergenceTester
          CheckPackingListIsNotDivergent
          ConfigureCategoryDivergenceTesterForSource
          CheckPackingListIsDivergent
          SetPreviousSource
          CheckPackingListIsNotDivergent
          Tic
    """
    sequence = Sequence(self)
    sequence(sequence_string, quiet=self.quiet)

  def stepSetNewStartDate(self, sequence=None, 
                       sequence_list=None, **kw):
    """
    Modify the source of the delivery
    """
    packing_list = sequence.get('packing_list')
    packing_list.setStartDate(packing_list.getStartDate()+10)

  def stepAddPropertyDivergenceTester(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Add a property divergence tester in the rule
    """
    rule = sequence.get('rule')
    tester = rule.newContent(portal_type='Property Divergence Tester')
    sequence.edit(tester=tester)

  def stepConfigurePropertyDivergenceTesterForStartDate(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Add a property divergence tester in the rule
    """
    tester = sequence.get('tester')
    tester.setTestedPropertyList(['start_date | Start Date'])

  def stepSetPreviousStartDate(self, sequence=None, 
                               sequence_list=None, **kw):
    """
    Reset the quantity of the delivery
    """
    sim_mvt = sequence.get('sim_mvt')
    packing_list = sequence.get('packing_list')
    packing_list.setStartDate(sim_mvt.getStartDate())

  def test_03_PropertyDivergenceTester(self, quiet=quiet, run=run_all_test):
    """
    Test the property divergence tester
    """
    if not run: return
    sequence_string = """
          GetPackingList
          CheckPackingListIsNotDivergent
          SetNewStartDate
          CheckPackingListIsNotDivergent
          AddPropertyDivergenceTester
          CheckPackingListIsNotDivergent
          ConfigurePropertyDivergenceTesterForStartDate
          CheckPackingListIsDivergent
          SetPreviousStartDate
          CheckPackingListIsNotDivergent
          Tic
    """
    sequence = Sequence(self)
    sequence(sequence_string, quiet=self.quiet)

  def stepSetNewAggregate(self, sequence=None, 
                          sequence_list=None, **kw):
    """
    Modify the aggregate of the delivery movement
    """
    movement = sequence.get('movement')
    # Set an aggregate value which does not exist
    # but it should not be a problem for testing the divergence
    movement.setAggregate('a_great_module/a_random_id')

  def stepConfigureCategoryDivergenceTesterForAggregate(self, sequence=None, 
                                                        sequence_list=None, **kw):
    """
    Add a category divergence tester in the rule
    """
    tester = sequence.get('tester')
    tester.setTestedPropertyList(['aggregate | Aggregate'])

  def stepSetPreviousAggregate(self, sequence=None, 
                            sequence_list=None, **kw):
    """
    Reset the quantity of the delivery
    """
    movement = sequence.get('movement')
    movement.setAggregate(None)

  def test_04_CategoryDivergenceTester(self, quiet=quiet, run=run_all_test):
    """
    Test the category divergence tester
    """
    if not run: return
    sequence_string = """
          GetPackingList
          CheckPackingListIsNotDivergent
          SetNewAggregate
          CheckPackingListIsNotDivergent
          AddCategoryDivergenceTester
          CheckPackingListIsNotDivergent
          ConfigureCategoryDivergenceTesterForAggregate
          CheckPackingListIsDivergent
          SetPreviousAggregate
          CheckPackingListIsNotDivergent
          Tic
    """
    sequence = Sequence(self)
    sequence(sequence_string, quiet=self.quiet)

  def test_QuantityDivergenceTesterCompareMethod(self):
    rule = self.portal.portal_rules.newContent(portal_type='Delivery Rule')
    divergence_tester = rule.newContent(portal_type='Quantity Divergence Tester')

    self.assertFalse(divergence_tester.isDecimalAlignmentEnabled())
    self.assertFalse(divergence_tester.compare(3.0, 3.001))
    self.assertTrue(divergence_tester.compare(3.0, 3.0))

    divergence_tester.setDecimalAlignmentEnabled(True)
    divergence_tester.setDecimalRoundingOption('ROUND_DOWN')
    divergence_tester.setDecimalExponent('0.01')

    self.assertTrue(divergence_tester.compare(3.0, 3.001))
    self.assertTrue(divergence_tester.compare(3.0, 3.0))

    divergence_tester.setDecimalExponent('0.001')
    self.assertFalse(divergence_tester.compare(3.0, 3.001))

    divergence_tester.setDecimalRoundingOption('ROUND_UP')
    divergence_tester.setDecimalExponent('0.01')
    self.assertFalse(divergence_tester.compare(3.0, 3.001))

    divergence_tester.setDecimalRoundingOption('ROUND_HALF_UP')
    divergence_tester.setDecimalExponent('0.01')
    self.assertTrue(divergence_tester.compare(3.0, 3.001))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDivergenceTester))
  return suite
