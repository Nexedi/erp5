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
from App.config import getConfiguration
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList

class TestBusinessTemplate(ERP5TypeTestCase):
  """
    Test these operations:

    - Create a template

    - Install a template

    - Uninstall a template

    - Upgrade a template
  """
  run_all_test = 1
  business_template_title = 'erp5_pdm'
  
  def getTitle(self):
    return "Business Template"

  def getBusinessTemplateList(self):
    """
    Install erp5_pdm in order to make some test on it.
    """
    return (self.business_template_title, )

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def stepTic(self,**kw):
    self.tic()

  def test_01_checkTools(self, quiet=0, run=run_all_test):
    if not run: return
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
    self.assertEquals(core.getBuildingState(), 'built')
    self.assertEquals(core.getInstallationState(), 'installed')
    
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

  def test_02_makeTemplate(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Make Template'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    self.makeObjects()

    pt = self.getTemplateTool()
    template = pt.newContent(portal_type = 'Business Template')
    self.failUnless(template.getBuildingState() == 'draft')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.edit(title='geek template',
                  template_portal_type_id_list = ['Geek Module', 'Geek'],
                  template_skin_id_list = ['local_geek'],
                  template_module_id_list = ['geek'],
                  template_base_category_list = ['geek'],
                  template_workflow_id_list = ['geek_workflow'])
    self.failUnless(template.getBuildingState() == 'modified')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.build()
    self.failUnless(template.getBuildingState() == 'built')
    self.failUnless(template.getInstallationState() == 'not_installed')
    # export Business Template
    cfg = getConfiguration()
    template_path = os.path.join(cfg.instancehome, 'tests', '%s' % (template.getTitle(),))
    template.export(path=template_path, local=1)

    self.removeObjects()
    
    # import and install Business Template
    pt.download(url='file:'+template_path, id='template_test')
    template = pt._getOb(id='template_test')  
    template.install()
    self.assertEquals(template.getBuildingState(), 'built')
    self.assertEquals(template.getInstallationState(), 'installed')

    # FIXME: check installed objects here
    
    template.uninstall()
    self.assertEquals(template.getBuildingState(), 'built')
    self.assertEquals(template.getInstallationState(), 'not_installed')

    # FIXME: check uninstalled objects here

  def stepGetCurrentBusinessTemplate(self, sequence=None, 
                                     sequence_list=None, **kw):
    """
      Get current business template.
    """
    template_tool = self.getTemplateTool()
    current_bt_sql = template_tool.searchFolder(
                              title=self.business_template_title)
    self.failUnless(len(current_bt_sql) == 1)
    current_bt = current_bt_sql[0].getObject()
    sequence.edit(current_bt=current_bt)

  def stepCopyBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
      Copy business template.
    """
    current_bt = sequence.get('current_bt')
    template_tool = self.getTemplateTool()
    copy_data = template_tool.manage_copyObjects(ids=[current_bt.getId()])
    new_id_list = template_tool.manage_pasteObjects(copy_data)
    self.failUnless(len(new_id_list) == 1)
    new_bt = getattr(template_tool, new_id_list[0]['new_id'])
    sequence.edit(new_bt=new_bt)

  def stepCreateNewBaseCategory(self, sequence=None, sequence_list=None, **kw):
    """
      Create new base category.
    """
    category_tool = self.getCategoryTool()
    new_base_category_id = "fake_base_category"
    new_base_category = category_tool.newContent(portal_type="Base Category",
                                                 id=new_base_category_id)
    sequence.edit(new_base_category=new_base_category)

  def stepEditNewBT(self, sequence=None, sequence_list=None, **kw):
    """
    Simply edit, in order to change the building status.
    """
    new_bt = sequence.get('new_bt')
    new_bt.edit()

  def stepAddNewBaseCategoryToNewBT(self, sequence=None, 
                                    sequence_list=None, **kw):
    """
    Add the base category to the business template.
    """
    new_bt = sequence.get('new_bt')
    new_base_category = sequence.get('new_base_category')
    base_category_id_list = list(new_bt.getTemplateBaseCategoryList())
    base_category_id_list.append(new_base_category.getId())
    new_bt.edit(template_base_category_list=base_category_id_list)

  def stepCheckModifiedBuildingState(self, sequence=None, 
                                     sequence_list=None, **kw):
    """
    Check if the building state is modified.
    """
    new_bt = sequence.get('new_bt')
    self.assertEquals(new_bt.getBuildingState(), 'modified')

  def stepCheckBuiltBuildingState(self, sequence=None, 
                                  sequence_list=None, **kw):
    """
    Check if the building state is built.
    """
    new_bt = sequence.get('new_bt')
    self.assertEquals(new_bt.getBuildingState(), 'built')

  def stepBuildNewBT(self, sequence=None, sequence_list=None, **kw):
    """
    Build the business template.
    """
    new_bt = sequence.get('new_bt')
    new_bt.build()

  def stepExportNewBT(self, sequence=None, sequence_list=None, **kw):
    """
    Export the business template.
    """
    new_bt = sequence.get('new_bt')
    cfg = getConfiguration()
    template_path = os.path.join(cfg.instancehome, 
                                 'tests', '%s' % (new_bt.getTitle(),))
    sequence.edit(template_path=template_path)
    new_bt.export(path=template_path, local=1)

  def stepImportNewBT(self, sequence=None, sequence_list=None, **kw):
    """
    Import the business template.
    """
    template_tool = self.getTemplateTool()

    template_path = sequence.get('template_path')
    template_tool.download(url='file:'+template_path, id='import_bt')
    import_bt = template_tool._getOb(id='import_bt')
    self.assertEquals(import_bt.getPortalType(), 'Business Template')
    sequence.edit(new_bt=import_bt)

  def stepInstallNewBT(self, sequence=None, sequence_list=None, **kw):
    """
    Build the business template.
    """
    new_bt = sequence.get('new_bt')
    new_bt.install()
#     try:
#       new_bt.install()
#     except:
#       import pdb; pdb.set_trace()
#       pass
#       raise

  def test_03_update(self, quiet=0, run=run_all_test):
    """
      Test to update a business template
    """
    if not run: return
    if not quiet:
      message = 'Test Update Template'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    # Copy 
    # Except after creating organisations
    sequence_string = '\
                      GetCurrentBusinessTemplate \
                      CopyBusinessTemplate \
                      Tic \
                      InstallNewBT \
                      '
#     sequence_string = '\
#                       GetCurrentBusinessTemplate \
#                       CopyBusinessTemplate \
#                       EditNewBT \
#                       BuildNewBT \
#                       CheckBuiltBuildingState \
#                       ExportNewBT \
#                       ImportNewBT \
#                       Tic \
#                       InstallNewBT \
#                       '
#     sequence_string = '\
#                       GetCurrentBusinessTemplate \
#                       CopyBusinessTemplate \
#                       CreateNewBaseCategory \
#                       AddNewBaseCategoryToNewBT \
#                       CheckModifiedBuildingState \
#                       BuildNewBT \
#                       CheckBuiltBuildingState \
#                       ExportNewBT \
#                       ImportNewBT \
#                       Tic \
#                       InstallNewBT \
#                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestBusinessTemplate))
        return suite
