##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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

"""Unit Tests for Inventory API.
"""

import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ.setdefault('EVENT_LOG_FILE', 'zLOG.log')
os.environ.setdefault('EVENT_LOG_SEVERITY', '-300')

import random
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.Base import initializePortalTypeDynamicProperties, \
                                   _aq_reset
from Products.ERP5Type.Utils import DocumentConstructor,\
                                    setDefaultClassProperties
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime

class InventoryAPITestCase(ERP5TypeTestCase):
  """Base class for Inventory API Tests {{{
  """
  RUN_ALL_TESTS = 1

  GROUP_CATEGORIES = ( 'group/test_group/A1/B1/C1',
                       'group/test_group/A1/B1/C2',
                       'group/test_group/A1/B2/C1',
                       'group/test_group/A1/B2/C2',
                       'group/test_group/A2/B1/C1',
                       'group/test_group/A2/B1/C2',
                       'group/test_group/A2/B2/C1',
                       'group/test_group/A2/B2/C2', )
  
  def getTitle(self):
    """Title of the test."""
    return self.__class__.__doc__

  def afterSetUp(self):
    """set up """
    self.createCategories()
    self.login()
    if not hasattr(self.getPortal(), 'testing_folder'):
      self.getPortal().newContent(portal_type='Folder',
                                              id='testing_folder')
    self.folder = self.getPortal().testing_folder
    
    self.section = self._makeOrganisation(title='Section')
    self.node = self._makeOrganisation(title='Node')
    self.payment_node = self.section.newContent(
                                  title='Payment Node',
                                  portal_type='Bank Account')
    self.mirror_section = self._makeOrganisation(title='Mirror Section')
    self.mirror_node = self._makeOrganisation(title='Mirror Node')
    self.resource = self.getCurrencyModule().newContent(
                                  title='Resource',
                                  portal_type='Currency')

  def _safeTic(self):
    """Like tic, but swallowing errors, usefull for teardown"""
    try:
      get_transaction().commit()
      self.tic()
    except RuntimeError:
      pass

  def beforeTearDown(self):
    """Clear everything for next test."""
    self._safeTic()
    for module in [ 'organisation_module',
                    'person_module',
                    'currency_module',
                    'portal_simulation',
                    self.folder.getId() ]:
      folder = getattr(self.getPortal(), module, None)
      if folder:
        [x.unindexObject() for x in folder.objectValues()]
        self._safeTic()
        folder.manage_delObjects([x.getId() for x in folder.objectValues()])
    self._safeTic()
    # cancel remaining messages
    activity_tool = self.getPortal().portal_activities
    for message in activity_tool.getMessageList():
      activity_tool.manageCancel(message.object_path, message.method_id)
      ZopeTestCase._print('\nCancelling active message %s.%s()\n'
                          % (message.object_path, message.method_id) )
    get_transaction().commit()

  def login(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)
  
  def createCategories(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList() :
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in path.objectIds() :
          path = path.newContent(
                    portal_type='Category',
                    id=cat,
                    immediate_reindex=1 )
        else:
          path = path[cat]
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)
                
  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return (  'region/level1/level2',
              'group/level1/level2',
              'group/anotherlevel',
              'product_line/level1/level2',
           # we create a huge group category for consolidation tests
           ) + self.GROUP_CATEGORIES
  
  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', 'erp5_dummy_movement')

  # TODO: move this to a base class {{{
  def _makeOrganisation(self, **kw):
    """Creates an organisation."""
    org = self.getPortal().organisation_module.newContent(
          portal_type='Organisation',
          **kw)
    get_transaction().commit()
    self.tic()
    return org

  def _makeSalePackingList(self, **kw):
    """Creates a sale packing list."""
    spl = self.getPortal().sale_packing_list_module.newContent(
          portal_type='Sale Packing List',)
    spl.edit(**kw)
    get_transaction().commit()
    self.tic()
    return spl
  
  def _makeSaleInvoice(self, created_by_builder=0, **kw):
    """Creates a sale invoice."""
    sit = self.getPortal().accounting_module.newContent(
          portal_type='Sale Invoice Transaction',
          created_by_builder=created_by_builder)
    sit.edit(**kw)
    get_transaction().commit()
    self.tic()
    return sit

  def _makeCurrency(self, **kw):
    """Creates a currency."""
    currency = self.getCurrencyModule().newContent(
            portal_type = 'Currency', **kw)
    get_transaction().commit()
    self.tic()
    return currency
  _makeResource = _makeCurrency
  # }}}

  def _makeMovement(self, **kw):
    """Creates a movement.
    """
    mvt = self.folder.newContent(portal_type='Dummy Movement')
    kw.setdefault('destination_section_value', self.section)
    kw.setdefault('source_section_value', self.mirror_section)
    kw.setdefault('destination_value', self.node)
    kw.setdefault('source_value', self.mirror_node)
    kw.setdefault('resource_value', self.resource)
    mvt.edit(**kw)
    get_transaction().commit()
    self.tic()
    return mvt

