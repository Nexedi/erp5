#############################################################################
#
# Copyright  2008 Nexedi SA Contributors. All Rights Reserved.
#              Romain Courteaud <romain@nexedi.com>
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

"""Tests Standards ERP5 Trade Reports
"""
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5ReportTestCase
from Products.ERP5Type.tests.utils import reindex
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime

class TestTradeReports(ERP5ReportTestCase):
  """Test Trade reports
  """
  def getTitle(self):
    return "Trade Reports"

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_core_proxy_field_legacy',
            'erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_pdm', )

  def login(self):
    """login with Manager roles."""
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', 'manager', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)

  def loginAsUser(self):
    """login as user, without Manager role"""
    uf = self.getPortal().acl_users
    uf._doAddUser('user', 'user', ['Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    """Setup the fixture.
    """
    self.portal = self.getPortal()
    self.organisation_module = self.portal.organisation_module
    self.inventory_module = self.portal.inventory_module
    self.sale_order_module = self.portal.sale_order_module
    self.product_module = self.portal.product_module
    self.portal_categories = self.portal.portal_categories

    # Create site category
    for site_id in ('demo_site_A', 'demo_site_B',):
      if not self.portal_categories['site'].has_key(site_id):
        self.portal_categories.site.newContent(
                                  portal_type='Category',
                                  title=site_id,
                                  reference=site_id,
                                  id=site_id)
    # Colour categories
    for colour_id in ('colour1', 'colour2',):
      if not self.portal_categories['colour'].has_key(colour_id):
        self.portal_categories.colour.newContent(
                                  portal_type='Category',
                                  title=colour_id,
                                  reference=colour_id,
                                  id=colour_id)

    # create group categories
    for group_id in ('g1', 'g2', 'g3'):
      if not self.portal_categories['group'].has_key(group_id):
        self.portal_categories.group.newContent(
                                  portal_type='Category',
                                  title=group_id,
                                  reference=group_id,
                                  id=group_id)
    # create organisations (with no organisation member of g3)
    if not self.organisation_module.has_key('Organisation_1'):
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_1',
                              title='Organisation_1',
                              id='Organisation_1',
                              group='g1',
                              site='demo_site_A',
                              default_email_coordinate_text='organisation1@example.com',
                              default_telephone_coordinate_text='11111',
                              default_address_street_address='1 Organisation Street',
                              default_address_zip_code='111',
                              default_address_city='City', )
    if not self.organisation_module.has_key('Organisation_2'):
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_2',
                              title='Organisation_2',
                              id='Organisation_2',
                              group='g2',
                              site='demo_site_B')
    # no group no site
    if not self.organisation_module.has_key('Organisation_3'):
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_3',
                              title='Organisation_3',
                              id='Organisation_3',)

    # create unit categories
    for unit_id in ('kg', 'g',):
      if not self.portal_categories['quantity_unit'].has_key(unit_id):
        self.portal_categories.quantity_unit.newContent(
                                  portal_type='Category',
                                  title=unit_id.title(),
                                  reference=unit_id,
                                  id=unit_id)

    # Create resources
    module = self.portal.product_module
    if not module.has_key('product_B'):
      product = module.newContent(
          portal_type='Product',
          id='product_B',
          title='product_B',
          reference='ref 1',
          quantity_unit='kg'
          )
    if not module.has_key('product_A'):
      product = module.newContent(
          portal_type='Product',
          id='product_A',
          title='product_A',
          reference='ref 2',
          quantity_unit='g'
          )
    if not module.has_key('product_C'):
      product = module.newContent(
          portal_type='Product',
          id='product_C',
          title='variated product',
          reference='ref 3',
          variation_base_category_list=['colour'],
          colour_list=['colour1', 'colour2'],
          )
    if not self.portal.service_module.has_key('service_a'):
      self.portal.service_module.newContent(
          portal_type='Service',
          id='service_a',
          title='Service A',
          reference='ref sA',
          )

    # and all this available to catalog
    self.tic()
    self.loginAsUser()

  def beforeTearDown(self):
    """Remove all documents.
    """
    self.abort()

    self.organisation_module.manage_delObjects(
                      list(self.organisation_module.objectIds()))
    self.product_module.manage_delObjects(
                      list(self.product_module.objectIds()))
    self.portal_categories.site.manage_delObjects(
        [x for x in self.portal_categories['site'].objectIds()])
    self.portal_categories.colour.manage_delObjects(
        [x for x in self.portal_categories['colour'].objectIds()])
    self.inventory_module.manage_delObjects(
                      list(self.inventory_module.objectIds()))
    self.sale_order_module.manage_delObjects(
                      list(self.sale_order_module.objectIds()))

    self.tic()

  @reindex
  def _makeOneInventory(self, simulation_state='draft',
                        resource=None, quantity=None, **kw):
    """Creates an inventory.
    """
    inventory = self.inventory_module.newContent(portal_type='Inventory', **kw)
    inventory_line = inventory.newContent(portal_type='Inventory Line',
                                          resource=resource,
                                          inventory=quantity)

    if simulation_state == 'delivered':
      inventory.deliver()

    # sanity check
    self.assertEqual(simulation_state, inventory.getSimulationState())
    return inventory

  @reindex
  def _makeOneSaleOrder(self, resource_dict={}, cancel=False, **kw):
    """
    Create a sale order
    """
    sale_order = self.sale_order_module.newContent(portal_type="Sale Order", **kw)
    for product, values in resource_dict.iteritems():
      sale_order_line = sale_order.newContent(portal_type="Sale Order Line",
                                              resource=product,
                                              quantity=values["quantity"],
                                              price=values["price"])

    self.assertEqual(sale_order.getSimulationState(), 'draft')
    if cancel:
      sale_order.cancel()
      self.assertEqual(sale_order.getSimulationState(), 'cancelled')

    return sale_order

  def _createSaleOrdersForSaleOrderReportTest(self):
    # Create sales orders to be used in testSaleOrderReportXXX tests
    first = self._makeOneSaleOrder(
              title='SO 1',
              destination_value=self.organisation_module.Organisation_1,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value=self.organisation_module.Organisation_1,
              source_value=self.organisation_module.Organisation_2,
              source_section_value=self.organisation_module.Organisation_2,
              source_decision_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2006, 2, 2, 10),
              resource_dict = {'product_module/product_A':{"quantity":11, "price":3},
                               'product_module/product_B':{"quantity":7, "price":6},}
              )
    second = self._makeOneSaleOrder(
              title='SO 2',
              destination_value=self.organisation_module.Organisation_1,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value=self.organisation_module.Organisation_1,
              source_value=self.organisation_module.Organisation_2,
              source_section_value=self.organisation_module.Organisation_2,
              source_decision_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 2, 2),
              resource_dict = {'product_module/product_A':{"quantity":3, "price":3},}
              )
    third = self._makeOneSaleOrder(
              title='SO 3',
              destination_value=self.organisation_module.Organisation_2,
              destination_section_value=self.organisation_module.Organisation_2,
              destination_decision_value=self.organisation_module.Organisation_2,
              source_value=self.organisation_module.Organisation_1,
              source_section_value=self.organisation_module.Organisation_1,
              source_decision_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2006, 2, 22),
              resource_dict = {'product_module/product_A':{"quantity":5, "price":3},
                               'product_module/product_B':{"quantity":1, "price":6},}
              )
    fourth = self._makeOneSaleOrder(
              title='SO 4',
              destination_value=self.organisation_module.Organisation_1,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value=self.organisation_module.Organisation_1,
              source_value=self.organisation_module.Organisation_2,
              source_section_value=self.organisation_module.Organisation_2,
              source_decision_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 2, 2),
              resource_dict = {'product_module/product_A':{"quantity":17, "price":3},
                               'product_module/product_B':{"quantity":13, "price":6},},
              cancel=True
              )

    self.tic()

  def testSaleOrderReportBefore2006(self):
    """
    before 2006
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['from_date'] = DateTime(2004, 1, 1)
    request['at_date'] = DateTime(2005, 1, 1)
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['simulation_state'] = ['cancelled', 'draft']
    request['section_category'] = 'group/g2'

    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(0, len(data_line_list))

  def testSaleOrderReport2005_2006_g2(self):
    """
    Year 2005 + 2006, first document for g2
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['from_date'] = DateTime(2005, 2, 2)
    request['at_date'] = DateTime("2006-12-31")
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['simulation_state'] = ['cancelled', 'draft']
    request['section_category'] = 'group/g2'

    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()

    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEqual(3, len(data_line_list))
    self.assertEqual(1, len(stat_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list, ['client',
                    'product',
                    'Amount 2005',
                    'Quantity 2005',
                    'Quantity Unit 2005',
                    'Amount 2006',
                    'Quantity 2006',
                    'Quantity Unit 2006',
                    'total amount',
                    'total quantity'])

    # First Organisation
    d =  {'Amount 2005': 0,
                 'Amount 2006': 75.0,
                 'Quantity 2005': None,
                 'Quantity 2006': None,
                 'Quantity Unit 2005': None,
                 'Quantity Unit 2006': None,
                 'client': 'Organisation_1',
                 'product': None,
                 'total amount': 75.0,
                 'total quantity': None}
    self.checkLineProperties(data_line_list[0],**d)

    # Product one for first organisation
    d={'Amount 2005': 0,
                 'Amount 2006': 33.0,
                 'Quantity 2005': 0,
                 'Quantity 2006': 11.0,
                 'Quantity Unit 2005': '',
                 'Quantity Unit 2006': 'G',
                 'client': None,
                 'product': 'product_A',
                 'total amount': 33.0,
                 'total quantity': 11.0}
    self.checkLineProperties(data_line_list[1],**d)

    # Product two for first organisation
    d = {'Amount 2005': 0,
                 'Amount 2006': 42.0,
                 'Quantity 2005': 0,
                 'Quantity 2006': 7.0,
                 'Quantity Unit 2005': '',
                 'Quantity Unit 2006': 'Kg',
                 'client': None,
                 'product': 'product_B',
                 'total amount': 42.0,
                 'total quantity': 7.0}
    self.checkLineProperties(data_line_list[2],**d)
    # stat line
    d = {'Amount 2005': None,
                 'Amount 2006': 75.0,
                 'Quantity 2005': None,
                 'Quantity 2006': None,
                 'Quantity Unit 2005': None,
                 'Quantity Unit 2006': None,
                 'client': 'Total',
                 'product': None,
                 'total amount': 75.0,
                 'total quantity': None}
    self.checkLineProperties(stat_line_list[0],**d)


  def testSaleOrderReport2005_2006_g2_check_at_date_inclusive(self):
    """
    This is exactly the same as testSaleOrderReport2005_2006_g2,
    but at_date is set as 02/02/2006
    so we check that first sale_order with start_date=DateTime(2006, 2, 2, 10)
    is counted, i.e. at_date is inclusive.
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['from_date'] = DateTime(2005, 2, 2)
    request['at_date'] = DateTime(2006, 2, 2)
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['simulation_state'] = ['cancelled', 'draft']
    request['section_category'] = 'group/g2'

    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()

    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEqual(3, len(data_line_list))
    self.assertEqual(1, len(stat_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list, ['client',
                    'product',
                    'Amount 2005',
                    'Quantity 2005',
                    'Quantity Unit 2005',
                    'Amount 2006',
                    'Quantity 2006',
                    'Quantity Unit 2006',
                    'total amount',
                    'total quantity'])

    # First Organisation
    d =  {'Amount 2005': 0,
                 'Amount 2006': 75.0,
                 'Quantity 2005': None,
                 'Quantity 2006': None,
                 'Quantity Unit 2005': None,
                 'Quantity Unit 2006': None,
                 'client': 'Organisation_1',
                 'product': None,
                 'total amount': 75.0,
                 'total quantity': None}
    self.checkLineProperties(data_line_list[0],**d)

    # Product one for first organisation
    d={'Amount 2005': 0,
                 'Amount 2006': 33.0,
                 'Quantity 2005': 0,
                 'Quantity 2006': 11.0,
                 'Quantity Unit 2005': '',
                 'Quantity Unit 2006': 'G',
                 'client': None,
                 'product': 'product_A',
                 'total amount': 33.0,
                 'total quantity': 11.0}
    self.checkLineProperties(data_line_list[1],**d)

    # Product two for first organisation
    d = {'Amount 2005': 0,
                 'Amount 2006': 42.0,
                 'Quantity 2005': 0,
                 'Quantity 2006': 7.0,
                 'Quantity Unit 2005': '',
                 'Quantity Unit 2006': 'Kg',
                 'client': None,
                 'product': 'product_B',
                 'total amount': 42.0,
                 'total quantity': 7.0}
    self.checkLineProperties(data_line_list[2],**d)
    # stat line
    d = {'Amount 2005': None,
                 'Amount 2006': 75.0,
                 'Quantity 2005': None,
                 'Quantity 2006': None,
                 'Quantity Unit 2005': None,
                 'Quantity Unit 2006': None,
                 'client': 'Total',
                 'product': None,
                 'total amount': 75.0,
                 'total quantity': None}
    self.checkLineProperties(stat_line_list[0],**d)

  def testSaleOrderReport2005_2006_g1(self):
    """
    Year 2005 + 2006, first document for g1
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['from_date'] = DateTime(2005, 2, 2)
    request['at_date'] = DateTime("2006-12-31")
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['simulation_state'] = ['cancelled', 'draft']
    request['section_category'] = 'group/g1'
    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()

    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEqual(3, len(data_line_list))
    self.assertEqual(1, len(stat_line_list))

    # Second organisation
    d = {'Amount 2005': 0,
                 'Amount 2006': 21.0,
                 'Quantity 2005': None,
                 'Quantity 2006': None,
                 'Quantity Unit 2005': None,
                 'Quantity Unit 2006': None,
                 'client': 'Organisation_2',
                 'product': None,
                 'total amount': 21.0,
                 'total quantity': None}
    self.checkLineProperties(data_line_list[0],**d)

    # Product one for second organisation
    d = {'Amount 2005': 0,
                 'Amount 2006': 15.0,
                 'Quantity 2005': 0,
                 'Quantity 2006': 5.0,
                 'Quantity Unit 2005': '',
                 'Quantity Unit 2006': 'G',
                 'client': None,
                 'product': 'product_A',
                 'total amount': 15.0,
                 'total quantity': 5.0}
    self.checkLineProperties(data_line_list[1],**d)

    # Product two for second organisation
    d = {'Amount 2005': 0,
                 'Amount 2006': 6.0,
                 'Quantity 2005': 0,
                 'Quantity 2006': 1.0,
                 'Quantity Unit 2005': '',
                 'Quantity Unit 2006': 'Kg',
                 'client': None,
                 'product': 'product_B',
                 'total amount': 6.0,
                 'total quantity': 1.0}
    self.checkLineProperties(data_line_list[2],**d)

    # stat line
    d = {'Amount 2005': None,
                 'Amount 2006': 21.0,
                 'Quantity 2005': None,
                 'Quantity 2006': None,
                 'Quantity Unit 2005': None,
                 'Quantity Unit 2006': None,
                 'client': 'Total',
                 'product': None,
                 'total amount': 21.0,
                 'total quantity': None}
    self.checkLineProperties(stat_line_list[0],**d)

  def testSaleOrderReport2006_2007_g1(self):
    """
    Year 2006 + 2007, only draft documents and one group
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['from_date'] = DateTime(2006, 2, 2)
    request['at_date'] = DateTime(2007, 12, 31)
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['simulation_state'] = ['draft',]
    request['section_category'] = 'group/g2'
    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEqual(3, len(data_line_list))
    self.assertEqual(1, len(stat_line_list))
    # First organisation
    d = {'Amount 2006': 75.0,
                 'Amount 2007': 9.0,
                 'Quantity 2006': None,
                 'Quantity 2007': None,
                 'Quantity Unit 2006': None,
                 'Quantity Unit 2007': None,
                 'client': 'Organisation_1',
                 'product': None,
                 'total amount': 84.0,
                 'total quantity': None}
    self.checkLineProperties(data_line_list[0],**d)
    # Product one for organisation
    d = {'Amount 2006': 33.0,
                 'Amount 2007': 9.0,
                 'Quantity 2006': 11.0,
                 'Quantity 2007': 3.0,
                 'Quantity Unit 2006': 'G',
                 'Quantity Unit 2007': 'G',
                 'client': None,
                 'product': 'product_A',
                 'total amount': 42.0,
                 'total quantity': 14.0}
    # Product two for organisation
    self.checkLineProperties(data_line_list[1],**d)
    d = {'Amount 2006': 42.0,
                 'Amount 2007': 0,
                 'Quantity 2006': 7.0,
                 'Quantity 2007': 0,
                 'Quantity Unit 2006': 'Kg',
                 'Quantity Unit 2007': '',
                 'client': None,
                 'product': 'product_B',
                 'total amount': 42.0,
                 'total quantity': 7.0}
    self.checkLineProperties(data_line_list[2],**d)
    # stat line
    d = {'Amount 2006': 75.0,
                 'Amount 2007': 9.0,
                 'Quantity 2006': None,
                 'Quantity 2007': None,
                 'Quantity Unit 2006': None,
                 'Quantity Unit 2007': None,
                 'client': 'Total',
                 'product': None,
                 'total amount': 84.0,
                 'total quantity': None}
    self.checkLineProperties(stat_line_list[0],**d)

  def testSaleOrderReport_weekly_aggregation_level_g2(self):
    """
    weekly aggregation level for g2
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['from_date'] = DateTime(2006, 2, 1)
    request['at_date'] = DateTime(2006, 2, 28)
    request['aggregation_level'] = "week"
    request['group_by'] = "client"
    request['simulation_state'] = ['cancelled', 'draft']
    request['section_category'] = 'group/g2'

    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                   **{'Amount 2006-05': 11*3 + 7*6,
                      'Amount 2006-06': 0,
                      'Amount 2006-07': 0,
                      'Amount 2006-08': 0,
                      'Amount 2006-09': 0,
                      'client': 'Organisation_1',
                      'total amount': 3*11 + 7*6})
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
                   **{'Amount 2006-05': 11*3 + 7*6,
                      'Amount 2006-06': None,
                      'Amount 2006-07': None,
                      'Amount 2006-08': None,
                      'Amount 2006-09': None,
                      'client': 'Total',
                      'total amount': 3*11 + 7*6})

  def testSaleOrderReport_weekly_aggregation_level_g1(self):
    """
    weekly aggregation level for g1
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['from_date'] = DateTime(2006, 2, 1)
    request['at_date'] = DateTime(2006, 2, 28)
    request['aggregation_level'] = "week"
    request['group_by'] = "client"
    request['simulation_state'] = ['cancelled', 'draft']
    request['section_category'] = 'group/g1'
    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                   **{'Amount 2006-05': 0,
                      'Amount 2006-06': 0,
                      'Amount 2006-07': 0,
                      'Amount 2006-08': 5*3 + 6,
                      'Amount 2006-09': 0,
                      'client': 'Organisation_2',
                      'total amount': 5*3 + 6})

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
                   **{'Amount 2006-05': None,
                      'Amount 2006-06': None,
                      'Amount 2006-07': None,
                      'Amount 2006-08': 5*3 + 6,
                      'Amount 2006-09': None,
                      'client': 'Total',
                      'total amount': 5*3 + 6})

  def testSaleOrderReport_dates_not_specified_g2(self):
    """
    dates not specified -> they should be guessed
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['from_date'] = None
    request['at_date'] = None
    request['simulation_state'] = ['draft',]
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['section_category'] = 'group/g2'
    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEqual(3, len(data_line_list))
    self.assertEqual(1, len(stat_line_list))
    # First organisation
    d = {'Amount 2006': 75.0,
                 'Amount 2007': 9.0,
                 'Quantity 2006': None,
                 'Quantity 2007': None,
                 'Quantity Unit 2006': None,
                 'Quantity Unit 2007': None,
                 'client': 'Organisation_1',
                 'product': None,
                 'total amount': 84.0,
                 'total quantity': None}
    self.checkLineProperties(data_line_list[0],**d)
    # Product one for organisation
    d = {'Amount 2006': 33.0,
                 'Amount 2007': 9.0,
                 'Quantity 2006': 11.0,
                 'Quantity 2007': 3.0,
                 'Quantity Unit 2006': 'G',
                 'Quantity Unit 2007': 'G',
                 'client': None,
                 'product': 'product_A',
                 'total amount': 42.0,
                 'total quantity': 14.0}
    # Product two for organisation
    self.checkLineProperties(data_line_list[1],**d)
    d = {'Amount 2006': 42.0,
                 'Amount 2007': 0,
                 'Quantity 2006': 7.0,
                 'Quantity 2007': 0,
                 'Quantity Unit 2006': 'Kg',
                 'Quantity Unit 2007': '',
                 'client': None,
                 'product': 'product_B',
                 'total amount': 42.0,
                 'total quantity': 7.0}
    self.checkLineProperties(data_line_list[2],**d)
    # stat line
    d = {'Amount 2006': 75.0,
                 'Amount 2007': 9.0,
                 'Quantity 2006': None,
                 'Quantity 2007': None,
                 'Quantity Unit 2006': None,
                 'Quantity Unit 2007': None,
                 'client': 'Total',
                 'product': None,
                 'total amount': 84.0,
                 'total quantity': None}
    self.checkLineProperties(stat_line_list[0],**d)

  def testSaleOrderReport_section_category_set(self):
    """
    section category set, with no matching organisations
    """
    self._createSaleOrdersForSaleOrderReportTest()
    request = self.portal.REQUEST

    request['simulation_state'] = ['draft',]
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['section_category'] = 'group/g3'
    parameter_dict, stat_columns, selection_columns = self.sale_order_module.OrderModule_getOrderReportParameterDict()
    active_process = self.sale_order_module.OrderModule_activateGetOrderStatList(tag="unit_test", **parameter_dict)
    request['active_process'] = active_process.getPath()
    self.tic()
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEqual(0, len(data_line_list))
    self.assertEqual(1, len(stat_line_list))
    # stat line
    d = {'Amount 2006': None,
                 'Amount 2007': None,
                 'Quantity 2006': None,
                 'Quantity 2007': None,
                 'Quantity Unit 2006': None,
                 'Quantity Unit 2007': None,
                 'client': 'Total',
                 'product': None,
                 'total amount': None,
                 'total quantity': None}
    self.checkLineProperties(stat_line_list[0],**d)

  def _createInventoryForStockReportTest(self):
    # Create inventories
    # Create inventories
    first = self._makeOneInventory(
              title='Inventory 1',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
              source_value=self.organisation_module.Organisation_3,
              start_date=DateTime(2006, 2, 2),
              resource='product_module/product_A',
              quantity=11,
              )

    second = self._makeOneInventory(
              title='Inventory 2',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_A',
              quantity=22,
              )

    third = self._makeOneInventory(
              title='Inventory 3',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_B',
              quantity=33,
              )

    fourth = self._makeOneInventory(
              title='Inventory 4',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_B',
              quantity=44,
              )

    fifth = self._makeOneInventory(
              title='Inventory 5',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_C',
              quantity=55,
              )
    fifth_line = fifth.contentValues(portal_type='Inventory Line')[0]
    fifth_line.edit(
        variation_category_list=['colour/colour1', 'colour/colour2'],
        )
    base_id = 'movement'
    cell_key_list = list(fifth_line.getCellKeyList(base_id=base_id))
    for cell_key in cell_key_list:
      cell = fifth_line.newCell(base_id=base_id,
                                portal_type='Inventory Cell',
                                *cell_key)
      cell.edit(mapped_value_property_list=['inventory'],
                inventory=66,
                predicate_category_list=cell_key,
                variation_category_list=cell_key)
    fifth.deliver()

    # services are ignored
    self._makeOneInventory(
              title='Inventory 6',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='service_module/service_a',
              quantity=11,
              )

    self.tic()

  def testStockReport_old_date(self):
    """
    Old date
    """
    self._createInventoryForStockReportTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2005, 1, 1)
    request.form['node_category'] = 'site/demo_site_A'

    line_list = self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=request)

    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(0, len(data_line_list))

  def testStockReport_middle_date(self):
    """
    Middle date
    """
    self._createInventoryForStockReportTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2006, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'

    line_list = self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list, ['resource_title',
                                           'resource_reference',
                                           'variation_category_item_list',
                                           'inventory',
                                           'quantity_unit'])
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_category_item_list=[],
                   inventory=11,
                   quantity_unit='G')

  def testStockReport_future_date(self):
    """
    Future date
    """
    self._createInventoryForStockReportTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'

    line_list = self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(4, len(data_line_list))

    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_B',
                   resource_reference='ref 1',
                   variation_category_item_list=[],
                   inventory=33,
                   quantity_unit='Kg')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_category_item_list=[],
                   inventory=22,
                   quantity_unit='G')
    self.checkLineProperties(
                   data_line_list[2],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_category_item_list=['colour1'],
                   inventory=66,
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[3],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_category_item_list=['colour2'],
                   inventory=66,
                   quantity_unit='')

  def _createInventoryForStockReportWithPositiveOrNegativeOrZeroStockTest(self):
    # Create inventories
    first = self._makeOneInventory(
              title='Inventory 1',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_A',
              quantity=22,
              )

    second = self._makeOneInventory(
              title='Inventory 2',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_A',
              quantity=-22,
              )

    third = self._makeOneInventory(
              title='Inventory 3',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_B',
              quantity=-33,
              )

    fourth = self._makeOneInventory(
              title='Inventory 4',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_B',
              quantity=-44,
              )

    fifth = self._makeOneInventory(
              title='Inventory 5',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='product_module/product_C',
              quantity=55,
              )
    fifth_line = fifth.contentValues(portal_type='Inventory Line')[0]
    fifth_line.edit(
        variation_category_list=['colour/colour1', 'colour/colour2'],
        )
    base_id = 'movement'
    cell_key_list = list(fifth_line.getCellKeyList(base_id=base_id))
    for cell_key in cell_key_list:
      cell = fifth_line.newCell(base_id=base_id,
                                portal_type='Inventory Cell',
                                *cell_key)
      cell.edit(mapped_value_property_list=['inventory'],
                inventory=66,
                predicate_category_list=cell_key,
                variation_category_list=cell_key)
    fifth.deliver()

    # services are ignored
    self._makeOneInventory(
              title='Inventory 6',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              resource='service_module/service_a',
              quantity=11,
              )

    self.tic()

  def testStockReportWithPositiveOrNegativeOrZeroStock_dont_display_positive_stock(self):
    """
    Don't Display Positive Stock
    """
    self._createInventoryForStockReportWithPositiveOrNegativeOrZeroStockTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'
    request.form['positive_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_B',
                   resource_reference='ref 1',
                   variation_category_item_list=[],
                   inventory=-33,
                   quantity_unit='Kg')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_category_item_list=[],
                   inventory=0,
                   quantity_unit='G')

  def testStockReportWithPositiveOrNegativeOrZeroStock_dont_display_negative_stock(self):
    """
    Don't Display Negative Stock
    """
    self._createInventoryForStockReportWithPositiveOrNegativeOrZeroStockTest()

    request = self.portal.REQUEST

    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'
    request.form['positive_stock'] = 0
    request.form['negative_stock'] = 1

    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(3, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_category_item_list=[],
                   inventory=0,
                   quantity_unit='G')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_category_item_list=['colour1'],
                   inventory=66,
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[2],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_category_item_list=['colour2'],
                   inventory=66,
                   quantity_unit='')

  def testStockReportWithPositiveOrNegativeOrZeroStock_dont_display_zero_stock(self):
    """
    Don't Display Zero Stock
    """
    self._createInventoryForStockReportWithPositiveOrNegativeOrZeroStockTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'
    request.form['positive_stock'] = 0
    request.form['negative_stock'] = 0
    request.form['zero_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(3, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_B',
                   resource_reference='ref 1',
                   variation_category_item_list=[],
                   inventory=-33,
                   quantity_unit='Kg')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_category_item_list=['colour1'],
                   inventory=66,
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[2],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_category_item_list=['colour2'],
                   inventory=66,
                   quantity_unit='')

  def testStockReportWithPositiveOrNegativeOrZeroStock_dont_display_positive_and_negative_stock(self):
    """
    Don't Display Positive Stock
    And Negative Stock
    """
    self._createInventoryForStockReportWithPositiveOrNegativeOrZeroStockTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'
    request.form['positive_stock'] = 1
    request.form['negative_stock'] = 1
    request.form['zero_stock'] = 0
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_category_item_list=[],
                   inventory=0,
                   quantity_unit='G')

  def testStockReportWithPositiveOrNegativeOrZeroStock_dont_display_positive_and_zero_stock(self):
    """
    Don't Display Positive
    And Zero Stock
    """
    self._createInventoryForStockReportWithPositiveOrNegativeOrZeroStockTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'
    request.form['positive_stock'] = 1
    request.form['negative_stock'] = 0
    request.form['zero_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_B',
                   resource_reference='ref 1',
                   variation_category_item_list=[],
                   inventory=-33,
                   quantity_unit='Kg')

  def testStockReportWithPositiveOrNegativeOrZeroStock_dont_display_negative_and_zero_stock(self):
    """
    Don't Display Negative
    And Zero Stock
    """
    self._createInventoryForStockReportWithPositiveOrNegativeOrZeroStockTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'
    request.form['positive_stock'] = 0
    request.form['negative_stock'] = 1
    request.form['zero_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_category_item_list=['colour1'],
                   inventory=66,
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_category_item_list=['colour2'],
                   inventory=66,
                   quantity_unit='')

  def testStockReportWithPositiveOrNegativeOrZeroStock_dont_display_positive_negative_and_zero_stock(self):
    """
    Don't Display Positive,Negative And Zero Stock
    """
    self._createInventoryForStockReportWithPositiveOrNegativeOrZeroStockTest()

    request = self.portal.REQUEST
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['node_category'] = 'site/demo_site_A'
    request.form['positive_stock'] = 1
    request.form['negative_stock'] = 1
    request.form['zero_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(0, len(data_line_list))


  def test_Folder_generateWorkflowReport(self):
    # Create sales orders
    first = self._makeOneSaleOrder(
              title='SO 1',
              destination_value=self.organisation_module.Organisation_1,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value=self.organisation_module.Organisation_1,
              source_value=self.organisation_module.Organisation_2,
              source_section_value=self.organisation_module.Organisation_2,
              source_decision_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2006, 2, 2),
              resource_dict = {'product_module/product_A':{"quantity":11, "price":3},
                               'product_module/product_B':{"quantity":7, "price":6},}
              )
    second = self._makeOneSaleOrder(
              title='SO 2',
              destination_value=self.organisation_module.Organisation_1,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value=self.organisation_module.Organisation_1,
              source_value=self.organisation_module.Organisation_2,
              source_section_value=self.organisation_module.Organisation_2,
              source_decision_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 2, 2),
              resource_dict = {'product_module/product_A':{"quantity":3, "price":3},}
              )
    third = self._makeOneSaleOrder(
              title='SO 4',
              destination_value=self.organisation_module.Organisation_1,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value=self.organisation_module.Organisation_1,
              source_value=self.organisation_module.Organisation_2,
              source_section_value=self.organisation_module.Organisation_2,
              source_decision_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 2, 2),
              resource_dict = {'product_module/product_A':{"quantity":17, "price":3},
                               'product_module/product_B':{"quantity":13, "price":6},},
              cancel=True
              )

    # call the report first, it will set selection
    report_html = \
        self.portal.sale_order_module.Folder_generateWorkflowReport()
    self.assertFalse('Site Error' in report_html)

    line_list = self.portal.sale_order_module.Folder_viewWorkflowReport.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(5, len(data_line_list))
    order_workflow_name = 'Sale Order - Order Workflow'
    causality_workflow_name = 'Sale Order - Causality Workflow'
    self.checkLineProperties(data_line_list[2],
                             translated_portal_type=order_workflow_name)
    self.checkLineProperties(data_line_list[3],
                             translated_portal_type='',
                             state='Cancelled',
                             count=1)
    self.checkLineProperties(data_line_list[4],
                             translated_portal_type='',
                             state='Draft',
                             count=2)
    self.checkLineProperties(data_line_list[0],
                             translated_portal_type=causality_workflow_name)
    self.checkLineProperties(data_line_list[1],
                             translated_portal_type='',
                             state='Draft',
                             count=3)

  def testShipmentReport(self):
    first = self.portal.sale_packing_list_module.newContent(
        portal_type='Sale Packing List',
        title='%s 1' % self.id(),
        destination_value=self.organisation_module.Organisation_1,
        destination_section_value=self.organisation_module.Organisation_1,
        source_value=self.organisation_module.Organisation_2,
        source_section_value=self.organisation_module.Organisation_2,
        start_date=DateTime(2006, 2, 2),
        description='The description',
    )
    first.newContent(
        portal_type='Sale Packing List Line',
        resource_value=self.portal.product_module.product_A,
        quantity=1,
        price=10,
    )
    first.newContent(
        portal_type='Sale Packing List Line',
        resource_value=self.portal.product_module.product_B,
        quantity=1,
        price=3,
    )

    second = self.portal.sale_packing_list_module.newContent(
        portal_type='Sale Packing List',
        title='%s 1' % self.id(),
        destination_value=self.organisation_module.Organisation_1,
        destination_section_value=self.organisation_module.Organisation_1,
        source_value=self.organisation_module.Organisation_2,
        source_section_value=self.organisation_module.Organisation_2,
        start_date=DateTime(2006, 2, 2),
    )
    line_with_variation = second.newContent(
        portal_type='Sale Packing List Line',
        resource_value=self.portal.product_module.product_C,
        variation_category_list=['colour/colour1', 'colour/colour2'],
        price=10,
    )
    base_id = 'movement'
    cell1 = line_with_variation.newCell(
        base_id=base_id,
        portal_type='Sale Packing List Cell',
        *['colour/colour1'])
    cell1.setVariationCategoryList(['colour/colour1'])
    cell1.setQuantity(3)
    cell2 = line_with_variation.newCell(
        base_id=base_id,
        portal_type='Sale Packing List Cell',
        *['colour/colour2'])
    cell2.setVariationCategoryList(['colour/colour2'])
    cell2.setQuantity(2)

    second.newContent(
        portal_type='Sale Packing List Line',
        resource_value=self.portal.product_module.product_B,
        quantity=1,
        price=3,
    )
    self.tic()

    # Display the module to set selection name in REQUEST
    self.portal.sale_packing_list_module.view()
    request = self.portal.REQUEST
    self.portal.portal_selections.setSelectionParamsFor(
        request['selection_name'],
        {"uid": (first.getUid(), second.getUid())})
    self.portal.portal_selections.setSelectionSortOrder(
        request['selection_name'],
        (('reference', 'asc', ),))

    request['delivery_line_list_mode'] = True
    request['delivery_list_mode'] = True
    report_section_list = self.getReportSectionList(
        self.portal.sale_packing_list_module,
        'DeliveryModule_viewShipmentReport')
    self.assertEqual(2, len(report_section_list))

    # Delivery Lines
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(5, len(data_line_list)) # 5 movements

    self.checkLineProperties(
        data_line_list[0],
        delivery_reference=first.getReference(),
        destination_default_address_text='1 Organisation Street\n111 City',
        destination_default_telephone_coordinate_text='11111',
        quantity=1,
        resource_reference='ref 2',
        resource_title='product_A',
        start_date=DateTime(2006, 2, 2),
        description='The description',)
    # a variated line
    self.checkLineProperties(
        data_line_list[2],
        quantity=3,
        resource_reference='ref 3',
        resource_title='variated product',
        variation='colour1')


    # Deliveries
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list)) # 2 deliveries

    self.checkLineProperties(
        data_line_list[0],
        delivery_reference=first.getReference(),
        destination_default_address_text='1 Organisation Street\n111 City',
        destination_default_telephone_coordinate_text='11111',
        # delivery_resource_text shows only resource references, as we have one piece of each product
        delivery_resource_text="ref 1\nref 2",
        start_date=DateTime(2006, 2, 2),
        description='The description',)

    self.checkLineProperties(
        data_line_list[1],
        # delivery_resource_text shows quantities and variations
        delivery_resource_text="ref 1: 1.0\nref 3 colour1: 3.0\nref 3 colour2: 2.0")


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTradeReports))
  return suite

