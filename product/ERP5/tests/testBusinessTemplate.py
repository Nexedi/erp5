##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Yoshinori Okuji <yo@nexedi.com>
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



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
import time
import os
from Products.ERP5Type import product_path
from DateTime import DateTime

class TestBusinessTemplate(ERP5TypeTestCase):
  """
    Test these operations:

    - Create a template

    - Install a template

    - Uninstall a template

    - Upgrade a template
  """

  def test_01_checkTools(self, quiet=0):
    if not quiet:
      message = 'Test Check Tools'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    self.failUnless(self.getCategoryTool() is not None)
    self.failUnless(self.getTemplateTool() is not None)
    self.failUnless(self.getTypeTool() is not None)
    self.failUnless(self.getSkinsTool() is not None)
    self.failUnless(self.getCatalogTool() is not None)
    
  def test_02_checkERP5Core(self, quiet=0):
    if not quiet:
      message = 'Test Check ERP5 Core'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    pt = self.getTemplateTool()
    core = None
    for bt in pt.objectValues(filter={'portal_type':'Business Template'}):
      if bt.getTitle() == 'erp5_core':
        core = bt
    self.failUnless(core is not None)
    self.failUnless(core.getBuildingState() == 'built')
    self.failUnless(core.getInstallationState() == 'installed')
    
  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    catalog_tool = self.getCatalogTool()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def makeObjects(self):
    """
      Make objects to create a template.
    """
    # Make types.
    pt = self.getTypeTool()
    pt.manage_addTypeInformation(ERP5TypeInformation.meta_type, id='Geek Module', typeinfo_name='ERP5Type: ERP5 Folder')
    module_type = pt._getOb('Geek Module', None)
    self.failUnless(module_type is not None)
    pt.manage_addTypeInformation(ERP5TypeInformation.meta_type, id='Geek', typeinfo_name='ERP5Type: ERP5 Person')
    object_type = pt._getOb('Geek', None)
    self.failUnless(object_type is not None)
    module_type.allowed_content_types = ('Geek',)

    # Make skin folders.
    ps = self.getSkinsTool()
    ps.manage_addProduct['OFSP'].manage_addFolder('local_geek')
    skin_folder = ps._getOb('local_geek', None)
    self.failUnless(skin_folder is not None)
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      if 'local_geek' not in selection:
        selection.append('local_geek')
      ps.manage_skinLayers(skinpath = tuple(selection), skinname = skin_name, add_skin = 1)

    # Make modules.
    portal = self.getPortal()
    module = portal.newContent(id = 'geek', portal_type = 'Geek Module')
    self.failUnless(module is not None)
    object = module.newContent(id = '1', portal_type = 'Geek')
    self.failUnless(object is not None)

    # Make categories.
    pc = self.getCategoryTool()
    base_category = pc.newContent(portal_type = 'Base Category', id = 'geek')
    self.failUnless(base_category is not None)
    category = base_category.newContent(portal_type = 'Category', id = 'computer')
    self.failUnless(category is not None)
    category = base_category.newContent(portal_type = 'Category', id = 'manga')
    self.failUnless(category is not None)
    category = base_category.newContent(portal_type = 'Category', id = 'game')
    self.failUnless(category is not None)

    # Make workflows.
    pw = self.getWorkflowTool()
    pw.manage_addWorkflow('dc_workflow (Web-configurable workflow)', 'geek_workflow')
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        props['chain_%s' % id] = ','.join(wf_ids)
    props['chain_geek'] = 'geek_workflow'
    pw.manage_changeWorkflows('', props=props)

    # FIXME: more objects must be created.

  def removeObjects(self):
    """
      Remove objects created by makeObjects.
    """
    # Remove types.
    pt = self.getTypeTool()
    pt.manage_delObjects(['Geek Module', 'Geek'])
    module_type = pt._getOb('Geek Module', None)
    self.failUnless(module_type is None)
    object_type = pt._getOb('Geek', None)
    self.failUnless(object_type is None)

    # Remove skin folders.
    ps = self.getSkinsTool()
    ps.manage_delObjects(['local_geek'])
    skin_folder = ps._getOb('local_geek', None)
    self.failUnless(skin_folder is None)
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      if 'local_geek' in selection:
        selection.remove('local_geek')
      ps.manage_skinLayers(skinpath = tuple(selection), skinname = skin_name, add_skin = 1)

    # Remove modules.
    portal = self.getPortal()
    portal.manage_delObjects(['geek'])
    module = portal._getOb('geek', None)
    self.failUnless(module is None)

    # Remove categories.
    pc = self.getCategoryTool()
    pc.manage_delObjects(['geek'])
    base_category = pc._getOb('geek', None)
    self.failUnless(base_category is None)

    # Make workflows.
    pw = self.getWorkflowTool()
    pw.manage_delObjects(['geek_workflow'])

    # FIXME: more objects must be removed.

  def test_02_makeTemplate(self, quiet=0):
    if not quiet:
      message = 'Test Make Template'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    self.makeObjects()

    pt = self.getTemplateTool()
    template = pt.newContent(portal_type = 'Business Template')
    self.failUnless(template.getBuildingState() == 'draft')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.edit(template_portal_type_id_list = ['Geek Module', 'Geek'],
                  template_skin_id_list = ['local_geek'],
                  template_module_id_list = ['geek'],
                  template_base_category_list = ['geek'],
                  template_workflow_id_list = ['geek_workflow'])
    self.failUnless(template.getBuildingState() == 'modified')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.build()
    self.failUnless(template.getBuildingState() == 'built')
    self.failUnless(template.getInstallationState() == 'not_installed')

    self.removeObjects()

    template.install()
    self.failUnless(template.getBuildingState() == 'built')
    self.failUnless(template.getInstallationState() == 'installed')

    # FIXME: check installed objects here
    
    template.uninstall()
    self.failUnless(template.getBuildingState() == 'built')
    self.failUnless(template.getInstallationState() == 'not_installed')

    # FIXME: check uninstalled objects here


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestBusinessTemplate))
        return suite