# }}}

class TestInventory(InventoryAPITestCase):
  """Tests getInventory methods.
  """
  RUN_ALL_TESTS = 1
  
  def testReturnedTypeIsList(self):
    """getInventory returns a float"""
    # XXX it may return a Decimal some day
    getInventory = self.getSimulationTool().getInventory
    self.assertEquals(type(getInventory()), type(0.1))
    # default is 0
    self.assertEquals(0, getInventory())

  def test_SectionCategory(self, quiet=0, run=RUN_ALL_TESTS):
    """Tests inventory on section category. """
    getInventory = self.getSimulationTool().getInventory
    self.section.setGroup('level1/level2')
    self._makeMovement(quantity=100)
    self.assertEquals(getInventory(
                        section_category='group/level1'), 100)
    self.assertEquals(getInventory(
                        section_category='group/level1/level2'), 100)
    self.assertEquals(getInventory(
                        section_category='group/anotherlevel'), 0)
    
    # section category can be a list
    self.assertEquals(getInventory(
            section_category=['group/anotherlevel', 'group/level1']), 100)

    # strict_section_category only takes movement where section is strict
    # member of the category.
    self.assertEquals(getInventory(
                section_category_strict_membership=['group/level1']), 0)
    self.section.setGroup('level1')
    get_transaction().commit()
    self.tic()
    self.assertEquals(getInventory(
                section_category_strict_membership=['group/level1']), 100)
    
    # non existing values to section_category are not silently ignored, but
    # raises an exception
    self.assertRaises(ValueError,
                      getInventory,
                      section_category='group/notexists')

  def test_MirrorSectionCategory(self, quiet=0, run=RUN_ALL_TESTS):
    """Tests inventory on mirror section category. """
    getInventory = self.getSimulationTool().getInventory
    self.mirror_section.setGroup('level1/level2')
    self._makeMovement(quantity=100)
    self.assertEquals(getInventory(
                        mirror_section_category='group/level1'), 100)
    self.assertEquals(getInventory(
                        mirror_section_category='group/level1/level2'), 100)
    self.assertEquals(getInventory(
                        mirror_section_category='group/anotherlevel'), 0)
    
    # section category can be a list
    self.assertEquals(getInventory(
            mirror_section_category=['group/anotherlevel',
                                     'group/level1']), 100)

    # strict_section_category only takes movement where section is strict
    # member of the category.
    self.assertEquals(getInventory(
              mirror_section_category_strict_membership=['group/level1']), 0)
    self.mirror_section.setGroup('level1')
    get_transaction().commit()
    self.tic()
    self.assertEquals(getInventory(
            mirror_section_category_strict_membership=['group/level1']), 100)
    
    # non existing values to section_category are not silently ignored, but
    # raises an exception
    self.assertRaises(ValueError,
                      getInventory,
                      mirror_section_category='group/notexists')

  def test_NodeCategory(self, quiet=0, run=RUN_ALL_TESTS):
    """Tests inventory on node_category """
    getInventory = self.getSimulationTool().getInventory
    self.node.setGroup('level1/level2')
    self._makeMovement(quantity=100,
                       source_value=None)
    self.assertEquals(getInventory(
                        node_category='group/level1'), 100)
    self.assertEquals(getInventory(
                        node_category='group/level1/level2'), 100)
    self.assertEquals(getInventory(
                node_category_strict_membership=['group/level1']), 0)
    self.node.setGroup('level1')
    get_transaction().commit()
    self.tic()
    self.assertEquals(getInventory(
                node_category_strict_membership=['group/level1']), 100)
  
  def test_ResourceCategory(self, quiet=0, run=RUN_ALL_TESTS):
    """Tests inventory on resource_category """
    getInventory = self.getSimulationTool().getInventory
    self.resource.setProductLine('level1/level2')
    self._makeMovement(quantity=100,
                       source_value=None)
    self.assertEquals(getInventory(
                        resource_category='product_line/level1'), 100)
    self.assertEquals(getInventory(
                        resource_category='product_line/level1/level2'), 100)
    self.assertEquals(getInventory(
                resource_category_strict_membership=['product_line/level1']), 0)
    self.resource.setProductLine('level1')
    get_transaction().commit()
    self.tic()
    self.assertEquals(getInventory(
            resource_category_strict_membership=['product_line/level1']), 100)

  def test_PaymentCategory(self, quiet=0, run=RUN_ALL_TESTS):
    """Tests inventory on payment_category """
    getInventory = self.getSimulationTool().getInventory
    # for now, BankAccount have a product_line category, so we can use this for
    # our category membership tests.
    self.payment_node.setProductLine('level1/level2')
    self._makeMovement(quantity=100,
                       destination_payment_value=self.payment_node,
                       source_value=None)
    self.assertEquals(getInventory(
                        payment_category='product_line/level1'), 100)
    self.assertEquals(getInventory(
                        payment_category='product_line/level1/level2'), 100)
    self.assertEquals(getInventory(
                payment_category_strict_membership=['product_line/level1']), 0)
    self.payment_node.setProductLine('level1')
    get_transaction().commit()
    self.tic()
    self.assertEquals(getInventory(
              payment_category_strict_membership=['product_line/level1']), 100)

  def test_SimulationState(self, quiet=0, run=RUN_ALL_TESTS):
    """Tests inventory on simulation state. """
    getInventory = self.getSimulationTool().getInventory
    self.payment_node.setProductLine('level1/level2')
    self._makeMovement(quantity=100,
                       simulation_state='confirmed',
                       source_value=None)
    self.assertEquals(getInventory(), 100)
    self.assertEquals(getInventory(simulation_state='confirmed'), 100)
    self.assertEquals(getInventory(simulation_state='planned'), 0)

    self.assertEquals(getInventory(simulation_state=['planned',
                                                     'confirmed']), 100)

  def test_MultipleNodes(self, quiet=0, run=RUN_ALL_TESTS):
    """Test section category with many nodes. """
    test_group = self.getCategoryTool().resolveCategory('group/test_group')
    self.assertNotEquals(len(test_group.objectValues()), 0)
    # we first create a section for each group category
    quantity_for_node = {}
    for category in test_group.getCategoryChildValueList():
      # we create a member node for each category
      node = self._makeOrganisation(group_value=category)
      # we create a movement to each node
      quantity = random.randint(100, 1000)
      self._makeMovement(quantity=quantity,
                         destination_section_value=node,
                         destination_value=node)
      # and record for later
      quantity_for_node[node] = quantity

    getInventory = self.getSimulationTool().getInventory
    for category in test_group.getCategoryChildValueList():
      node_list = category.getGroupRelatedValueList(portal_type='Organisation')
      self.assertNotEquals(len(node_list), 0)

      # getInventory on node uid for all member of a category ...
      total_quantity = sum([quantity_for_node[node] for node in node_list])
      self.assertEquals(getInventory(
        node_uid=[node.getUid() for node in node_list]), total_quantity)
      # ... is equivalent to node_category
      self.assertEquals(getInventory(
        node_category=category.getRelativeUrl()), total_quantity)
  
  # FIXME: this test is currently broken
  def TODO_test_DoubleSectionCategory(self, quiet=0, run=RUN_ALL_TESTS):
    """Tests inventory on section category, when the section is twice member\
    of the same category like it happens for group and mapping"""
    getInventory = self.getSimulationTool().getInventory
    self.section.setGroup('level1/level2')
    self.section.setMapping('group/level1/level2')
    self._makeMovement(quantity=100)
    # We are twice member of the section_category, but the quantity should not
    # change.
    self.assertEquals(getInventory(
                        section_category='group/level1'), 100)
    self.assertEquals(getInventory(
                        section_category='group/level1/level2'), 100)
    self.assertEquals(getInventory(
            section_category_strict_membership=['group/level1/level2']), 100)

  def test_NoSection(self, quiet=0, run=RUN_ALL_TESTS):
    """Tests inventory on section category / section uid, when the section is\
    empty."""
    getInventory = self.getSimulationTool().getInventory
    self.section.setGroup('level1/level2')
    self._makeMovement(quantity=100, source_section_value=None)
    self.assertEquals(getInventory(
                        section_category='group/level1/level2'), 100)
    self.assertEquals(getInventory(
            section_category_strict_membership=['group/level1/level2']), 100)
    self.assertEquals(getInventory(
                        section_uid=self.section.getUid()), 100)
  

