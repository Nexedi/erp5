##############################################################################
#
# Copyright (c) 2009 Nexedi KK and Contributors. All Rights Reserved.
#          Tatuya Kamada <tatuya@nexedi.com>
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

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5.tests.testPackingList import TestPackingListMixin
from DateTime import DateTime
from Products.ERP5Type.Errors import UnsupportedWorkflowMethod
from Products.ERP5.tests.utils import newSimulationExpectedFailure

class ReturnedSalePackingListMixin(TestPackingListMixin):
  """Mixing class with steps to test returned sale packing lists.
  """

  returned_packing_list_portal_type = 'Returned Sale Packing List'
  returned_packing_list_line_portal_type = 'Returned Sale Packing List Line'
  returned_packing_list_cell_portal_type = 'Returned Sale Packing List Cell'
  inventory_line_portal_type = 'Inventory Line'
  view_stock_date = '2009/12/01'
  first_date_string = '2009/01/01'
  shipping_date_string = '2009/10/03'
  inventory_quantity = 2000.

  default_sequence = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateOrganisation3 \
                      stepCreateCurrency \
                      stepCreateNotVariatedResource \
                      stepTic '


  def beforeTearDown(self):
    self.abort()
    self.tic()
    for folder in (self.portal.organisation_module,
                   self.portal.sale_order_module,
                   self.portal.inventory_module,
                   self.portal.apparel_model_module,
                   self.portal.product_module,
                   self.portal.returned_sale_packing_list_module,
                   self.portal.portal_simulation,):
      folder.manage_delObjects([x for x in folder.objectIds()])
    self.tic()


  def loginAsManager(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', '', ['Manager', 'Member', 'Assignee'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)

  def loginAsMember(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('member', '', ['Member', 'Assignor'], [])
    user = uf.getUserById('member').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self, quiet=1, run=1):
    self.loginAsManager()
    portal = self.getPortal()
    self.createCategories()
    self.validateRules()
    self.setUpPreferences()
    # test with not a manager
    self.loginAsMember()

  def stepCreateReturnedPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Adds a Returned Packing List
    """
    returned_packing_list = self.getPortal().getDefaultModule(
        self.returned_packing_list_portal_type).newContent(
            portal_type=self.returned_packing_list_portal_type)


    organisation = sequence.get('organisation1')
    organisation3 = sequence.get('organisation3')

    start_date = DateTime(self.shipping_date_string)
    returned_packing_list.edit(
      title = "RPL%s" % returned_packing_list.getId(),
      start_date = start_date,
      stop_date = start_date + 20,
    )
    if organisation is not None:
      returned_packing_list.edit(source_value=organisation3,
                 source_section_value=organisation3,
                 destination_value=organisation,
                 destination_section_value=organisation,
                 source_decision_value=organisation3,
                 destination_decision_value=organisation,
                 source_administration_value=organisation3,
                 destination_administration_value=organisation,
                 )

    returned_packing_list_line = returned_packing_list.newContent(
        portal_type=self.returned_packing_list_line_portal_type)
    resource = sequence.get('resource')
    returned_packing_list_line.setResourceValue(resource)
    returned_packing_list_line.edit(quantity=200)
    sequence.edit(returned_packing_list=returned_packing_list)

  def stepCheckReturnedPackingListCreating(self, sequence=None, sequence_list=None, **kw):
    """
      Check that returned packing list creating
    """
    returned_packing_list = sequence.get('returned_packing_list')
    organisation = sequence.get('organisation1')
    organisation3 = sequence.get('organisation3')

    self.assertEqual(organisation3, returned_packing_list.getSourceValue())
    self.assertEqual(organisation3, returned_packing_list.getSourceSectionValue())
    self.assertEqual(organisation, returned_packing_list.getDestinationValue())
    self.assertEqual(organisation, returned_packing_list.getDestinationSectionValue())
    self.assertEqual(organisation3, returned_packing_list.getSourceDecisionValue())
    self.assertEqual(organisation, returned_packing_list.getDestinationDecisionValue())
    self.assertEqual(organisation3, returned_packing_list.getSourceAdministrationValue())
    self.assertEqual(organisation, returned_packing_list.getDestinationAdministrationValue())

    returned_packing_list_line_list = returned_packing_list.objectValues(
                        portal_type=self.returned_packing_list_line_portal_type)

    self.assertEqual(1, len(returned_packing_list_line_list))
    returned_packing_list_line = returned_packing_list_line_list[0]
    self.assertEqual(self.returned_packing_list_line_portal_type,
                      returned_packing_list_line.getPortalType())
    resource = sequence.get('resource')
    created_resource = returned_packing_list_line.getResourceValue()
    self.assertEqual(resource, created_resource)
    self.assertEqual(200, returned_packing_list_line.getQuantity())

  def stepCheckReturnedPackingListDeleting(self, sequence=None,
                                           sequence_list=None, **kw):
    """
     Check that returned packing list deleting
    """
    returned_packing_list = sequence.get('returned_packing_list')
    returned_packing_list_line_list = returned_packing_list.objectValues(
                        portal_type=self.returned_packing_list_line_portal_type)
    self.assertEqual(1, len(returned_packing_list_line_list))
    returned_packing_list_line = returned_packing_list_line_list[0]
    # delete a line
    returned_packing_list.manage_delObjects([returned_packing_list_line.getId()])

    portal_catalog = self.getCatalogTool()
    returned_packing_list_uid = returned_packing_list.getUid()
    found_rpl = portal_catalog(uid=returned_packing_list_uid)
    self.assertEqual(1, len(found_rpl))
    rpl = found_rpl[0].getObject()
    self.assertEqual(0, len(rpl.objectValues(
        portal_type=self.returned_packing_list_line_portal_type)))

    # delete a delivery
    self.portal.returned_sale_packing_list_module.manage_delObjects(
        [returned_packing_list.getId(),])

    found_rpl =  portal_catalog(uid=returned_packing_list_uid)
    self.assertEqual(0, len(found_rpl))

  def stepConfirmReturnedPackingList(self, sequence=None, sequence_list=None, **kw):
    returned_packing_list = sequence.get('returned_packing_list')
    returned_packing_list.confirm()

  def stepShipReturnedPackingList(self,sequence=None, sequence_list=None, **kw):
    returned_packing_list = sequence.get('returned_packing_list')
    returned_packing_list.start()

  def stepReceiveReturnedPackingList(self,sequence=None, sequence_list=None, **kw):
    returned_packing_list = sequence.get('returned_packing_list')
    returned_packing_list.stop()

  def stepDeliverReturnedPackingList(self,sequence=None, sequence_list=None, **kw):
    returned_packing_list = sequence.get('returned_packing_list')
    returned_packing_list.deliver()

  def stepCheckConfirmedReturnedPackingList(self, sequence=None,
                                            sequence_list=None, **kw):
    returned_packing_list = sequence.get('returned_packing_list')
    self.assertEqual('confirmed', returned_packing_list.getSimulationState())

  def stepCheckShippedReturnedPackingList(self, sequence=None,
                                          sequence_list=None, **kw):
    returned_packing_list = sequence.get('returned_packing_list')
    self.assertEqual('started', returned_packing_list.getSimulationState())

  def stepCheckReceivedReturnedPackingList(self, sequence=None,
                                           sequence_list=None, **kw):
    returned_packing_list = sequence.get('returned_packing_list')
    self.assertEqual('stopped', returned_packing_list.getSimulationState())


  def stepCheckDeliveredReturnedPackingList(self, sequence=None,
                                            sequence_list=None, **kw):
    returned_packing_list = sequence.get('returned_packing_list')
    self.assertEqual('delivered', returned_packing_list.getSimulationState())


  def _getInventoryModule(self):
    return getattr(self.getPortal(), 'inventory_module',None)

  def stepCreateInitialInventory(self, sequence=None, **kw):
    """
    create a inventory
    """
    portal = self.getPortal()
    organisation =  sequence.get('organisation1')
    inventory = self._getInventoryModule().newContent()
    inventory.edit(start_date=self.first_date_string,
                   destination_value=organisation,
                   destination_section_value=organisation)
    inventory_list = sequence.get('inventory_list', [])
    inventory_line = inventory.newContent(portal_type = self.inventory_line_portal_type)
    inventory_line.edit(resource_value = sequence.get('resource'),
                        quantity = self.inventory_quantity)
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)

  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kw):
    """
     Check that creating inventory and its resource
    """
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    # inventory quantity:2000 (2009/01/01)
    first_date = DateTime(self.first_date_string) + 1
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                                                     resource=resource_url,
                                                     to_date=first_date)
    self.assertEqual(2000, quantity)

    view_date = DateTime(self.view_stock_date)
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=view_date)
    self.assertEqual(2000, quantity)

  def stepCheckReturnedInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Check that returned sale packing list with inventory
    """
    # returned packing list returns
    # From: 'organisation3'
    # To:   'organisation1'
    # Quantity: 200
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date)
    self.assertEqual(2200, quantity)

    shipping_date = DateTime(self.shipping_date_string)
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                                                     resource=resource_url,
                                                     to_date=shipping_date)
    self.assertEqual(2000, quantity)


  def stepCheckReturnedPackingLineEmptyCell(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check if the matrix of the current returned packing list is empty.
    """
    order_line = sequence.get('returned_packing_list')
    cell_list = order_line.objectValues(portal_type=self.order_cell_portal_type)
    self.failIfDifferentSet( cell_list , [] )


  def stepCreateReturnedPackingListWithCell(self, sequence=None,
                                            sequence_list=None, **kw):
    """
      Creating a returned sale packing list with variations
    """
    returned_packing_list = self.getPortal().getDefaultModule(
        self.returned_packing_list_portal_type).newContent(
            portal_type=self.returned_packing_list_portal_type)

    organisation = sequence.get('organisation1')
    organisation3 = sequence.get('organisation3')

    start_date = DateTime(self.shipping_date_string)
    returned_packing_list.edit(
      title = "RPL%s" % returned_packing_list.getId(),
      start_date = start_date,
      stop_date = start_date + 20,
    )
    if organisation is not None:
      returned_packing_list.edit(source_value=organisation3,
                 source_section_value=organisation3,
                 destination_value=organisation,
                 destination_section_value=organisation,
                 source_decision_value=organisation3,
                 destination_decision_value=organisation,
                 source_administration_value=organisation3,
                 destination_administration_value=organisation,
                 )

    returned_packing_list_line = returned_packing_list.newContent(
        portal_type=self.returned_packing_list_line_portal_type)
    size_list = ['Baby','Child', 'Man', 'Woman']
    resource = sequence.get('resource')
    resource.edit(
      industrial_phase_list=["phase1", "phase2"],
      size_list=size_list,
      variation_base_category_list=['size']
    )

    returned_packing_list_line.setResourceValue(resource)
    variation_category_list = ['size/Baby', 'size/Child']

    resource_vbcl = resource.getVariationBaseCategoryList()
    line_vcl = []
    for vbc in resource_vbcl:
      resource_vcl = list(resource.getVariationCategoryList(
                                  base_category_list=[vbc],
                                  omit_individual_variation=0))
      resource_vcl.sort()
      line_vcl.extend(self.splitList(resource_vcl)[0])

    returned_packing_list_line.setVariationCategoryList(line_vcl)
    base_id = 'variation'
    returned_packing_list_line.setCellRange(line_vcl, base_id=base_id)
    self.tic()

    self.assertEqual(2, len(variation_category_list))
    cell_key_list = list(returned_packing_list_line.getCellKeyList(base_id=base_id))

    self.assertNotEquals(0, len(cell_key_list))
    for cell_key in cell_key_list:
      cell = returned_packing_list_line.newCell(base_id=base_id,
                                         portal_type=self.returned_packing_list_cell_portal_type,
                                         *cell_key)
      cell.edit(mapped_value_property_list=['price','quantity'],
                price=100, quantity=200,
                predicate_category_list=cell_key,
                variation_category_list=cell_key)
    self.commit()
    cell_list = returned_packing_list_line.objectValues(
        portal_type=self.returned_packing_list_cell_portal_type)
    self.assertEqual(2, len(cell_list))
    sequence.edit(returned_packing_list_with_cell=returned_packing_list)


  def stepCheckReturnedPackingListWithCell(self, sequence=None,
                                           sequence_list=None, **kw):
    """
      Check that returned sale packing list with variation
    """
    rplwc = sequence.get('returned_packing_list_with_cell')
    rplwc_line_list = rplwc.objectValues(
                portal_type=self.returned_packing_list_line_portal_type)
    self.assertEqual(1, len(rplwc_line_list))
    rplwc_line = rplwc_line_list[0]

    vcl = rplwc_line.getVariationCategoryList(omit_optional_variation=1)
    self.assertEqual(2, len(vcl))
    cell_list = rplwc_line.objectValues(
        portal_type=self.returned_packing_list_cell_portal_type)
    self.assertEqual(2, len(cell_list))


  def stepCheckReturnedPackingListWithCellDeleting(self, sequence=None,
                                            sequence_list=None, **kw):
    """
      Check that deleting cell
    """
    rplwc = sequence.get('returned_packing_list_with_cell')
    rplwc_line_list = rplwc.objectValues(
                portal_type=self.returned_packing_list_line_portal_type)
    self.assertEqual(1, len(rplwc_line_list))
    rplwc_line = rplwc_line_list[0]

    vcl = rplwc_line.getVariationCategoryList(omit_optional_variation=1)
    self.assertEqual(2, len(vcl))
    cell_list = rplwc_line.objectValues(
        portal_type=self.returned_packing_list_cell_portal_type)
    self.assertEqual(2, len(cell_list))
    # delete cells
    rplwc_line.deleteContent(map(lambda x: x.getId(), cell_list))
    self.commit()

    cell_list = rplwc_line.objectValues(
    ortal_type=self.returned_packing_list_cell_portal_type)
    self.assertEqual(0, len(cell_list))

  def stepCheckReturnedPackingListIsNotDivergent(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Test if packing list is not divergent
    """
    packing_list = sequence.get('returned_packing_list')
    self.assertFalse(packing_list.isDivergent())

class TestReturnedSalePackingList(ReturnedSalePackingListMixin, ERP5TypeTestCase):
  """Tests for returned sale packing list.
  """
  run_all_test = 1
  quiet = 0

  @newSimulationExpectedFailure
  def test_01_ReturnedSalePackingListWithInventory(self, quiet=quiet,
                                                   run=run_all_test):
    """
      Test that returned sale packing list with its inventory
    """
    if not run: return

    sequence_list = SequenceList()

    sequence_string = self.default_sequence + '\
                      stepTic \
                      stepCreateInitialInventory \
                      stepTic \
                      stepCheckInitialInventory \
                      stepCreateReturnedPackingList \
                      stepConfirmReturnedPackingList \
                      stepShipReturnedPackingList \
                      stepReceiveReturnedPackingList \
                      stepDeliverReturnedPackingList \
                      stepTic \
                      stepCheckReturnedInventory \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)


  @newSimulationExpectedFailure
  def test_02_ReturnedSalePackingListWorkflow(self, quiet=quiet,
                                                   run=run_all_test):
    """
      Test that returned sale packing list workflow
    """
    if not run: return

    sequence_list = SequenceList()

    sequence_string = self.default_sequence + '\
                      stepTic \
                      stepCreateReturnedPackingList \
                      stepConfirmReturnedPackingList \
                      stepTic \
                      stepCheckConfirmedReturnedPackingList \
                      stepShipReturnedPackingList \
                      stepTic \
                      stepCheckShippedReturnedPackingList \
                      stepReceiveReturnedPackingList \
                      stepTic \
                      stepCheckReceivedReturnedPackingList \
                      stepDeliverReturnedPackingList \
                      stepTic \
                      stepCheckDeliveredReturnedPackingList \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


  @newSimulationExpectedFailure
  def test_03_ReturnedSalePackingListWorkflowFail(self, quiet=quiet,
                                                   run=run_all_test):
    """
      Test that can not change workflow when delivered
    """
    if not run: return

    sequence_list = SequenceList()

    sequence_string = self.default_sequence + '\
                      stepTic \
                      stepCreateReturnedPackingList \
                      stepConfirmReturnedPackingList \
                      stepTic \
                      stepCheckConfirmedReturnedPackingList \
                      stepShipReturnedPackingList \
                      stepTic \
                      stepCheckShippedReturnedPackingList \
                      stepReceiveReturnedPackingList \
                      stepTic \
                      stepCheckReceivedReturnedPackingList \
                      stepDeliverReturnedPackingList \
                      stepTic \
                      stepCheckDeliveredReturnedPackingList \
                      stepTic \
                      stepConfirmReturnedPackingList \
                      stepTic \
                      '
    sequence_list.addSequenceString(sequence_string)
    try:
      sequence_list.play(self, quiet=quiet)
    except UnsupportedWorkflowMethod as e:
      self.assertTrue(True)

  def test_04_ReturnedSalePackingListCreating(self, quiet=quiet,
                                              run=run_all_test):
    """
      Test that returned sale packing List creating
    """
    if not run: return

    sequence_list = SequenceList()

    sequence_string = self.default_sequence + '\
                      stepTic \
                      stepCreateReturnedPackingList \
                      stepTic \
                      stepCheckReturnedPackingListCreating \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_05_ReturnedSalePackingListDeleting(self, quiet=quiet,
                                              run=run_all_test):
    """
      Test that returned sale packing list deleting
    """
    if not run: return

    sequence_list = SequenceList()
    sequence_string = self.default_sequence + '\
                      stepTic \
                      stepCreateReturnedPackingList \
                      stepTic \
                      stepCheckReturnedPackingListDeleting \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_06_ReturnedSalePackingListWithCell(self, quiet=quit,
                                              run=run_all_test):
    """
      Test that returned sale packing list with variations
    """
    sequence_list = SequenceList()
    sequence_string = self.default_sequence + '\
                      stepTic \
                      stepCreateReturnedPackingListWithCell \
                      stepCheckReturnedPackingListWithCell \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_07_ReturnedSalePackingListWithCellDeleting(self, quiet=quit,
                                              run=run_all_test):
    """
      Test that deleting variations in returned sale packing list
    """
    sequence_list = SequenceList()
    sequence_string = self.default_sequence + '\
                      stepTic \
                      stepCreateReturnedPackingListWithCell \
                      stepCheckReturnedPackingListWithCellDeleting \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestReturnedSalePackingList))
  return suite
