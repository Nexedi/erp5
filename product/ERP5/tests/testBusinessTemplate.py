##############################################################################
# -*- coding: utf8 -*-
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
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

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_base
from zLOG import LOG
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.RoleInformation import RoleInformation
from App.config import getConfiguration
from Products.ERP5Type.tests.Sequence import SequenceList
from urllib import pathname2url
from Globals import PersistentMapping
from Products.CMFCore.Expression import Expression
from Products.CMFCore.tests.base.testcase import LogInterceptor
import shutil
import os

class TestBusinessTemplate(ERP5TypeTestCase, LogInterceptor):
  """
    Test these operations:

    - Create a template

    - Install a template

    - Uninstall a template

    - Upgrade a template
  """
  run_all_test = 1
  quiet = 1

  def getBusinessTemplateList(self):
    return ('erp5_csv_style', 'erp5_pdf_style')

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
    # create the fake catalog table
    sql_connection = self.getSQLConnection()
    sql = 'create table if not exists `fake_catalog` (`toto` BIGINT)'
    sql_connection.manage_test(sql)
    self._catch_log_errors()

    # remove default predicate which matches anything
    content_type_registry = getattr(portal, 'content_type_registry', None)
    if (content_type_registry is not None and
        'any' in content_type_registry.predicate_ids):
      content_type_registry.removePredicate('any')
      get_transaction().commit()

  def beforeTearDown(self):
    """Remove objects created tests."""
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        if id != "Geek Object":
          props['chain_%s' % id] = ', '.join(wf_ids)
    pw.manage_changeWorkflows('', props=props)
    if 'erp5_geek' in self.getSkinsTool().objectIds():
      self.getSkinsTool().manage_delObjects(['erp5_geek'])
      ps = self.getSkinsTool()
      for skin_name, selection in ps.getSkinPaths():
        new_selection = []
        selection = selection.split(',')
        for skin_id in selection:
          if skin_id != 'erp5_geek':
            new_selection.append(skin_id)
        ps.manage_skinLayers(skinpath=tuple(new_selection),
                             skinname=skin_name, add_skin=1)
    if 'Geek Object' in self.getTypeTool().objectIds():
      self.getTypeTool().manage_delObjects(['Geek Object', 'Geek Module'])
    if 'geek_module' in self.getPortal().objectIds():
      self.getPortal().manage_delObjects(['geek_module'])
    if 'geek_workflow' in self.getWorkflowTool().objectIds():
      self.getWorkflowTool().manage_delObjects(['geek_workflow'])
    if 'custom_geek_workflow' in self.getWorkflowTool().objectIds():
      self.getWorkflowTool().manage_delObjects(['custom_geek_workflow'])
    for business_template in self.getTemplateTool().contentValues():
      if business_template.getTitle() == 'geek template':
        self.getTemplateTool().manage_delObjects([business_template.getId()])
    get_transaction().commit()
    self._ignore_log_errors()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def stepTic(self,**kw):
    self.tic()

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
    new_id = ids[0]['new_id']
    new_bt = template_tool._getOb(new_id)
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

  def stepUseSecondBusinessTemplate(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Define second_export_bt as current bt
    """
    bt = sequence.get('second_export_bt')
    sequence.edit(current_bt=bt)

  def stepUseDependencyBusinessTemplate(self, sequence=None,
                                  sequence_list=None, **kw):
    """
      Define dependency_bt as current bt
    """
    bt = sequence.get('dependency_bt')
    sequence.edit(current_bt=bt)

  def stepUseImportBusinessTemplate(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Define import_bt as current bt
    """
    bt = sequence.get('import_bt')
    sequence.edit(current_bt=bt)

  def stepCheckInstalledInstallationState(self, sequence=None,
                                        sequence_list=None, **kw):
    """
    Check if installation state is installed
    """
    bt = sequence.get('current_bt', None)
    self.assertEquals(bt.getInstallationState(), 'installed')

  def stepCheckNotInstalledInstallationState(self, sequence=None,
                                        sequence_list=None, **kw):
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
        self.failIf('erp5_xhtml_style' not in selection)
      if skin_name == 'Print':
        self.failIf('erp5_xhtml_style' in selection)
        self.failIf('erp5_csv_style' in selection)
        self.failIf('erp5_core' not in selection)
        self.failIf('erp5_pdf_style' not in selection)
      if skin_name == 'CSV':
        self.failIf('erp5_pdf_style' in selection)
        self.failIf('erp5_xhtml_style' in selection)
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
    pt.manage_addTypeInformation(ERP5TypeInformation.meta_type,
                                 id='Geek Object',
                                 typeinfo_name='ERP5Type: ERP5 Person',)
    object_type = pt._getOb('Geek Object', None)
    self.failUnless(object_type is not None)
    sequence.edit(object_ptype_id=object_type.getId())
    # create module portal type
    pt.manage_addTypeInformation(ERP5TypeInformation.meta_type,
                                 id='Geek Module',
                                 typeinfo_name='ERP5Type: ERP5 Folder')
    module_type = pt._getOb('Geek Module', None)
    self.failUnless(module_type is not None)
    module_type.filter_content_types = 1
    module_type.allowed_content_types = ('Geek Object',)
    module_type.hidden_content_type_list = ('Geek Object',)
    sequence.edit(module_ptype_id=module_type.getId(),
          module_ptype_filter_content_types=module_type.filter_content_types,
          module_ptype_allowed_content_types=module_type.allowed_content_types,
          module_ptype_hidden_content_type_list=module_type.hidden_content_type_list)

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

  def stepAddDuplicatedPortalTypeToBusinessTemplate(self, sequence=None,
                                                    sequence_list=None, **kw):
    """
    Add duplicated portal type to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    ptype_ids = []
    ptype_ids.append(sequence.get('object_ptype_id', ''))
    self.assertEqual(len(ptype_ids), 1)
    bt.edit(template_portal_type_id_list=ptype_ids)

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

  def stepRemoveViewAction(self, sequence=None, sequence_list=None, **kw):
    """
    Remove PortalType
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    object_type = pt._getOb(object_id, None)
    object_type.deleteActions([0])

  def stepCheckPortalTypeExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of portal type
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    module_type = pt._getOb(module_id, None)
    self.failUnless(module_type is not None)
    self.assertEquals(module_type.allowed_content_types,
        sequence.get('module_ptype_allowed_content_types'))
    self.assertEquals(module_type.hidden_content_type_list,
        sequence.get('module_ptype_hidden_content_type_list'))
    self.assertEquals(module_type.filter_content_types,
        sequence.get('module_ptype_filter_content_types'))
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

  def stepCheckDuplicatedPortalTypeRemoved(self, sequence=None,
                                           sequence_list=None, **kw):
    """
    Check non presence of portal type
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    object_type = pt._getOb(object_id, None)
    self.failUnless(object_type is None)

  def stepFillPortalTypesFields(self, sequence=None, sequence_list=None, **kw):
    """
    Fill portal types properties field in business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    bt.getPortalTypesProperties()

  def stepFillWrongPortalTypesFields(self, sequence=None, sequence_list=None, **kw):
    """
    Fill portal types properties field in business template with wrong values
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    bt.getPortalTypesProperties()
    bt_allowed_content_type_list = list(getattr(self, 'template_portal_type_allowed_content_type', []) or [])
    bt_allowed_content_type_list.append("Geek Module | BusinessTemplate")
    bt.setProperty('template_portal_type_allowed_content_type', bt_allowed_content_type_list)

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
    # add a specific permission to module which do not use acquisition
    module.manage_permission('Copy or Move', ['Assignor'], False)
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

  def stepCheckModulePermissions(self, sequence=None, sequence_list=None, **kw):
    """
    Check specific permissions defined on module do no get acquired flag
    """
    portal = self.getPortal()
    module_id = sequence.get("module_id")
    new_module = portal._getOb(module_id, None)
    perms = new_module.permission_settings('Copy or Move')
    self.assertEqual(len(perms), 1)
    # check we do not have acquire
    for perm in perms:
      self.assertEqual(perm['name'], 'Copy or Move')
      self.assertNotEqual(perm['acquire'], 'CHECKED')
    # check permission defined for the right role
    perms = new_module.rolesOfPermission(permission='Copy or Move')
    for perm in perms:
      if perm['name'] == 'Assignor':
        self.assertEqual(perm["selected"], "SELECTED")
      else:
        self.assertNotEqual(perm["selected"], "SELECTED")

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

  def stepCreateSkinSubFolder(self, sequence=None, sequence_list=None, **kw):
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.failUnless(skin_folder is not None)
    skin_folder.manage_addFolder('erp5_subgeek')
    skin_subfolder = skin_folder._getOb('erp5_subgeek', None)
    self.failUnless(skin_subfolder is not None)
    sequence.edit(skin_subfolder_id=skin_subfolder.getId())

  def stepCheckSkinSubFolderExists(self, sequence=None,sequence_list=None, **kw):
    """
    Check presence of skin sub folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    self.failUnless(skin_folder is not None)
    subskin_id = sequence.get('skin_subfolder_id')
    skin_subfolder = skin_folder._getOb(subskin_id, None)
    self.failUnless(skin_subfolder is not None)

  def stepCreateNewForm(self, sequence=None, sequence_list=None):
    """Create a new ERP5 Form in a skin folder."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = 'Geek_view'
    addERP5Form = skin_folder.manage_addProduct['ERP5Form'].addERP5Form
    addERP5Form(form_id, 'View')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    self.assertEquals(sorted(form.get_groups(include_empty=1)),
                      sorted(['left', 'right', 'center', 'bottom', 'hidden']))
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_title', 'Title', 'StringField')
    field = form.get_field('my_title')
    self.assertEquals(form.get_fields_in_group('left'), [field])
    group_dict = {}
    for group in form.get_groups(include_empty=1):
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      group_dict[group] = id_list
    sequence.edit(form_id=form_id, group_dict=group_dict)

  def stepRemoveForm(self, sequence=None, sequence_list=None):
    """Remove an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    skin_folder.manage_delObjects([form_id])
    form = skin_folder._getOb(form_id, None)
    self.assertEquals(form, None)

  def stepAddFormField(self, sequence=None, sequence_list=None):
    """Add a field to an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    self.assertEquals(sorted(form.get_groups(include_empty=1)),
                      sorted(['left', 'right', 'center', 'bottom', 'hidden']))
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_reference', 'Reference', 'StringField')
    form.move_field_group(['my_reference'], 'left', 'right')
    field = form.get_field('my_reference')
    self.assertEquals(form.get_fields_in_group('right'), [field])
    group_dict = {}
    for group in form.get_groups(include_empty=1):
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      group_dict[group] = id_list
    sequence.edit(group_dict=group_dict, field_id=field.getId())

  def stepModifyFormTitle(self, sequence=None, sequence_list=None):
    """Add a field to an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    form_title = 'First Form Title'
    form.title = form_title
    self.assertNotEquals(form, None)
    self.assertEquals(sorted(form.get_groups(include_empty=1)),
                      sorted(['left', 'right', 'center', 'bottom', 'hidden']))
    group_dict = {}
    for group in form.get_groups(include_empty=1):
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      group_dict[group] = id_list
    sequence.edit(group_dict=group_dict, field_id=field.getId(),
                  form_title=form_title)

  def stepRevertFormTitle(self, sequence=None, sequence_list=None):
    """Add a field to an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    form_title = 'Second Form Title'
    form.title = form_title

  def stepCheckFormTitle(self, sequence=None, sequence_list=None):
    """Add a field to an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertEquals('First Form Title', form.title)

  def stepRemoveFormField(self, sequence=None, sequence_list=None):
    """Remove a field from an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    field_id = sequence.get('field_id')
    field = form.get_field(field_id)
    self.assertNotEquals(field, None)
    form.manage_delObjects([field_id])
    self.assertRaises(AttributeError, form.get_field, field_id)

  def stepCheckFormGroups(self, sequence=None, sequence_list=None):
    """Check the groups of an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    group_dict = sequence.get('group_dict')
    self.assertEquals(sorted(form.get_groups(include_empty=1)),
                      sorted(group_dict.iterkeys()))
    for group in group_dict.iterkeys():
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      self.assertEquals(group_dict[group], id_list)

  def stepCreateNewObjectInSkinSubFolder(self, sequence=None, sequence_list=None, **kw):
    """
    Create a new object in skin subfolder
    """
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.failUnless(skin_folder is not None)
    skin_subfolder = skin_folder._getOb('erp5_subgeek', None)
    self.failUnless(skin_subfolder is not None)
    method_id = "z_fake_method"
    addSQLMethod = skin_subfolder.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
    addSQLMethod(id=method_id, title='', connection_id='erp5_sql_connection',
                 arguments='', template='')
    zsql_method = skin_subfolder._getOb(method_id, None)
    self.failUnless(zsql_method is not None)
    sequence.edit(zsql_method_id = method_id)

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
    Add skin folder to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    wf_ids = []
    wf_ids.append(sequence.get('skin_folder_id', ''))
    self.assertEqual(len(wf_ids), 1)
    bt.edit(template_skin_id_list=wf_ids)

  def stepAddPathToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add a path to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    bt.edit(template_path_list=['geek_path',])

  # Base Category
  def stepCreateBaseCategory(self, sequence=None, sequence_list=None, **kw):
    """
    Create Base category
    """
    pc = self.getCategoryTool()
    base_category = pc.newContent(portal_type = 'Base Category')
    self.failUnless(base_category is not None)
    sequence.edit(bc_id=base_category.getId(),)

  # Content Type Registry
  def stepAddEntryToContentTypeRegistry(self, sequence=None, sequence_list=None, **kw):
    """
    Add entry to content type registry
    """
    ctr = getattr(self.getPortal(), 'content_type_registry')
    ctr.addPredicate('test', 'extension')
    ctr.assignTypeName('test', 'What Not')
    ctr.getPredicate('test').extensions = ('abc', 'def')

  def stepCheckContentTypeRegistryHasNewEntry(self, sequence=None, sequence_list=None, **kw):
    """
      Check that we can find new type name in ctr
    """
    ctr = getattr(self.getPortal(), 'content_type_registry')
    self.failUnless(ctr.findTypeName('bzzz.def', None, None) == 'What Not')

  def stepAddContentTypeRegistryAsPathToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
      Add Content Type Registry to Business template
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    path = 'content_type_registry'
    bt.edit(template_path_list=[path])

  def stepRemoveContentTypeRegistryNewEntry(self, sequence=None, sequence_list=None, **kw):
    """
      Remove new entry from content_type_registry
    """
    ctr = getattr(self.getPortal(), 'content_type_registry')
    ctr.removePredicate('test')

  def stepCheckContentTypeRegistryHasNoNewEntry(self, sequence=None, sequence_list=None, **kw):
    """
      Check that we can not find new type name in ctr anymore
    """
    ctr = getattr(self.getPortal(), 'content_type_registry')
    self.failUnless(ctr.findTypeName('bzzz.def', None, None) is None)

  def stepAddBaseCategoryToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Base category to Business template
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    bt.edit(template_base_category_list=[bc_id,])

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
    self.failUnless(base_category is None)

  def stepSaveBaseCategoryUid(self, sequence=None, sequence_list=None, **kw):
    """
    Check uid has not changed after an upgrade
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    sequence.edit(bc_uid = base_category.getUid())

  def stepCheckBaseCategoryUid(self, sequence=None, sequence_list=None, **kw):
    """
    Check uid has not changed after an upgrade
    """
    bc_id = sequence.get('bc_id')
    bc_uid = sequence.get('bc_uid')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertEqual(bc_uid, base_category.getUid())

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
    props['chain_Geek Object'] = 'geek_workflow'
    pw.manage_changeWorkflows('', props=props)

  def stepCheckWorkflowChainRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check if the workflowChain has been removed
    """
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    if cbt is not None:
      for id, wf_ids in cbt.items():
        self.failUnless(id!="Geek Object")

  def stepCheckWorkflowChainExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check if the workflowChain has been removed
    """
    present = 0
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    if cbt is not None:
      for id, wf_ids in cbt.items():
        if id == "Geek Object":
          present = 1
    self.assertEqual(present, 1)

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

  def stepAddWorkflowChainToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add workflow to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    wf_chain_ids = ['Geek Object | %s' % sequence.get('workflow_id', '')]
    bt.edit(template_portal_type_workflow_chain_list=wf_chain_ids)

  def stepRemoveWorkflow(self, sequence=None, sequence_list=None, **kw):
    """
    Remove Workflow
    """
    wf_id = sequence.get('workflow_id')
    pw = self.getWorkflowTool()
    pw.manage_delObjects([wf_id])
    workflow = pw._getOb(wf_id, None)
    self.failUnless(workflow is None)
    # remove workflowChain
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        wf_ids = list(wf_ids)
        if id == "Geek Object":
          wf_ids.remove(wf_id)
        props['chain_%s' % id] = ','.join(wf_ids)
    pw.manage_changeWorkflows('', props=props)

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

  def stepCheckWorkflowBackup(self, sequence=None, sequence_list=None, **kw):
    """
    Check workflow and its subobjects has been well backup in portal trash
    """
    wf_id = sequence.get('workflow_id')
    tt = self.getPortal()['portal_trash']
    self.assertEqual(len(tt.objectIds()), 1)
    bin = tt.objectValues()[0]
    self.assertNotEqual(len(bin.portal_workflow_items[wf_id].objectIds()), 0)

  # Actions
  def stepCreateFirstAction(self, sequence=None, sequence_list=None, **kw):
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
      , priority = 2.0 )
    sequence.edit(first_action_id='become_geek')

  def stepCreateEmptyAction(self, sequence=None, sequence_list=None, **kw):
    """
    Create an empty action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    object_pt.addAction(id = ''
      , name = ' Nerd'
      , action = ''
      , condition = ''
      , permission = ()
      , category = ''
      , visible = 1
      , priority = 1.2)

  def stepCreateSecondAction(self, sequence=None, sequence_list=None, **kw):
    """
    Create a second action
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
      , priority = 1.5 )
    sequence.edit(second_action_id='become_nerd')

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

  def stepCheckFirstActionExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('first_action_id')
    self.failUnless(action_id in [x.getId() for x in object_pt.listActions()])

  def stepCheckFirstActionNotExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check non-presence of action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('first_action_id')
    self.failUnless(action_id not in [x.getId() for x in object_pt.listActions()])

  def stepCheckSecondActionExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of the second action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('second_action_id')
    self.failUnless(action_id in [x.getId() for x in object_pt.listActions()])

  def stepCheckSecondActionNotExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check non-presence of optional action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('second_action_id')
    self.failUnless(action_id not in [x.getId() for x in object_pt.listActions()])

  def stepAddSecondActionToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Second Action to business template
    """
    object_id = sequence.get('object_ptype_id')
    action_id = sequence.get('second_action_id')
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    bt.edit(template_action_path=['%s | %s' %(object_id, action_id)])

  # Catalog Method
  def stepCreateCatalogMethod(self, sequence=None, sequence_list=None, **kw):
    """
    Create ZSQL Method into catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    self.failUnless(catalog is not None)
    method_id = "z_fake_method"
    addSQLMethod = catalog.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
    addSQLMethod(id=method_id, title='', connection_id='erp5_sql_connection',
                 arguments='', template='')
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

  def stepCreateNewCatalogMethod(self, sequence=None, sequence_list=None, **kw):
    """
    Create ZSQL Method into catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    method_id = "z_another_fake_method"
    addSQLMethod =catalog.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
    addSQLMethod(id=method_id, title='', connection_id='erp5_sql_connection',
                 arguments='', template='')
    zsql_method = catalog._getOb(method_id, None)
    self.failUnless(zsql_method is not None)
    sequence.edit(another_zsql_method_id = method_id)
    # set this method in update_object properties of catalog
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_uncatalog_object.append(method_id)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)

  def stepChangePreviousCatalogMethod(self, sequence=None, sequence_list=None, **kw):
    """
    Create ZSQL Method into catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    method_id = sequence.get('zsql_method_id')
    previous_method = catalog._getOb(method_id,None)
    self.assertEquals(previous_method.title,'')
    previous_method.title='toto'
    self.assertEquals(previous_method.title,'toto')

  def stepCheckCatalogMethodChangeKept(self, sequence=None, sequence_list=None, **kw):
    """
    Create ZSQL Method into catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    method_id = sequence.get('zsql_method_id')
    previous_method = catalog._getOb(method_id,None)
    self.assertEquals(previous_method.title,'toto')

  def stepAddCatalogMethodToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add catalog method into the business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    method_id = sequence.get('zsql_method_id', None)
    self.failUnless(method_id is not None)
    pc = self.getCatalogTool()
    catalog_id = pc.getSQLCatalog().id
    bt.edit(template_catalog_method_id_list=[catalog_id+'/'+method_id])

  def stepAddNewCatalogMethodToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add catalog method into the business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    method_id = sequence.get('zsql_method_id', None)
    self.failUnless(method_id is not None)
    another_method_id = sequence.get('another_zsql_method_id', None)
    pc = self.getCatalogTool()
    catalog_id = pc.getSQLCatalog().id
    bt.edit(template_catalog_method_id_list=[catalog_id+'/'+method_id,
            catalog_id+'/'+another_method_id])

  def stepCheckCatalogMethodExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of ZSQL Method in catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
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
    catalog = pc.getSQLCatalog()
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
    catalog = pc.getSQLCatalog()
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
    # define variables
    related_key = 'fake_id | category/catalog/z_fake_method'
    result_key = 'catalog.title'
    result_table = 'fake_catalog'
    keyword_key = 'fake_keyword'
    full_text_key = 'fake_full_text'
    request_key = 'fake_request'
    multivalue_key = 'fake_multivalue'
    topic_key = 'fake_topic'
    scriptable_key = 'fake_search_text | fake_script_query'
    role_key = 'Foo | catalog.owner'
    local_role_key = 'Bar | catalog.owner'
    catalog = self.getCatalogTool().getSQLCatalog()
    self.failUnless(catalog is not None)
    # result table
    if result_table not in catalog.sql_search_tables:
      sql_search_tables = list(catalog.sql_search_tables)
      sql_search_tables.append(result_table)
      sql_search_tables.sort()
      catalog.sql_search_tables = tuple(sql_search_tables)
    self.failUnless(result_table in catalog.sql_search_tables)
    # result key
    if result_key not in catalog.sql_search_result_keys:
      sql_search_result_keys = list(catalog.sql_search_result_keys)
      sql_search_result_keys.append(result_key)
      sql_search_result_keys.sort()
      catalog.sql_search_result_keys = tuple(sql_search_result_keys)
    self.failUnless(result_key in catalog.sql_search_result_keys)
    # related key
    if related_key not in catalog.sql_catalog_related_keys:
      sql_search_related_keys = list(catalog.sql_catalog_related_keys)
      sql_search_related_keys.append(related_key)
      sql_search_related_keys.sort()
      catalog.sql_catalog_related_keys = tuple(sql_search_related_keys)
    self.failUnless(related_key in catalog.sql_catalog_related_keys)
    # keyword keys
    if keyword_key not in catalog.sql_catalog_keyword_search_keys:
      sql_catalog_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
      sql_catalog_keyword_keys.append(keyword_key)
      sql_catalog_keyword_keys.sort()
      catalog.sql_catalog_keyword_search_keys = tuple(sql_catalog_keyword_keys)
    self.failUnless(keyword_key in catalog.sql_catalog_keyword_search_keys)
    # full_text keys
    if full_text_key not in catalog.sql_catalog_full_text_search_keys:
      sql_catalog_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
      sql_catalog_full_text_keys.append(full_text_key)
      sql_catalog_full_text_keys.sort()
      catalog.sql_catalog_full_text_search_keys = tuple(sql_catalog_full_text_keys)
    self.failUnless(full_text_key in catalog.sql_catalog_full_text_search_keys)
    # request
    if request_key not in catalog.sql_catalog_request_keys:
      sql_catalog_request_keys = list(catalog.sql_catalog_request_keys)
      sql_catalog_request_keys.append(request_key)
      sql_catalog_request_keys.sort()
      catalog.sql_catalog_request_keys = tuple(sql_catalog_request_keys)
    self.failUnless(request_key in catalog.sql_catalog_request_keys)
    # multivalue
    if multivalue_key not in catalog.sql_catalog_multivalue_keys:
      sql_catalog_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
      sql_catalog_multivalue_keys.append(multivalue_key)
      sql_catalog_multivalue_keys.sort()
      catalog.sql_catalog_multivalue_keys = tuple(sql_catalog_multivalue_keys)
    self.failUnless(multivalue_key in catalog.sql_catalog_multivalue_keys)
    # topic keys
    if topic_key not in catalog.sql_catalog_topic_search_keys:
      sql_catalog_topic_keys = list(catalog.sql_catalog_topic_search_keys)
      sql_catalog_topic_keys.append(topic_key)
      sql_catalog_topic_keys.sort()
      catalog.sql_catalog_topic_search_keys = tuple(sql_catalog_topic_keys)
    self.failUnless(topic_key in catalog.sql_catalog_topic_search_keys)
    # scriptable keys
    if scriptable_key not in catalog.sql_catalog_scriptable_keys:
      sql_catalog_scriptable_keys = list(catalog.sql_catalog_scriptable_keys)
      sql_catalog_scriptable_keys.append(scriptable_key)
      sql_catalog_scriptable_keys.sort()
      catalog.sql_catalog_scriptable_keys = tuple(sql_catalog_scriptable_keys)
    self.failUnless(scriptable_key in catalog.sql_catalog_scriptable_keys)
    # role keys
    if role_key not in catalog.sql_catalog_role_keys:
      sql_catalog_role_keys = list(catalog.sql_catalog_role_keys)
      sql_catalog_role_keys.append(role_key)
      sql_catalog_role_keys.sort()
      catalog.sql_catalog_role_keys = tuple(sql_catalog_role_keys)
    self.failUnless(role_key in catalog.sql_catalog_role_keys)
    # local_role keys
    if local_role_key not in catalog.sql_catalog_local_role_keys:
      sql_catalog_local_role_keys = list(catalog.sql_catalog_local_role_keys)
      sql_catalog_local_role_keys.append(local_role_key)
      sql_catalog_local_role_keys.sort()
      catalog.sql_catalog_local_role_keys = tuple(sql_catalog_local_role_keys)
    self.failUnless(local_role_key in catalog.sql_catalog_local_role_keys)

    sequence.edit(related_key=related_key, result_key=result_key,
                  result_table=result_table,
                  keyword_key=keyword_key, full_text_key=full_text_key,
                  request_key=request_key,
                  multivalue_key=multivalue_key, topic_key=topic_key, \
                  scriptable_key=scriptable_key,
                  role_key=role_key, local_role_key=local_role_key)

  def stepModifyCatalogConfiguration(self, sequence, **kw):
    """Modify the current configuration of the catalog.
    """
    catalog = self.getCatalogTool().getSQLCatalog()
    # modify method related configuration
    copy_data = catalog.manage_copyObjects(ids=["z_getitem_by_uid"])
    ids = catalog.manage_pasteObjects(copy_data)
    new_id = ids[0]['new_id']
    new_method = catalog._getOb(new_id)
    catalog.manage_renameObjects([new_id,], ["z_getitem_by_uid_2",])
    new_method = catalog._getOb("z_getitem_by_uid_2")
    self.assertNotEqual(new_method, None)
    catalog.sql_getitem_by_uid = 'z_getitem_by_uid_2'
    # modify table related configuration
    catalog.sql_search_tables = tuple( list(catalog.sql_search_tables) +
                                     ['translation'] )
    # modify column related configuration
    catalog.sql_search_result_keys = tuple( list(catalog.sql_search_result_keys) +
                                     ['catalog.reference'] )
    sequence.edit(result_key='catalog.reference', search_table="translation")

  def stepCheckCatalogConfigurationKept(self, sequence, **kw):
    """Check modification made in stepModifyCatalogConfiguration are still
    present.
    """
    catalog = self.getCatalogTool().getSQLCatalog()
    # method related configuration
    self.assertEquals(catalog.sql_getitem_by_uid, 'z_getitem_by_uid_2')
    # table related configuration
    self.failUnless('translation' in catalog.sql_search_tables)
    # column related configuration
    self.failUnless('catalog.reference'
                    in catalog.sql_search_result_keys)

  def stepRemoveCatalogLocalConfiguration(self, sequence, **kw):
    """
    Remove modification made in stepModifyCatalogConfiguration
    """
    result_key = sequence.get('result_key', None)
    self.failUnless(result_key is not None)
    result_table = sequence.get('search_table', None)
    self.failUnless(result_table is not None)
    catalog = self.getCatalogTool().getSQLCatalog()
    self.failUnless(catalog is not None)
    # result key
    sql_search_result_keys = list(catalog.sql_search_result_keys)
    sql_search_result_keys.remove(result_key)
    sql_search_result_keys.sort()
    catalog.sql_search_result_keys = tuple(sql_search_result_keys)
    self.failUnless(result_key not in catalog.sql_search_result_keys)
    # search table
    sql_search_tables = list(catalog.sql_search_tables)
    sql_search_tables.remove(result_table)
    sql_search_tables.sort()
    catalog.sql_search_tables = tuple(sql_search_tables)
    self.failUnless(result_table not in catalog.sql_search_tables)

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
    scriptable_key = sequence.get('scriptable_key', None)
    self.failUnless(scriptable_key is not None)
    role_key = sequence.get('role_key', None)
    self.failUnless(role_key is not None)
    local_role_key = sequence.get('local_role_key', None)
    self.failUnless(local_role_key is not None)

    bt.edit(template_catalog_related_key_list=[related_key],
            template_catalog_result_key_list=[result_key],
            template_catalog_result_table_list=[result_table],
            template_catalog_keyword_key_list=[keyword_key],
            template_catalog_full_text_key_list=[full_text_key],
            template_catalog_request_key_list=[request_key],
            template_catalog_multivalue_key_list=[multivalue_key],
            template_catalog_topic_key_list=[topic_key],
            template_catalog_scriptable_key_list=[scriptable_key],
            template_catalog_role_key_list=[role_key],
            template_catalog_local_role_key_list=[local_role_key],
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
    scriptable_key = sequence.get('scriptable_key', None)
    self.failUnless(scriptable_key is not None)
    role_key = sequence.get('role_key', None)
    self.failUnless(role_key is not None)
    local_role_key = sequence.get('local_role_key', None)
    self.failUnless(local_role_key is not None)

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
    # scriptable keys
    sql_catalog_scriptable_keys = list(catalog.sql_catalog_scriptable_keys)
    sql_catalog_scriptable_keys.remove(scriptable_key)
    sql_catalog_scriptable_keys.sort()
    catalog.sql_catalog_scriptable_keys = tuple(sql_catalog_scriptable_keys)
    self.failUnless(scriptable_key not in catalog.sql_catalog_scriptable_keys)
    # role keys
    sql_catalog_role_keys = list(catalog.sql_catalog_role_keys)
    sql_catalog_role_keys.remove(role_key)
    sql_catalog_role_keys.sort()
    catalog.sql_catalog_role_keys = tuple(sql_catalog_role_keys)
    self.failUnless(role_key not in catalog.sql_catalog_role_keys)
    # local_role keys
    sql_catalog_local_role_keys = list(catalog.sql_catalog_local_role_keys)
    sql_catalog_local_role_keys.remove(local_role_key)
    sql_catalog_local_role_keys.sort()
    catalog.sql_catalog_local_role_keys = tuple(sql_catalog_local_role_keys)
    self.failUnless(local_role_key not in catalog.sql_catalog_local_role_keys)

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
    scriptable_key = sequence.get('scriptable_key', None)
    self.failUnless(scriptable_key is not None)
    role_key = sequence.get('role_key', None)
    self.failUnless(role_key is not None)
    local_role_key = sequence.get('local_role_key', None)
    self.failUnless(local_role_key is not None)

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
    # scriptable key
    self.failUnless(scriptable_key in catalog.sql_catalog_scriptable_keys)
    # role key
    self.failUnless(role_key in catalog.sql_catalog_role_keys)
    # local_role key
    self.failUnless(local_role_key in catalog.sql_catalog_local_role_keys)

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
    scriptable_key = sequence.get('scriptable_key', None)
    self.failUnless(scriptable_key is not None)
    role_key = sequence.get('role_key', None)
    self.failUnless(role_key is not None)
    local_role_key = sequence.get('local_role_key', None)
    self.failUnless(local_role_key is not None)

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
    # scriptable key
    self.failUnless(scriptable_key not in catalog.sql_catalog_scriptable_keys)
    # role key
    self.failUnless(role_key not in catalog.sql_catalog_role_keys)
    # local_role key
    self.failUnless(local_role_key not in catalog.sql_catalog_local_role_keys)

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

  # Local Roles
  def stepCreateLocalRoles(self, sequence=None, sequence_list=None, **kw):
    """
    Create local roles
    """
    new_local_roles = {'ac':['Owner', 'Manager'],
                       'group_function': ['Auditor']}
    new_local_group_roles = {'role:Authenticated':['Owner', 'Manager']}
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.failUnless(module is not None)
    module.__ac_local_roles__ = new_local_roles
    module.__ac_local_group_roles__ = new_local_group_roles
    self.assertEquals(module.__ac_local_roles__, new_local_roles)
    self.assertEquals(module.__ac_local_group_roles__, new_local_group_roles)
    sequence.edit(local_roles=new_local_roles, local_group_roles=new_local_group_roles)

  def stepRemoveLocalRoles(self, sequence=None, sequence_list=None, **kw):
    """
    Remove local roles
    """
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.failUnless(module is not None)
    module.__ac_local_roles__ = {'someone_else': ['Associate']}
    module.__ac_local_group_roles__ = {}
    new_local_roles = sequence.get('local_roles')
    new_local_group_roles = sequence.get('local_group_roles')
    self.assertNotEquals(module.__ac_local_roles__, new_local_roles)
    self.assertNotEquals(module.__ac_local_group_roles__, new_local_group_roles)

  def stepAddLocalRolesToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Local Roles to Business Template
    """
    module_id = sequence.get('module_id')
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    bt.edit(template_local_roles_list=[module_id])

  def stepCheckLocalRolesExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of local roles
    """
    new_local_roles = sequence.get('local_roles')
    new_local_group_roles = sequence.get('local_group_roles')
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.failUnless(module is not None)
    self.assertEquals(module.__ac_local_roles__, new_local_roles)
    self.assertEquals(module.__ac_local_group_roles__, new_local_group_roles)

  def stepCheckLocalRolesRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check non-presence of local roles
    """
    new_local_roles = sequence.get('local_roles')
    new_local_group_roles = sequence.get('local_group_roles')
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.failUnless(module is not None)
    self.assertNotEquals(module.__ac_local_roles__, new_local_roles)
    self.assertNotEquals(module.__ac_local_group_roles__, new_local_group_roles)

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
    sequence.edit(ps_title=ps_title, ps_path=file_path, ps_data=ps_data)

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
    ps_data = sequence.get('ps_data', None)
    self.failUnless(ps_path is not None)
    self.failUnless(os.path.exists(ps_path))
    # check data in property sheet
    f = file(ps_path, 'r')
    data = f.read()
    self.assertEqual(data, ps_data)

  def stepCheckPropertySheetRemoved(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Property Sheet
    """
    ps_path = sequence.get('ps_path', None)
    self.failUnless(ps_path is not None)
    self.failIf(os.path.exists(ps_path))

  def stepCreateUpdatedPropertySheet(self, sequence=None, sequence_list=None, **kw):
    """
    Create a Property Sheet
    """
    ps_title = 'UnitTest'
    ps_data =  ' \nclass UnitTest2: \n  """ \n  Second Fake property sheet for unit test \n \
    """ \n  _properties = ( \n  ) \n  _categories = ( \n  ) \n\n'
    cfg = getConfiguration()
    file_path = os.path.join(cfg.instancehome, 'PropertySheet', ps_title+'.py')
    if os.path.exists(file_path):
      os.remove(file_path)
    f = file(file_path, 'w')
    f.write(ps_data)
    f.close()
    self.failUnless(os.path.exists(file_path))
    sequence.edit(ps_data_u=ps_data)

  def stepCheckUpdatedPropertySheetExists(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Property Sheet
    """
    ps_path = sequence.get('ps_path', None)
    ps_data = sequence.get('ps_data_u', None)
    self.failUnless(ps_path is not None)
    self.failUnless(os.path.exists(ps_path))
    # check data in property sheet
    f = file(ps_path, 'r')
    data = f.read()
    self.assertEqual(data, ps_data)

  # Test Constraint
  def stepCreateConstraint(self, sequence=None, sequence_list=None, **kw):
    """
    Create a Constraint
    """
    ct_title = 'UnitTest'
    ct_data =  ' \nclass UnitTest: \n  """ \n  Fake constraint for unit test \n \
    """ \n  _properties = ( \n  ) \n  _categories = ( \n  ) \n\n'
    cfg = getConfiguration()
    file_path = os.path.join(cfg.instancehome, 'Constraint', ct_title+'.py')
    if os.path.exists(file_path):
      os.remove(file_path)
    f = file(file_path, 'w')
    f.write(ct_data)
    f.close()
    self.failUnless(os.path.exists(file_path))
    sequence.edit(ct_title=ct_title, ct_path=file_path, ct_data=ct_data)

  def stepAddConstraintToBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Add Constraint to Business Template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    ct_title = sequence.get('ct_title', None)
    self.failUnless(ct_title is not None)
    bt.edit(template_constraint_id_list=[ct_title])

  def stepRemoveConstraint(self, sequence=None, sequencer_list=None, **kw):
    """
    Remove Constraint
    """
    ct_path = sequence.get('ct_path', None)
    self.failUnless(ct_path is not None)
    self.failUnless(os.path.exists(ct_path))
    os.remove(ct_path)
    self.failIf(os.path.exists(ct_path))

  def stepCheckConstraintExists(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Constraint
    """
    ct_path = sequence.get('ct_path', None)
    ct_data = sequence.get('ct_data', None)
    self.failUnless(ct_path is not None)
    self.failUnless(os.path.exists(ct_path))
    # check data in property sheet
    f = file(ct_path, 'r')
    data = f.read()
    self.assertEqual(data, ct_data)

  def stepCheckConstraintRemoved(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Constraint
    """
    ct_path = sequence.get('ct_path', None)
    self.failUnless(ct_path is not None)
    self.failIf(os.path.exists(ct_path))

  def stepCreateUpdatedConstraint(self, sequence=None, sequence_list=None, **kw):
    """
    Create a Constraint
    """
    ct_title = 'UnitTest'
    ct_data =  ' \nclass UnitTest2: \n  """ \n  Second Fake constraint for unit test \n \
    """ \n  _properties = ( \n  ) \n  _categories = ( \n  ) \n\n'
    cfg = getConfiguration()
    file_path = os.path.join(cfg.instancehome, 'Constraint', ct_title+'.py')
    if os.path.exists(file_path):
      os.remove(file_path)
    f = file(file_path, 'w')
    f.write(ct_data)
    f.close()
    self.failUnless(os.path.exists(file_path))
    sequence.edit(ct_data_u=ct_data)

  def stepCheckUpdatedConstraintExists(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Constraint
    """
    ct_path = sequence.get('ct_path', None)
    ct_data = sequence.get('ct_data_u', None)
    self.failUnless(ct_path is not None)
    self.failUnless(os.path.exists(ct_path))
    # check data in property sheet
    f = file(ct_path, 'r')
    data = f.read()
    self.assertEqual(data, ct_data)

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

  def stepAddExtraSlashesToTemplatePath(self, sequence=None, sequence_list=None, **kw):
    """Add extra slashes to the template path for testing.
    """
    template_path = sequence.get('template_path')
    sequence.edit(template_path = template_path + '//')

  def stepInstallBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Install importzed business template
    """
    import_bt = sequence.get('import_bt')
    import_bt.install(force=1)

  def stepReinstallBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Install importzed business template
    """
    import_bt = sequence.get('current_bt')
    diff_list = import_bt.BusinessTemplate_getModifiedObject()
    self.assertTrue('portal_types/Geek Object/view' in [line.object_id for line in diff_list])
    import_bt.reinstall()

  def stepInstallCurrentBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Install importzed business template
    """
    import_bt = sequence.get('current_bt')
    import_bt.install(force=1)

  def stepInstallWithoutForceBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Install importzed business template
    """
    import_bt = sequence.get('import_bt')
    object_list = import_bt.preinstall()
    install_object_dict = {}
    for obj in object_list.keys():
      state = object_list[obj][0]
      if state == 'Removed':
        install_state = 'save_and_remove'
      elif state == 'Modified':
        install_state = 'backup'
      elif state == 'New':
        install_state = 'install'
      else:
        install_state = ""
      install_object_dict[obj] = install_state
    import_bt.install(force=0, object_to_update=install_object_dict)

  def stepInstallDuplicatedBusinessTemplate(self, sequence=None,
                                            sequence_list=None, **kw):
    """
    Install importzed business template
    """
    import_bt = sequence.get('import_bt')
    pt_id = sequence.get('object_ptype_id')
    object_to_update = {
      'portal_types/%s' % pt_id: 'install'}
    import_bt.install(object_to_update=object_to_update)

  def stepPartialCatalogMethodInstall(self, sequence=None, sequence_list=None, **kw):
    """
    Install importzed business template
    """
    import_bt = sequence.get('import_bt')
    pc = self.getCatalogTool()
    catalog_id = pc.getSQLCatalog().id
    object_to_update = {'portal_catalog/'+catalog_id+'/z_another_fake_method':'install'}
    import_bt.install(object_to_update=object_to_update)

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

  def stepCreateSecondBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Create a second Business Template
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.failUnless(template.getBuildingState() == 'draft')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.edit(title='geek template',
                  version='2.0',
                  description='bt for unit_test')
    sequence.edit(second_export_bt=template)

  def stepCreateDuplicatedBusinessTemplate(self, sequence=None,
                                           sequence_list=None, **kw):
    """
    Create a new Business Template which will duplicate
    the configuration.
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.failUnless(template.getBuildingState() == 'draft')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.edit(title='duplicated geek template',
                  version='1.0',
                  description='bt for unit_test')
    sequence.edit(
        export_bt=template,
        previous_bt=sequence.get('current_bt'))

  def stepBuildBusinessTemplateFail(self, sequence=None, sequence_list=None, **kw):
    """
    Build Business Template
    """
    template = sequence.get('current_bt')
    self.assertRaises(AttributeError,
                      template.build)

  def stepCheckBuildWithBadPortalTypeFailed(self, sequence=None, sequence_list=None, **kw):
    """
    Build Business Template
    """
    template = sequence.get('current_bt')
    self.assertRaises(ValueError,
                      template.build)

  def stepBuildBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Build Business Template
    """
    template = sequence.get('current_bt')
    template.build()

  def stepEditBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Edit Business Template
    """
    template = sequence.get('current_bt')
    template.edit()

  def stepSaveBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Export Business Template
    """
    template = sequence.get('current_bt')
    cfg = getConfiguration()
    bt_title = pathname2url(template.getTitle())
    template_path = os.path.join(cfg.instancehome, 'tests', '%s' % (bt_title,))
    # remove previous version of bt it exists
    if os.path.exists(template_path):
      shutil.rmtree(template_path)
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

  def stepCheckUnindexActivityPresence(self, sequence=None, sequence_list=None, **kw):
    """
    Check if we have activity for unindex
    """
    message_list = [ m for m in self.portal.portal_activities.getMessageList()
                     if m.method_id == 'unindexObject'
                     and m.kw.get('uid') is not None ]
    self.assertEquals(len(message_list), 0)

  def stepCheckPathNotUnindexAfterBuild(self, sequence=None, sequence_list=None, **kw):
    """
    Check that after a build, not unindex has been done
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    path = 'portal_categories/'+bc_id
    category_id_list = sequence.get('category_id_list')
    portal = self.getPortal()
    ob = portal.unrestrictedTraverse(path)
    self.failUnless(ob is not None)
    for id_ in category_id_list:
      cat = ob[id_]
      catalog_ob_list = [x.getObject() for x in portal.portal_catalog(uid=cat.getUid())]
      self.failUnless(len(catalog_ob_list) > 0)

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

  def stepUninstallPreviousBusinessTemplate(self, sequence=None,
                                            sequence_list=None, **kw):
    """
    Uninstall current Business Template
    """
    bt = sequence.get('previous_bt')
    bt.uninstall()

  def stepClearBusinessTemplateField(self, sequence=None, sequence_list=None, **kw):
    """
    Clear business template field
    """
    bt = sequence.get('current_bt')
    prop_dict = {}
    for prop in bt.propertyMap():
      prop_type = prop['type']
      pid = prop['id']
      if pid in ('id', 'uid', 'rid', 'sid', 'id_group', 'last_id',
                'install_object_list_list', 'title', 'version', 'description'):
          continue
      if prop_type == 'text' or prop_type == 'string':
        prop_dict[pid] = ''
      elif prop_type == 'int':
        prop_dict[pid] = 0
      elif prop_type == 'lines' or prop_type == 'tokens':
        prop_dict[pid[:-5]] = ()
    bt.edit(**prop_dict)

  def stepRemoveSimulationTool(self, sequence=None, sequence_list=None, **kw):
    """
    Remove Trash Tool from site
    """
    p = self.getPortal()
    p.manage_delObjects(['portal_simulation'])
    self.failUnless(p._getOb('portal_simulation', None) is None)

  def stepCheckSimulationToolExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check presence of trash tool
    """
    self.failUnless(self.getSimulationTool() is not None)

  def stepCheckSubobjectsNotIncluded(self, sequence=None,
                                     sequence_list=None, **kw):
    """Check subobjects are not included in the base category.
    """
    base_category_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    # XXX maybe too low level
    base_category_obj = bt._category_item._objects.get(
        'portal_categories/%s' % base_category_id)
    self.failUnless(base_category_obj is not None)
    self.assertEquals(len(base_category_obj.objectIds()), 0)

  def stepCheckInitialRevision(self, sequence=None, sequence_list=None, **kw):
    """ Check if revision of a new bt is an empty string
    """
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getRevision(), '')

  def stepCheckFirstRevision(self, sequence=None, sequence_list=None, **kw):
    """ Check if revision of the bt is 1
    """
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getRevision(), '1')

  def stepCheckSecondRevision(self, sequence=None, sequence_list=None, **kw):
    """ Check if revision of the bt is 2
    """
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getRevision(), '2')

  def stepCheckNoMissingDependencies(self, sequence=None, sequence_list=None, **kw):
    """ Check if bt has no missing dependency
    """
    missing_dep = False
    bt = sequence.get('current_bt')
    try:
      bt.checkDependencies()
    except:
      missing_dep = True
    self.failUnless(not missing_dep)

  def stepCheckMissingDependencies(self, sequence=None, sequence_list=None, **kw):
    """ Check if bt has missing dependency
    """
    missing_dep = False
    bt = sequence.get('current_bt')
    try:
      bt.checkDependencies()
    except:
      missing_dep = True
    self.failUnless(missing_dep)

  def stepAddDependency(self, sequence=None, sequence_list=None, **kw):
    """ Add a dependency to the business template
    """
    bt = sequence.get('current_bt')
    bt.setDependencyList(['dependency_bt',])

  def stepCreateDependencyBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
      Create a new Business Template
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.failUnless(template.getBuildingState() == 'draft')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.edit(title='dependency_bt',
                  version='1.0',
                  description='bt for unit_test')
    sequence.edit(dependency_bt=template)

  # tests
  def test_Title(self):
    """Tests the Title of the Template Tool."""
    self.assertEquals('Template Tool', self.getTemplateTool().Title())

  def test_01_checkNewSite(self, quiet=quiet, run=run_all_test):
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
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test of portal types
  def test_02_BusinessTemplateWithPortalTypes(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_021_BusinessTemplateWithPortalTypesAndWrongValues(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Portal Types and Bad Values'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       FillWrongPortalTypesFields \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckBuildWithBadPortalTypeFailed \
                       RemovePortalType \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test of skins
  def test_03_BusinessTemplateWithSkins(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckSkinFolderExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckSkinFolderRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test of workflow
  def test_04_BusinessTemplateWithWorkflow(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Workflow'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateWorkflow \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckWorkflowExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckWorkflowRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_041_BusinessTemplateWithWorkflowRemoved(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Remove Of Workflow'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateWorkflow \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckWorkflowExists \
                       CheckWorkflowChainExists \
                       CreateSecondBusinessTemplate \
                       UseSecondBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckSkinsLayers \
                       CheckWorkflowRemoved \
                       CheckWorkflowChainRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test of module
  def test_05_BusinessTemplateWithModule(self, quiet=quiet, run=run_all_test):
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
                       FillPortalTypesFields \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckModulePermissions \
                       CheckModuleObjectsRemoved \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckModuleRemoved \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test of categories
  def test_06_BusinessTemplateWithBaseCategory(self, quiet=quiet, run=run_all_test):
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
                       Tic \
                       CheckBaseCategoryRemoved \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckBaseCategoryExists \
                       SaveBaseCategoryUid \
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
                       CheckBaseCategoryExists \
                       CheckBaseCategoryUid \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckBaseCategoryRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test of actions
  def test_07_BusinessTemplateWithOneAction(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With One Action'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateFirstAction \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckFirstActionExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_07_BusinessTemplateWithEmptyAction(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template Upgrade With Empty Action'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateFirstAction \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       CreateEmptyAction \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckFirstActionExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_08_BusinessTemplateWithTwoActions(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Two Actions'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateFirstAction \
                       CreateSecondAction \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddSecondActionToBusinessTemplate \
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
                       CreateFirstAction \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckFirstActionExists \
                       CheckSecondActionExists \
                       CheckActionsOrder \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckSecondActionNotExists \
                       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_09_BusinessTemplateWithPath(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckBaseCategoryExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckBaseCategoryRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_091_BusinessTemplateDoNotUnindexObject(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template Do Not Unindex Object At Build'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    # a simple path
    sequence_string = '\
                       CreateBaseCategory \
                       CreateCategories \
                       CreateNewBusinessTemplate \
                       Tic \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddBaseCategoryAsPathToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckUnindexActivityPresence \
                       Tic \
                       CheckPathNotUnindexAfterBuild \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       RemoveBaseCategory \
                       '

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_10_BusinessTemplateWithPathAndJoker1(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckCategoriesExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckCategoriesRemoved \
                       RemoveBaseCategory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_101_BusinessTemplateUninstallWithPathAndJoker1Removed(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template Uninstall With Path And Joker * Removed'
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckCategoriesExists \
                       RemoveCategories \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckCategoriesRemoved \
                       RemoveBaseCategory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_11_BusinessTemplateWithPathAndJoker2(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
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
    sequence_list.play(self, quiet=quiet)

  def test_111_BusinessTemplateWithContentTypeRegistry(self, quiet=quiet, run=run_all_test):
    """
      Test if content_type_registry is propertly exported and installed within
      business template (as path).
      This test shows that there is a slight issue - when the bt that brought
      content_type_registry is uninstalled, the registry is removed altogether,
      not restored, which maybe is an issue and maybe not.
      The sequence string does not do CheckNoTrashBin after installing
      template because there is the old registry (I think) and it is ok.
    """
    if not run: return
    if not quiet:
      message = 'Test Business Template With Content Type Registry As Path'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    # a simple path
    sequence_string = '\
                       AddEntryToContentTypeRegistry \
                       CheckContentTypeRegistryHasNewEntry \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddContentTypeRegistryAsPathToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveContentTypeRegistryNewEntry \
                       CheckContentTypeRegistryHasNoNewEntry \
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
                       CheckSkinsLayers \
                       CheckContentTypeRegistryHasNewEntry \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_12_BusinessTemplateWithCatalogMethod(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
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
    sequence_list.play(self, quiet=quiet)

  def test_13_BusinessTemplateWithRole(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckRoleExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckRoleRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_14_BusinessTemplateWithLocalRoles(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Local Roles'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateModuleAndObjects \
                       CreateLocalRoles \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddLocalRolesToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveLocalRoles \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckLocalRolesExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckLocalRolesRemoved \
                       RemoveModule \
                       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_15_BusinessTemplateWithPropertySheet(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckPropertySheetExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPropertySheetRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_155_BusinessTemplateUpdateWithPropertySheet(self, quiet=quiet, run=run_all_test):
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckPropertySheetExists \
                       RemovePropertySheet \
                       CreateUpdatedPropertySheet \
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
                       CreatePropertySheet \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckUpdatedPropertySheetExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPropertySheetRemoved \
                       CheckWorkflowChainRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_156_BusinessTemplateWithConstraint(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Constraint'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateConstraint \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddConstraintToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveConstraint \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckConstraintExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckConstraintRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_157_BusinessTemplateUpdateWithConstraint(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Constraint'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateConstraint \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddConstraintToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveConstraint \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckConstraintExists \
                       RemoveConstraint \
                       CreateUpdatedConstraint \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddConstraintToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CreateConstraint \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckUpdatedConstraintExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckConstraintRemoved \
                       CheckWorkflowChainRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_16_BusinessTemplateWithAllItems(self, quiet=quiet, run=run_all_test):
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
                       CreateFirstAction \
                       CreateSecondAction \
                       CreateCatalogMethod \
                       CreateKeysAndTable \
                       CreateRole \
                       CreateLocalRoles \
                       CreatePropertySheet \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       AddModuleToBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       AddSubCategoriesAsPathToBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
                       AddCatalogMethodToBusinessTemplate \
                       AddKeysAndTableToBusinessTemplate \
                       AddRoleToBusinessTemplate \
                       AddLocalRolesToBusinessTemplate \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckSkinFolderExists \
                       CheckBaseCategoryExists \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       CheckWorkflowExists \
                       CheckFirstActionExists \
                       CheckSecondActionExists \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       CheckRoleExists \
                       CheckLocalRolesExists \
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
    sequence_list.play(self, quiet=quiet)

  def test_17_SubobjectsAfterUpgradOfBusinessTemplate(self, quiet=quiet, run=run_all_test):
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
                       FillPortalTypesFields \
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
                       CheckNoTrashBin \
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
    sequence_list.play(self, quiet=quiet)

  def test_18_upgradeBusinessTemplateWithAllItems(self, quiet=quiet, run=run_all_test):
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
                       CreateFirstAction \
                       CreateSecondAction \
                       CreateCatalogMethod \
                       CreateKeysAndTable \
                       CreateRole \
                       CreateLocalRoles \
                       CreatePropertySheet \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       AddModuleToBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       AddSubCategoriesAsPathToBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
                       AddCatalogMethodToBusinessTemplate \
                       AddKeysAndTableToBusinessTemplate \
                       AddRoleToBusinessTemplate \
                       AddLocalRolesToBusinessTemplate \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckSkinFolderExists \
                       CheckBaseCategoryExists \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       CheckWorkflowExists \
                       CheckFirstActionExists \
                       CheckSecondActionExists \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       CheckRoleExists \
                       CheckLocalRolesExists \
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
                       CheckWorkflowBackup \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckSkinFolderExists \
                       CheckBaseCategoryExists \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       CheckWorkflowExists \
                       CheckWorkflowChainExists \
                       CheckFirstActionExists \
                       CheckSecondActionExists \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       CheckRoleExists \
                       CheckLocalRolesExists \
                       CheckPropertySheetExists \
                       CheckSkinsLayers \
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
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test specific to erp5_core
  def test_19_checkUpdateBusinessTemplateWorkflow(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Update of Business Template Workflows is working'
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
                       CreateFirstAction \
                       CreateSecondAction \
                       CreateCatalogMethod \
                       CreateKeysAndTable \
                       CreateRole \
                       CreateLocalRoles \
                       CreatePropertySheet \
                       CopyCoreBusinessTemplate \
                       UseCopyCoreBusinessTemplate  \
                       ClearBusinessTemplateField \
                       SetUpdateWorkflowFlagInBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       AddModuleToBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       AddSubCategoriesAsPathToBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
                       AddCatalogMethodToBusinessTemplate \
                       AddKeysAndTableToBusinessTemplate \
                       AddRoleToBusinessTemplate \
                       AddLocalRolesToBusinessTemplate \
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
                       CheckFirstActionExists \
                       CheckSecondActionExists \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       CheckRoleExists \
                       CheckLocalRolesExists \
                       CheckPropertySheetExists \
                       RemovePortalType \
                       RemoveModule \
                       RemoveSkinFolder \
                       RemoveBaseCategory \
                       RemoveWorkflow \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveRole \
                       RemovePropertySheet \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_20_checkUpdateTool(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Update of Tool is working'
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
                       CreateFirstAction \
                       CreateSecondAction \
                       CreateCatalogMethod \
                       CreateKeysAndTable \
                       CreateRole \
                       CreateLocalRoles \
                       CreatePropertySheet \
                       CopyCoreBusinessTemplate \
                       UseCopyCoreBusinessTemplate  \
                       ClearBusinessTemplateField \
                       SetUpdateToolFlagInBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       AddModuleToBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       AddSubCategoriesAsPathToBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
                       AddCatalogMethodToBusinessTemplate \
                       AddKeysAndTableToBusinessTemplate \
                       AddRoleToBusinessTemplate \
                       AddLocalRolesToBusinessTemplate \
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
                       RemoveSimulationTool \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckSimulationToolExists \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       CheckModuleExists \
                       CheckSkinFolderExists \
                       CheckBaseCategoryExists \
                       CheckCategoriesExists \
                       CheckSubCategoriesExists \
                       CheckWorkflowExists \
                       CheckFirstActionExists \
                       CheckSecondActionExists \
                       CheckCatalogMethodExists \
                       CheckKeysAndTableExists \
                       CheckRoleExists \
                       CheckLocalRolesExists \
                       CheckPropertySheetExists \
                       RemovePortalType \
                       RemoveModule \
                       RemoveSkinFolder \
                       RemoveBaseCategory \
                       RemoveWorkflow \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveRole \
                       RemovePropertySheet \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_21_CategoryIncludeSubobjects(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Category includes subobjects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateBaseCategory \
                       CreateCategories \
                       CreateSubCategories \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddBaseCategoryToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckSubobjectsNotIncluded \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test of portal types
  def test_22_RevisionNumberIsIncremented(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test is revision number is incremented with the bt is built'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
    		       CreatePortalType \
                       CreateNewBusinessTemplate \
		       UseExportBusinessTemplate \
		       CheckInitialRevision \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
		       stepCheckFirstRevision \
		       BuildBusinessTemplate \
		       stepCheckSecondRevision \
                       RemoveBusinessTemplate \
		       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_23_CheckNoDependencies(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test if a new Business Template has no dependencies'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
    		       CreatePortalType \
                       CreateNewBusinessTemplate \
		       UseExportBusinessTemplate \
                       CheckNoMissingDependencies \
                       RemoveBusinessTemplate \
		       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_24_CheckMissingDependency(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test if a exception is raised when a dependency is missing'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
    		       CreatePortalType \
                       CreateNewBusinessTemplate \
		       UseExportBusinessTemplate \
                       AddDependency \
                       CheckMissingDependencies \
                       RemoveBusinessTemplate \
		       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_25_CheckNoMissingDependency(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test if the dependency problem is fixed when the dependency is installed'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
    		       CreatePortalType \
                       CreateNewBusinessTemplate \
		       UseExportBusinessTemplate \
                       AddDependency \
                       CheckMissingDependencies \
                       CreateDependencyBusinessTemplate \
                       CheckMissingDependencies \
                       UseDependencyBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemovePortalType \
                       RemoveBusinessTemplate \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       CheckInstalledInstallationState \
                       UseExportBusinessTemplate \
                       CheckNoMissingDependencies \
                       UseImportBusinessTemplate \
                       UninstallBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckMissingDependencies \
                       UseImportBusinessTemplate \
                       RemoveBusinessTemplate \
                       UseExportBusinessTemplate \
                       RemoveBusinessTemplate \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # test of skins
  def test_26_ImportWithDoubleSlashes(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Importing Business Template With Double Slashes'
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
                       AddExtraSlashesToTemplatePath \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckSkinFolderExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckSkinFolderRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_27_CheckInstallWithBackup(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test if backup works during installation of a bt with subfolder in skin folder'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
    		       CreatePortalType \
                       CreateSkinFolder \
                       CheckSkinFolderExists \
                       CreateSkinSubFolder \
                       CheckSkinSubFolderExists \
                       CreateNewObjectInSkinSubFolder \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemovePortalType \
                       RemoveBusinessTemplate \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       UninstallBusinessTemplate \
                       RemoveBusinessTemplate \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_28_CheckBuildWithUnexistingPath(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test if build fails when one of the paths does not exist'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
    		       CreatePortalType \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPathToBusinessTemplate \
                       BuildBusinessTemplateFail \
                       RemoveBusinessTemplate \
                       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_29_CheckUninstallRemovedSkinFolder(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test if uninstall works even when the skin folder has already been removed from the site'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateSkinFolder \
                       CheckSkinFolderExists \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveBusinessTemplate \
                       RemovePortalType \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       RemoveSkinFolder \
                       UninstallBusinessTemplate \
                       RemoveBusinessTemplate \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_30_CheckInstalledCatalogProperties(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test if installing some new catalog properties overwrites '\
                'existing ones'
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
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       ModifyCatalogConfiguration \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       CheckCatalogConfigurationKept \
                       UninstallBusinessTemplate \
                       CheckCatalogConfigurationKept \
                       RemoveCatalogLocalConfiguration \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_31_BusinessTemplateWithCatalogMethod(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test that we keep local changes if we specify a list of objects to update'
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
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       CreateNewCatalogMethod \
                       CreateKeysAndTable \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddNewCatalogMethodToBusinessTemplate \
                       CheckCatalogMethodExists \
                       AddKeysAndTableToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       ChangePreviousCatalogMethod \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       PartialCatalogMethodInstall \
                       CheckCatalogMethodChangeKept \
                       RemoveKeysAndTable \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_32_BusinessTemplateWithDuplicatedPortalTypes(self, quiet=quiet,
                                                        run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With Duplicated Portal Types'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateFirstAction \
                       CreateSecondAction \
                       CreateWorkflow \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
                       AddSecondActionToBusinessTemplate \
                       FillPortalTypesFields \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemovePortalType \
                       RemoveWorkflow \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       \
                       CreateDuplicatedBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddDuplicatedPortalTypeToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallDuplicatedBusinessTemplate \
                       Tic \
                       \
                       CheckPortalTypeExists \
                       CheckSecondActionExists \
                       \
                       UninstallBusinessTemplate \
                       CheckDuplicatedPortalTypeRemoved \
                       UninstallPreviousBusinessTemplate \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepSetSkinFolderRegistredSelections(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    skin_folder._setProperty(
          'business_template_registered_skin_selections', ('Foo',),
          type='tokens')

  def stepCheckSkinSelectionAdded(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_paths = ps.getSkinPaths()
    # a new skin selection is added
    self.assertTrue('Foo' in ps.getSkinSelections())
    # and it contains good layers
    layers = ps.getSkinPath('Foo').split(',')
    self.assertTrue(skin_id in layers, layers)
    self.assertTrue('erp5_core' in layers, layers)
    self.assertFalse('erp5_xhtml_style' in layers, layers)

  def test_33_BusinessTemplateWithNewSkinSelection(self, quiet=quiet,
                                                        run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template With New Skin Selection'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       SetSkinFolderRegistredSelections \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveSkinFolder \
                       \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       \
                       CheckSkinSelectionAdded \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_34_UpgradeForm(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Upgrade Form'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateNewForm \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveForm \
                       \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckFormGroups \
                       AddFormField \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveFormField \
                       \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckFormGroups \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_34_UpgradeFormAttribute(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Upgrade Form'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateNewForm \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveForm \
                       \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckFormGroups \
                       ModifyFormTitle \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RevertFormTitle \
                       \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckFormTitle \
                       CheckFormGroups \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_getInstalledBusinessTemplate(self):
    self.assertNotEquals(None, self.getPortal()\
        .portal_templates.getInstalledBusinessTemplate('erp5_core'))

  def test_CompareVersions(self):
    """Tests compare version on template tool. """
    compareVersions = self.getPortal().portal_templates.compareVersions
    self.assertEquals(0, compareVersions('1', '1'))
    self.assertEquals(0, compareVersions('1.2', '1.2'))
    self.assertEquals(0, compareVersions('1.2rc3', '1.2rc3'))
    self.assertEquals(0, compareVersions('1.0.0', '1.0'))

    self.assertEquals(-1, compareVersions('1.0', '1.0.1'))
    self.assertEquals(-1, compareVersions('1.0rc1', '1.0'))
    self.assertEquals(-1, compareVersions('1.0a', '1.0.1'))
    self.assertEquals(-1, compareVersions('1.1', '2.0'))

  def test_CompareVersionStrings(self):
    """Test compareVersionStrings on template tool"""
    compareVersionStrings = \
        self.getPortal().portal_templates.compareVersionStrings
    self.assertTrue(compareVersionStrings('1.1', '> 1.0'))
    self.assertFalse(compareVersionStrings('1.1rc1', '= 1.0'))
    self.assertFalse(compareVersionStrings('1.0rc1', '> 1.0'))
    self.assertFalse(compareVersionStrings('1.0rc1', '>= 1.0'))
    self.assertTrue(compareVersionStrings('1.0rc1', '>= 1.0rc1'))

  def test_checkDependencies(self):
    from Products.ERP5Type.Document.BusinessTemplate import \
          BusinessTemplateMissingDependency
    template_tool = self.getPortal().portal_templates
    erp5_core_version = template_tool.getInstalledBusinessTemplate(
                                    'erp5_core').getVersion()
    bt5 = self.getPortal().portal_templates.newContent(
          portal_type='Business Template',
          dependency_list=['erp5_core (>= %s)' % erp5_core_version])
    self.assertEquals(None, bt5.checkDependencies())

    bt5.setDependencyList(['erp5_core (> %s)' % erp5_core_version])
    self.assertRaises(BusinessTemplateMissingDependency, bt5.checkDependencies)

    bt5.setDependencyList(['not_exists (= 1.0)'])
    self.assertRaises(BusinessTemplateMissingDependency, bt5.checkDependencies)

  def test_download_http(self):
    test_web = self.portal.portal_templates.download(
        'http://www.erp5.org/dists/snapshot/test_bt5/test_web.bt5')
    self.assertEquals(test_web.getPortalType(), 'Business Template')
    self.assertEquals(test_web.getTitle(), 'test_web')
    self.assertTrue(test_web.getRevision())

  def test_download_svn(self):
    # if the page looks like a svn repository, template tool will use pysvn to
    # get the bt5.
    test_web = self.portal.portal_templates.download(
        'https://svn.erp5.org/repos/public/erp5/trunk/bt5/test_web')
    self.assertEquals(test_web.getPortalType(), 'Business Template')
    self.assertEquals(test_web.getTitle(), 'test_web')
    self.assertTrue(test_web.getRevision())

  def stepCreateCustomWorkflow(self, sequence=None, sequence_list=None, **kw):
    """
    Create a custom workflow
    """
    pw = self.getWorkflowTool()
    pw.manage_addWorkflow('dc_workflow (Web-configurable workflow)',
                          'custom_geek_workflow')
    workflow = pw._getOb('custom_geek_workflow', None)
    self.failUnless(workflow is not None)
    sequence.edit(workflow_id=workflow.getId())
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        props['chain_%s' % id] = ','.join(wf_ids)
    key = 'chain_Geek Object'
    if props.has_key(key):
      props[key] = '%s,custom_geek_workflow' % props[key]
    else:
      props['chain_Geek Object'] = 'custom_geek_workflow'
    pw.manage_changeWorkflows('', props=props)

  def stepCreateCustomBusinessTemplate(self, sequence=None,
                                       sequence_list=None, **kw):
    """
    Create a custom Business Template
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.failUnless(template.getBuildingState() == 'draft')
    self.failUnless(template.getInstallationState() == 'not_installed')
    template.edit(title='custom geek template',
                  version='1.0',
                  description='custom bt for unit_test')
    sequence.edit(export_bt=template)

  def stepCheckCustomWorkflowChain(self, sequence=None, sequence_list=None, **kw):
    """
    Check custom workflow chain
    """
    present = 0
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    if cbt is not None:
      for id, wf_ids in cbt.items():
        if id == "Geek Object":
          present = 1
    self.assertEqual(present, 1)
    self.assertSameSet(cbt['Geek Object'],
                       ('geek_workflow', 'custom_geek_workflow'))

  def stepCheckOriginalWorkflowChain(self, sequence=None,
                                     sequence_list=None, **kw):
    """
    Check original workflow chain
    """
    present = 0
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    if cbt is not None:
      for id, wf_ids in cbt.items():
        if id == "Geek Object":
          present = 1
    self.assertEqual(present, 1)
    self.assertSameSet(cbt['Geek Object'],
                       ('geek_workflow', ))

  def stepCheckEmptyWorkflowChain(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check that workflow chain is empty
    """
    present = 0
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    if cbt is not None:
      for id, wf_ids in cbt.items():
        if id == "Geek Object":
          present = 1
          break
    if present:
      self.assertEqual(0, len(wf_ids))

  def test_34_RemovePartialWorkflowChain(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Remove Chain'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateWorkflow \
                       CheckOriginalWorkflowChain \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
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
                       CheckEmptyWorkflowChain \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       CheckOriginalWorkflowChain \
                       Tic \
                       \
                       CreateCustomWorkflow \
                       CheckCustomWorkflowChain \
                       CreateCustomBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveWorkflow \
                       CheckOriginalWorkflowChain \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       \
                       CheckCustomWorkflowChain \
                       \
                       UninstallBusinessTemplate \
                       Tic \
                       CheckOriginalWorkflowChain \
                       CheckWorkflowChainExists \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCopyBusinessTemplate(self, sequence=None, sequence_list=None, **kw):
    """
    Copy business template
    """
    portal = self.getPortalObject()
    template_tool = portal.portal_templates
    import_bt = sequence.get('current_bt')
    cb_data = template_tool.manage_copyObjects([import_bt.getId()])
    copied, = template_tool.manage_pasteObjects(cb_data)
    sequence.edit(current_bt=template_tool._getOb(copied['new_id']))

  def stepRemoveWorkflowFromBusinessTemplate(self, sequence=None,
                                             sequence_list=None, **kw):
    """
    Remove workflow to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    current_twi = list(bt.getTemplateWorkflowIdList())
    current_twi.remove(sequence.get('workflow_id', ''))
    bt.edit(template_workflow_id_list=current_twi)

  def stepRemoveWorkflowChainFromBusinessTemplate(self, sequence=None,
                                                  sequence_list=None, **kw):
    """
    Remove workflow chain to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    workflow_id = sequence.get('workflow_id', '')
    new_value = []
    workflow_chain_list = list(bt.getTemplatePortalTypeWorkflowChainList())
    for workflow_chain in workflow_chain_list:
      portal_type, wkflow_id = workflow_chain.split(' | ')
      if wkflow_id != workflow_id:
        new_value.append(workflow_chain)
    bt.edit(template_portal_type_workflow_chain_list=new_value)

  def test_35_UpdatePartialWorkflowChain(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Update Workflow Chain'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreateWorkflow \
                       CheckOriginalWorkflowChain \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
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
                       CheckEmptyWorkflowChain \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       CheckOriginalWorkflowChain \
                       Tic \
                       \
                       CreateCustomWorkflow \
                       CheckCustomWorkflowChain \
                       CreateCustomBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddWorkflowToBusinessTemplate \
                       AddWorkflowChainToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveWorkflow \
                       CheckOriginalWorkflowChain \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       \
                       CheckCustomWorkflowChain \
                       \
                       CopyBusinessTemplate \
                       Tic \
                       RemoveWorkflowFromBusinessTemplate \
                       RemoveWorkflowChainFromBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       SaveBusinessTemplate \
                       ImportBusinessTemplate \
                       Tic \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       CheckOriginalWorkflowChain \
                       CheckWorkflowChainExists \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCreatePortalTypeRole(self, sequence=None, sequence_list=None, **kw):
    """
    Create portal type role
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    object_pt.addRole(id='geek_role_definition',
                       description='A definition with non ascii chars éàè',
                       name='Geek Role Definition',
                       condition='',
                       category='group/g1\nfunction/f1\n',
                       base_category_script='Base Category Script',
                       base_category='group site',)

    sequence.edit(portal_type_role='geek_role_definition')

  def stepAddPortalTypeRolesToBusinessTemplate(self, sequence=None,
                                              sequence_list=None, **kw):
    """
    Add type role to business template
    """
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    ptype_ids = []
    ptype_ids.append(sequence.get('object_ptype_id', ''))
    ptype_ids.append(sequence.get('module_ptype_id', ''))
    self.assertEqual(len(ptype_ids), 2)
    bt.edit(template_portal_type_roles_list=ptype_ids)

  def stepCheckPortalTypeRoleExists(self, sequence=None,
                                    sequence_list=None, **kw):
    """
    Cehck that portal type role exist
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    role_list = object_pt._roles
    role_list = [x for x in role_list if x.id == 'geek_role_definition']
    self.assertEquals(1, len(role_list))
    role = role_list[0]
    self.assertEquals('Geek Role Definition', role.title)
    self.assertEquals('A definition with non ascii chars éàè', role.description)
    self.assertEquals(('group/g1','function/f1'), role.getCategory())
    self.assertEquals(('group','site'), role.getBaseCategory())
    self.assertEquals('Base Category Script', role.getBaseCategoryScript())
    # role name is a string, not unicode
    self.assertTrue(isinstance(role.id, str))

  def test_36_CheckPortalTypeRoles(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Portal Type Roles'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreatePortalType \
                       CreatePortalTypeRole \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddPortalTypeToBusinessTemplate \
                       AddPortalTypeRolesToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       RemovePortalType \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckPortalTypeExists \
                       CheckPortalTypeRoleExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepModifyPortalType(self, sequence=None, sequence_list=None, **kw):
    """
    Modify Portal Type
    """
    pt = self.getTypeTool()
    object_type = pt._getOb('Geek Object', None)
    object_type.title = 'Modified %s' % object_type.title

  def stepUnmodifyPortalType(self, sequence=None, sequence_list=None, **kw):
    """
    Unmodify Portal Type
    """
    pt = self.getTypeTool()
    object_type = pt._getOb('Geek Object', None)
    object_type.title = object_type.title[len('Modified '):]

  def stepCheckModifiedPortalTypeExists(self, sequence=None,
                                        sequence_list=None, **kw):
    """
    Check presence of modified portal type
    """
    self.stepCheckPortalTypeExists(sequence=sequence,
                                   sequence_list=sequence_list, **kw)
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_type = pt._getOb(object_id, None)
    self.failUnless(object_type.title.startswith('Modified '))

  def test_37_UpdatePortalType(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Update Portal Type'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()

    sequence_string = '\
                       CreatePortalType \
                       CreateFirstAction \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemovePortalType \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       CheckFirstActionExists \
                       \
                       CreateSecondAction \
                       CheckSecondActionExists \
                       CreatePortalTypeRole \
                       CheckPortalTypeRoleExists \
                       \
                       ModifyPortalType \
                       \
                       CopyBusinessTemplate \
                       Tic \
                       EditBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       SaveBusinessTemplate \
                       \
                       UnmodifyPortalType \
                       \
                       ImportBusinessTemplate \
                       Tic \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckModifiedPortalTypeExists \
                       CheckFirstActionExists \
                       CheckSecondActionExists \
                       CheckPortalTypeRoleExists \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_38_CheckReinstallation(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Reinstallation'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()

    sequence_string = '\
                       CreatePortalType \
                       CreateFirstAction \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       InstallCurrentBusinessTemplate Tic \
                       Tic \
                       RemoveViewAction \
                       ReinstallBusinessTemplate Tic \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepSetOldSitePropertyValue(self, sequence=None, sequence_list=None, **kw):
    """Set the old value to a site property."""
    sequence.set('site_property_value', 'old')

  def stepSetNewSitePropertyValue(self, sequence=None, sequence_list=None, **kw):
    """Set the new value to a site property."""
    sequence.set('site_property_value', 'new')

  def stepCreateSiteProperty(self, sequence=None, sequence_list=None, **kw):
    """Create a site property."""
    portal = self.getPortal()
    portal._setProperty('a_property', sequence.get('site_property_value'))

  def stepModifySiteProperty(self, sequence=None, sequence_list=None, **kw):
    """Modify a site property."""
    portal = self.getPortal()
    portal._updateProperty('a_property', sequence.get('site_property_value'))

  def stepCheckSiteProperty(self, sequence=None, sequence_list=None, **kw):
    """Check a site property."""
    portal = self.getPortal()
    self.assertEquals(portal.getProperty('a_property'),
                      sequence.get('site_property_value'))

  def stepCheckSitePropertyRemoved(self, sequence=None, sequence_list=None, **kw):
    """Check if a site property is removed."""
    portal = self.getPortal()
    self.failIf(portal.hasProperty('a_property'))

  def stepAddSitePropertyToBusinessTemplate(self, sequence=None, sequence_list=None,
                                            **kw):
    """Add a site property into a business template."""
    bt = sequence.get('current_bt', None)
    self.failUnless(bt is not None)
    bt.edit(template_site_property_id_list=('a_property',))

  def stepCheckSkinSelectionRemoved(self, sequence=None, sequence_list=None, **kw):
    """
    Check that a skin selection has been removed.
    """
    self.assertTrue('Foo' not in self.portal.portal_skins.getSkinSelections())

  def stepUserDisableSkinSelectionRegistration(self, sequence=None, sequence_list=None, **kw):
    """
    Simulate User disabling skin registration from UI.
    """
    self.app.REQUEST.set('your_register_skin_selection', 0)

  def stepUserSelectSkinToBeChanged(self, sequence=None, sequence_list=None, **kw):
    """
    User selects skin to be changed from UI.
    """
    select_skin_to_be_changed_list = self.portal.portal_skins.getSkinSelections()[:1]
    select_skin_not_to_be_changed_list = self.portal.portal_skins.getSkinSelections()[1:]
    sequence.edit(select_skin_to_be_changed_list = select_skin_to_be_changed_list, \
                  select_skin_not_to_be_changed_list = select_skin_not_to_be_changed_list)
    self.app.REQUEST.set('your_skin_layer_list', select_skin_to_be_changed_list)

  def stepCheckUserSelectedSkinToBeChanged(self, sequence=None, sequence_list=None, **kw):
    """
    Check that only selected to be changed skins are affected.
    """
    skin_folder_id = sequence.get('skin_folder_id')
    select_skin_to_be_changed_list = sequence.get('select_skin_to_be_changed_list')
    select_skin_not_to_be_changed_list = sequence.get('select_skin_not_to_be_changed_list')
    for skin_name in select_skin_to_be_changed_list:
      self.assertTrue(skin_folder_id in self.portal.portal_skins.getSkinPath(skin_name))
    for skin_name in select_skin_not_to_be_changed_list:
      self.assertTrue(skin_folder_id not in self.portal.portal_skins.getSkinPath(skin_name))

  def stepCheckSkinFolderPriorityOn(self, sequence=None, sequence_list=None, **kw):
    """
    Check skin folder priority
    """
    ps = self.portal.portal_skins
    for skin in ps.getSkinSelections():
      self.assertEquals('erp5_core', ps.getSkinPath(skin).split(',')[0])
      self.assertEquals('erp5_geek', ps.getSkinPath(skin).split(',')[1])

  def stepCheckSkinFolderPriorityOff(self, sequence=None, sequence_list=None, **kw):
    """
    Check skin folder priority off
    """
    ps = self.portal.portal_skins
    for skin in ps.getSkinSelections():
      self.assertEquals('erp5_geek', ps.getSkinPath(skin).split(',')[0])
      self.assertEquals('erp5_core', ps.getSkinPath(skin).split(',')[1])

  def stepUserDisableSkinFolderPriority(self, sequence=None, sequence_list=None, **kw):
    """
    User chooses skin folder priority off from UI
    """
    self.app.REQUEST.set('your_reorder_skin_selection', 0)

  def stepSetExistingSkinFolderPriority(self, sequence=None, sequence_list=None, **kw):
    """
    Set exisitng skin priority for test
    """
    skin_folder = self.portal.portal_skins['erp5_core']
    if not skin_folder.hasProperty('business_template_skin_layer_priority'):
      skin_folder.manage_addProperty('business_template_skin_layer_priority', \
                                     10000.0, 'float')

  def stepSetBusinessTemplateSkinFolderPriority(self, sequence=None, sequence_list=None, **kw):
    """
    Set skin folder priority.
    """
    skin_folder_id = sequence.get('skin_folder_id')
    skin_folder = self.portal.portal_skins[skin_folder_id]
    skin_folder.manage_addProperty('business_template_skin_layer_priority', 9999.0, 'float')

  def test_39_CheckSiteProperties(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Site Properties'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       SetOldSitePropertyValue \
                       CreateSiteProperty \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       AddSitePropertyToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       SetNewSitePropertyValue \
                       ModifySiteProperty \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       SetOldSitePropertyValue \
                       CheckSiteProperty \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       SetOldSitePropertyValue \
                       CheckSitePropertyRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_158_BusinessTemplateSkinSelectionRemove(self, quiet=quiet,
                                                        run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template Uninstall With Skin Selection'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = 'CreateSkinFolder \
                       SetSkinFolderRegistredSelections \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveSkinFolder \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       CheckSkinSelectionAdded \
                       UninstallBusinessTemplate \
                       CheckSkinSelectionRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_159_BusinessTemplateNotRegisterSkin(self, quiet=quiet,
                                                        run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template will not register existing Skin'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = 'CreateSkinFolder \
                       SetSkinFolderRegistredSelections \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveSkinFolder \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       UserDisableSkinSelectionRegistration \
                       InstallBusinessTemplate \
                       Tic \
                       CheckSkinSelectionRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_160_BusinessTemplateChangeOnlySelectedSkin(self, quiet=quiet,
                                                        run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template will change only selected skins'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = 'CreateSkinFolder \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveSkinFolder \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       UserSelectSkinToBeChanged \
                       InstallBusinessTemplate \
                       Tic \
                       CheckUserSelectedSkinToBeChanged \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_161_BusinessTemplateCheckSkinPriorityOrderingEnabled(self, quiet=quiet,
                                                        run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template will reorder skins path in Skin'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = 'CreateSkinFolder \
                       SetBusinessTemplateSkinFolderPriority \
                       SetExistingSkinFolderPriority \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveSkinFolder \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       CheckSkinFolderPriorityOn \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_162_BusinessTemplateCheckSkinPriorityOrderingDisabled(self, quiet=quiet,
                                                        run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Business Template will not reorder skins path in Skin'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = 'CreateSkinFolder \
                       SetBusinessTemplateSkinFolderPriority \
                       SetExistingSkinFolderPriority \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveSkinFolder \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       UserDisableSkinFolderPriority \
                       InstallBusinessTemplate \
                       Tic \
                       CheckSkinFolderPriorityOff \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBusinessTemplate))
  return suite