class TestInventoryList(InventoryAPITestCase):
  """Tests getInventoryList methods.
  """
  RUN_ALL_TESTS = 1


class TestMovementHistoryList(InventoryAPITestCase):
  """Tests Movement history list methods.
  """
  RUN_ALL_TESTS = 1
  
  def testReturnedTypeIsList(self):
    """Movement History List returns a sequence object""" 
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    mvt_history_list = getMovementHistoryList()
    self.failUnless(str(mvt_history_list.__class__),
                    'Shared.DC.ZRDB.Results.Results')
    # default is an empty list
    self.assertEquals(0, len(mvt_history_list))
  
  def testMovementBothSides(self):
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    self._makeMovement(quantity=100)
    # we don't filter, so we have the same movement from both sides.
    self.assertEquals(2, len(getMovementHistoryList()))

  def testBrainClass(self):
    """Movement History List uses InventoryListBrain for brains""" 
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    self._makeMovement(quantity=100)
    # maybe this check is too low level (Shared/DC/ZRDB//Results.py, class r) 
    r_bases = getMovementHistoryList()._class.__bases__
    brain_class = r_bases[2].__name__
    self.assertEquals('InventoryListBrain', brain_class,
      "unexpected brain class for getMovementHistoryList InventoryListBrain"
      " != %s (bases %s)" % (brain_class, r_bases))
  
  def testSection(self):
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    mvt = self._makeMovement(quantity=100)
    mvt_history_list = getMovementHistoryList(
                            section_uid = self.section.getUid())
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(mvt.getUid(), mvt_history_list[0].uid)
    self.assertEquals(100, mvt_history_list[0].total_quantity)
    self.assertEquals(self.section.getRelativeUrl(),
                  mvt_history_list[0].section_relative_url)
  
  def testMirrorSection(self):
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    mvt = self._makeMovement(quantity=100)
    mvt_history_list = getMovementHistoryList(
                            mirror_section_uid = self.section.getUid())
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(mvt.getUid(), mvt_history_list[0].uid)
    self.assertEquals(-100, mvt_history_list[0].total_quantity)
    self.assertEquals(self.mirror_section.getRelativeUrl(),
                  mvt_history_list[0].section_relative_url)
    self.assertEquals(self.mirror_node.getRelativeUrl(),
                  mvt_history_list[0].node_relative_url)
    
    # if we look from the other side, everything is reverted
    mvt_history_list = getMovementHistoryList(
                            section_uid = self.section.getUid())
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(100, mvt_history_list[0].total_quantity)
    self.assertEquals(self.section.getRelativeUrl(),
                  mvt_history_list[0].section_relative_url)
    self.assertEquals(self.node.getRelativeUrl(),
                  mvt_history_list[0].node_relative_url)
  
  def testDifferentDatesPerSection(self):
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    start_date = DateTime(2001, 1, 1)
    stop_date = DateTime(2002, 2, 2)
    mvt = self._makeMovement(quantity=100,
                             start_date=start_date,
                             stop_date=stop_date)
    # start_date is for source
    self.assertEquals(start_date, getMovementHistoryList(
                            section_uid=self.mirror_section.getUid())[0].date)
    # stop_date is for destination
    self.assertEquals(stop_date, getMovementHistoryList(
                            section_uid=self.section.getUid())[0].date)
    
  def testNode(self):
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    mvt = self._makeMovement(quantity=100)
    mvt_history_list = getMovementHistoryList(
                            node_uid = self.node.getUid())
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(mvt.getUid(), mvt_history_list[0].uid)
    self.assertEquals(100, mvt_history_list[0].total_quantity)

  def testMirrorNode(self):
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    mvt = self._makeMovement(quantity=100)
    mvt_history_list = getMovementHistoryList(
                            mirror_node_uid = self.node.getUid())
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(mvt.getUid(), mvt_history_list[0].uid)
    self.assertEquals(-100, mvt_history_list[0].total_quantity)

  def testResource(self):
    getMovementHistoryList = self.getSimulationTool().getMovementHistoryList
    mvt = self._makeMovement(quantity=100)
    another_resource = self._makeResource()
    another_mvt = self._makeMovement(quantity=3,
                                     resource_value=another_resource)
    # we can query resource directly by uid
    mvt_history_list = getMovementHistoryList(
                            node_uid=self.node.getUid(),
                            resource_uid=self.resource.getUid())
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(100, mvt_history_list[0].total_quantity)
    # getMovementHistoryList should return only movement for
    mvt_history_list = getMovementHistoryList(
                            node_uid=self.node.getUid(),
                            resource_uid=another_resource.getUid())
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(3, mvt_history_list[0].total_quantity)

    # wrong value yields an empty list
    self.assertEquals(0, len(getMovementHistoryList(
                            resource_uid = self.node.getUid())))
    

class TestInventoryStat(InventoryAPITestCase):
  """Tests Inventory Stat methods.
  """
  RUN_ALL_TESTS = 1

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInventory))
    suite.addTest(unittest.makeSuite(TestInventoryList))
    suite.addTest(unittest.makeSuite(TestMovementHistoryList))
    suite.addTest(unittest.makeSuite(TestInventoryStat))
    return suite

# vim: foldmethod=marker
