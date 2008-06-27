# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#          Łukasz Nowak <lukasz.nowak@ventis.com.pl>
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
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.CMFCore.utils import getToolByName
from testProductionOrder import TestProductionOrderMixin
from testPackingList import TestPackingListMixin

class TestProductionPackingReportListMixin(TestProductionOrderMixin, TestPackingListMixin, \
                          ERP5TypeTestCase):
  """Mixin for testing Production Packing Lists and Production Reports"""

  def stepCreatePackingList(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty packing_list
    """
    organisation = sequence.get('organisation')
#     person = sequence.get('person')
    portal = self.getPortal()
    packing_list_module = portal.getDefaultModule(portal_type=self.packing_list_portal_type)
    packing_list = packing_list_module.newContent(portal_type=self.packing_list_portal_type)
    packing_list.edit(
      title = "PackingList",
      start_date = self.datetime + 10,
      stop_date = self.datetime + 20,
    )
    if organisation is not None:
      packing_list.edit(source_value=organisation,
                 source_section_value=organisation,
                 destination_value=organisation,
                 destination_section_value=organisation,
                 source_decision_value=organisation,
                 destination_decision_value=organisation,
                 source_administration_value=organisation,
                 destination_administration_value=organisation,
                 )
    sequence.edit( packing_list = packing_list )

  def stepSetPackingListProfile(self,sequence=None, sequence_list=None, **kw):
    """
      Set different source and destination on the packing_list
    """
    organisation1 = sequence.get('organisation1')
    organisation2 = sequence.get('organisation2')
    packing_list = sequence.get('packing_list')
    packing_list.edit( source_value = organisation1,
                source_section_value = organisation1,
                destination_value = organisation2,
                destination_section_value = organisation2 )
    self.failUnless('Site Error' not in packing_list.view())

  def modifyPackingListState(self, transition_name,
                             sequence,packing_list=None):
    """ calls the workflow for the packing list """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list, transition_name)

  def stepConfirmPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('confirm_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'confirmed')

  def stepSetReadyPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('set_ready_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'ready')

  def stepStartPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('start_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'started')

  def stepStopPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('stop_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'stopped')

  def stepDeliverPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('deliver_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'delivered')

  def stepCreatePackingListLine(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty packing_list line
    """
    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.newContent(portal_type=self.packing_list_line_portal_type)
    packing_list_line.edit(
      title = "PackingList Line"
    )
    sequence.edit(packing_list_line=packing_list_line)

  def stepSetPackingListLineResource(self, sequence=None, sequence_list=None, **kw):
    """
      Set packing_list line resource with the current resource
    """
    packing_list_line = sequence.get('packing_list_line')
    resource = sequence.get('resource')
    packing_list_line.setResourceValue(resource)

  def stepSetPackingListLineDefaultValues(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Set the default price and quantity on the packing_list line.
    """
    packing_list_line = sequence.get('packing_list_line')
    packing_list_line.edit(quantity=self.default_quantity,
                    price=self.default_price)

  def stepCheckPackingListSimulation(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    
    applied_rule = packing_list.getCausalityRelatedValueList(portal_type=\
        self.applied_rule_portal_type)
    self.logMessage("TODO")

class TestProductionPackingListReport(TestProductionPackingReportListMixin):
  pass

class TestProductionPackingList(TestProductionPackingReportListMixin):
  """Test Production Packing Lists"""
  run_all_test = 1

  packing_list_portal_type = 'Production Packing List'
  packing_list_line_portal_type = 'Production Packing List Line'
  packing_list_cell_portal_type = 'Production Packing List Cell'

  def getTitle(self):
    return "Production Packing List"

  def test_01_checkForProductionPackingListWorkflow(self, quiet=0, run=run_all_test):
    """
      Test that production packing list workflow works, and updates simulations
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepClearActivities \
                      stepCreatePackingList \
                      stepSetPackingListProfile \
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreatePackingListLine \
                      stepSetPackingListLineResource \
                      stepSetPackingListLineDefaultValues \
                      stepTic \
                      \
                      stepConfirmPackingList \
                      stepTic \
                      \
                      stepSetReadyPackingList \
                      stepTic \
                      \
                      stepStartPackingList \
                      stepTic \
                      \
                      stepStopPackingList \
                      stepTic \
                      \
                      stepDeliverPackingList \
                      stepTic \
'

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

class TestProductionReport(TestProductionPackingList):
  """Test Production Reports"""
  run_all_test = 1

  def getTitle(self):
    return "Production Report"

  packing_list_portal_type = 'Production Report'
  packing_list_line_portal_type = 'Production Report Line'
  packing_list_cell_portal_type = 'Production Report Cell'

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestProductionPackingListReport))
  #suite.addTest(unittest.makeSuite(TestProductionPackingList))
  #suite.addTest(unittest.makeSuite(TestProductionReport))
  return suite
