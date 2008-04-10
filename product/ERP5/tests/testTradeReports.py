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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime

class TestTradeReports(ERP5TypeTestCase):
  """Test Trade reports
  """
  def getTitle(self):
    return "Trade Reports"

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base', 'erp5_trade', 'erp5_pdm')

  def login(self):
    """login with Manager roles."""
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', 'manager', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)

  def setUp(self):
    """Setup the fixture.
    """
    ERP5TypeTestCase.setUp(self)
    self.portal = self.getPortal()
    self.organisation_module = self.portal.organisation_module
    self.inventory_module = self.portal.inventory_module
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

    # create organisations
    if not self.organisation_module.has_key('Organisation_1'): 
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_1',
                              title='Organisation_1',
                              id='Organisation_1',
                              site='demo_site_A')
    if not self.organisation_module.has_key('Organisation_2'): 
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_2',
                              title='Organisation_2',
                              id='Organisation_2',
                              site='demo_site_B')

    # Create products
    module = self.portal.product_module
    if not module.has_key('product_B'): 
      product = module.newContent(
          portal_type='Product',
          id='product_B',
          title='product_B',
          reference='ref 1',
          )
    if not module.has_key('product_A'): 
      product = module.newContent(
          portal_type='Product',
          id='product_A',
          title='product_A',
          reference='ref 2',
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
    
    # and all this available to catalog
    get_transaction().commit()
    self.tic()

  def tearDown(self):
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
                      
    get_transaction().commit()
    self.tic()

    ERP5TypeTestCase.tearDown(self)

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

  def checkLineProperties(self, line, **kw):
    """Check properties of a report line.
    """
    for k, v in kw.items():
      self.assertEquals(v, line.getColumnProperty(k),
          '`%s`: expected: %r actual: %r' % (k, v, line.getColumnProperty(k)))
  # /utility methods for ERP5 Report

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
                   quantity_unit='')

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
                   quantity_unit='')
    self.checkLineProperties(
                   data_line_list[1],
                   resource_title='product_A',
                   resource_reference='ref 2',
                   variation_text='',
                   inventory=22,
                   quantity_unit='')
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTradeReports))
  return suite

