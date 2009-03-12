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
    return ('erp5_base', 'erp5_trade', 'erp5_pdm', )

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
    for group_id in ('g1', 'g2',):
      if not self.portal_categories['group'].has_key(group_id):
        self.portal_categories.group.newContent(
                                  portal_type='Category',
                                  title=group_id,
                                  reference=group_id,
                                  id=group_id)
    # create organisations
    if not self.organisation_module.has_key('Organisation_1'): 
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_1',
                              title='Organisation_1',
                              id='Organisation_1',
                              group='g1',
                              site='demo_site_A')
    if not self.organisation_module.has_key('Organisation_2'): 
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_2',
                              title='Organisation_2',
                              id='Organisation_2',
                              group='g2',
                              site='demo_site_B')
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
    get_transaction().commit()
    self.tic()
    self.loginAsUser()

  def beforeTearDown(self):
    """Remove all documents.
    """
    get_transaction().abort()

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
                      
    get_transaction().commit()
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
    self.assertEquals(simulation_state, inventory.getSimulationState())
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
      
    self.assertEquals(sale_order.getSimulationState(), 'draft')
    if cancel:
      sale_order.cancel()
      self.assertEquals(sale_order.getSimulationState(), 'cancelled')
      
    return sale_order
      
  def testSaleOrderReport(self):
    """
    Sale order report.
    """
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

    get_transaction().commit()
    self.tic()


    request = self.portal.REQUEST
    #
    # Before 2006
    #
    request['from_date'] = DateTime(2004, 1, 1)
    request['at_date'] = DateTime(2005, 1, 1)
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['simulation_state'] = ['cancelled', 'draft']
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(0, len(data_line_list))

    #
    # Year 2005 + 2006, all documents
    #
    request['from_date'] = DateTime(2005, 2, 2)
    request['at_date'] = DateTime("2006-12-31")

    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEquals(6, len(data_line_list))
    self.assertEquals(1, len(stat_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list, ['client',
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
    self.checkLineProperties(data_line_list[3],**d)
                             
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
    self.checkLineProperties(data_line_list[4],**d)
                             
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
    self.checkLineProperties(data_line_list[5],**d)
                             
    # stat line
    d = {'Amount 2005': None,
                 'Amount 2006': 96.0,
                 'Quantity 2005': None,
                 'Quantity 2006': None,
                 'Quantity Unit 2005': None,
                 'Quantity Unit 2006': None,
                 'client': 'Total',
                 'product': None,
                 'total amount': 96.0,
                 'total quantity': None}
    self.checkLineProperties(stat_line_list[0],**d)
                             
    
    #
    # Year 2006 + 2007, only draft documents and one group
    #
    request['from_date'] = DateTime(2006, 2, 2)
    request['at_date'] = DateTime(2007, 12, 31)
    request['simulation_state'] = ['draft',]
    request['group'] = 'g2'
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEquals(3, len(data_line_list))
    self.assertEquals(1, len(stat_line_list))
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
  
    # weekly aggregation level
    request['from_date'] = DateTime(2006, 2, 1)
    request['at_date'] = DateTime(2006, 2, 28)
    request['aggregation_level'] = "week"
    request['group'] = None
    request['group_by'] = "client"
    request['simulation_state'] = ['cancelled', 'draft']
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                   **{'Amount 2006-05': 11*3 + 7*6,
                      'Amount 2006-06': 0,
                      'Amount 2006-07': 0,
                      'Amount 2006-08': 0,
                      'Amount 2006-09': 0,
                      'client': 'Organisation_1',
                      'total amount': 3*11 + 7*6})
    self.checkLineProperties(data_line_list[1],
                   **{'Amount 2006-05': 0,
                      'Amount 2006-06': 0,
                      'Amount 2006-07': 0,
                      'Amount 2006-08': 5*3 + 6,
                      'Amount 2006-09': 0,
                      'client': 'Organisation_2',
                      'total amount': 5*3 + 6})

    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
                   **{'Amount 2006-05': 11*3 + 7*6,
                      'Amount 2006-06': None,
                      'Amount 2006-07': None,
                      'Amount 2006-08': 5*3 + 6,
                      'Amount 2006-09': None,
                      'client': 'Total',
                      'total amount': 3*11 + 7*6 + 5*3 + 6})


    # dates not specified -> they should be guessed
    request['from_date'] = None
    request['at_date'] = None
    request['simulation_state'] = ['draft',]
    request['aggregation_level'] = "year"
    request['group_by'] = "both"
    request['group'] = 'g2'
    report_section_list = self.getReportSectionList(self.sale_order_module,
                                                    'OrderModule_viewOrderReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    stat_line_list = [l for l in line_list if l.isStatLine()]
    self.assertEquals(3, len(data_line_list))
    self.assertEquals(1, len(stat_line_list))
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
  
  def testStockReport(self):
    """
    Stock report.
    """
    # Create inventories
    first = self._makeOneInventory(
              title='Inventory 1',
              simulation_state='delivered',
              destination_value=self.organisation_module.Organisation_1,
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

    get_transaction().commit()
    self.tic()

    request = self.portal.REQUEST
    ################################
    # Old date
    ################################
    request.form['at_date'] = DateTime(2005, 1, 1)
    request.form['site'] = 'demo_site_A'
    
    line_list = self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=request)

    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(0, len(data_line_list))
    ################################
    # Middle date
    ################################
    request.form['at_date'] = DateTime(2006, 4, 4)
    request.form['site'] = 'demo_site_A'
    
    line_list = self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(1, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['resource_title', 'resource_reference', 'variation_text', 
          'inventory', 'quantity_unit'])

    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_text='',
                   inventory=11,
                   quantity_unit='G')

    ################################
    # Futur date
    ################################
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['site'] = 'demo_site_A'
    
    line_list = self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(4, len(data_line_list))
    
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_B',
                   resource_reference='ref 1',
                   variation_text='',
                   inventory=33,
                   quantity_unit='Kg')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_text='',
                   inventory=22,
                   quantity_unit='G')
    self.checkLineProperties(
                   data_line_list[2],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_text='colour/colour1',
                   inventory=66,
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[3],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_text='colour/colour2',
                   inventory=66,
                   quantity_unit='')
                    
  def testStockReportWithPositiveOrNegativeOrZeroStock(self):
    """
    Stock report.
    """
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

    get_transaction().commit()
    self.tic()

    request = self.portal.REQUEST
    ################################
    # Don't Display Positive Stock
    ################################
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['site'] = 'demo_site_A'
    request.form['positive_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
  
    self.assertEquals(2, len(data_line_list))
    
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_B',
                   resource_reference='ref 1',
                   variation_text='',
                   inventory=-33,
                   quantity_unit='Kg')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_text='',
                   inventory=0,
                   quantity_unit='G')
    ################################
    # Don't Display Negative Stock
    ################################
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['site'] = 'demo_site_A'
    request.form['positive_stock'] = 0
    request.form['negative_stock'] = 1
    
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
  
    self.assertEquals(3, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_text='',
                   inventory=0,
                   quantity_unit='G')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_text='colour/colour1',
                   inventory=66,
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[2],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_text='colour/colour2',
                   inventory=66,
                   quantity_unit='')
    ################################
    # Don't Display Zero Stock
    ################################
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['site'] = 'demo_site_A'
    request.form['positive_stock'] = 0
    request.form['negative_stock'] = 0
    request.form['zero_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
  
    self.assertEquals(3, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_B',
                   resource_reference='ref 1',
                   variation_text='',
                   inventory=-33,
                   quantity_unit='Kg')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_text='colour/colour1',
                   inventory=66,
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[2],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_text='colour/colour2',
                   inventory=66,
                   quantity_unit='')
    
                   
    ################################
    # Don't Display Positive Stock
    # And Negative Stock
    ################################
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['site'] = 'demo_site_A'
    request.form['positive_stock'] = 1
    request.form['negative_stock'] = 1
    request.form['zero_stock'] = 0
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
  
    self.assertEquals(1, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_text='',
                   inventory=0,
                   quantity_unit='G')
    ########################################
    # Don't Display Positive And Zero Stock
    ########################################
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['site'] = 'demo_site_A'
    request.form['positive_stock'] = 1
    request.form['negative_stock'] = 0
    request.form['zero_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
  
    self.assertEquals(1, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='product_B',
                   resource_reference='ref 1',
                   variation_text='',
                   inventory=-33,
                   quantity_unit='Kg')
    ########################################
    # Don't Display Negative And Zero Stock
    ########################################
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['site'] = 'demo_site_A'
    request.form['positive_stock'] = 0
    request.form['negative_stock'] = 1
    request.form['zero_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
  
    self.assertEquals(2, len(data_line_list))
    self.checkLineProperties(
                   data_line_list[0],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_text='colour/colour1',
                   inventory=66,
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='variated product',
                   resource_reference='ref 3',
                   variation_text='colour/colour2',
                   inventory=66,
                   quantity_unit='')
    ################################################
    # Don't Display Positive,Negative And Zero Stock
    ################################################
    request.form['at_date'] = DateTime(2008, 4, 4)
    request.form['site'] = 'demo_site_A'
    request.form['positive_stock'] = 1
    request.form['negative_stock'] = 1
    request.form['zero_stock'] = 1
    line_list = \
      self.portal.inventory_module.Base_viewStockReportBySite.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)

    data_line_list = [l for l in line_list if l.isDataLine()]
  
    self.assertEquals(0, len(data_line_list))

    
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
    self.failIf('Site Error' in report_html)

    line_list = self.portal.sale_order_module.Folder_viewWorkflowReport.listbox.\
        get_value('default',
                  render_format='list', REQUEST=self.portal.REQUEST)
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(6, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             translated_portal_type='Sale Order')
    self.checkLineProperties(data_line_list[1],
                             translated_portal_type='',
                             state='Cancelled',
                             count=1)
    self.checkLineProperties(data_line_list[2],
                             translated_portal_type='',
                             state='Draft',
                             count=2)
    self.checkLineProperties(data_line_list[3],
                             translated_portal_type='All')
    self.checkLineProperties(data_line_list[4],
                             translated_portal_type='',
                             state='Cancelled',
                             count=1)
    self.checkLineProperties(data_line_list[5],
                             translated_portal_type='',
                             state='Draft',
                             count=2)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTradeReports))
  return suite

