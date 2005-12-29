##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
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

from random import randint

import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_base
from zLOG import LOG
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from App.config import getConfiguration
from Products.ERP5Type.tests.Sequence import SequenceList
from urllib import pathname2url
from Globals import PersistentMapping
from Products.CMFCore.Expression import Expression
import os

class TestBusinessTemplate(ERP5TypeTestCase):
  """
    Test these operations:

    - Create a template

    - Install a template

    - Uninstall a template

    - Upgrade a template
  """
  run_all_test = 1
  
  def getTitle(self):
    return "Business Template"

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    catalog_tool = self.getCatalogTool()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def stepTic(self,**kw):
    self.tic()

  def stepCommitTransaction(self, **kw):
    get_transaction().commit()

  def stepUseCoreBusinessTemplate(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Define erp5_core as current bt
    """
    template_tool = self.getTemplateTool()
    core_bt = None
    for bt in template_tool.objectValues(filter={'portal_type':'Business Template'}):
      if bt.getTitle() == 'erp5_core':
        core_bt = bt
        break
    self.failIf(core_bt is None)
    sequence.edit(current_bt=core_bt)


  def stepCopyCoreBusinessTemplate(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Copy erp5_core as new Business Template
    """
    template_tool = self.getTemplateTool()
    core_bt = None
    for bt in template_tool.objectValues(filter={'portal_type':'Business Template'}):
      if bt.getTitle() == 'erp5_core':
        core_bt = bt
        break
    self.failIf(core_bt is None)
    # make copy
    copy_data = template_tool.manage_copyObjects(ids=[core_bt.getId()])
    ids = template_tool.manage_pasteObjects(copy_data)
    LOG('id after copy', 0, ids)
    new_id = ids[0]['new_id']
    new_bt = template_tool._getOb(new_id)
    LOG(new_bt, 0, str((new_bt.getTitle(), new_id)))
    self.assertEqual(new_bt.getTitle(), 'erp5_core')
    sequence.edit(copy_bt=new_bt)

  def stepUseCopyCoreBusinessTemplate(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Define erp5_core as current bt
    """
    bt = sequence.get('copy_bt')
    sequence.edit(current_bt=bt, export_bt=bt)

  def stepUseExportBusinessTemplate(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Define export_bt as current bt
    """
    bt = sequence.get('export_bt')
    sequence.edit(current_bt=bt)

  def stepUseImportBusinessTemplate(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Define import_bt as current bt
    """
    bt = sequence.get('import_bt')
    sequence.edit(current_bt=bt)
    
  def stepCheckInstalledInstallationState(self, sequence=None,
                                        seqeunce_list=None, **kw):
    """
    Check if installation state is installed
    """
    bt = sequence.get('current_bt', None)
    self.assertEquals(bt.getInstallationState(), 'installed')

  def stepCheckNotInstalledInstallationState(self, sequence=None,
                                        seqeunce_list=None, **kw):
    """
    Check if installation state is not_installed
    """
    bt = sequence.get('current_bt')
    self.assertEquals(bt.getInstallationState(), 'not_installed')

  def stepCheckReplacedInstallationState(self, sequence=None,
                                        seqeunce_list=None, **kw):
    """
    Check if installation state is replaced
    """
    bt = sequence.get('current_bt')
    self.assertEquals(bt.getInstallationState(), 'replaced')

  def stepCheckModifiedBuildingState(self, sequence=None, 
                                     sequence_list=None, **kw):
    """
    Check if the building state is modified.
    """
    bt = sequence.get('current_bt')
    self.assertEquals(bt.getBuildingState(), 'modified')

  def stepCheckBuiltBuildingState(self, sequence=None, 
                                  sequence_list=None, **kw):
    """
    Check if the building state is built.
    """
    bt = sequence.get('current_bt')
    self.assertEquals(bt.getBuildingState(), 'built')

  def stepCheckTools(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of tools
    """
    self.failUnless(self.getCategoryTool() is not None)
    self.failUnless(self.getTemplateTool() is not None)
    self.failUnless(self.getTypeTool() is not None)
    self.failUnless(self.getSkinsTool() is not None)
    self.failUnless(self.getCatalogTool() is not None)
    self.failUnless(self.getTrashTool() is not None)    
    
  def stepCheckSkinsLayers(self, sequence=None, sequence_list=None, **kw):
    """
    Check skins layers
    """
    skins_tool = self.getSkinsTool()
    for skin_name, selection in skins_tool.getSkinPaths():
      if skin_name == 'View':
        self.failIf('erp5_pdf_style' in selection)
        self.failIf('erp5_csv_style' in selection)
        self.failIf('erp5_core' not in selection)
        self.failIf('erp5_html_style' not in selection)
      if skin_name == 'Print':
        self.failIf('erp5_html_style' in selection)
        self.failIf('erp5_csv_style' in selection)
        self.failIf('erp5_core' not in selection)
        self.failIf('erp5_pdf_style' not in selection)
      if skin_name == 'CSV':
        self.failIf('erp5_pdf_style' in selection)
        self.failIf('erp5_html_style' in selection)
        self.failIf('erp5_core' not in selection)
        self.failIf('erp5_csv_style' not in selection)

  def stepCheckNoTrashBin(self, sequence=None, sequence_list=None, **kw):
    """
    Check if there is no trash bins
    """
    trash = self.getTrashTool()
    self.assertEquals(len(trash.objectIds()), 0)

  def stepRemoveAllTrashBins(self, sequence=None, sequence_list=None, **kw):
    """
    Remove all trash bins
    """
    trash = self.getTrashTool()
    trash_ids = list(trash.objectIds())
    for id in trash_ids:
      trash.deleteContent(id)
    self.failIf(len(trash.objectIds()) > 0)

  def stepCheckTrashBin(self, sequence=None, sequence_list=None, **kw):
    """
    Check trash bin presence
    """
    trash = self.getTrashTool()
    trash_ids = list(trash.objectIds())
    self.assertEquals(len(trash.objectIds()), 1)
    bt_id = sequence.get('import_bt').getId()
    self.failUnless(bt_id not in trash_ids[0])

  # portal types
  def stepCreatePortalType(self, sequence=None, sequence_list=None, **kw):
    """
    Create Portal Type
    """
    pt = self.getTypeTool()
    # create module object portal type
    pt.manage_addTypeInformation(ERP5TypeInformation.meta_type, id='Geek Object', typeinfo_name='ERP5Type: ERP5 Person')
    object_type = pt._getOb('Geek Object', None)
    self.failUnless(object_type is not None)
    sequence.edit(object_ptype_id=object_type.getId())
    # create module portal type
    pt.manage_addTypeInformation(ERP5TypeInformation.meta_type, id='Geek Module', typeinfo_name='ERP5Type: ERP5 Folder')
    module_type = pt._getOb('Geek Module', None)
    self.failUnless(module_type is not None)
    module_type.filter_content_types = 1
    module_type.allowed_content_types = ('Geek Object',)
    sequence.edit(module_ptype_id=module_type.getId())

  def stepAddPortalTypeToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add types to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    ptype_ids = []
    ptype_ids.append(sequence.get('object_ptype_id', ''))
    ptype_ids.append(sequence.get('module_ptype_id', ''))
    self.assertEqual(len(ptype_ids), 2)    
    bt.edit(template_portal_type_id_list=ptype_ids)
    self.stepFillPortalTypesFields(sequence=sequence, sequence_list=sequence_list, **kw)
    
  def stepRemovePortalType(self, sequence=None, sequence_list=None, **kw):
    """
    Remove PortalType    
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    pt.manage_delObjects([module_id, object_id])
    module_type = pt._getOb(module_id, None)
    self.failUnless(module_type is None)
    object_type = pt._getOb(object_id, None)
    self.failUnless(object_type is None)

  def stepCheckPortalTypeExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of portal type
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    module_type = pt._getOb(module_id, None)
    self.failUnless(module_type is not None)
    object_type = pt._getOb(object_id, None)
    self.failUnless(object_type is not None)
    
  def stepCheckPortalTypeRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non presence of portal type
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    module_type = pt._getOb(module_id, None)
    self.failUnless(module_type is None)
    object_type = pt._getOb(object_id, None)
    self.failUnless(object_type is None)

  def stepFillPortalTypesFields(self, sequence=None, sequence_list=None, **kw):
    """
    Fill portal types properties field in business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    bt.getPortalTypesProperties()
    LOG("portal types properties added for", 0, bt.getTitle())

  # module
  def stepCreateModuleAndObjects(self, sequence=None, sequence_list=None, **kw):
    """
    Create Module with objects
    """
    portal = self.getPortal()
    id = 'geek_module'
    n = 0
    while id in portal.objectIds():
      n = n + 1
      id = "%s_%s" %('geek_module', n)      
    module = portal.newContent(id=id, portal_type='Geek Module')
    self.failUnless(module is not None)
    sequence.edit(module_id=module.getId())
    module_object_list = []
    for i in xrange(10):
      object = module.newContent(portal_type = 'Geek Object')
      self.failUnless(object is not None)
      module_object_list.append(object)
    sequence.edit(module_object_id_list=module_object_list)

  def stepAddModuleToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add module to business template
    """
    bt = sequence.get('current_bt', None)
    module_id = sequence.get('module_id', None)
    self.failUnless(module_id is not None)
    bt.edit(template_module_id_list=[module_id])

  def stepCreateModuleObjects(self, sequence=None, sequence_list=None, **kw):
    """
    Create objects into module
    """
    portal = self.getPortal()    
    module_id = sequence.get('module_id')
    module = portal._getOb(module_id, None)
    self.failUnless(module is not None)
    module_object_list = []
    for i in xrange(10):
      object = module.newContent(portal_type = 'Geek Object')
      self.failUnless(object is not None)
      module_object_list.append(object.getId())
    sequence.edit(module_object_id_list=module_object_list)    

  def stepRemoveModule(self, sequence=None, sequence_list=None, **kw):
    """
    Remove Module
    """
    portal = self.getPortal()
    module_id = sequence.get("module_id")
    portal.manage_delObjects([module_id])
    self.failIf(portal._getOb(module_id, None) is not None)

  def stepCheckModuleExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of module
    """
    portal = self.getPortal()
    module_id = sequence.get("module_id")
    new_module = portal._getOb(module_id, None)
    self.failIf(new_module is None)

  def stepCheckModuleObjectsExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of objects in module
    """
    portal = self.getPortal()
    module_id = sequence.get('module_id')
    module = portal._getOb(module_id)
    self.failUnless(module is not None)
    object_id_list = sequence.get('module_object_id_list')
    for object_id in object_id_list:
      object = module._getOb(object_id, None)
      self.failUnless(object is not None)

  def stepCheckModuleObjectsRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non presence of objects in module
    """
    portal = self.getPortal()
    module_id = sequence.get('module_id')
    module = portal._getOb(module_id)
    self.failUnless(module is not None)
    object_id_list = sequence.get('module_object_id_list')
    for object_id in object_id_list:
      object = module._getOb(object_id, None)
      self.failUnless(object is None)
      
  def stepCheckModuleRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non presence of module
    """
    portal = self.getPortal()
    module_id = sequence.get("module_id")
    self.failIf(portal._getOb(module_id, None) is not None)    

  # skins folder
  def stepCreateSkinFolder(self, sequence=None, sequence_list=None, **kw):
    """
    Create a skin folder
    """
    ps = self.getSkinsTool()
    ps.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = ps._getOb('erp5_geek', None)
    self.failUnless(skin_folder is not None)
    sequence.edit(skin_folder_id=skin_folder.getId())
    # add skin in layers
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      if 'erp5_geek' not in selection:
        selection.append('erp5_geek')
      ps.manage_skinLayers(skinpath = tuple(selection), skinname = skin_name, add_skin = 1)

  def stepRemoveSkinFolder(self, sequence=None, sequence_list=None, **kw):
    """
    Remove Skin folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    ps.manage_delObjects([skin_id])
    skin_folder = ps._getOb(skin_id, None)
    self.failUnless(skin_folder is None)
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      if skin_id in selection:
        selection.remove(skin_id)
      ps.manage_skinLayers(skinpath = tuple(selection), skinname = skin_name, add_skin = 1)

  def stepCheckSkinFolderExists(self, sequence=None,sequence_list=None, **kw):
    """
    Check presence of skin folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    self.failUnless(skin_folder is not None)    

  def stepCheckSkinFolderRemoved(self, sequence=None,sequence_list=None, **kw):
    """
    Check non presence of skin folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    self.failUnless(skin_folder is None)

  def stepAddSkinFolderToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add sin folder to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    wf_ids = []
    wf_ids.append(sequence.get('skin_folder_id', ''))
    self.assertEqual(len(wf_ids), 1)
    bt.edit(template_skin_id_list=wf_ids)

  # Base Category
  def stepCreateBaseCategory(self, sequence=None, sequence_list=None, **kw):
    """
    Create Base category
    """
    pc = self.getCategoryTool()
    base_category = pc.newContent(portal_type = 'Base Category')
    self.failUnless(base_category is not None)
    sequence.edit(bc_id=base_category.getId())

  def stepAddBaseCategoryToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Base category to Business template
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    bt.edit(template_base_category_list=[bc_id])

  def stepAddBaseCategoryAsPathToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Base category to Business template
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    path = 'portal_categories/'+bc_id
    bt.edit(template_path_list=[path])

  def stepRemoveBaseCategory(self, sequence=None, sequence_list=None, **kw):
    """
    Remove Base category
    """
    pc = self.getCategoryTool()
    bc_id = sequence.get('bc_id')
    pc.manage_delObjects([bc_id])
    base_category = pc._getOb(bc_id, None)
    self.failUnless(base_category is None)    

  def stepCheckBaseCategoryExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of Base category
    """
    pc = self.getCategoryTool()
    bc_id = sequence.get('bc_id')
    base_category = pc._getOb(bc_id, None)
    self.failUnless(base_category is not None)    

  def stepCheckBaseCategoryRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non presence of Base category
    """
    pc = self.getCategoryTool()
    bc_id = sequence.get('bc_id')
    base_category = pc._getOb(bc_id, None)
    LOG('base category is', 0, base_category)
    self.failUnless(base_category is None)    

  # categories
  def stepCreateCategories(self, sequence=None, sequence_list=None, **kw):
    """
    Create categories into a base category
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)    
    self.failUnless(base_category is not None)
    category_list = []
    for i in xrange(10):
      category = base_category.newContent(portal_type='Category')
      self.failUnless(category is not None)
      category_list.append(category.getId())
    sequence.edit(category_id_list=category_list)

  def stepAddCategoriesAsPathToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Categories in path with the joker *
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    path = 'portal_categories/'+bc_id+'/*'
    bt.edit(template_path_list=[path])

  def stepCheckCategoriesExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of categories
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.failUnless(base_category is not None)
    category_id_list = sequence.get('category_id_list')
    for category_id in category_id_list:
      category = base_category._getOb(category_id, None)
      self.failUnless(category is not None)

  def stepCheckCategoriesRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non-presence of categories
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.failUnless(base_category is not None)
    category_id_list = sequence.get('category_id_list')
    for category_id in category_id_list:
      category = base_category._getOb(category_id, None)
      self.failUnless(category is None)

  def stepRemoveCategories(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of categories
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.failUnless(base_category is not None)
    category_id_list = sequence.get('category_id_list')
    base_category.manage_delObjects(category_id_list)
    for category_id in category_id_list:
      category = base_category._getOb(category_id, None)
      self.failUnless(category is None)
      
  # sub categories
  def stepCreateSubCategories(self, sequence=None, sequence_list=None, **kw):
    """
    Add sub category to a category
    """
    pc = self.getCategoryTool()
    bc_id = sequence.get('bc_id')
    base_category = pc._getOb(bc_id, None)
    self.failUnless(base_category is not None)
    cat_id_list = sequence.get('category_id_list')
    # only use one category
    cat_id = cat_id_list[0]
    category = base_category._getOb(cat_id, None)
    self.failUnless(category is not None)
    subcategory_list = []
    for i in xrange(10):
      subcategory = category.newContent(portal_type='Category')
      self.failUnless(subcategory is not None)
      subcategory_list.append(subcategory.getId())
    sequence.edit(subcategory_id_list=subcategory_list, parent_category_id=category.getId())

  def stepAddSubCategoriesAsPathToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add All Categories in path with the joker **
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    path = 'portal_categories/'+bc_id+'/**'
    bt.edit(template_path_list=[path])
  
  def stepCheckSubCategoriesExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of categories
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.failUnless(base_category is not None)
    parent_category_id = sequence.get('parent_category_id')
    category = base_category._getOb(parent_category_id, None)
    self.failUnless(category is not None)
    subcategory_id_list = sequence.get('subcategory_id_list')
    for subcategory_id in subcategory_id_list:
      subcategory = category._getOb(subcategory_id, None)
      self.failUnless(subcategory is not None)
  
  # workflow
  def stepCreateWorkflow(self, sequence=None, sequence_list=None, **kw):
    """
    Create a workflow
    """
    pw = self.getWorkflowTool()
    pw.manage_addWorkflow('dc_workflow (Web-configurable workflow)', 'geek_workflow')
    workflow = pw._getOb('geek_workflow', None)
    self.failUnless(workflow is not None)
    sequence.edit(workflow_id=workflow.getId())
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        props['chain_%s' % id] = ','.join(wf_ids)
    props['chain_geek'] = 'geek_workflow'
    pw.manage_changeWorkflows('', props=props)

  def stepAddWorkflowToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add workflow to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    wf_ids = []
    wf_ids.append(sequence.get('workflow_id', ''))
    self.assertEqual(len(wf_ids), 1)
    bt.edit(template_workflow_id_list=wf_ids)
    
  def stepRemoveWorkflow(self, sequence=None, sequence_list=None, **kw):
    """
    Remove Workflow
    """
    wf_id = sequence.get('workflow_id')
    pw = self.getWorkflowTool()
    pw.manage_delObjects([wf_id])
    workflow = pw._getOb(wf_id, None)
    self.failUnless(workflow is None)

  def stepCheckWorkflowExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of Workflow
    """
    wf_id = sequence.get('workflow_id')
    pw = self.getWorkflowTool()
    workflow = pw._getOb(wf_id, None)
    self.failUnless(workflow is not None)

  def stepCheckWorkflowRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non presence of Workflow
    """
    wf_id = sequence.get('workflow_id')
    pw = self.getWorkflowTool()
    workflow = pw._getOb(wf_id, None)
    self.failUnless(workflow is None)

  # Actions
  def stepCreateAction(self, sequence=None, sequence_list=None, **kw):
    """
    Create action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    object_pt.addAction(
      id = 'become_geek'
      , name = 'Become Geek'
      , action = 'become_geek_action'
      , condition = ''
      , permission = ('View', )
      , category = 'object_action'
      , visible = 1
      , optional = 0
      , priority = 2.0 )
    sequence.edit(action_id='become_geek')

  def stepCreateOptionalAction(self, sequence=None, sequence_list=None, **kw):
    """
    Create optional action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    object_pt.addAction(
      id = 'become_nerd'
      , name = 'Become Nerd'
      , action = 'become_nerd_action'
      , condition = ''
      , permission = ('View', )
      , category = 'object_action'
      , visible = 1
      , optional = 1
      , priority = 1.5 )
    sequence.edit(opt_action_id='become_nerd')

  def stepCheckActionsOrder(self, sequence=None, sequence_list=None, **kw):
    """
    Check Actions Order
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    actions_list = object_pt.listActions()
    priority = 0
    for action in actions_list:
      self.failIf(action.priority < priority)
      priority = action.priority


  def stepCheckActionExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of action 
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('action_id')
    self.failUnless(action_id in [x.getId() for x in object_pt.listActions()])

  def stepCheckActionNotExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check non-presence of action 
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('action_id')
    self.failUnless(action_id not in [x.getId() for x in object_pt.listActions()])

  def stepCheckOptionalActionExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of optional action 
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('opt_action_id')
    self.failUnless(action_id in [x.getId() for x in object_pt.listActions()])

  def stepCheckOptionalActionNotExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check non-presence of optional action 
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('opt_action_id')
    self.failUnless(action_id not in [x.getId() for x in object_pt.listActions()])    

  def stepAddOptionalActionToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add optionpal action into the business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    opt_action_id = sequence.get('opt_action_id', None)
    self.failUnless(opt_action_id is not None)
    object_ptype_id = sequence.get('object_ptype_id', None)
    self.failUnless(object_ptype_id is not None)
    action_path = object_ptype_id+'[id='+opt_action_id+']'
    bt.edit(template_action_path_list=[action_path])

  # Catalog Method
  def stepCreateCatalogMethod(self, sequence=None, sequence_list=None, **kw):
    """
    Create ZSQL Method into catalog
    """
    pc = self.getCatalogTool()
    catalog = pc._getOb('erp5_mysql', None)
    self.failUnless(catalog is not None)
    method_id = "z_fake_method"
    addSQLMethod =catalog.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
    addSQLMethod(id=method_id,title='', connection_id='test test', arguments='', template='')
    zsql_method = catalog._getOb(method_id, None)  
    self.failUnless(zsql_method is not None)
    sequence.edit(zsql_method_id = method_id)
    # set this method in update_object properties of catalog
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_uncatalog_object.append(method_id)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    # set filter for this method
    expression = 'python: isMovement'
    expr_instance = Expression(expression)
    catalog.filter_dict[method_id] = PersistentMapping()
    catalog.filter_dict[method_id]['filtered'] = 1
    catalog.filter_dict[method_id]['expression'] = expression
    catalog.filter_dict[method_id]['expression_instance'] = expr_instance
    catalog.filter_dict[method_id]['type'] = []
    
  def stepAddCatalogMethodToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add catalog method into the business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    method_id = sequence.get('zsql_method_id', None)
    self.failUnless(method_id is not None)
    bt.edit(template_catalog_method_id_list=['erp5_mysql/'+method_id])

  def stepCheckCatalogMethodExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of ZSQL Method in catalog
    """
    pc = self.getCatalogTool()
    catalog = pc._getOb('erp5_mysql', None)
    self.failUnless(catalog is not None)
    method_id = sequence.get('zsql_method_id', None)
    zsql_method = catalog._getOb(method_id, None)  
    self.failUnless(zsql_method is not None)
    # check catalog properties
    self.failUnless(method_id in catalog.sql_uncatalog_object)
    # check filter
    self.failUnless(method_id in catalog.filter_dict.keys())
    filter_dict = catalog.filter_dict[method_id]
    self.assertEqual(filter_dict['filtered'], 1)
    self.assertEqual(filter_dict['expression'], 'python: isMovement')
    self.assertEqual(filter_dict['type'], [])

  def stepCheckCatalogMethodRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non-presence of ZSQL Method in catalog
    """
    pc = self.getCatalogTool()
    catalog = pc._getOb('erp5_mysql', None)
    self.failUnless(catalog is not None)
    method_id = sequence.get('zsql_method_id', None)
    zsql_method = catalog._getOb(method_id, None)  
    self.failUnless(zsql_method is None)
    # check catalog properties
    self.failUnless(method_id not in catalog.sql_uncatalog_object)
    # check filter
    self.failUnless(method_id not in catalog.filter_dict.keys())

    
  def stepRemoveCatalogMethod(self, sequence=None, sequence_list=None, **kw):
    """
    Remove ZSQL Method from catalog
    """
    pc = self.getCatalogTool()
    catalog = pc._getOb('erp5_mysql', None)
    self.failUnless(catalog is not None)
    method_id = sequence.get('zsql_method_id', None)
    catalog.manage_delObjects([method_id])
    zsql_method = catalog._getOb(method_id, None)
    self.failUnless(zsql_method is None)
    # remove catalog properties
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_uncatalog_object.remove(method_id)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    self.failUnless(method_id not in catalog.sql_uncatalog_object)
    # remove filter
    del catalog.filter_dict[method_id]
    self.failUnless(method_id not in catalog.filter_dict.keys())        

  # Related key, Result key and table, and others
  def stepCreateKeysAndTable(self, sequence=list, sequence_list=None, **kw):
    """
    Create some keys and tables
    """
    related_key = 'fake_id | category/catalog/z_fake_method'
    result_key = 'fake_catalog.uid'
    result_table = 'fake_catalog'
    keyword_key = 'fake_keyword'
    full_text_key = 'fake_full_text'
    request_key = 'fake_request'
    multivalue_key = 'fake_multivalue'
    topic_key = 'fake_topic'
    catalog = self.getCatalogTool().getSQLCatalog()
    self.failUnless(catalog is not None)
    LOG("catalog is", 0, catalog.getId())
    # result key
    sql_search_result_keys = list(catalog.sql_search_result_keys)
    sql_search_result_keys.append(result_key)
    sql_search_result_keys.sort()
    catalog.sql_search_result_keys = tuple(sql_search_result_keys)
    self.failUnless(result_key in catalog.sql_search_result_keys)
    # related key
    sql_search_related_keys = list(catalog.sql_catalog_related_keys)
    sql_search_related_keys.append(related_key)
    sql_search_related_keys.sort()
    catalog.sql_catalog_related_keys = tuple(sql_search_related_keys)
    self.failUnless(related_key in catalog.sql_catalog_related_keys)
    # result table
    sql_search_tables = list(catalog.sql_search_tables)
    sql_search_tables.append(result_table)
    sql_search_tables.sort()
    catalog.sql_search_tables = tuple(sql_search_tables)
    self.failUnless(result_table in catalog.sql_search_tables)
    # keyword keys
    sql_catalog_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
    sql_catalog_keyword_keys.append(keyword_key)
    sql_catalog_keyword_keys.sort()
    catalog.sql_catalog_keyword_search_keys = tuple(sql_catalog_keyword_keys)
    self.failUnless(keyword_key in catalog.sql_catalog_keyword_search_keys)
    # full_text keys
    sql_catalog_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
    sql_catalog_full_text_keys.append(full_text_key)
    sql_catalog_full_text_keys.sort()
    catalog.sql_catalog_full_text_search_keys = tuple(sql_catalog_full_text_keys)
    self.failUnless(full_text_key in catalog.sql_catalog_full_text_search_keys)
    # request
    sql_catalog_request_keys = list(catalog.sql_catalog_request_keys)
    sql_catalog_request_keys.append(request_key)
    sql_catalog_request_keys.sort()
    catalog.sql_catalog_request_keys = tuple(sql_catalog_request_keys)
    self.failUnless(request_key in catalog.sql_catalog_request_keys)
    # multivalue
    sql_catalog_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
    sql_catalog_multivalue_keys.append(multivalue_key)
    sql_catalog_multivalue_keys.sort()
    catalog.sql_catalog_multivalue_keys = tuple(sql_catalog_multivalue_keys)
    self.failUnless(multivalue_key in catalog.sql_catalog_multivalue_keys)
    # topic keys
    sql_catalog_topic_keys = list(catalog.sql_catalog_topic_search_keys)
    sql_catalog_topic_keys.append(topic_key)
    sql_catalog_topic_keys.sort()
    catalog.sql_catalog_topic_search_keys = tuple(sql_catalog_topic_keys)
    self.failUnless(topic_key in catalog.sql_catalog_topic_search_keys)

    sequence.edit(related_key=related_key, result_key=result_key, result_table=result_table, \
                  keyword_key=keyword_key, full_text_key=full_text_key, request_key=request_key, \
                  multivalue_key=multivalue_key, topic_key=topic_key)
    
  def stepAddKeysAndTableToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add some related, result key and tables to Business Temlpate
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    related_key = sequence.get('related_key', None)
    self.failUnless(related_key is not None)
    result_key = sequence.get('result_key', None)
    self.failUnless(result_key is not None)
    result_table = sequence.get('result_table', None)
    self.failUnless(result_table is not None)
    keyword_key = sequence.get('keyword_key', None)
    self.failUnless(keyword_key is not None)
    full_text_key = sequence.get('full_text_key', None)
    self.failUnless(full_text_key is not None)
    request_key = sequence.get('request_key', None)
    self.failUnless(request_key is not None)
    multivalue_key = sequence.get('multivalue_key', None)
    self.failUnless(multivalue_key is not None)
    topic_key = sequence.get('topic_key', None)
    self.failUnless(topic_key is not None)
    
    bt.edit(template_catalog_related_key_list=[related_key],
            template_catalog_result_key_list=[result_key],
            template_catalog_result_table_list=[result_table],
            template_catalog_keyword_key_list=[keyword_key],
            template_catalog_full_text_key_list=[full_text_key],
            template_catalog_request_key_list=[request_key],
            template_catalog_multivalue_key_list=[multivalue_key],
            template_catalog_topic_key_list=[topic_key],
            )

  def stepRemoveKeysAndTable(self, sequence=list, sequence_list=None, **kw):
    """
    Remove some keys and tables
    """
    related_key = sequence.get('related_key', None)
    self.failUnless(related_key is not None)
    result_key = sequence.get('result_key', None)
    self.failUnless(result_key is not None)
    result_table = sequence.get('result_table', None)
    self.failUnless(result_table is not None)
    keyword_key = sequence.get('keyword_key', None)
    self.failUnless(keyword_key is not None)
    full_text_key = sequence.get('full_text_key', None)
    self.failUnless(full_text_key is not None)
    request_key = sequence.get('request_key', None)
    self.failUnless(request_key is not None)
    multivalue_key = sequence.get('multivalue_key', None)
    self.failUnless(multivalue_key is not None)
    topic_key = sequence.get('topic_key', None)
    self.failUnless(topic_key is not None)

    catalog = self.getCatalogTool().getSQLCatalog()
    self.failUnless(catalog is not None)    
    # result key
    sql_search_result_keys = list(catalog.sql_search_result_keys)
    sql_search_result_keys.remove(result_key)
    sql_search_result_keys.sort()
    catalog.sql_search_result_keys = tuple(sql_search_result_keys)
    self.failUnless(result_key not in catalog.sql_search_result_keys)
    # related key
    sql_search_related_keys = list(catalog.sql_catalog_related_keys)
    sql_search_related_keys.remove(related_key)
    sql_search_related_keys.sort()
    catalog.sql_catalog_related_keys = tuple(sql_search_related_keys)
    self.failUnless(related_key not in catalog.sql_catalog_related_keys)
    # result table
    sql_search_tables = list(catalog.sql_search_tables)
    sql_search_tables.remove(result_table)
    sql_search_tables.sort()
    catalog.sql_search_tables = tuple(sql_search_tables)
    self.failUnless(result_table not in catalog.sql_search_tables)
    # keyword keys
    sql_catalog_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
    sql_catalog_keyword_keys.remove(keyword_key)
    sql_catalog_keyword_keys.sort()
    catalog.sql_catalog_keyword_search_keys = tuple(sql_catalog_keyword_keys)
    self.failUnless(keyword_key not in catalog.sql_catalog_keyword_search_keys)
    # full_text keys
    sql_catalog_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
    sql_catalog_full_text_keys.remove(full_text_key)
    sql_catalog_full_text_keys.sort()
    catalog.sql_catalog_full_text_search_keys = tuple(sql_catalog_full_text_keys)
    self.failUnless(full_text_key not in catalog.sql_catalog_full_text_search_keys)
    # request
    sql_catalog_request_keys = list(catalog.sql_catalog_request_keys)
    sql_catalog_request_keys.remove(request_key)
    sql_catalog_request_keys.sort()
    catalog.sql_catalog_request_keys = tuple(sql_catalog_request_keys)
    self.failUnless(request_key not in catalog.sql_catalog_request_keys)
    # multivalue
    sql_catalog_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
    sql_catalog_multivalue_keys.remove(multivalue_key)
    sql_catalog_multivalue_keys.sort()
    catalog.sql_catalog_multivalue_keys = tuple(sql_catalog_multivalue_keys)
    self.failUnless(multivalue_key not in catalog.sql_catalog_multivalue_keys)
    # topic keys
    sql_catalog_topic_keys = list(catalog.sql_catalog_topic_search_keys)
    sql_catalog_topic_keys.remove(topic_key)
    sql_catalog_topic_keys.sort()
    catalog.sql_catalog_topic_search_keys = tuple(sql_catalog_topic_keys)
    self.failUnless(topic_key not in catalog.sql_catalog_topic_search_keys)


  def stepCheckKeysAndTableExists(self, sequence=list, sequence_list=None, **kw):
    """
    Check presence of some keys and tables
    """
    related_key = sequence.get('related_key', None)
    self.failUnless(related_key is not None)
    result_key = sequence.get('result_key', None)
    self.failUnless(result_key is not None)
    result_table = sequence.get('result_table', None)
    self.failUnless(result_table is not None)
    keyword_key = sequence.get('keyword_key', None)
    self.failUnless(keyword_key is not None)
    full_text_key = sequence.get('full_text_key', None)
    self.failUnless(full_text_key is not None)
    request_key = sequence.get('request_key', None)
    self.failUnless(request_key is not None)
    multivalue_key = sequence.get('multivalue_key', None)
    self.failUnless(multivalue_key is not None)
    topic_key = sequence.get('topic_key', None)
    self.failUnless(topic_key is not None)

    catalog = self.getCatalogTool().getSQLCatalog()
    self.failUnless(catalog is not None)
    # result key
    self.failUnless(result_key in catalog.sql_search_result_keys)
    # related key
    self.failUnless(related_key in catalog.sql_catalog_related_keys)
    # result table
    self.failUnless(result_table in catalog.sql_search_tables)
    # keyword key
    self.failUnless(keyword_key in catalog.sql_catalog_keyword_search_keys)
    # full text key
    self.failUnless(full_text_key in catalog.sql_catalog_full_text_search_keys)
    # request key
    self.failUnless(request_key in catalog.sql_catalog_request_keys)
    # multivalue key
    self.failUnless(multivalue_key in catalog.sql_catalog_multivalue_keys)
    # topic key
    self.failUnless(topic_key in catalog.sql_catalog_topic_search_keys)

  def stepCheckKeysAndTableRemoved(self, sequence=list, sequence_list=None, **kw):
    """
    Check non-presence of some keys and tables
    """
    related_key = sequence.get('related_key', None)
    self.failUnless(related_key is not None)
    result_key = sequence.get('result_key', None)
    self.failUnless(result_key is not None)
    result_table = sequence.get('result_table', None)
    self.failUnless(result_table is not None)
    keyword_key = sequence.get('keyword_key', None)
    self.failUnless(keyword_key is not None)
    full_text_key = sequence.get('full_text_key', None)
    self.failUnless(full_text_key is not None)
    request_key = sequence.get('request_key', None)
    self.failUnless(request_key is not None)
    multivalue_key = sequence.get('multivalue_key', None)
    self.failUnless(multivalue_key is not None)
    topic_key = sequence.get('topic_key', None)
    self.failUnless(topic_key is not None)

    catalog = self.getCatalogTool().getSQLCatalog()
    self.failUnless(catalog is not None)
    # result key
    self.failUnless(result_key not in catalog.sql_search_result_keys)
    # related key
    self.failUnless(related_key not in catalog.sql_catalog_related_keys)
    # result table
    self.failUnless(result_table not in catalog.sql_search_tables)
    # keyword key
    self.failUnless(keyword_key not in catalog.sql_catalog_keyword_search_keys)
    # full text key
    self.failUnless(full_text_key not in catalog.sql_catalog_full_text_search_keys)
    # request key
    self.failUnless(request_key not in catalog.sql_catalog_request_keys)
    # multivalue key
    self.failUnless(multivalue_key not in catalog.sql_catalog_multivalue_keys)
    # topic key
    self.failUnless(topic_key not in catalog.sql_catalog_topic_search_keys)

  # Roles
  def stepCreateRole(self, sequence=None, sequence_list=None, **kw):
    """
    Create a role
    """
    new_role = "Unit Tester"
    p = self.getPortal()
    role_list = list(p.__ac_roles__)
    role_list.append(new_role)
    p.__ac_roles__ = tuple(role_list)
    self.failUnless(new_role in p.__ac_roles__)
    sequence.edit(role=new_role)

  def stepRemoveRole(self, sequence=None, sequence_list=None, **kw):
    """
    Remove a role
    """
    role = sequence.get('role', None)
    self.failUnless(role is not None)
    p = self.getPortal()
    role_list = list(p.__ac_roles__)
    role_list.remove(role)
    p.__ac_roles__ = tuple(role_list)
    self.failUnless(role not in p.__ac_roles__)

  def stepAddRoleToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Role to Business Template
    """
    role = sequence.get('role', None)
    self.failUnless(role is not None)
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    bt.edit(template_role_list=[role])

  def stepCheckRoleExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of role
    """
    role = sequence.get('role', None)
    self.failUnless(role is not None)
    p = self.getPortal()
    self.failUnless(role in p.__ac_roles__)
    
  def stepCheckRoleRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non-presence of role
    """
    role = sequence.get('role', None)
    self.failUnless(role is not None)
    p = self.getPortal()
    self.failUnless(role not in p.__ac_roles__)

  # Document, Property Sheet, Extension And Test
  # they use the same class so only one test is required for them
  def stepCreatePropertySheet(self, sequence=None, sequence_list=None, **kw):
    """
    Create a Property Sheet
    """
    ps_title = 'UnitTest'
    ps_data =  ' \nclass UnitTest: \n  """ \n  Fake property sheet for unit test \n \
    """ \n  _properties = ( \n  ) \n  _categories = ( \n  ) \n\n'
    cfg = getConfiguration()
    file_path = os.path.join(cfg.instancehome, 'PropertySheet', ps_title+'.py')
    if os.path.exists(file_path):
      os.remove(file_path)
    f = file(file_path, 'w')
    f.write(ps_data)
    f.close()
    self.failUnless(os.path.exists(file_path))
    sequence.edit(ps_title=ps_title, ps_path=file_path)

  def stepAddPropertySheetToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Property Sheet to Business Template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    ps_title = sequence.get('ps_title', None)
    self.failUnless(ps_title is not None)
    bt.edit(template_property_sheet_id_list=[ps_title])

  def stepRemovePropertySheet(self, sequence=None, sequencer_list=None, **kw):
    """
    Remove Property Sheet
    """
    ps_path = sequence.get('ps_path', None)
    self.failUnless(ps_path is not None)
    self.failUnless(os.path.exists(ps_path))
    os.remove(ps_path)
    self.failIf(os.path.exists(ps_path))

  def stepCheckPropertySheetExists(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Property Sheet
    """
    ps_path = sequence.get('ps_path', None)
    self.failUnless(ps_path is not None)
    self.failUnless(os.path.exists(ps_path))

  def stepCheckPropertySheetRemoved(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Property Sheet
    """
    ps_path = sequence.get('ps_path', None)
    self.failUnless(ps_path is not None)
    self.failIf(os.path.exists(ps_path))
    
  # Busines templates
  def stepImportBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Import Business Template from a dir
    """
    template_path = sequence.get('template_path')
    template_tool = self.getTemplateTool()
    exported_bt_id = sequence.get('export_bt').getId()
    import_id = 'imported_%s' %exported_bt_id
    n = 0
    while import_id in template_tool.objectIds():
      n = n + 1    
      import_id = "%s_%s" %(import_id, n)
    template_tool.download(url='file:'+template_path, id=import_id)
    import_bt = template_tool._getOb(id=import_id)
    self.failIf(import_bt is None)
    self.assertEquals(import_bt.getPortalType(), 'Business Template')
    sequence.edit(import_bt=import_bt)
    
  def stepInstallBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Install importzed business template
    """
    import_bt = sequence.get('import_bt')
    import_bt.install(force=1)

  def stepCreateNewBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Create a new Business Template
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.failUnless(template.getBuildingState() == 'draft')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.edit(title='geek template',
                  version='1.0',
                  description='bt for unit_test')
    sequence.edit(export_bt=template)

  def stepBuildBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Build Business Template
    """
    template = sequence.get('current_bt')  
    template.build()

  def stepSaveBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Export Business Template
    """
    template = sequence.get('current_bt')
    cfg = getConfiguration()
    bt_title = pathname2url(template.getTitle())
    template_path = os.path.join(cfg.instancehome, 'tests', '%s' % (bt_title,))
    template.export(path=template_path, local=1)
    sequence.edit(template_path=template_path)
    self.failUnless(os.path.exists(template_path))

  def stepCheckObjectPropertiesInBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Check that ac_local_roles, uid and _owner are set to None
    """
    bt = sequence.get('current_bt')
    item_list = [
      '_workflow_item',
      '_catalog_method_item',
      '_portal_type_item',
      '_category_item',
      '_skin_item',
      '_path_item',
      '_action_item',
    ]
    for item_name in item_list:
      item = getattr(bt, item_name)
      if item is not None:
        for key, data in item._objects.items():
          if hasattr(data, '__ac_local_roles__'):
            self.failUnless(data.__ac_local_roles__ is None)
          if hasattr(data, '_owner'):
            self.failUnless(data._owner is None)
          if hasattr(aq_base(data), 'uid'):
            self.failUnless(data.uid is None)

  def stepSetUpdateWorkflowFlagInBusinessTemplate(self, sequence=None, sequence_list=None):
    """
    Set flag for update in Business Template    
    """
    template_tool = self.getTemplateTool()
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getTitle(),'erp5_core')
    bt.edit(template_update_business_template_workflow=1)
    self.assertEqual(bt.getTemplateUpdateBusinessTemplateWorkflow(), 1)

  def stepSetUpdateToolFlagInBusinessTemplate(self, sequence=None, sequence_list=None):
    """
    Set flag for update in Business Template    
    """
    template_tool = self.getTemplateTool()
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getTitle(),'erp5_core')
    bt.edit(template_update_tool=1)
    self.assertEqual(bt.getTemplateUpdateTool(), 1)

  def stepRemoveBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Remove current Business Template
    """
    bt_id = sequence.get('current_bt').getId()
    template_tool = self.getTemplateTool()
    template_tool.manage_delObjects([bt_id])
    bt = template_tool._getOb(bt_id, None)
    self.failUnless(bt is None)

  def stepUninstallBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Uninstall current Business Template
    """
    bt = sequence.get('current_bt')
    bt.uninstall()

  # tests
  def test_01_checkNewSite(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check New Site'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       UseCoreBusinessTemplate  \
                       CheckTools \
                       CheckBuiltBuildingState \
                       CheckInstalledInstallationState \
                       CheckSkinsLayers \
                       CheckNoTrashBin \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)      

  # test of portal types
  def test_02_BusinessTemplateWithPortalTypes(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Portal Types'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemovePortalType \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  # test of skins
  def test_03_BusinessTemplateWithSkins(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Skin Folder'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveSkinFolder \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckSkinFolderExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckSkinFolderRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  # test of workflow
  def test_04_BusinessTemplateWithWorkflow(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Workflow'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateWorkflow \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveWorkflow \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckWorkflowExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckWorkflowRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  # test of module
  def test_05_BusinessTemplateWithModule(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Module'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateModuleAndObjects \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       AddModuleToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemovePortalType \
                       RemoveModule \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckModuleObjectsRemoved \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckModuleRemoved \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  # test of categories
  def test_06_BusinessTemplateWithBaseCategory(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Base Category'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateBaseCategory \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveBaseCategory \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckBaseCategoryExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckBaseCategoryRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
    
  # test of actions
  def test_07_BusinessTemplateWithoutOptionalAction(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template Without Optional Action'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateAction \
                       CreateOptionalAction \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddPortalTypeToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemovePortalType \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckActionExists \
                       CheckOptionalActionNotExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  def test_08_BusinessTemplateWithOptionalAction(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Optional Action'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateAction \
                       CreateOptionalAction \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddOptionalActionToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemovePortalType \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       CreatePortalType \
                       CreateAction \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckActionExists \
                       CheckOptionalActionExists \
                       CheckActionsOrder \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckOptionalActionNotExists \
                       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  def test_09_BusinessTemplateWithPath(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With A Simple Path'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    # a simple path
    sequence_string = '\
                       CreateBaseCategory \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddBaseCategoryAsPathToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveBaseCategory \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckBaseCategoryExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckBaseCategoryRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_10_BusinessTemplateWithPathAndJoker1(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Path And Joker *'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()    
    # path with subobjects
    sequence_string = '\
                       CreateBaseCategory \
                       CreateCategories \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddCategoriesAsPathToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveCategories \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckCategoriesExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckCategoriesRemoved \
                       RemoveBaseCategory \
                       '    
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_11_BusinessTemplateWithPathAndJoker2(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Path And Joker **'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    # path with subobject recursively
    sequence_string = '\
                       CreateBaseCategory \
                       CreateCategories \
                       CreateSubCategories \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddSubCategoriesAsPathToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveCategories \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckCategoriesRemoved \
                       RemoveBaseCategory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  def test_12_BusinessTemplateWithCatalogMethod(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Catalog Method, Related Key, Result Key And Table'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateCatalogMethod \
                       CreateKeysAndTable \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddCatalogMethodToBusinessTemplate \
                       AddKeysAndTableToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckKeysAndTableRemoved \
                       CheckCatalogMethodRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  def test_13_BusinessTemplateWithRole(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Role'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateRole \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddRoleToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveRole \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckRoleExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckRoleRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  def test_14_BusinessTemplateWithPropertySheet(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Property Sheet'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePropertySheet \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPropertySheetToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemovePropertySheet \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckPropertySheetExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPropertySheetRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    


  def test_15_BusinessTemplateWithAllItems(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With All Items'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateModuleAndObjects \
                       CreateSkinFolder \
                       CreateBaseCategory \
                       CreateCategories \
                       CreateSubCategories \
                       CreateWorkflow \
                       CreateAction \
                       CreateOptionalAction \
                       CreateCatalogMethod \
                       CreateKeysAndTable \
                       CreateRole \
                       CreatePropertySheet \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       AddModuleToBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       AddSubCategoriesAsPathToBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddOptionalActionToBusinessTemplate \
                       AddCatalogMethodToBusinessTemplate \
                       AddKeysAndTableToBusinessTemplate \
                       AddRoleToBusinessTemplate \
                       AddPropertySheetToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemovePortalType \
                       RemoveModule \
                       RemoveSkinFolder \
                       RemoveBaseCategory \
                       RemoveWorkflow \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveRole \
                       RemovePropertySheet \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckSkinFolderExists \
                       CheckBaseCategoryExists \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       CheckWorkflowExists \
                       CheckOptionalActionExists \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       CheckRoleExists \
                       CheckPropertySheetExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       CheckModuleRemoved \
                       CheckSkinFolderRemoved \
                       CheckBaseCategoryRemoved \
                       CheckWorkflowRemoved \
                       CheckCatalogMethodRemoved \
                       CheckKeysAndTableRemoved \
                       CheckRoleRemoved \
                       CheckPropertySheetRemoved \
                       CheckSkinsLayers \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    



  def test_16_SubobjectsAfterUpgradOfBusinessTemplate(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Upgrade Of Business Template Keeps Subobjects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    # check if subobjects in module and catalog still remains after an update
    sequence_string = '\
                       CreatePortalType \
                       CreateModuleAndObjects \
                       CreateBaseCategory \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       AddModuleToBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveModule \
                       RemoveBaseCategory \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckModuleObjectsRemoved \
                       CheckBaseCategoryExists \
                       CreateModuleObjects \
                       CreateCategories \
                       CreateSubCategories \
                       CreateNewBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckBaseCategoryExists \
                       CheckModuleObjectsExists \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       CheckModuleRemoved \
                       CheckBaseCategoryRemoved \
                       CheckSkinsLayers \
                       '    
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_17_upgradeBusinessTemplateWithAllItems(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Upgrade Business Template With All Items'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    # by default action is backup, so everything will be replace
    sequence_string = '\
                       CreatePortalType \
                       CreateModuleAndObjects \
                       CreateSkinFolder \
                       CreateBaseCategory \
                       CreateCategories \
                       CreateSubCategories \
                       CreateWorkflow \
                       CreateAction \
                       CreateOptionalAction \
                       CreateCatalogMethod \
                       CreateKeysAndTable \
                       CreateRole \
                       CreatePropertySheet \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       AddModuleToBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       AddSubCategoriesAsPathToBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddOptionalActionToBusinessTemplate \
                       AddCatalogMethodToBusinessTemplate \
                       AddKeysAndTableToBusinessTemplate \
                       AddRoleToBusinessTemplate \
                       AddPropertySheetToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemovePortalType \
                       RemoveModule \
                       RemoveSkinFolder \
                       RemoveBaseCategory \
                       RemoveWorkflow \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveRole \
                       RemovePropertySheet \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckSkinFolderExists \
                       CheckBaseCategoryExists \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       CheckWorkflowExists \
                       CheckOptionalActionExists \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       CheckRoleExists \
                       CheckPropertySheetExists \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckSkinFolderExists \
                       CheckBaseCategoryExists \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       CheckWorkflowExists \
                       CheckOptionalActionExists \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       CheckRoleExists \
                       CheckPropertySheetExists \
                       CheckSkinsLayers \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    


  # test specific to erp5_core
  def test_18_checkUpdateBusinessTemplateWorkflow(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Update of Business Template Workflows is working'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CopyCoreBusinessTemplate \
                       UseCopyCoreBusinessTemplate  \
                       SetUpdateWorkflowFlagInBusinessTemplate \
                       FillPortalTypesFields \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)      


  def test_19_checkUpdateTool(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Update of Tool is working'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CopyCoreBusinessTemplate \
                       UseCopyCoreBusinessTemplate  \
                       SetUpdateToolFlagInBusinessTemplate \
                       FillPortalTypesFields \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTrashBin \
                       CheckSkinsLayers \
                       '
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
