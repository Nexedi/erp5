# -*- coding: utf-8 -*-
##############################################################################
#
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
import logging
from unittest import expectedFailure, skip

from AccessControl import getSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Acquisition import aq_base
from OFS.SimpleItem import SimpleItem
from App.config import getConfiguration
from Products.ERP5Type.tests.Sequence import SequenceList, Sequence
from urllib import pathname2url
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken
from Products.ERP5Type.tests.utils import LogInterceptor
from Products.ERP5Type.Workflow import addWorkflowByType
import shutil
import os
import gc
import random
import string
import tempfile
import glob
import sys

WORKFLOW_TYPE = 'erp5_workflow'

from Products.MimetypesRegistry.common import MimeTypeException
from Products.PortalTransforms.Transform import Transform
Transform_tr_init = Transform._tr_init
Transform_manage_beforeDelete = Transform.manage_beforeDelete

from Products.ERP5.Document.Organisation import Organisation
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from ZODB.broken import Broken

instance_home = os.environ['INSTANCE_HOME']

class MockBrokenOrganisation(Organisation, Broken):
  meta_type = 'ERP5 Mock Broken Organisation'
  portal_type = 'Mock Broken Organisation'

class BusinessTemplateMixin(ERP5TypeTestCase, LogInterceptor):
  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_csv_style',
            )
  ## Ignore errors from PortalTransforms (e.g. missing binaries)

  def _catch_log_errors(self):
    LogInterceptor._catch_log_errors(self)
    level = self.level
    def _tr_init(*args, **kw):
      self.level = logging.ERROR
      try:
        Transform_tr_init(*args, **kw)
      finally:
        self.level = level
    Transform._tr_init = _tr_init
    def manage_beforeDelete(self, *args, **kw):
      try:
        Transform_manage_beforeDelete(self, *args, **kw)
      except MimeTypeException:
        assert self.output == 'BROKEN'
    Transform.manage_beforeDelete = manage_beforeDelete

  def _ignore_log_errors(self):
    Transform._tr_init = Transform_tr_init
    Transform.manage_beforeDelete = Transform_manage_beforeDelete
    LogInterceptor._ignore_log_errors(self)

  ###

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
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
      self.commit()

    # Create old static dirs for migration tests
    self.rmdir_list = []
    for d in "Constraint", "Document", "Extensions", "PropertySheet":
      d = os.path.join(instance_home, d)
      try:
        os.mkdir(d)
      except OSError:
        continue
      self.rmdir_list.append(d)
    self._has_cleared_catalog = []
    from Products.ERP5Catalog.Document.ERP5Catalog import ERP5Catalog
    orig_manage_catalogClear = ERP5Catalog.manage_catalogClear
    def manage_catalogClear(*args, **kw):
      self._has_cleared_catalog.append(None)
      return orig_manage_catalogClear(*args, **kw)
    ERP5Catalog.manage_catalogClear = manage_catalogClear

  def beforeTearDown(self):
    """Remove objects created in tests."""
    for d in getattr(self, "rmdir_list", ()):
      shutil.rmtree(d)

    pw = self.getWorkflowTool()

    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        wf_ids = list(wf_ids)
        if 'geek_workflow' in wf_ids:
          wf_ids.remove('geek_workflow')
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
    if 'erp5_static' in self.getSkinsTool().objectIds():
      self.getSkinsTool().manage_delObjects(['erp5_static'])
      ps = self.getSkinsTool()
      for skin_name, selection in ps.getSkinPaths():
        new_selection = []
        selection = selection.split(',')
        for skin_id in selection:
          if skin_id != 'erp5_static':
            new_selection.append(skin_id)
        ps.manage_skinLayers(skinpath=tuple(new_selection),
                             skinname=skin_name, add_skin=1)

    if 'Foo' in self.getSkinsTool().getSkinSelections():
      self.getSkinsTool().manage_skinLayers(chosen=('Foo',), del_skin=1)

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
    self.stepRemoveAllTrashBins()
    catalog = self.portal.portal_catalog.erp5_mysql_innodb
    for method_id in ('z_fake_method', 'z_another_fake_method'):
      if method_id in catalog.objectIds():
        catalog.manage_delObjects([method_id])
      sql_uncatalog_object = list(catalog.sql_uncatalog_object)
      if method_id in sql_uncatalog_object:
        sql_uncatalog_object.remove(method_id)
        sql_uncatalog_object.sort()
        catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
      try:
        del catalog._getFilterDict()[method_id]
      except KeyError:
        pass
    for obj_id in ('another_file', 'test_document', 'dummy_type_provider'):
      if obj_id in self.portal.objectIds():
        self.portal.manage_delObjects([obj_id])
    types_tool = self.portal.portal_types
    registered_type_provider_list = list(types_tool.type_provider_list)
    if 'dummy_type_provider' in registered_type_provider_list:
      registered_type_provider_list.remove('dummy_type_provider')
      types_tool.type_provider_list = tuple(registered_type_provider_list)
    property_sheet_tool = self.getPortalObject().portal_property_sheets
    for property_sheet in ('UnitTest',):
      if property_sheet in property_sheet_tool.objectIds():
        property_sheet_tool.manage_delObjects([property_sheet])
    self.commit()
    self._ignore_log_errors()

  def getBusinessTemplate(self,title):
    """
      Get a business template at portal_templates
    """
    template_tool = self.getTemplateTool()
    for bt in template_tool.objectValues(filter={'portal_type':'Business Template'}):
      if bt.getTitle() == title:
        return bt
    return None

  def stepUseCoreBusinessTemplate(self, sequence=None, **kw):
    """
    Define erp5_core as current bt
    """
    core_bt = self.getBusinessTemplate('erp5_core')
    self.assertFalse(core_bt is None)
    sequence.edit(current_bt=core_bt)

  def stepCreateTest(self, sequence=None, **kw):
    test_title = 'UnitTest'
    test_data = """class UnitTest:
  pass"""
    cfg = getConfiguration()
    file_path = os.path.join(cfg.instancehome, 'tests', test_title+'.py')
    if os.path.exists(file_path):
      os.remove(file_path)
    f = file(file_path, 'w')
    f.write(test_data)
    f.close()
    self.assertTrue(os.path.exists(file_path))
    sequence.edit(test_title=test_title, test_path=file_path,
        test_data=test_data)

  def stepAddTestToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence['current_bt']
    bt.edit(template_test_id_list=[sequence['test_title']])

  def stepRemoveTest(self, sequence=None, **kw):
    test_path = sequence['test_path']
    os.remove(test_path)
    self.assertFalse(os.path.exists(test_path))

  def stepCheckTestExists(self, sequence=None, **kw):
    self.assertFalse(not os.path.exists(sequence['test_path']))

  def stepCheckTestRemoved(self, sequence=None, **kw):
    self.assertFalse(os.path.exists(sequence['test_path']))

  def stepCopyCoreBusinessTemplate(self, sequence=None, **kw):
    """
    Copy erp5_core as new Business Template
    """
    template_tool = self.getTemplateTool()
    core_bt = self.getBusinessTemplate('erp5_core')
    self.assertFalse(core_bt is None)
    # make copy
    copy_data = template_tool.manage_copyObjects(ids=[core_bt.getId()])
    ids = template_tool.manage_pasteObjects(copy_data)
    new_id = ids[0]['new_id']
    new_bt = template_tool._getOb(new_id)
    self.assertEqual(new_bt.getTitle(), 'erp5_core')
    sequence.edit(copy_bt=new_bt)

  def stepUseCopyCoreBusinessTemplate(self, sequence=None, **kw):
    """
    Define erp5_core as current bt
    """
    bt = sequence.get('copy_bt')
    sequence.edit(current_bt=bt, export_bt=bt)

  def stepBuildCopyCoreBusinessTemplate(self, sequence=None, **kw):
    """
    Build copied core bt
    """
    bt = sequence.get('copy_bt')
    self.assertEqual(bt.getTitle(), 'erp5_core')
    bt.build()

  def stepInstallCopyCoreBusinessTemplate(self, sequence=None, **kw):
    """
    Install copied core bt
    """
    bt = sequence.get('copy_bt')
    self.assertEqual(bt.getTitle(), 'erp5_core')
    self.assertEqual(bt.getInstallationState(), 'not_installed')
    bt.install()

  def stepCheckOriginalAndCopyBusinessTemplate(self, sequence=None, **kw):
    original_bt = sequence.get('current_bt')
    copy_bt = sequence.get('copy_bt')
    self.assertEqual(original_bt.getBuildingState(), 'built')
    self.assertEqual(copy_bt.getBuildingState(), 'built')

    for item_name in original_bt._item_name_list:
      original_obj = getattr(original_bt, item_name)
      copy_obj = getattr(copy_bt, item_name)
      self.assertFalse(original_obj is None)
      self.assertFalse(copy_obj is None)
      self.failIfDifferentSet(original_obj.getKeys(), copy_obj.getKeys())

  def stepUseExportBusinessTemplate(self, sequence=None, **kw):
    """
    Define export_bt as current bt
    """
    bt = sequence.get('export_bt')
    sequence.edit(current_bt=bt)

  def stepUseSecondBusinessTemplate(self, sequence=None, **kw):
    """
    Define second_export_bt as current bt
    """
    bt = sequence.get('second_export_bt')
    sequence.edit(current_bt=bt)

  def stepUseDependencyBusinessTemplate(self, sequence=None, **kw):
    """
      Define dependency_bt as current bt
    """
    bt = sequence.get('dependency_bt')
    sequence.edit(current_bt=bt)

  def stepUseImportBusinessTemplate(self, sequence=None, **kw):
    """
    Define import_bt as current bt
    """
    bt = sequence.get('import_bt')
    sequence.edit(current_bt=bt)

  def stepCheckPreinstallReturnSomething(self, sequence=None, **kw):
    """
    In case of upgrade preinstall call must return at least one element
    which is marked as new/updated/removed
    """
    bt = sequence.get('current_bt', None)
    self.assertNotEquals(len(bt.preinstall()), 0)

  def stepCheckCatalogPreinstallReturnCatalogMethod(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertEqual(bt.preinstall(), {'portal_catalog/erp5_mysql_innodb/z_fake_method': ('Modified', 'CatalogMethod')})

  def stepCheckInstalledInstallationState(self, sequence=None, **kw):
    """
    Check if installation state is installed
    """
    bt = sequence.get('current_bt', None)
    self.assertEqual(bt.getInstallationState(), 'installed')

  def stepCheckNotInstalledInstallationState(self, sequence=None, **kw):
    """
    Check if installation state is not_installed
    """
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getInstallationState(), 'not_installed')

  def stepCheckReplacedInstallationState(self, sequence=None, seqeunce_list=None, **kw):
    """
    Check if installation state is replaced
    """
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getInstallationState(), 'replaced')

  def stepCheckModifiedBuildingState(self, sequence=None, **kw):
    """
    Check if the building state is modified.
    """
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getBuildingState(), 'modified')

  def stepCheckBuiltBuildingState(self, sequence=None, **kw):
    """
    Check if the building state is built.
    """
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getBuildingState(), 'built')

  def stepCheckTools(self, sequence=None, **kw):
    """
    Check presence of tools
    """
    self.assertTrue(self.getCategoryTool() is not None)
    self.assertTrue(self.getTemplateTool() is not None)
    self.assertTrue(self.getTypeTool() is not None)
    self.assertTrue(self.getSkinsTool() is not None)
    self.assertTrue(self.getCatalogTool() is not None)
    self.assertTrue(self.getTrashTool() is not None)

  def stepCheckSkinsLayers(self, sequence=None, **kw):
    """
    Check skins layers
    """
    skins_tool = self.getSkinsTool()
    for skin_name, selection in skins_tool.getSkinPaths():
      if skin_name == 'View':
        self.assertNotIn('erp5_csv_style', selection)
        self.assertIn('erp5_core', selection)
        self.assertIn('erp5_xhtml_style', selection)
      if skin_name == 'Print':
        self.assertIn('erp5_xhtml_style', selection)
        self.assertIn('erp5_csv_style', selection)
        self.assertNotIn('erp5_core', selection)
      if skin_name == 'CSV':
        self.assertNotIn('erp5_xhtml_style', selection)
        self.assertIn('erp5_core', selection)
        self.assertIn('erp5_csv_style', selection)

  def stepCheckNoTrashBin(self, sequence=None, **kw):
    """
    Check if there is no trash bins
    """
    trash = self.getTrashTool()
    self.assertEqual(len(trash.objectIds()), 0)

  def stepRemoveAllTrashBins(self, sequence=None, **kw):
    """
    Remove all trash bins
    """
    trash = self.getTrashTool()
    trash_ids = list(trash.objectIds())
    for id in trash_ids:
      trash.deleteContent(id)
    self.assertFalse(len(trash.objectIds()) > 0)

  def stepCheckTrashBin(self, sequence=None, **kw):
    """
    Check trash bin presence
    """
    trash = self.getTrashTool()
    trash_ids = list(trash.objectIds())
    self.assertEqual(len(trash.objectIds()), 1)
    bt_id = sequence.get('import_bt').getId()
    self.assertNotIn(bt_id, trash_ids[0])

  # portal types
  def stepCreatePortalType(self, sequence=None, **kw):
    """
    Create Portal Type
    """
    pt = self.getTypeTool()
    # create module object portal type
    object_type = pt.newContent('Geek Object', 'Base Type',
                                type_class='Person')
    self.assertTrue(object_type is not None)
    sequence.edit(object_ptype_id=object_type.getId())
    # create module portal type
    module_type = pt.newContent('Geek Module', 'Base Type',
      type_class='Folder',
      type_filter_content_type=1,
      type_allowed_content_type_list=('Geek Object',),
      type_hidden_content_type_list=('Geek Object',),
      type_base_category_list=('destination',),
      type_property_sheet_list=('Version',))
    self.assertTrue(module_type is not None)
    sequence.edit(module_ptype_id=module_type.getId(),
      module_ptype_filter_content_types=module_type.getTypeFilterContentType(),
      module_ptype_allowed_content_types=module_type.getTypeAllowedContentTypeList(),
      module_ptype_hidden_content_type_list=module_type.getTypeHiddenContentTypeList(),
      module_ptype_base_category_list=module_type.getTypeBaseCategoryList(),
      module_ptype_property_sheet_list=module_type.getTypePropertySheetList())

  def stepModifyPortalTypeInBusinessTemplate(self, sequence=None, **kw):
    """
    Modify Portal Type
    * remove Geek Object and add Geek Module in allowed_content_type
    * empty hidden_content_type
    * remove 'destination' and add 'source' in base_category_list
    * empty property_sheet_list
    """
    pt = self.getTypeTool()
    module_type = pt._getOb('Geek Module', None)
    self.assertTrue(module_type is not None)
    module_type.allowed_content_types = list(module_type.allowed_content_types) + ['Geek Module']
    module_type.base_category_list = list(module_type.base_category_list) + ['source']
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_portal_type_allowed_content_type=('Geek Module | Geek Module',),
            template_portal_type_hidden_content_type=(),
            template_portal_type_base_category=('Geek Module | source',),
            template_portal_type_property_sheet=())
    sequence.edit(module_ptype_allowed_content_types=['Geek Module'],
                  module_ptype_hidden_content_type_list=[],
                  module_ptype_base_category_list=['source'],
                  module_ptype_property_sheet_list=[])

  def stepAddPortalTypeToBusinessTemplate(self, sequence=None, **kw):
    """
    Add types to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    ptype_ids = []
    ptype_ids.append(sequence.get('object_ptype_id', ''))
    ptype_ids.append(sequence.get('module_ptype_id', ''))
    self.assertEqual(len(ptype_ids), 2)
    bt.edit(template_portal_type_id_list=ptype_ids)
    self.stepFillPortalTypesFields(sequence=sequence, **kw)

  def stepAddDuplicatedPortalTypeToBusinessTemplate(self, sequence=None, **kw):
    """
    Add duplicated portal type to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    ptype_ids = []
    ptype_ids.append(sequence.get('object_ptype_id', ''))
    self.assertEqual(len(ptype_ids), 1)
    bt.edit(template_portal_type_id_list=ptype_ids)

  def stepRemovePortalType(self, sequence=None, **kw):
    """
    Remove PortalType
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    pt.manage_delObjects([module_id, object_id])
    module_type = pt._getOb(module_id, None)
    self.assertTrue(module_type is None)
    object_type = pt._getOb(object_id, None)
    self.assertTrue(object_type is None)

  def stepRemoveFirstAction(self, sequence=None, **kw):
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    action_id = sequence.get('first_action_id')
    object_type = pt[object_id]
    action_id, = [x.getId() for x in object_type.getActionInformationList()
                            if x.getReference() == action_id]
    object_type._delObject(action_id)

  def stepCheckPortalTypeExists(self, sequence=None, **kw):
    """
    Check presence of portal type
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    module_type = pt._getOb(module_id, None)
    self.assertTrue(module_type is not None)
    self.assertEqual(module_type.getTypeAllowedContentTypeList(),
        sequence.get('module_ptype_allowed_content_types'))
    self.assertEqual(module_type.getTypeHiddenContentTypeList(),
        sequence.get('module_ptype_hidden_content_type_list'))
    self.assertEqual(module_type.getTypeFilterContentType(),
        sequence.get('module_ptype_filter_content_types'))
    self.assertEqual(module_type.getTypeBaseCategoryList(),
        sequence.get('module_ptype_base_category_list'))
    self.assertEqual(module_type.getTypePropertySheetList(),
        sequence.get('module_ptype_property_sheet_list'))
    object_type = pt._getOb(object_id, None)
    self.assertTrue(object_type is not None)

  def stepCheckPortalTypeRemoved(self, sequence=None, **kw):
    """
    Check non presence of portal type
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    module_id = sequence.get('module_ptype_id')
    module_type = pt._getOb(module_id, None)
    self.assertTrue(module_type is None)
    object_type = pt._getOb(object_id, None)
    self.assertTrue(object_type is None)

  def stepCheckDuplicatedPortalTypeRemoved(self, sequence=None, **kw):
    """
    Check non presence of portal type
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_type = pt._getOb(object_id, None)
    self.assertTrue(object_type is None)

  def stepFillPortalTypesFields(self, sequence=None, **kw):
    """
    Fill portal types properties field in business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.getPortalTypesProperties()

  def stepFillWrongPortalTypesFields(self, sequence=None, **kw):
    """
    Fill portal types properties field in business template with wrong values
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.getPortalTypesProperties()
    bt_allowed_content_type_list = list(getattr(self, 'template_portal_type_allowed_content_type', []) or [])
    bt_allowed_content_type_list.append("Geek Module | BusinessTemplate")
    bt.setProperty('template_portal_type_allowed_content_type', bt_allowed_content_type_list)

  # module
  def stepCreateModuleAndObjects(self, sequence=None, **kw):
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
    self.assertTrue(module is not None)
    # add a specific permission to module which do not use acquisition
    module.manage_permission('Copy or Move', ['Assignor'], False)
    sequence.edit(module_id=module.getId())
    module_object_list = []
    for i in xrange(10):
      object = module.newContent(portal_type = 'Geek Object')
      self.assertTrue(object is not None)
      module_object_list.append(object)
    sequence.edit(module_object_id_list=module_object_list)

  def stepAddModuleToBusinessTemplate(self, sequence=None, **kw):
    """
    Add module to business template
    """
    bt = sequence.get('current_bt', None)
    module_id = sequence.get('module_id', None)
    self.assertTrue(module_id is not None)
    bt.edit(template_module_id_list=[module_id])

  def stepCreateModuleObjects(self, sequence=None, **kw):
    """
    Create objects into module
    """
    portal = self.getPortal()
    module_id = sequence.get('module_id')
    module = portal._getOb(module_id, None)
    self.assertTrue(module is not None)
    module_object_list = []
    for i in xrange(10):
      object = module.newContent(portal_type = 'Geek Object')
      self.assertTrue(object is not None)
      module_object_list.append(object.getId())
    sequence.edit(module_object_id_list=module_object_list)

  def stepRemoveModule(self, sequence=None, **kw):
    """
    Remove Module
    """
    portal = self.getPortal()
    module_id = sequence.get("module_id")
    portal.manage_delObjects([module_id])
    self.assertFalse(portal._getOb(module_id, None) is not None)

  def stepCheckModuleExists(self, sequence=None, **kw):
    """
    Check presence of module
    """
    portal = self.getPortal()
    module_id = sequence.get("module_id")
    new_module = portal._getOb(module_id, None)
    self.assertFalse(new_module is None)

  def stepCheckModulePermissions(self, sequence=None, **kw):
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

  def stepCheckModuleObjectsExists(self, sequence=None, **kw):
    """
    Check presence of objects in module
    """
    portal = self.getPortal()
    module_id = sequence.get('module_id')
    module = portal._getOb(module_id)
    self.assertTrue(module is not None)
    object_id_list = sequence.get('module_object_id_list')
    for object_id in object_id_list:
      object = module._getOb(object_id, None)
      self.assertTrue(object is not None)

  def stepCheckModuleObjectsRemoved(self, sequence=None, **kw):
    """
    Check non presence of objects in module
    """
    portal = self.getPortal()
    module_id = sequence.get('module_id')
    module = portal._getOb(module_id)
    self.assertTrue(module is not None)
    object_id_list = sequence.get('module_object_id_list')
    for object_id in object_id_list:
      object = module._getOb(object_id, None)
      self.assertTrue(object is None)

  def stepCheckModuleRemoved(self, sequence=None, **kw):
    """
    Check non presence of module
    """
    portal = self.getPortal()
    module_id = sequence.get("module_id")
    self.assertFalse(portal._getOb(module_id, None) is not None)

  # skins folder
  def stepCreateSkinFolder(self, sequence=None, **kw):
    """
    Create a skin folder
    """
    ps = self.getSkinsTool()
    ps.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertTrue(skin_folder is not None)
    sequence.edit(skin_folder_id=skin_folder.getId())
    # add skin in layers
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      if 'erp5_geek' not in selection:
        selection.append('erp5_geek')
      ps.manage_skinLayers(skinpath = tuple(selection), skinname = skin_name, add_skin = 1)

  def stepCreateAnotherSkinFolder(self, sequence=None, **kw):
    """
    Create another skin folder
    """
    ps = self.getSkinsTool()
    ps.manage_addProduct['OFSP'].manage_addFolder('erp5_nerd')
    skin_folder = ps._getOb('erp5_nerd', None)
    self.assertTrue(skin_folder is not None)
    sequence.edit(another_skin_folder_id=skin_folder.getId())
    # add skin in layers
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      if 'erp5_nerd' not in selection:
        selection.append('erp5_nerd')
      ps.manage_skinLayers(skinpath = tuple(selection), skinname = skin_name, add_skin = 1)

  def stepCreateStaticSkinFolder(self, sequence=None, **kw):
    """
    Create a skin folder not managed by the bt5
    """
    ps = self.getSkinsTool()
    ps.manage_addProduct['OFSP'].manage_addFolder('erp5_static')
    skin_folder = ps._getOb('erp5_static', None)
    self.assertTrue(skin_folder is not None)
    sequence.edit(static_skin_folder_id=skin_folder.getId())
    # add skin in layers
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      if 'erp5_static' not in selection:
        selection.append('erp5_static')
      ps.manage_skinLayers(skinpath=tuple(selection), skinname=skin_name,
                           add_skin=1)

  def stepCreateSkinSubFolder(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertTrue(skin_folder is not None)
    skin_folder.manage_addFolder('erp5_subgeek')
    skin_subfolder = skin_folder._getOb('erp5_subgeek', None)
    self.assertTrue(skin_subfolder is not None)
    sequence.edit(skin_subfolder_id=skin_subfolder.getId())

  def stepCheckSkinSubFolderExists(self, sequence=None, **kw):
    """
    Check presence of skin sub folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    self.assertTrue(skin_folder is not None)
    subskin_id = sequence.get('skin_subfolder_id')
    skin_subfolder = skin_folder._getOb(subskin_id, None)
    self.assertTrue(skin_subfolder is not None)

  def stepCreateNewForm(self, sequence=None):
    """Create a new ERP5 Form in a skin folder."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = 'Geek_view'
    addERP5Form = skin_folder.manage_addProduct['ERP5Form'].addERP5Form
    addERP5Form(form_id, 'View')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    self.assertEqual(sorted(form.get_groups(include_empty=1)),
                      sorted(['left', 'right', 'center', 'bottom', 'hidden']))
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_title', 'Title', 'StringField')
    field = form.get_field('my_title')
    self.assertEqual(form.get_fields_in_group('left'), [field])
    group_dict = {}
    for group in form.get_groups(include_empty=1):
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      group_dict[group] = id_list
    sequence.edit(form_id=form_id, group_dict=group_dict)

  def stepCreateNewFormIntoErp5Nerd(self, sequence=None):
    """Create a new ERP5 Form in a skin folder."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_nerd', None)
    self.assertNotEquals(skin_folder, None)
    form_id = 'Geek_view'
    addERP5Form = skin_folder.manage_addProduct['ERP5Form'].addERP5Form
    addERP5Form(form_id, 'View')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    self.assertEqual(sorted(form.get_groups(include_empty=1)),
                      sorted(['left', 'right', 'center', 'bottom', 'hidden']))
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_title', 'Title', 'StringField')
    field = form.get_field('my_title')
    self.assertEqual(form.get_fields_in_group('left'), [field])
    group_dict = {}
    for group in form.get_groups(include_empty=1):
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      group_dict[group] = id_list
    sequence.edit(another_form_id=form_id)

  def stepRemoveForm(self, sequence=None):
    """Remove an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    skin_folder.manage_delObjects([form_id])
    form = skin_folder._getOb(form_id, None)
    self.assertEqual(form, None)

  def stepAddFormField(self, sequence=None):
    """Add a field to an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    self.assertEqual(sorted(form.get_groups(include_empty=1)),
                      sorted(['left', 'right', 'center', 'bottom', 'hidden']))
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_reference', 'Reference', 'StringField')
    form.move_field_group(['my_reference'], 'left', 'right')
    field = form.get_field('my_reference')
    self.assertEqual(form.get_fields_in_group('right'), [field])
    group_dict = {}
    for group in form.get_groups(include_empty=1):
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      group_dict[group] = id_list
    sequence.edit(group_dict=group_dict, field_id=field.getId())

  def stepModifyFormTitle(self, sequence=None):
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    form_title = 'First Form Title'
    form.title = form_title
    self.assertNotEquals(form, None)
    self.assertEqual(sorted(form.get_groups(include_empty=1)),
                      sorted(['left', 'right', 'center', 'bottom', 'hidden']))
    group_dict = {}
    for group in form.get_groups(include_empty=1):
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      group_dict[group] = id_list
    sequence.edit(group_dict=group_dict, field_id=field.getId(),
                  form_title=form_title)

  def stepRevertFormTitle(self, sequence=None):
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    form_title = 'Second Form Title'
    form.title = form_title

  def stepCheckFormTitle(self, sequence=None):
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertEqual('First Form Title', form.title)

  def stepCheckFormIsRemoved(self, sequence=None):
    """Check the form is exist in erp5_geek."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertEqual(form, None)

  def stepCheckFormIsNotRemovedFromErp5Nerd(self, sequence=None):
    """Check the form is not exist in erp5_nerd."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_nerd', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)

  def stepRemoveFormField(self, sequence=None):
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

  def stepCheckFormGroups(self, sequence=None):
    """Check the groups of an ERP5 Form."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    group_dict = sequence.get('group_dict')
    self.assertEqual(sorted(form.get_groups(include_empty=1)),
                      sorted(group_dict.iterkeys()))
    for group in group_dict.iterkeys():
      id_list = []
      for field in form.get_fields_in_group(group):
        id_list.append(field.getId())
      self.assertEqual(group_dict[group], id_list)

  def stepCheckFieldTitleIsNotRemovedFromErp5Nerd(self, sequence=None):
    """Check that field title is not removed form erp5_nerd."""
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_nerd', None)
    self.assertNotEquals(skin_folder, None)
    form_id = sequence.get('form_id')
    form = skin_folder._getOb(form_id, None)
    self.assertNotEquals(form, None)
    title_field =form._getOb('my_title', None)
    self.assertNotEquals(title_field, None)

  def stepCreateNewObjectInSkinSubFolder(self, sequence=None, **kw):
    """
    Create a new object in skin subfolder
    """
    ps = self.getSkinsTool()
    skin_folder = ps._getOb('erp5_geek', None)
    self.assertTrue(skin_folder is not None)
    skin_subfolder = skin_folder._getOb('erp5_subgeek', None)
    self.assertTrue(skin_subfolder is not None)
    method_id = "z_fake_method"
    addSQLMethod = skin_subfolder.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
    addSQLMethod(id=method_id, title='', connection_id='erp5_sql_connection',
                 arguments='', template='')
    zsql_method = skin_subfolder._getOb(method_id, None)
    self.assertTrue(zsql_method is not None)
    sequence.edit(zsql_method_id = method_id)

  def stepRemoveSkinFolder(self, sequence=None, **kw):
    """
    Remove Skin folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    ps.manage_delObjects([skin_id])
    skin_folder = ps._getOb(skin_id, None)
    self.assertTrue(skin_folder is None)
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      if skin_id in selection:
        selection.remove(skin_id)
      ps.manage_skinLayers(skinpath = tuple(selection), skinname = skin_name, add_skin = 1)

  def stepCheckSkinFolderExists(self, sequence=None, **kw):
    """
    Check presence of skin folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    self.assertTrue(skin_folder is not None)

  def stepCheckSkinFolderRemoved(self, sequence=None, **kw):
    """
    Check non presence of skin folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    self.assertTrue(skin_folder is None)

  def stepAddSkinFolderToBusinessTemplate(self, sequence=None, **kw):
    """
    Add skin folder to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    skin_id = sequence.get('skin_folder_id', '')
    self.assertNotEqual(skin_id, '')
    bt.edit(template_skin_id_list=[skin_id])

  def stepAddAnotherSkinFolderToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    skin_id = sequence.get('another_skin_folder_id', '')
    self.assertNotEqual(skin_id, '')
    current_skin_id_list = bt.getTemplateSkinIdList()
    template_skin_id_list = []
    template_skin_id_list.extend(current_skin_id_list)
    template_skin_id_list.append(skin_id)
    bt.edit(template_skin_id_list=template_skin_id_list)


  def stepAddRegisteredSelectionToBusinessTemplate(self, sequence=None, **kw):
    """
    Add registered selection to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_registered_skin_selection_list = \
        ('%s | Foo' % sequence.get('skin_folder_id'), ))

  def stepEditRegisteredSelectionToBusinessTemplate(self, sequence=None, **kw):
    """
    Add registered selection to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_registered_skin_selection_list = \
        ('%s | Foo' % sequence.get('skin_folder_id'),
         '%s | Bar' % sequence.get('skin_folder_id'),))

  def stepAddPathToBusinessTemplate(self, sequence=None, **kw):
    """
    Add a path to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_path_list=['geek_path',])

  # Base Category
  def stepCreateBaseCategory(self, sequence=None, **kw):
    """
    Create Base category
    """
    pc = self.getCategoryTool()
    base_category = pc.newContent(portal_type = 'Base Category')
    self.assertTrue(base_category is not None)
    sequence.edit(bc_id=base_category.getId(),)
    sequence.edit(base_category_uid=base_category.getUid(),)

  # Content Type Registry
  def stepAddEntryToContentTypeRegistry(self, sequence=None, **kw):
    """
    Add entry to content type registry
    """
    ctr = getattr(self.getPortal(), 'content_type_registry')
    ctr.addPredicate('test', 'extension')
    ctr.assignTypeName('test', 'What Not')
    ctr.getPredicate('test').extensions = ('abc', 'def')

  def stepCheckContentTypeRegistryHasNewEntry(self, sequence=None, **kw):
    """
      Check that we can find new type name in ctr
    """
    ctr = getattr(self.getPortal(), 'content_type_registry')
    self.assertTrue(ctr.findTypeName('bzzz.def', None, None) == 'What Not')

  def stepAddContentTypeRegistryAsPathToBusinessTemplate(self, sequence=None, **kw):
    """
      Add Content Type Registry to Business template
    """
    bt = sequence.get('current_bt')
    path = 'content_type_registry'
    bt.edit(template_path_list=[path])

  def stepRemoveContentTypeRegistryNewEntry(self, sequence=None, **kw):
    """
      Remove new entry from content_type_registry
    """
    ctr = getattr(self.getPortal(), 'content_type_registry')
    ctr.removePredicate('test')

  def stepCheckContentTypeRegistryHasNoNewEntry(self, sequence=None, **kw):
    """
      Check that we can not find new type name in ctr anymore
    """
    ctr = getattr(self.getPortal(), 'content_type_registry')
    self.assertTrue(ctr.findTypeName('bzzz.def', None, None) is None)

  def stepAddBaseCategoryToBusinessTemplate(self, sequence=None, **kw):
    """
    Add Base category to Business template
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    bt.edit(template_base_category_list=[bc_id,])

  def stepAddBaseCategoryAsPathToBusinessTemplate(self, sequence=None, **kw):
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    path = 'portal_categories/'+bc_id
    bt.edit(template_path_list=[path])

  def stepRemoveBaseCategory(self, sequence=None, **kw):
    """
    Remove Base category
    """
    pc = self.getCategoryTool()
    bc_id = sequence.get('bc_id')
    pc.manage_delObjects([bc_id])
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is None)

  def stepCheckBaseCategoryExists(self, sequence=None, **kw):
    """
    Check presence of Base category
    """
    pc = self.getCategoryTool()
    bc_id = sequence.get('bc_id')
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)

  def stepCheckBaseCategoryRemoved(self, sequence=None, **kw):
    """
    Check non presence of Base category
    """
    pc = self.getCategoryTool()
    bc_id = sequence.get('bc_id')
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is None)

  def stepSaveBaseCategoryUid(self, sequence=None, **kw):
    """
    Check uid has not changed after an upgrade
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    sequence.edit(bc_uid = base_category.getUid())

  def stepCheckBaseCategoryUid(self, sequence=None, **kw):
    """
    Check uid has not changed after an upgrade
    """
    bc_id = sequence.get('bc_id')
    bc_uid = sequence.get('bc_uid')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertEqual(bc_uid, base_category.getUid())

  # categories
  def stepCreateCategories(self, sequence=None, **kw):
    """
    Create categories into a base category
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    category_list = []
    for i in xrange(10):
      category = base_category.newContent(portal_type='Category')
      self.assertTrue(category is not None)
      category_list.append(category.getId())
    sequence.edit(category_id_list=category_list)

  def stepAddCategoriesAsPathToBusinessTemplate(self, sequence=None, **kw):
    """
    Add Categories in path with the joker *
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    path = 'portal_categories/'+bc_id+'/*'
    bt.edit(template_path_list=[path])

  def stepCheckCategoriesExists(self, sequence=None, **kw):
    """
    Check presence of categories
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    category_id_list = sequence.get('category_id_list')
    for category_id in category_id_list:
      category = base_category._getOb(category_id, None)
      self.assertTrue(category is not None)

  def stepCheckCategoriesRemoved(self, sequence=None, **kw):
    """
    Check non-presence of categories
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    category_id_list = sequence.get('category_id_list')
    for category_id in category_id_list:
      category = base_category._getOb(category_id, None)
      self.assertTrue(category is None)

  def stepRemoveCategories(self, sequence=None, **kw):
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    category_id_list = sequence.get('category_id_list')
    base_category.manage_delObjects(category_id_list)
    for category_id in category_id_list:
      category = base_category._getOb(category_id, None)
      self.assertTrue(category is None)

  # sub categories
  def stepCreateSubCategories(self, sequence=None, **kw):
    """
    Add sub category to a category
    """
    pc = self.getCategoryTool()
    bc_id = sequence.get('bc_id')
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    cat_id_list = sequence.get('category_id_list')
    # only use one category
    cat_id = cat_id_list[0]
    category = base_category._getOb(cat_id, None)
    self.assertTrue(category is not None)
    subcategory_list = []
    subcategory_uid_dict = {}
    for i in xrange(10):
      subcategory = category.newContent(portal_type='Category', title='toto')
      self.assertTrue(subcategory is not None)
      subcategory_list.append(subcategory.getId())
      subcategory_uid_dict[subcategory.getId()] = subcategory.getUid()
    sequence.edit(subcategory_id_list=subcategory_list, \
                  parent_category_id=category.getId(), \
                  subcategory_uid_dict=subcategory_uid_dict)

  def stepModifySubCategories(self, sequence=None, **kw):
    """
      Modify the title some subcategories
    """
    base_category_id = sequence.get('bc_id')
    category_tool = self.getCategoryTool()
    base_category = category_tool._getOb(base_category_id, None)
    parent_category_id = sequence.get('parent_category_id')
    category = base_category._getOb(parent_category_id, None)
    subcategory_id_list = sequence.get('subcategory_id_list')
    for subcategory_id in subcategory_id_list:
      subcategory = category._getOb(subcategory_id, None)
      subcategory.edit(title='foo')

  def stepAddSubCategoriesAsPathToBusinessTemplate(self, sequence=None, **kw):
    """
    Add All Categories in path with the joker **
    """
    bc_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    path = 'portal_categories/'+bc_id+'/**'
    bt.edit(template_path_list=[path])

  def stepCheckSubCategoriesExists(self, sequence=None, **kw):
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    parent_category_id = sequence.get('parent_category_id')
    category = base_category._getOb(parent_category_id, None)
    self.assertTrue(category is not None)
    subcategory_id_list = sequence.get('subcategory_id_list')
    for subcategory_id in subcategory_id_list:
      subcategory = category._getOb(subcategory_id, None)
      self.assertTrue(subcategory is not None)
      self.assertEqual(subcategory.getTitle(), 'toto')

  def stepCheckUidSubCategories(self, sequence=None, **kw):
    """
    Check Uid on base category and the sub categories
    """
    base_category_id = sequence.get('bc_id')
    category_tool = self.getCategoryTool()
    base_category = category_tool._getOb(base_category_id, None)
    self.assertEqual(base_category.getUid(), \
                      sequence.get('base_category_uid'))
    parent_category_id = sequence.get('parent_category_id')
    category = base_category._getOb(parent_category_id, None)
    subcategory_id_list = sequence.get('subcategory_id_list')
    subcategory_uid_dict = sequence.get('subcategory_uid_dict')
    for subcategory_id in subcategory_id_list:
      subcategory = category._getOb(subcategory_id, None)
      self.assertEqual(subcategory.getUid(), \
           subcategory_uid_dict[subcategory_id])

  # workflow
  def stepCreateWorkflow(self, sequence=None, **kw):
    """
    Create a workflow
    """
    wf_id = 'geek_workflow'
    pw = self.getWorkflowTool()
    addWorkflowByType(pw, WORKFLOW_TYPE, wf_id)
    workflow = pw._getOb(wf_id, None)
    self.assertTrue(workflow is not None)
    sequence.edit(workflow_id=workflow.getId())
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        props['chain_%s' % id] = ','.join(wf_ids)
    props['chain_Geek Object'] = wf_id
    pw.manage_changeWorkflows('', props=props)

  def stepModifyWorkflowChain(self, sequence=None, **kw):
    """
    Modify the workflow chain not by business template installation
    """
    wf_id = 'geek_workflow'
    pw = self.getWorkflowTool()
    workflow = pw._getOb(wf_id, None)
    self.assertTrue(workflow is not None)
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        props['chain_%s' % id] = ','.join(wf_ids)
    props['chain_Base Category'] = 'edit_workflow,%s' % wf_id
    pw.manage_changeWorkflows('', props=props)

  def stepSaveWorkflowChain(self, sequence=None, **kw):
    """
    Save the workflow chain as it is
    """
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        props['chain_%s' % id] = ','.join(wf_ids)
    pw.manage_changeWorkflows('', props=props)

  def stepCheckWorkflowChainRemoved(self, sequence=None, **kw):
    """
    Check if the workflowChain has been removed
    """
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    if cbt is not None:
      for id, wf_ids in cbt.items():
        if id == "Geek Object":
          self.assertEqual(len(wf_ids), 0)

  def stepCheckWorkflowChainExists(self, sequence=None, **kw):
    """
    Check if the workflowChain has been added
    """
    present = 0
    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type
    if cbt is not None:
      for id, wf_ids in cbt.items():
        if id == "Geek Object":
          present = 1
    self.assertEqual(present, 1)

  def stepAppendWorkflowToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    wf_ids = list(bt.getTemplateWorkflowIdList())
    wf_ids.append(sequence.get('workflow_id', ''))
    self.assertEqual(len(wf_ids), 2)
    bt.edit(template_workflow_id_list=wf_ids)

  def stepAddWorkflowToBusinessTemplate(self, sequence=None, **kw):
    """
    Add workflow to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    wf_ids = []
    wf_ids.append(sequence.get('workflow_id', ''))
    self.assertEqual(len(wf_ids), 1)
    bt.edit(template_workflow_id_list=wf_ids)

  def stepAppendWorkflowChainToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    wf_chain_ids = list(bt.getTemplatePortalTypeWorkflowChainList())
    wf_chain_ids.append('Geek Object | %s' % sequence.get('workflow_id', ''))
    bt.edit(template_portal_type_workflow_chain_list=wf_chain_ids)

  def stepAddWorkflowChainToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    wf_chain_ids = ['Geek Object | %s' % sequence.get('workflow_id', '')]
    bt.edit(template_portal_type_workflow_chain_list=wf_chain_ids)

  def stepAddRemovedWorkflowChainToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    wf_chain_ids = ['Geek Object | -%s' % sequence.get('workflow_id', '')]
    bt.edit(template_portal_type_workflow_chain_list=wf_chain_ids)

  def stepRemoveWorkflow(self, sequence=None, **kw):
    """
    Remove Workflow
    """
    wf_id = sequence.get('workflow_id')
    pw = self.getWorkflowTool()
    pw.manage_delObjects([wf_id])
    workflow = pw._getOb(wf_id, None)
    self.assertTrue(workflow is None)
    # remove workflowChain
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        wf_ids = list(wf_ids)
        if wf_id in wf_ids:
          wf_ids.remove(wf_id)
        props['chain_%s' % id] = ','.join(wf_ids)
    pw.manage_changeWorkflows('', props=props)

  def stepCheckWorkflowExists(self, sequence=None, **kw):
    """
    Check presence of Workflow
    """
    wf_id = sequence.get('workflow_id')
    pw = self.getWorkflowTool()
    workflow = pw._getOb(wf_id, None)
    self.assertTrue(workflow is not None)

  def stepCheckWorkflowRemoved(self, sequence=None, **kw):
    """
    Check non presence of Workflow
    """
    wf_id = sequence.get('workflow_id')
    pw = self.getWorkflowTool()
    workflow = pw._getOb(wf_id, None)
    self.assertTrue(workflow is None)

  def stepCheckWorkflowBackup(self, sequence=None, **kw):
    """
    Check workflow and its subobjects has been well backup in portal trash
    """
    wf_id = sequence.get('workflow_id')
    tt = self.getPortal()['portal_trash']
    self.assertEqual(len(tt.objectIds()), 1)
    bin = tt.objectValues()[0]
    self.assertNotEqual(len(bin.portal_workflow_items[wf_id].objectIds()), 0)

  # Actions
  def stepCreateFirstAction(self, sequence=None, **kw):
    """
    Create action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    object_pt.newContent(portal_type='Action Information',
                         reference='become_geek',
                         title='Become Geek',
                         action='become_geek_action',
                         action_type='object_action',
                         float_index=2.0)
    sequence.edit(first_action_id='become_geek')

  def stepCreateEmptyAction(self, sequence=None, **kw):
    """
    Create an empty action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    object_pt.newContent(portal_type='Action Information',
                         title='Name',
                         action_permission_list=(),
                         float_index=1.2)

  def stepCreateSecondAction(self, sequence=None, **kw):
    """
    Create a second action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    object_pt.newContent(portal_type='Action Information',
                         reference='become_nerd',
                         title='Become Nerd',
                         action='become_nerd_action',
                         action_type='object_action',
                         float_index=1.5)
    sequence.edit(second_action_id='become_nerd')

  def stepCheckFirstActionExists(self, sequence=None, **kw):
    """
    Check presence of action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('first_action_id')
    self.assertIn(action_id, [x.getReference()
      for x in object_pt.getActionInformationList()])

  def stepCheckFirstActionNotExists(self, sequence=None, **kw):
    """
    Check non-presence of action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('first_action_id')
    self.assertNotIn(action_id, [x.getReference()
      for x in object_pt.getActionInformationList()])

  def stepCheckSecondActionExists(self, sequence=None, **kw):
    """
    Check presence of the second action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('second_action_id')
    self.assertIn(action_id, [x.getReference()
      for x in object_pt.getActionInformationList()])

  def stepCheckSecondActionNotExists(self, sequence=None, **kw):
    """
    Check non-presence of optional action
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    action_id = sequence.get('second_action_id')
    self.assertNotIn(action_id, [x.getReference()
      for x in object_pt.getActionInformationList()])

  def stepAddSecondActionToBusinessTemplate(self, sequence=None, **kw):
    """
    Add Second Action to business template
    """
    object_id = sequence.get('object_ptype_id')
    action_id = sequence.get('second_action_id')
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_action_path=['%s | %s' %(object_id, action_id)])

  # Catalog Method
  def stepCreateCatalogMethod(self, sequence=None, **kw):
    """
    Create ZSQL Method into catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    self.assertTrue(catalog is not None)
    method_id = "z_fake_method"
    addSQLMethod = catalog.newContent
    addSQLMethod(portal_type='SQL Method', id=method_id, title='',
                 connection_id='erp5_sql_connection', arguments_src='', src='')
    zsql_method = catalog._getOb(method_id, None)
    self.assertTrue(zsql_method is not None)
    sequence.edit(zsql_method_id = method_id)
    # set this method in update_object properties of catalog
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_uncatalog_object.append(method_id)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    # set filter for this method
    expression = 'python: context.isPredicate()'
    zsql_method.setFiltered(1)
    zsql_method.setExpression(expression)
    zsql_method.setExpressionCacheKey('portal_type')
    zsql_method.setTypeList([])

  def stepCreateUpdateCatalogMethod(self, sequence=None, **kw):
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    self.assertTrue(catalog is not None)
    method_id = "z_fake_method"
    addSQLMethod = catalog.newContent
    addSQLMethod(portal_type='SQL Method', id=method_id, title='',
                 connection_id='erp5_sql_connection', arguments_src='', src='')
    zsql_method = catalog._getOb(method_id, None)
    self.assertTrue(zsql_method is not None)
    sequence.edit(zsql_method_id = method_id)
    # set this method in update_object properties of catalog
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_uncatalog_object.append(method_id)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    # set filter for this method
    expression = 'python: context.isDelivery()'
    zsql_method.setFiltered(1)
    zsql_method.setExpression(expression)
    zsql_method.setExpressionCacheKey('portal_type')
    zsql_method.setTypeList([])

  def stepCreateNewCatalogMethod(self, sequence=None, **kw):
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    method_id = "z_another_fake_method"
    addSQLMethod =catalog.newContent
    addSQLMethod(portal_type='SQL Method', id=method_id, title='',
                 connection_id='erp5_sql_connection', arguments_src='', src='')
    zsql_method = catalog._getOb(method_id, None)
    self.assertTrue(zsql_method is not None)
    sequence.edit(another_zsql_method_id = method_id)
    # set this method in update_object properties of catalog
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_uncatalog_object.append(method_id)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)

  def stepChangePreviousCatalogMethod(self, sequence=None, **kw):
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    method_id = sequence.get('zsql_method_id')
    previous_method = catalog._getOb(method_id,None)
    self.assertEqual(previous_method.title,'')
    previous_method.title='toto'
    self.assertEqual(previous_method.title,'toto')

  def stepCheckCatalogMethodChangeKept(self, sequence=None, **kw):
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    method_id = sequence.get('zsql_method_id')
    previous_method = catalog._getOb(method_id,None)
    self.assertEqual(previous_method.title,'toto')

  def stepAddCatalogMethodToBusinessTemplate(self, sequence=None, **kw):
    """
    Add catalog method into the business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    method_id = sequence.get('zsql_method_id', None)
    self.assertTrue(method_id is not None)
    pc = self.getCatalogTool()
    catalog_id = pc.getSQLCatalog().id
    bt.edit(template_catalog_method_id_list=[catalog_id+'/'+method_id])

  def stepRemoveCatalogMethodToBusinessTemplate(self, sequence=None, **kw):
    """
    Remove catalog method into the business template
    """
    business_template = sequence.get('current_bt', None)
    self.assertTrue(business_template is not None)
    method_id = sequence.get('zsql_method_id', None)
    current_method_list = list(business_template.\
                          getTemplateCatalogMethodIdList())
    catalog_tool = self.getCatalogTool()
    catalog_id = catalog_tool.getSQLCatalog().id
    current_method_list.remove(catalog_id+'/'+method_id)
    business_template.edit(template_catalog_method_id_list=current_method_list)

  def stepAddNewCatalogMethodToBusinessTemplate(self, sequence=None, **kw):
    """
    Add catalog method into the business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    method_id = sequence.get('zsql_method_id', None)
    self.assertTrue(method_id is not None)
    another_method_id = sequence.get('another_zsql_method_id', None)
    pc = self.getCatalogTool()
    catalog_id = pc.getSQLCatalog().id
    bt.edit(template_catalog_method_id_list=[catalog_id+'/'+method_id,
            catalog_id+'/'+another_method_id])

  def stepCheckCatalogMethodExists(self, sequence=None, **kw):
    """
    Check presence of ZSQL Method in catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    self.assertTrue(catalog is not None)
    method_id = sequence.get('zsql_method_id', None)
    zsql_method = catalog._getOb(method_id, None)
    self.assertNotEqual(zsql_method, None)
    # check catalog properties
    self.assertIn(method_id, catalog.sql_uncatalog_object)
    # check filter
    filter_dict = catalog._getFilterDict()
    filter = filter_dict[method_id]
    self.assertItemsEqual(filter['expression_cache_key'], ['portal_type'])
    self.assertEqual(filter['type'], [])
    self.assertEqual(filter['filtered'], 1)
    self.assertEqual(filter['expression'], 'python: context.isPredicate()')

  def stepCheckUpdatedCatalogMethodExists(self, sequence=None, **kw):
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    self.assertTrue(catalog is not None)
    method_id = sequence.get('zsql_method_id', None)
    zsql_method = catalog._getOb(method_id, None)
    self.assertNotEqual(zsql_method, None)
    # check catalog properties
    self.assertIn(method_id, catalog.sql_uncatalog_object)
    # check filter
    filter_dict = catalog._getFilterDict()
    filter = filter_dict[method_id]
    self.assertItemsEqual(filter['expression_cache_key'], ['portal_type'])
    self.assertEqual(filter['type'], [])
    self.assertEqual(filter['filtered'], 1)
    self.assertEqual(filter['expression'], 'python: context.isDelivery()')

  def stepCheckCatalogMethodRemoved(self, sequence=None, **kw):
    """
    Check non-presence of ZSQL Method in catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    self.assertTrue(catalog is not None)
    method_id = sequence.get('zsql_method_id', None)
    zsql_method = catalog._getOb(method_id, None)
    self.assertTrue(zsql_method is None)
    # check catalog properties
    self.assertNotIn(method_id, catalog.sql_uncatalog_object)
    # check filter
    with self.assertRaises(KeyError):
      catalog._getFilterDict()[method_id]

  def stepRemoveCatalogMethod(self, sequence=None, **kw):
    """
    Remove ZSQL Method from catalog
    """
    pc = self.getCatalogTool()
    catalog = pc.getSQLCatalog()
    self.assertTrue(catalog is not None)
    method_id = sequence.get('zsql_method_id', None)
    catalog.manage_delObjects([method_id])
    zsql_method = catalog._getOb(method_id, None)
    self.assertTrue(zsql_method is None)
    # remove catalog properties
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_uncatalog_object.remove(method_id)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    self.assertNotIn(method_id, catalog.sql_uncatalog_object)
    # remove filter
    with self.assertRaises(KeyError):
      catalog._getFilterDict()[method_id]

  # Related key, Result key and table, and others
  def stepCreateKeysAndTable(self, sequence=list, **kw):
    """
    Create some keys and tables
    """
    # define variables
    related_key = 'fake_id | category/catalog/z_fake_method'
    result_key = 'catalog.title'
    result_table = 'fake_catalog'
    search_key = 'fake_search_key | FakeSearchKey'
    keyword_key = 'fake_keyword'
    full_text_key = 'fake_full_text'
    request_key = 'fake_request'
    multivalue_key = 'fake_multivalue'
    topic_key = 'fake_topic'
    scriptable_key = 'fake_search_text | fake_script_query'
    role_key = 'Foo | catalog.owner'
    local_role_key = 'Bar | catalog.owner'
    catalog = self.getCatalogTool().getSQLCatalog()
    self.assertTrue(catalog is not None)
    # result table
    if result_table not in catalog.sql_search_tables:
      sql_search_tables = list(catalog.sql_search_tables)
      sql_search_tables.append(result_table)
      sql_search_tables.sort()
      catalog.sql_search_tables = tuple(sql_search_tables)
    self.assertIn(result_table, catalog.sql_search_tables)
    # result key
    if result_key not in catalog.sql_search_result_keys:
      sql_search_result_keys = list(catalog.sql_search_result_keys)
      sql_search_result_keys.append(result_key)
      sql_search_result_keys.sort()
      catalog.sql_search_result_keys = tuple(sql_search_result_keys)
    self.assertIn(result_key, catalog.sql_search_result_keys)
    # related key
    if related_key not in catalog.sql_catalog_related_keys:
      sql_search_related_keys = list(catalog.sql_catalog_related_keys)
      sql_search_related_keys.append(related_key)
      sql_search_related_keys.sort()
      catalog.sql_catalog_related_keys = tuple(sql_search_related_keys)
    self.assertIn(related_key, catalog.sql_catalog_related_keys)
    # search keys
    if search_key not in catalog.sql_catalog_search_keys:
      sql_catalog_search_keys = list(catalog.sql_catalog_search_keys)
      sql_catalog_search_keys.append(search_key)
      sql_catalog_search_keys.sort()
      catalog.sql_catalog_search_keys = tuple(sql_catalog_search_keys)
    self.assertIn(search_key, catalog.sql_catalog_search_keys)
    # keyword keys
    if keyword_key not in catalog.sql_catalog_keyword_search_keys:
      sql_catalog_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
      sql_catalog_keyword_keys.append(keyword_key)
      sql_catalog_keyword_keys.sort()
      catalog.sql_catalog_keyword_search_keys = tuple(sql_catalog_keyword_keys)
    self.assertIn(keyword_key, catalog.sql_catalog_keyword_search_keys)
    # full_text keys
    if full_text_key not in catalog.sql_catalog_full_text_search_keys:
      sql_catalog_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
      sql_catalog_full_text_keys.append(full_text_key)
      sql_catalog_full_text_keys.sort()
      catalog.sql_catalog_full_text_search_keys = tuple(sql_catalog_full_text_keys)
    self.assertIn(full_text_key, catalog.sql_catalog_full_text_search_keys)
    # request
    if request_key not in catalog.sql_catalog_request_keys:
      sql_catalog_request_keys = list(catalog.sql_catalog_request_keys)
      sql_catalog_request_keys.append(request_key)
      sql_catalog_request_keys.sort()
      catalog.sql_catalog_request_keys = tuple(sql_catalog_request_keys)
    self.assertIn(request_key, catalog.sql_catalog_request_keys)
    # multivalue
    if multivalue_key not in catalog.sql_catalog_multivalue_keys:
      sql_catalog_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
      sql_catalog_multivalue_keys.append(multivalue_key)
      sql_catalog_multivalue_keys.sort()
      catalog.sql_catalog_multivalue_keys = tuple(sql_catalog_multivalue_keys)
    self.assertIn(multivalue_key, catalog.sql_catalog_multivalue_keys)
    # topic keys
    if topic_key not in catalog.sql_catalog_topic_search_keys:
      sql_catalog_topic_keys = list(catalog.sql_catalog_topic_search_keys)
      sql_catalog_topic_keys.append(topic_key)
      sql_catalog_topic_keys.sort()
      catalog.sql_catalog_topic_search_keys = tuple(sql_catalog_topic_keys)
    self.assertIn(topic_key, catalog.sql_catalog_topic_search_keys)
    # scriptable keys
    if scriptable_key not in catalog.sql_catalog_scriptable_keys:
      sql_catalog_scriptable_keys = list(catalog.sql_catalog_scriptable_keys)
      sql_catalog_scriptable_keys.append(scriptable_key)
      sql_catalog_scriptable_keys.sort()
      catalog.sql_catalog_scriptable_keys = tuple(sql_catalog_scriptable_keys)
    self.assertIn(scriptable_key, catalog.sql_catalog_scriptable_keys)
    # role keys
    if role_key not in catalog.sql_catalog_role_keys:
      sql_catalog_role_keys = list(catalog.sql_catalog_role_keys)
      sql_catalog_role_keys.append(role_key)
      sql_catalog_role_keys.sort()
      catalog.sql_catalog_role_keys = tuple(sql_catalog_role_keys)
    self.assertIn(role_key, catalog.sql_catalog_role_keys)
    # local_role keys
    if local_role_key not in catalog.sql_catalog_local_role_keys:
      sql_catalog_local_role_keys = list(catalog.sql_catalog_local_role_keys)
      sql_catalog_local_role_keys.append(local_role_key)
      sql_catalog_local_role_keys.sort()
      catalog.sql_catalog_local_role_keys = tuple(sql_catalog_local_role_keys)
    self.assertIn(local_role_key, catalog.sql_catalog_local_role_keys)

    sequence.edit(related_key=related_key, result_key=result_key,
                  result_table=result_table, search_key=search_key,
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
    self.assertEqual(catalog.sql_getitem_by_uid, 'z_getitem_by_uid_2')
    # table related configuration
    self.assertIn('translation', catalog.sql_search_tables)
    # column related configuration
    self.assertIn('catalog.reference',
                  catalog.sql_search_result_keys)

  def stepModifyRelatedKey(self, sequence):
    catalog = self.getCatalogTool().getSQLCatalog()
    related_key = sequence['related_key']
    related_key_list = list(catalog.sql_catalog_related_keys)
    related_key_list.remove(related_key)
    # related_key_2 <- 'fake_id | category/catalog/z_fake_method_2':
    related_key_2 = related_key + '_2'
    related_key_list.append(related_key_2)
    catalog.sql_catalog_related_keys = tuple(related_key_list)
    sequence['related_key_2'] = related_key_2
    # check related key column is not present twice:
    self.assertTrue(related_key_2.startswith('fake_id |'), related_key_2)
    self.assertEqual(len([key for key in related_key_list
                          if key.startswith('fake_id |')]), 1)

  def stepCheckRelatedKeyNonDuplicated(self, sequence):
    catalog = self.getCatalogTool().getSQLCatalog()
    related_key = sequence['related_key']
    related_key_2 = sequence['related_key_2']
    related_key_list = list(catalog.sql_catalog_related_keys)
    # stepModifyRelatedKey added related_key_2 and removed related_key
    # but the reinstallation of the BT replaced related_key_2 with
    # related_key:
    self.assertIn(related_key, related_key_list)
    self.assertNotIn(related_key_2, related_key_list)
    # make sure there's only one entry
    self.assertTrue(related_key.startswith('fake_id |'), related_key)
    self.assertEqual(len([key for key in related_key_list
                          if key.startswith('fake_id |')]), 1)

  def stepDuplicateRelatedKeyColumn(self, sequence):
    catalog = self.getCatalogTool().getSQLCatalog()
    related_key = sequence['related_key']
    related_key_2 = sequence['related_key_2']
    related_key_list = list(catalog.sql_catalog_related_keys)
    self.assertIn(related_key, related_key_list)
    self.assertNotIn(related_key_2, related_key_list)
    # we manually duplicate the key in the list, creating an invalid situation
    self.assertEqual(len([key for key in related_key_list
                          if key.startswith('fake_id |')]), 1)
    related_key_list.append(related_key_2)
    catalog.sql_catalog_related_keys = tuple(related_key_list)
    self.assertEqual(len([key for key in related_key_list
                          if key.startswith('fake_id |')]), 2)

  def stepCheckOnlyDuplicateRelatedKeyRemains(self, sequence):
    catalog = self.getCatalogTool().getSQLCatalog()
    related_key = sequence['related_key']
    related_key_2 = sequence['related_key_2']
    related_key_list = list(catalog.sql_catalog_related_keys)
    # after the uninstallation of the BT, only the wrong/duplicated
    # entry remains because the original was uninstalled with the BT.
    # This also means that an uninstallation of a BT does not
    # accidentally removes an overriding key from another BT that
    # depends on it.
    self.assertNotIn(related_key, related_key_list)
    self.assertIn(related_key_2, related_key_list)
    self.assertEqual(len([key for key in related_key_list
                          if key.startswith('fake_id |')]), 1)

  def stepRemoveCatalogLocalConfiguration(self, sequence, **kw):
    """
    Remove modification made in stepModifyCatalogConfiguration
    """
    result_key = sequence.get('result_key', None)
    self.assertTrue(result_key is not None)
    result_table = sequence.get('search_table', None)
    self.assertTrue(result_table is not None)
    catalog = self.getCatalogTool().getSQLCatalog()
    self.assertTrue(catalog is not None)
    # result key
    sql_search_result_keys = list(catalog.sql_search_result_keys)
    sql_search_result_keys.remove(result_key)
    sql_search_result_keys.sort()
    catalog.sql_search_result_keys = tuple(sql_search_result_keys)
    self.assertNotIn(result_key, catalog.sql_search_result_keys)
    # search table
    sql_search_tables = list(catalog.sql_search_tables)
    sql_search_tables.remove(result_table)
    sql_search_tables.sort()
    catalog.sql_search_tables = tuple(sql_search_tables)
    self.assertNotIn(result_table, catalog.sql_search_tables)
    # related key
    related_key_2 = sequence['related_key_2']
    sql_catalog_related_keys = list(catalog.sql_catalog_related_keys)
    sql_catalog_related_keys.remove(related_key_2)
    catalog.sql_catalog_related_keys = tuple(sql_catalog_related_keys)
    self.assertNotIn(related_key_2, catalog.sql_catalog_related_keys)

  def stepAddKeysAndTableToBusinessTemplate(self, sequence=None, **kw):
    """
    Add some related, result key and tables to Business Temlpate
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    related_key = sequence.get('related_key', None)
    self.assertTrue(related_key is not None)
    result_key = sequence.get('result_key', None)
    self.assertTrue(result_key is not None)
    result_table = sequence.get('result_table', None)
    self.assertTrue(result_table is not None)
    search_key = sequence.get('search_key', None)
    self.assertTrue(search_key is not None)
    keyword_key = sequence.get('keyword_key', None)
    self.assertTrue(keyword_key is not None)
    full_text_key = sequence.get('full_text_key', None)
    self.assertTrue(full_text_key is not None)
    request_key = sequence.get('request_key', None)
    self.assertTrue(request_key is not None)
    multivalue_key = sequence.get('multivalue_key', None)
    self.assertTrue(multivalue_key is not None)
    topic_key = sequence.get('topic_key', None)
    self.assertTrue(topic_key is not None)
    scriptable_key = sequence.get('scriptable_key', None)
    self.assertTrue(scriptable_key is not None)
    role_key = sequence.get('role_key', None)
    self.assertTrue(role_key is not None)
    local_role_key = sequence.get('local_role_key', None)
    self.assertTrue(local_role_key is not None)

    bt.edit(template_catalog_related_key_list=[related_key],
            template_catalog_result_key_list=[result_key],
            template_catalog_result_table_list=[result_table],
            template_catalog_search_key_list=[search_key],
            template_catalog_keyword_key_list=[keyword_key],
            template_catalog_full_text_key_list=[full_text_key],
            template_catalog_request_key_list=[request_key],
            template_catalog_multivalue_key_list=[multivalue_key],
            template_catalog_topic_key_list=[topic_key],
            template_catalog_scriptable_key_list=[scriptable_key],
            template_catalog_role_key_list=[role_key],
            template_catalog_local_role_key_list=[local_role_key],
            )

  def stepRemoveKeysAndTable(self, sequence=list, **kw):
    """
    Remove some keys and tables
    """
    related_key = sequence.get('related_key', None)
    self.assertTrue(related_key is not None)
    result_key = sequence.get('result_key', None)
    self.assertTrue(result_key is not None)
    result_table = sequence.get('result_table', None)
    self.assertTrue(result_table is not None)
    search_key = sequence.get('search_key', None)
    self.assertTrue(search_key is not None)
    keyword_key = sequence.get('keyword_key', None)
    self.assertTrue(keyword_key is not None)
    full_text_key = sequence.get('full_text_key', None)
    self.assertTrue(full_text_key is not None)
    request_key = sequence.get('request_key', None)
    self.assertTrue(request_key is not None)
    multivalue_key = sequence.get('multivalue_key', None)
    self.assertTrue(multivalue_key is not None)
    topic_key = sequence.get('topic_key', None)
    self.assertTrue(topic_key is not None)
    scriptable_key = sequence.get('scriptable_key', None)
    self.assertTrue(scriptable_key is not None)
    role_key = sequence.get('role_key', None)
    self.assertTrue(role_key is not None)
    local_role_key = sequence.get('local_role_key', None)
    self.assertTrue(local_role_key is not None)

    catalog = self.getCatalogTool().getSQLCatalog()
    self.assertTrue(catalog is not None)
    # result key
    sql_search_result_keys = list(catalog.sql_search_result_keys)
    sql_search_result_keys.remove(result_key)
    sql_search_result_keys.sort()
    catalog.sql_search_result_keys = tuple(sql_search_result_keys)
    self.assertNotIn(result_key, catalog.sql_search_result_keys)
    # related key
    sql_search_related_keys = list(catalog.sql_catalog_related_keys)
    sql_search_related_keys.remove(related_key)
    sql_search_related_keys.sort()
    catalog.sql_catalog_related_keys = tuple(sql_search_related_keys)
    self.assertNotIn(related_key, catalog.sql_catalog_related_keys)
    # result table
    sql_search_tables = list(catalog.sql_search_tables)
    sql_search_tables.remove(result_table)
    sql_search_tables.sort()
    catalog.sql_search_tables = tuple(sql_search_tables)
    self.assertNotIn(result_table, catalog.sql_search_tables)
    # search keys
    sql_catalog_search_keys = list(catalog.sql_catalog_search_keys)
    sql_catalog_search_keys.remove(search_key)
    sql_catalog_search_keys.sort()
    catalog.sql_catalog_search_keys = tuple(sql_catalog_search_keys)
    self.assertNotIn(search_key, catalog.sql_catalog_search_keys)
    # keyword keys
    sql_catalog_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
    sql_catalog_keyword_keys.remove(keyword_key)
    sql_catalog_keyword_keys.sort()
    catalog.sql_catalog_keyword_search_keys = tuple(sql_catalog_keyword_keys)
    self.assertNotIn(keyword_key, catalog.sql_catalog_keyword_search_keys)
    # full_text keys
    sql_catalog_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
    sql_catalog_full_text_keys.remove(full_text_key)
    sql_catalog_full_text_keys.sort()
    catalog.sql_catalog_full_text_search_keys = tuple(sql_catalog_full_text_keys)
    self.assertNotIn(full_text_key, catalog.sql_catalog_full_text_search_keys)
    # request
    sql_catalog_request_keys = list(catalog.sql_catalog_request_keys)
    sql_catalog_request_keys.remove(request_key)
    sql_catalog_request_keys.sort()
    catalog.sql_catalog_request_keys = tuple(sql_catalog_request_keys)
    self.assertNotIn(request_key, catalog.sql_catalog_request_keys)
    # multivalue
    sql_catalog_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
    sql_catalog_multivalue_keys.remove(multivalue_key)
    sql_catalog_multivalue_keys.sort()
    catalog.sql_catalog_multivalue_keys = tuple(sql_catalog_multivalue_keys)
    self.assertNotIn(multivalue_key, catalog.sql_catalog_multivalue_keys)
    # topic keys
    sql_catalog_topic_keys = list(catalog.sql_catalog_topic_search_keys)
    sql_catalog_topic_keys.remove(topic_key)
    sql_catalog_topic_keys.sort()
    catalog.sql_catalog_topic_search_keys = tuple(sql_catalog_topic_keys)
    self.assertNotIn(topic_key, catalog.sql_catalog_topic_search_keys)
    # scriptable keys
    sql_catalog_scriptable_keys = list(catalog.sql_catalog_scriptable_keys)
    sql_catalog_scriptable_keys.remove(scriptable_key)
    sql_catalog_scriptable_keys.sort()
    catalog.sql_catalog_scriptable_keys = tuple(sql_catalog_scriptable_keys)
    self.assertNotIn(scriptable_key, catalog.sql_catalog_scriptable_keys)
    # role keys
    sql_catalog_role_keys = list(catalog.sql_catalog_role_keys)
    sql_catalog_role_keys.remove(role_key)
    sql_catalog_role_keys.sort()
    catalog.sql_catalog_role_keys = tuple(sql_catalog_role_keys)
    self.assertNotIn(role_key, catalog.sql_catalog_role_keys)
    # local_role keys
    sql_catalog_local_role_keys = list(catalog.sql_catalog_local_role_keys)
    sql_catalog_local_role_keys.remove(local_role_key)
    sql_catalog_local_role_keys.sort()
    catalog.sql_catalog_local_role_keys = tuple(sql_catalog_local_role_keys)
    self.assertNotIn(local_role_key, catalog.sql_catalog_local_role_keys)

  def stepCheckKeysAndTableExists(self, sequence=list, **kw):
    """
    Check presence of some keys and tables
    """
    related_key = sequence.get('related_key', None)
    self.assertTrue(related_key is not None)
    result_key = sequence.get('result_key', None)
    self.assertTrue(result_key is not None)
    result_table = sequence.get('result_table', None)
    self.assertTrue(result_table is not None)
    search_key = sequence.get('search_key', None)
    self.assertTrue(search_key is not None)
    keyword_key = sequence.get('keyword_key', None)
    self.assertTrue(keyword_key is not None)
    full_text_key = sequence.get('full_text_key', None)
    self.assertTrue(full_text_key is not None)
    request_key = sequence.get('request_key', None)
    self.assertTrue(request_key is not None)
    multivalue_key = sequence.get('multivalue_key', None)
    self.assertTrue(multivalue_key is not None)
    topic_key = sequence.get('topic_key', None)
    self.assertTrue(topic_key is not None)
    scriptable_key = sequence.get('scriptable_key', None)
    self.assertTrue(scriptable_key is not None)
    role_key = sequence.get('role_key', None)
    self.assertTrue(role_key is not None)
    local_role_key = sequence.get('local_role_key', None)
    self.assertTrue(local_role_key is not None)

    catalog = self.getCatalogTool().getSQLCatalog()
    self.assertTrue(catalog is not None)
    # result key
    self.assertIn(result_key, catalog.sql_search_result_keys)
    # related key
    self.assertIn(related_key, catalog.sql_catalog_related_keys)
    # result table
    self.assertIn(result_table, catalog.sql_search_tables)
    # search key
    self.assertIn(search_key, catalog.sql_catalog_search_keys)
    # keyword key
    self.assertIn(keyword_key, catalog.sql_catalog_keyword_search_keys)
    # full text key
    self.assertIn(full_text_key, catalog.sql_catalog_full_text_search_keys)
    # request key
    self.assertIn(request_key, catalog.sql_catalog_request_keys)
    # multivalue key
    self.assertIn(multivalue_key, catalog.sql_catalog_multivalue_keys)
    # topic key
    self.assertIn(topic_key, catalog.sql_catalog_topic_search_keys)
    # scriptable key
    self.assertIn(scriptable_key, catalog.sql_catalog_scriptable_keys)
    # role key
    self.assertIn(role_key, catalog.sql_catalog_role_keys)
    # local_role key
    self.assertIn(local_role_key, catalog.sql_catalog_local_role_keys)

  def stepCheckKeysAndTableRemoved(self, sequence=list, **kw):
    """
    Check non-presence of some keys and tables
    """
    related_key = sequence.get('related_key', None)
    self.assertTrue(related_key is not None)
    result_key = sequence.get('result_key', None)
    self.assertTrue(result_key is not None)
    result_table = sequence.get('result_table', None)
    self.assertTrue(result_table is not None)
    search_key = sequence.get('search_key', None)
    self.assertTrue(search_key is not None)
    keyword_key = sequence.get('keyword_key', None)
    self.assertTrue(keyword_key is not None)
    full_text_key = sequence.get('full_text_key', None)
    self.assertTrue(full_text_key is not None)
    request_key = sequence.get('request_key', None)
    self.assertTrue(request_key is not None)
    multivalue_key = sequence.get('multivalue_key', None)
    self.assertTrue(multivalue_key is not None)
    topic_key = sequence.get('topic_key', None)
    self.assertTrue(topic_key is not None)
    scriptable_key = sequence.get('scriptable_key', None)
    self.assertTrue(scriptable_key is not None)
    role_key = sequence.get('role_key', None)
    self.assertTrue(role_key is not None)
    local_role_key = sequence.get('local_role_key', None)
    self.assertTrue(local_role_key is not None)

    catalog = self.getCatalogTool().getSQLCatalog()
    self.assertTrue(catalog is not None)
    # result key
    self.assertTrue(result_key, catalog.sql_search_result_keys)
    # related key
    self.assertTrue(related_key, catalog.sql_catalog_related_keys)
    # result table
    self.assertTrue(result_table, catalog.sql_search_tables)
    # search key
    self.assertTrue(search_key, catalog.sql_catalog_search_keys)
    # keyword key
    self.assertTrue(keyword_key, catalog.sql_catalog_keyword_search_keys)
    # full text key
    self.assertTrue(full_text_key, catalog.sql_catalog_full_text_search_keys)
    # request key
    self.assertTrue(request_key, catalog.sql_catalog_request_keys)
    # multivalue key
    self.assertTrue(multivalue_key, catalog.sql_catalog_multivalue_keys)
    # topic key
    self.assertTrue(topic_key, catalog.sql_catalog_topic_search_keys)
    # scriptable key
    self.assertTrue(scriptable_key, catalog.sql_catalog_scriptable_keys)
    # role key
    self.assertTrue(role_key, catalog.sql_catalog_role_keys)
    # local_role key
    self.assertTrue(local_role_key, catalog.sql_catalog_local_role_keys)

  # Roles
  def stepCreateRole(self, sequence=None, **kw):
    """
    Create a role
    """
    new_role = "Unit Tester"
    p = self.getPortal()
    role_list = list(p.__ac_roles__)
    role_list.append(new_role)
    p.__ac_roles__ = tuple(role_list)
    self.assertIn(new_role, p.__ac_roles__)
    sequence.edit(role=new_role)

  def stepRemoveRole(self, sequence=None, **kw):
    """
    Remove a role
    """
    role = sequence.get('role', None)
    self.assertTrue(role is not None)
    p = self.getPortal()
    role_list = list(p.__ac_roles__)
    role_list.remove(role)
    p.__ac_roles__ = tuple(role_list)
    self.assertNotIn(role, p.__ac_roles__)

  def stepAddRoleToBusinessTemplate(self, sequence=None, **kw):
    """
    Add Role to Business Template
    """
    role = sequence.get('role', None)
    self.assertTrue(role is not None)
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_role_list=[role])

  def stepCheckRoleExists(self, sequence=None, **kw):
    """
    Check presence of role
    """
    role = sequence.get('role', None)
    self.assertTrue(role is not None)
    p = self.getPortal()
    self.assertIn(role, p.__ac_roles__)

  def stepCheckRoleRemoved(self, sequence=None, **kw):
    """
    Check non-presence of role
    """
    role = sequence.get('role', None)
    self.assertTrue(role is not None)
    p = self.getPortal()
    self.assertNotIn(role, p.__ac_roles__)

  # Local Roles
  def stepCreateLocalRoles(self, sequence=None, **kw):
    """
    Create local roles
    """
    # We'll export an owner in local roles ...
    new_local_roles = {
      'ac': ['Owner', 'Manager'],
      'group_function': ['Auditor']
    }
    # ... but after installing this business template, the owner
    # will be reset:
    expected_local_roles = {
      'ac': ['Manager'],
      getSecurityManager().getUser().getId(): ['Owner'],
      'group_function': ['Auditor']
    }
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.assertTrue(module is not None)
    module.__ac_local_roles__ = new_local_roles
    self.assertEqual(module.__ac_local_roles__, new_local_roles)
    sequence.edit(local_roles=expected_local_roles)

  def stepRemoveLocalRoles(self, sequence=None, **kw):
    """
    Remove local roles
    """
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.assertTrue(module is not None)
    module.__ac_local_roles__ = {'someone_else': ['Associate']}
    new_local_roles = sequence.get('local_roles')
    self.assertNotEquals(module.__ac_local_roles__, new_local_roles)

  def stepAddLocalRolesToBusinessTemplate(self, sequence=None, **kw):
    """
    Add Local Roles to Business Template
    """
    module_id = sequence.get('module_id')
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_local_role_list=[module_id])

  def stepCheckLocalRolesExists(self, sequence=None, **kw):
    """
    Check presence of local roles
    """
    new_local_roles = sequence.get('local_roles')
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.assertTrue(module is not None)
    self.assertEqual(module.__ac_local_roles__, new_local_roles)

  def stepCheckModuleLocalRolesInCatalogBeforeUpdate(self, sequence=None, **kw):
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.assertTrue(module is not None)
    sql = "select distinct roles_and_users.uid as uid, allowedRolesAndUsers as role from catalog, roles_and_users where catalog.security_uid = roles_and_users.uid and catalog.uid=%s" %(module.getUid(),)
    sql_connection = self.getSQLConnection()
    result = sql_connection.manage_test(sql)
    result = [(x.uid, x.role) for x in result]
    sequence.edit(local_roles_catalog_result=result)

  def stepCheckModuleLocalRolesInCatalogAfterUpdate(self, sequence=None, **kw):
    p = self.getPortal()
    module_id = sequence.get('module_id')
    before_update_local_roles = sequence.get('local_roles_catalog_result')
    module = p._getOb(module_id, None)
    self.assertTrue(module is not None)
    sql = "select distinct roles_and_users.uid as uid, allowedRolesAndUsers as role from catalog, roles_and_users where catalog.security_uid = roles_and_users.uid and catalog.uid=%s" %(module.getUid(),)
    sql_connection = self.getSQLConnection()
    result = sql_connection.manage_test(sql)
    for line in result:
      self.assertNotIn((line.uid, line.role), before_update_local_roles)

  def stepCheckLocalRolesRemoved(self, sequence=None, **kw):
    """
    Check non-presence of local roles
    """
    new_local_roles = sequence.get('local_roles')
    p = self.getPortal()
    module_id = sequence.get('module_id')
    module = p._getOb(module_id, None)
    self.assertTrue(module is not None)
    self.assertNotEquals(module.__ac_local_roles__, new_local_roles)

  # Document, Property Sheet, Extension And Test
  # they use the same class so only one test is required for them
  def stepCreatePropertySheet(self, sequence=None, **kw):
    """
    Create a Property Sheet
    """
    ps_title = 'UnitTest'
    ps_data =  ' \nclass UnitTest: \n  """ \n  Fake property sheet for unit test \n \
    """ \n  _properties = ({"id": "ps_prop1", "type": "string"},) \n  _categories = ( \n  ) \n\n'
    cfg = getConfiguration()
    file_path = os.path.join(cfg.instancehome, 'PropertySheet', ps_title+'.py')
    if os.path.exists(file_path):
      os.remove(file_path)
    f = file(file_path, 'w')
    f.write(ps_data)
    f.close()
    self.assertTrue(os.path.exists(file_path))
    sequence.edit(ps_title=ps_title, ps_path=file_path, ps_data=ps_data)

  def stepAddPropertySheetToBusinessTemplate(self, sequence=None, **kw):
    """
    Add Property Sheet to Business Template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    ps_title = sequence.get('ps_title', None)
    self.assertTrue(ps_title is not None)
    bt.edit(template_property_sheet_id_list=[ps_title])

  def stepCheckPropertySheetMigration(self, sequence=None, **kw):
    """
    Check migration of Property Sheets from the Filesystem to ZODB
    """
    property_sheet_tool = self.getPortalObject().portal_property_sheets
    self.assertIn('UnitTest', property_sheet_tool.objectIds())

    property_list = property_sheet_tool.UnitTest.contentValues()

    self.assertEqual(len(property_list), 1)
    self.assertEqual(property_list[0].getReference(), 'ps_prop1')
    self.assertEqual(property_list[0].getElementaryType(), 'string')

  def stepRemovePropertySheet(self, sequence=None, sequencer_list=None, **kw):
    """
    Remove Property Sheet
    """
    ps_title = sequence.get('ps_title', None)
    ps_path = sequence.get('ps_path', None)
    self.assertTrue(ps_path is not None)
    self.assertTrue(os.path.exists(ps_path))
    os.remove(ps_path)
    self.assertFalse(os.path.exists(ps_path))
    return
    # Property Sheet will not be installed in file sytem
    self.assertFalse(os.path.exists(ps_path))
    # Property Sheet will be installed in ZODB
    self.assertTrue(getattr(self.portal.portal_property_sheets, ps_title, None) is not None)
    self.portal.portal_property_sheets.manage_delObjects([ps_title])
    self.assertFalse(getattr(self.portal.portal_property_sheets, ps_title, None) is not None)

  def stepRemovePropertySheetFromZODB(self, sequence=None, sequencer_list=None, **kw):
    """
    Remove Property Sheet from ZODB
    """
    ps_title = sequence.get('ps_title', None)
    ps_path = sequence.get('ps_path', None)
    self.assertTrue(ps_path is not None)
    # Property Sheet will not be installed in file sytem
    self.assertFalse(os.path.exists(ps_path))
    # Property Sheet will be installed in ZODB
    self.assertTrue(getattr(self.portal.portal_property_sheets, ps_title, None) is not None)
    self.portal.portal_property_sheets.manage_delObjects([ps_title])
    self.assertFalse(getattr(self.portal.portal_property_sheets, ps_title, None) is not None)

  def stepCheckPropertySheetExists(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Property Sheet
    """
    ps_title = sequence.get('ps_title', None)
    ps_path = sequence.get('ps_path', None)
    self.assertTrue(ps_path is not None)
    # Property Sheet will not be installed in file sytem
    self.assertFalse(os.path.exists(ps_path))
    # Property Sheet will be installed in ZODB
    self.assertTrue(getattr(self.portal.portal_property_sheets, ps_title, None) is not None)

  def stepCheckPropertySheetRemoved(self, sequence=None, sequencer_list=None, **kw):
    """
    Check deletion of Property Sheet
    """
    ps_path = sequence.get('ps_path', None)
    self.assertTrue(ps_path is not None)
    self.assertFalse(os.path.exists(ps_path))

  def stepCheckMigratedPropertySheetRemoved(self, sequence=None, **kw):
    """
    Check deletion of migrated Property Sheet
    """
    ps_id = sequence.get('ps_title', None)
    self.assertFalse(ps_id is None)
    self.assertNotIn(ps_id, self.getPortalObject().portal_property_sheets.objectIds())

  def stepCreateUpdatedPropertySheet(self, sequence=None, **kw):
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
    self.assertTrue(os.path.exists(file_path))
    sequence.edit(ps_data_u=ps_data)

  def stepCheckUpdatedPropertySheetExists(self, sequence=None, sequencer_list=None, **kw):
    """
    Check presence of Property Sheet
    """
    ps_title = sequence.get('ps_title', None)
    ps_path = sequence.get('ps_path', None)
    self.assertTrue(ps_path is not None)
    # Property Sheet will not be installed in file sytem
    self.assertFalse(os.path.exists(ps_path))
    # Property Sheet will be installed in ZODB
    self.assertTrue(getattr(self.portal.portal_property_sheets, ps_title, None) is not None)

  # Busines templates
  def stepImportBusinessTemplate(self, sequence=None, **kw):
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
    self.assertFalse(import_bt is None)
    self.assertEqual(import_bt.getPortalType(), 'Business Template')
    sequence.edit(import_bt=import_bt)

  def stepAddExtraSlashesToTemplatePath(self, sequence=None, **kw):
    """Add extra slashes to the template path for testing.
    """
    template_path = sequence.get('template_path')
    sequence.edit(template_path = template_path + '//')

  def stepInstallBusinessTemplate(self, sequence=None, **kw):
    """
    Install imported business template
    """
    import_bt = sequence.get('import_bt')
    import_bt.install(force=1)

  def stepReinstallBusinessTemplate(self, sequence=None, **kw):
    import_bt = sequence.get('current_bt')
    listbox_object_list = import_bt.BusinessTemplate_getModifiedObject()
    install_kw = {}
    for listbox_line in listbox_object_list:
      install_kw[listbox_line.object_id] = listbox_line.choice_item_list[0][1]
    import_bt.reinstall(object_to_update=install_kw)

  def stepCheckBeforeReinstall(self, sequence=None, **kw):
    import_bt = sequence.get('current_bt')
    diff_list = import_bt.BusinessTemplate_getModifiedObject()
    self.assertTrue('portal_types/Geek Object/become_geek'
                    in [line.object_id for line in diff_list])

  def stepInstallCurrentBusinessTemplate(self, sequence=None, **kw):
    import_bt = sequence.get('current_bt')
    import_bt.install(force=1)

  def stepInstallWithoutForceBusinessTemplate(self, sequence=None, **kw):
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
    import_bt.install(force=0, object_to_update=install_object_dict,
                      update_catalog=1)

  def stepInstallWithRemoveCheckedBusinessTemplate(self, sequence=None, **kw):
    import_bt = sequence.get('import_bt')
    object_list = import_bt.preinstall()
    install_object_dict = {}
    for obj in object_list.keys():
      state = object_list[obj][0]
      if state in ('Removed', 'Removed but used'):
        install_state = 'save_and_remove'
      elif state == 'Modified':
        install_state = 'backup'
      elif state == 'New':
        install_state = 'install'
      else:
        install_state = ""
      install_object_dict[obj] = install_state
    import_bt.install(force=0, object_to_update=install_object_dict,
                      update_catalog=1)

  def stepInstallDuplicatedBusinessTemplate(self, sequence=None, **kw):
    import_bt = sequence.get('import_bt')
    pt_id = sequence.get('object_ptype_id')
    object_to_update = {
      'portal_types/%s' % pt_id: 'install'}
    import_bt.install(object_to_update=object_to_update)

  def stepPartialCatalogMethodInstall(self, sequence=None, **kw):
    import_bt = sequence.get('import_bt')
    pc = self.getCatalogTool()
    catalog_id = pc.getSQLCatalog().id
    object_to_update = {'portal_catalog/'+catalog_id+'/z_another_fake_method':'install'}
    import_bt.install(object_to_update=object_to_update)

  def stepCreateNewBusinessTemplate(self, sequence=None, **kw):
    """
    Create a new Business Template
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.assertTrue(template.getBuildingState() == 'draft')
    self.assertTrue(template.getInstallationState() == 'not_installed')
    template.edit(title='geek template',
                  version='1.0',
                  description='bt for unit_test')
    sequence.edit(export_bt=template)

  def stepCreateSecondBusinessTemplate(self, sequence=None, **kw):
    """
    Create a second Business Template
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.assertTrue(template.getBuildingState() == 'draft')
    self.assertTrue(template.getInstallationState() == 'not_installed')
    template.edit(title='geek template',
                  version='2.0',
                  description='bt for unit_test')
    sequence.edit(second_export_bt=template)

  def stepCreateDuplicatedBusinessTemplate(self, sequence=None, **kw):
    """
    Create a new Business Template which will duplicate
    the configuration.
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.assertTrue(template.getBuildingState() == 'draft')
    self.assertTrue(template.getInstallationState() == 'not_installed')
    template.edit(title='duplicated geek template',
                  version='1.0',
                  description='bt for unit_test')
    sequence.edit(
        export_bt=template,
        previous_bt=sequence.get('current_bt'))

  def stepBuildBusinessTemplateFail(self, sequence=None, **kw):
    template = sequence.get('current_bt')
    self.assertRaises(AttributeError,
                      template.build)

  def stepCheckBuildWithBadPortalTypeFailed(self, sequence=None, **kw):
    template = sequence.get('current_bt')
    self.assertRaises(ValueError,
                      template.build)

  def stepBuildBusinessTemplate(self, sequence=None, **kw):
    """
    Build Business Template
    """
    template = sequence.get('current_bt')
    template.build()

  def stepEditBusinessTemplate(self, sequence=None, **kw):
    """
    Edit Business Template
    """
    template = sequence.get('current_bt')
    template.edit()

  def stepSaveBusinessTemplate(self, sequence=None, **kw):
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
    self.assertTrue(os.path.exists(template_path))

  def stepCheckObjectPropertiesInBusinessTemplate(self, sequence=None, **kw):
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
            self.assertTrue(data.__ac_local_roles__ is None)
          if hasattr(data, '_owner'):
            self.assertTrue(data._owner is None)
          if hasattr(aq_base(data), 'uid'):
            self.assertTrue(data.uid is None)

  def stepCheckUnindexActivityPresence(self, sequence=None, **kw):
    """
    Check if we have activity for unindex
    """
    message_list = [ m for m in self.portal.portal_activities.getMessageList()
                     if m.method_id == 'unindexObject'
                     and m.kw.get('uid') is not None ]
    self.assertEqual(len(message_list), 0)

  def stepCheckHasClearedCatalog(self, sequence=None, **kw):
    self.assertTrue(self._has_cleared_catalog)
    del self._has_cleared_catalog[:]

  def stepCheckPathNotUnindexAfterBuild(self, sequence=None, **kw):
    """
    Check that after a build, not unindex has been done
    """
    bc_id = sequence.get('bc_id')
    path = 'portal_categories/'+bc_id
    category_id_list = sequence.get('category_id_list')
    portal = self.getPortal()
    ob = portal.unrestrictedTraverse(path)
    self.assertTrue(ob is not None)
    for id_ in category_id_list:
      cat = ob[id_]
      catalog_ob_list = [x.getObject() for x in portal.portal_catalog(uid=cat.getUid())]
      self.assertTrue(len(catalog_ob_list) > 0)

  def stepSetUpdateToolFlagInBusinessTemplate(self, sequence=None):
    """
    Set flag for update in Business Template
    """
    bt = sequence.get('current_bt')
    self.assertEqual(bt.getTitle(),'erp5_core')
    bt.edit(template_update_tool=1)
    self.assertEqual(bt.getTemplateUpdateTool(), 1)

  def stepRemoveBusinessTemplate(self, sequence=None, **kw):
    """
    Remove current Business Template
    """
    bt_id = sequence.get('current_bt').getId()
    template_tool = self.getTemplateTool()
    template_tool.manage_delObjects([bt_id])
    bt = template_tool._getOb(bt_id, None)
    self.assertTrue(bt is None)

  def stepUninstallBusinessTemplate(self, sequence=None, **kw):
    """
    Uninstall current Business Template
    """
    bt = sequence.get('current_bt')
    bt.uninstall()

  def stepUninstallPreviousBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('previous_bt')
    bt.uninstall()

  def stepClearBusinessTemplateField(self, sequence=None, **kw):
    """
    Clear business template field
    """
    bt = sequence.get('current_bt')
    prop_dict = {}
    for prop in bt.propertyMap():
      prop_type = prop['type']
      pid = prop['id']
      if pid in ('id', 'uid', 'rid', 'sid', 'id_group', 'last_id',
                 'install_object_list_list', 'title', 'version', 'description',
                 'template_portal_type_allowed_content_type_list',
                 'template_portal_type_hidden_content_type_list',
                 'template_portal_type_property_sheet_list',
                 'template_portal_type_base_category_list'):
          continue
      if prop_type == 'text' or prop_type == 'string':
        prop_dict[pid] = ''
      elif prop_type == 'int':
        prop_dict[pid] = 0
      elif prop_type == 'lines' or prop_type == 'tokens':
        prop_dict[pid[:-5]] = ()
    bt.edit(**prop_dict)

  def stepRemoveSimulationTool(self, sequence=None, **kw):
    p = self.getPortal()
    p.manage_delObjects(['portal_simulation'])
    self.assertTrue(p._getOb('portal_simulation', None) is None)

  def stepCheckSimulationToolExists(self, sequence=None, **kw):
    self.assertTrue(self.getSimulationTool() is not None)

  def stepCheckSubobjectsNotIncluded(self, sequence=None, **kw):
    """Check subobjects are not included in the base category.
    """
    base_category_id = sequence.get('bc_id')
    bt = sequence.get('current_bt')
    # XXX maybe too low level
    base_category_obj = bt._category_item._objects.get(
        'portal_categories/%s' % base_category_id)
    self.assertTrue(base_category_obj is not None)
    self.assertEqual(len(base_category_obj.objectIds()), 0)

  def stepCheckNoMissingDependencies(self, sequence=None, **kw):
    """ Check if bt has no missing dependency
    """
    missing_dep = False
    bt = sequence.get('current_bt')
    try:
      bt.checkDependencies()
    except:
      missing_dep = True
    self.assertTrue(not missing_dep)

  def stepCheckMissingDependencies(self, sequence=None, **kw):
    """ Check if bt has missing dependency
    """
    missing_dep = False
    bt = sequence.get('current_bt')
    try:
      bt.checkDependencies()
    except:
      missing_dep = True
    self.assertTrue(missing_dep)

  def stepAddDependency(self, sequence=None, **kw):
    """ Add a dependency to the business template
    """
    bt = sequence.get('current_bt')
    bt.setDependencyList(['dependency_bt',])

  def stepCreateDependencyBusinessTemplate(self, sequence=None, **kw):
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.assertTrue(template.getBuildingState() == 'draft')
    self.assertTrue(template.getInstallationState() == 'not_installed')
    template.edit(title='dependency_bt',
                  version='1.0',
                  description='bt for unit_test')
    sequence.edit(dependency_bt=template)

  def stepSetSkinFolderRegisteredSelections(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    skin_folder._setProperty(
          'business_template_registered_skin_selections', ('Foo',),
          type='tokens')

  def stepSetSkinFolderRegisteredSelections2(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    skin_folder._updateProperty(
          'business_template_registered_skin_selections', ('Foo', 'Bar',))

  def stepCreateSkinSelection(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    ps.manage_skinLayers(skinpath=('erp5_core',), skinname='Foo', add_skin=1)

  def stepSetStaticSkinFolderRegisteredSelections(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_id = sequence.get('static_skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    skin_folder._setProperty(
          'business_template_registered_skin_selections', ('Foo',),
          type='tokens')
    selection = ps.getSkinPath('Foo')
    selection = selection.split(',')
    if skin_id not in selection:
      selection.append(skin_id)
      ps.manage_skinLayers(skinpath=tuple(selection),
                           skinname='Foo', add_skin=1)

  def stepCheckSkinSelectionAdded(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    # a new skin selection is added
    self.assertIn('Foo', ps.getSkinSelections())
    # and it contains good layers
    layers = ps.getSkinPath('Foo').split(',')
    self.assertIn(skin_id, layers)
    self.assertIn('erp5_core', layers)
    self.assertNotIn('erp5_xhtml_style', layers)
    skin_folder = ps._getOb(skin_id, None)
    skin_selection_list = skin_folder.getProperty(
        'business_template_registered_skin_selections', ())
    self.assertIn('Foo', skin_selection_list)

  def stepCheckStaticSkinSelection(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    static_skin_id = sequence.get('static_skin_folder_id')
    # a new skin selection is added
    self.assertIn('Foo', ps.getSkinSelections())
    # and it contains good layers
    layers = ps.getSkinPath('Foo').split(',')
    self.assertIn(skin_id, layers)
    self.assertIn('erp5_core', layers)
    self.assertNotIn('erp5_xhtml_style', layers)
    self.assertIn(static_skin_id, layers)

  def stepCreateCustomWorkflow(self, sequence=None, **kw):
    """
    Create a custom workflow
    """
    wf_id = 'custom_geek_workflow'
    pw = self.getWorkflowTool()
    addWorkflowByType(pw, WORKFLOW_TYPE, wf_id)
    workflow = pw._getOb(wf_id, None)
    self.assertTrue(workflow is not None)
    sequence.edit(workflow_id=workflow.getId())
    cbt = pw._chains_by_type
    props = {}
    if cbt is not None:
      for id, wf_ids in cbt.items():
        props['chain_%s' % id] = ','.join(wf_ids)
    key = 'chain_Geek Object'
    if props.has_key(key):
      props[key] = '%s,%s' % (props[key], wf_id)
    else:
      props[key] = wf_id
    pw.manage_changeWorkflows('', props=props)

  def stepCreateCustomBusinessTemplate(self, sequence=None, **kw):
    """
    Create a custom Business Template
    """
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.assertEquals(template.getBuildingState(), 'draft')
    self.assertEquals(template.getInstallationState(), 'not_installed')
    template.edit(title='custom geek template',
                  version='1.0',
                  description='custom bt for unit_test')
    sequence.edit(export_bt=template)

  def stepCheckCustomWorkflowChain(self, sequence=None, **kw):
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

  def stepCheckOriginalWorkflowChain(self, sequence=None, **kw):
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

  def stepCheckEmptyWorkflowChain(self, sequence=None, **kw):
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

  def stepCopyBusinessTemplate(self, sequence=None, **kw):
    """
    Copy business template
    """
    portal = self.getPortalObject()
    template_tool = portal.portal_templates
    import_bt = sequence.get('current_bt')
    cb_data = template_tool.manage_copyObjects([import_bt.getId()])
    copied, = template_tool.manage_pasteObjects(cb_data)
    sequence.edit(current_bt=template_tool._getOb(copied['new_id']))

  def stepRemoveWorkflowFromBusinessTemplate(self, sequence=None, **kw):
    """
    Remove workflow to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    current_twi = list(bt.getTemplateWorkflowIdList())
    current_twi.remove(sequence.get('workflow_id', ''))
    bt.edit(template_workflow_id_list=current_twi)

  def stepRemoveWorkflowChainFromBusinessTemplate(self, sequence=None, **kw):
    """
    Remove workflow chain to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    workflow_id = sequence.get('workflow_id', '')
    new_value = []
    workflow_chain_list = list(bt.getTemplatePortalTypeWorkflowChainList())
    for workflow_chain in workflow_chain_list:
      portal_type, wkflow_id = workflow_chain.split(' | ')
      if wkflow_id != workflow_id:
        new_value.append(workflow_chain)
    bt.edit(template_portal_type_workflow_chain_list=new_value)

  def stepCreatePortalTypeRole(self, sequence=None, **kw):
    """
    Create portal type role
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_pt = pt._getOb(object_id)
    object_pt.newContent(portal_type='Role Information',
      title='Geek Role Definition',
      description='A definition with non ascii chars éàè & ampersand',
      role_name_list=('geek_role_definition',),
      role_category_list=('group/g1','function/f1'),
      role_base_category_script_id='Base Category Script',
      role_base_category_list=('group','site'))

    sequence.edit(portal_type_role='geek_role_definition')

  def stepAddPortalTypeRolesToBusinessTemplate(self, sequence=None, **kw):
    """
    Add type role to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    ptype_ids = []
    ptype_ids.append(sequence.get('object_ptype_id', ''))
    ptype_ids.append(sequence.get('module_ptype_id', ''))
    self.assertEqual(len(ptype_ids), 2)
    bt.edit(template_portal_type_role_list=ptype_ids)

  def stepCheckPortalTypeRoleExists(self, sequence=None, **kw):
    """
    Cehck that portal type role exist
    """
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    role, = pt[object_id].getRoleInformationList()
    self.assertEqual('Geek Role Definition', role.getTitle())
    self.assertEqual(['geek_role_definition'], role.getRoleNameList())
    self.assertEqual('A definition with non ascii chars éàè & ampersand', role.getDescription())
    self.assertEqual(['group/g1','function/f1'], role.getRoleCategoryList())
    self.assertEqual(['group','site'], role.getRoleBaseCategoryList())
    self.assertEqual('Base Category Script', role.getRoleBaseCategoryScriptId())

  def stepModifyPortalType(self, sequence=None, **kw):
    """
    Modify Portal Type
    """
    pt = self.getTypeTool()
    object_type = pt._getOb('Geek Object', None)
    object_type.title = 'Modified %s' % object_type.title

  def stepUnmodifyPortalType(self, sequence=None, **kw):
    """
    Unmodify Portal Type
    """
    pt = self.getTypeTool()
    object_type = pt._getOb('Geek Object', None)
    object_type.title = object_type.title[len('Modified '):]

  def stepCheckModifiedPortalTypeExists(self, sequence=None, **kw):
    """
    Check presence of modified portal type
    """
    self.stepCheckPortalTypeExists(sequence=sequence, **kw)
    pt = self.getTypeTool()
    object_id = sequence.get('object_ptype_id')
    object_type = pt._getOb(object_id, None)
    self.assertTrue(object_type.title.startswith('Modified '))

  def stepCreateFakeZODBScript(self, sequence=None, **kw):
    """Create a Script inside portal_skins
    """
    grain_of_sand = ''.join([random.choice(string.ascii_letters) for i in xrange(10)])
    python_script_id = 'ERP5Site_dummyScriptWhichRandomId%s' % grain_of_sand
    skin_folder_id = 'custom'
    if getattr(self.portal.portal_skins, skin_folder_id, None) is None:
        self.portal.portal_skins.manage_addProduct['OFSP'].manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]
    skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(
                                                                 id=python_script_id)
    skin_folder[python_script_id].ZPythonScript_edit('param=""', 'return "body"')
    sequence.set('python_script_id', python_script_id)
    sequence.set('skin_folder_id', skin_folder_id)

  def stepModifyFakeZODBScript(self, sequence=None, **kw):
    script = self.portal.portal_skins[sequence['skin_folder_id']]\
        [sequence['python_script_id']]
    script.ZPythonScript_edit('new_param=""', 'return "new body"')

  def stepCheckFakeZODBScriptIsUpdated(self, sequence=None, **kw):
    script = self.portal.portal_skins[sequence['skin_folder_id']]\
        [sequence['python_script_id']]
    self.assertEquals('return "body"\n',
        script._body)

  def stepCheckFakeZODBScriptIsBackedUp(self, sequence=None, **kw):
    trash = self.getTrashTool()
    trash_bin, = trash.objectValues()
    backup_script = trash_bin.portal_skins_items[sequence['skin_folder_id']]\
        [sequence['python_script_id']]
    self.assertEquals('return "new body"\n',
        backup_script._body)

  def stepAddCustomSkinFolderToBusinessTemplate(self, sequence=None, **kw):
    """
    Add types to business template
    """
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    template_skin_id_list = list(bt.getProperty('template_skin_id_list'))
    template_skin_id_list.append('custom')
    bt.edit(template_skin_id_list=template_skin_id_list)

  def stepCheckFakeScriptIsDeleted(self, sequence=None, **kw):
    """Check that script inside ZODB is deleted by BT reinstallation
    """
    python_script_id = sequence.get('python_script_id')
    skin_folder_id = sequence.get('skin_folder_id')
    folder = self.portal.portal_skins[skin_folder_id]
    self.assertNotIn(python_script_id, folder.objectIds())

  def stepSetOldSitePropertyValue(self, sequence=None, **kw):
    """Set the old value to a site property."""
    sequence.set('site_property_value', 'old')

  def stepSetNewSitePropertyValue(self, sequence=None, **kw):
    """Set the new value to a site property."""
    sequence.set('site_property_value', 'new')

  def stepCreateSiteProperty(self, sequence=None, **kw):
    """Create a site property."""
    portal = self.getPortal()
    portal._setProperty('a_property', sequence.get('site_property_value'))

  def stepModifySiteProperty(self, sequence=None, **kw):
    """Modify a site property."""
    portal = self.getPortal()
    portal._updateProperty('a_property', sequence.get('site_property_value'))

  def stepCheckSiteProperty(self, sequence=None, **kw):
    """Check a site property."""
    portal = self.getPortal()
    self.assertEqual(portal.getProperty('a_property'),
                      sequence.get('site_property_value'))

  def stepCheckSitePropertyRemoved(self, sequence=None, **kw):
    """Check if a site property is removed."""
    portal = self.getPortal()
    self.assertFalse(portal.hasProperty('a_property'))

  def stepAddSitePropertyToBusinessTemplate(self, sequence=None, **kw):
    """Add a site property into a business template."""
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_site_property_id_list=('a_property',))

  def stepCheckSkinSelectionRemoved(self, sequence=None, **kw):
    """
    Check that a skin selection has been removed.
    """
    self.assertNotIn('Foo', self.portal.portal_skins.getSkinSelections())

  def stepCheckSkinSelectionNotRemoved(self, sequence=None, **kw):
    """
    Check that a skin selection has not been removed.
    """
    self.assertIn('Foo', self.portal.portal_skins.getSkinSelections())

  def stepUserDisableSkinSelectionRegistration(self, sequence=None, **kw):
    """
    Simulate User disabling skin registration from UI.
    """
    self.app.REQUEST.set('your_register_skin_selection', 0)

  def stepUserSelectSkinToBeChanged(self, sequence=None, **kw):
    """
    User selects skin to be changed from UI.
    """
    select_skin_to_be_changed_list = self.portal.portal_skins.getSkinSelections()[:1]
    select_skin_not_to_be_changed_list = self.portal.portal_skins.getSkinSelections()[1:]
    sequence.edit(select_skin_to_be_changed_list = select_skin_to_be_changed_list, \
                  select_skin_not_to_be_changed_list = select_skin_not_to_be_changed_list)
    self.app.REQUEST.set('your_skin_layer_list', select_skin_to_be_changed_list)

  def stepCheckUserSelectedSkinToBeChanged(self, sequence=None, **kw):
    """
    Check that only selected to be changed skins are affected.
    """
    skin_folder_id = sequence.get('skin_folder_id')
    select_skin_to_be_changed_list = sequence.get('select_skin_to_be_changed_list')
    select_skin_not_to_be_changed_list = sequence.get('select_skin_not_to_be_changed_list')
    for skin_name in select_skin_to_be_changed_list:
      self.assertIn(skin_folder_id, self.portal.portal_skins.getSkinPath(skin_name))
    for skin_name in select_skin_not_to_be_changed_list:
      self.assertNotIn(skin_folder_id, self.portal.portal_skins.getSkinPath(skin_name))

  def stepCheckSkinFolderPriorityOn(self, sequence=None, **kw):
    """
    Check skin folder priority
    """
    ps = self.portal.portal_skins
    for skin in ps.getSkinSelections():
      self.assertEqual('erp5_core', ps.getSkinPath(skin).split(',')[0])
      self.assertEqual('erp5_geek', ps.getSkinPath(skin).split(',')[1])

  def stepCheckSkinFolderPriorityOff(self, sequence=None, **kw):
    """
    Check skin folder priority off
    """
    ps = self.portal.portal_skins
    for skin in ps.getSkinSelections():
      self.assertEqual('erp5_geek', ps.getSkinPath(skin).split(',')[0])
      self.assertEqual('erp5_core', ps.getSkinPath(skin).split(',')[1])

  def stepUserDisableSkinFolderPriority(self, sequence=None, **kw):
    """
    User chooses skin folder priority off from UI
    """
    self.app.REQUEST.set('your_reorder_skin_selection', 0)

  def stepSetExistingSkinFolderPriority(self, sequence=None, **kw):
    """
    Set exisitng skin priority for test
    """
    skin_folder = self.portal.portal_skins['erp5_core']
    if not skin_folder.hasProperty('business_template_skin_layer_priority'):
      skin_folder.manage_addProperty('business_template_skin_layer_priority', \
                                     10000.0, 'float')

  def stepSetBusinessTemplateSkinFolderPriority(self, sequence=None, **kw):
    """
    Set skin folder priority.
    """
    skin_folder_id = sequence.get('skin_folder_id')
    skin_folder = self.portal.portal_skins[skin_folder_id]
    skin_folder.manage_addProperty('business_template_skin_layer_priority', 9999.0, 'float')

  def stepModifySkinFolder(self, sequence=None, **kw):
    """
    Modify the skin folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    skin_folder._setProperty(
                    'business_template_skin_layer_priority',
                    99, type='float')
    # Make sure it is really set.
    self.assertEqual(
        99, skin_folder.getProperty('business_template_skin_layer_priority'))

  def stepUnmodifySkinFolder(self, sequence=None, **kw):
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    skin_folder._delProperty('business_template_skin_layer_priority')
    self.assertEqual(
        None, skin_folder.getProperty('business_template_skin_layer_priority'))

  def stepCheckModifiedSkinFolderExists(self, sequence=None, **kw):
    """
    Check modified skin folder
    """
    ps = self.getSkinsTool()
    skin_id = sequence.get('skin_folder_id')
    skin_folder = ps._getOb(skin_id, None)
    self.assertEqual(
        99, skin_folder.getProperty('business_template_skin_layer_priority'))

  def stepCheckDocumentPropertySheetSameName(self, sequence=None, **kw):
    self.assertEqual(sequence['ps_title'], sequence['document_title'])
    self.assertEqual(os.path.basename(sequence['document_path']),
        os.path.basename(sequence['ps_path']))

  def stepRemovePropertySheetFromBusinessTemplate(self, sequence=None, **kw):
    """
    Add Property Sheet to Business Template
    """
    sequence['current_bt'].edit(template_property_sheet_id_list=[])

  def stepCreateAllPropertySheetsFromFilesystem(self, sequence=None, **kw):
    self.portal.portal_property_sheets.createAllPropertySheetsFromFilesystem()

  def stepRemovePropertySheetZodbOnly(self, sequence=None, **kw):
    """
    Remove Property Sheet, but only from ZODB
    """
    self.portal.portal_property_sheets.manage_delObjects([sequence['ps_title']])

  def stepCheckDraftBuildingState(self, sequence=None, **kw):
    self.assertEqual(sequence['current_bt'].getBuildingState(), 'draft')

  def stepSimulateAndCopyPrePropertySheetMigrationBusinessTemplate(self, sequence=None, **kw):
    portal = self.getPortalObject()
    template_tool = portal.portal_templates
    current_bt = sequence['current_bt']
    cb_data = template_tool.manage_copyObjects([current_bt.getId()])
    copied, = template_tool.manage_pasteObjects(cb_data)
    current = current_bt._property_sheet_item._objects.copy()
    current_bt._property_sheet_item._objects = PersistentMapping()
    for k,v in current.iteritems():
      k = k.lstrip('portal_property_sheets/')
      current_bt._property_sheet_item._objects[k] = v
    sequence.edit(current_bt=template_tool._getOb(copied['new_id']))


class TestBusinessTemplate(BusinessTemplateMixin):
  """
    Test these operations:

    - Create a template

    - Install a template

    - Uninstall a template

    - Upgrade a template
  """

  def getTitle(self):
    return "Business Template"

  # tests
  def test_Title(self):
    """Tests the Title of the Template Tool."""
    self.assertEqual('Template Tool', self.getTemplateTool().Title())

  def test_01_checkNewSite(self):
    """Test Check New Site"""
    sequence_list = SequenceList()
    sequence_string = '\
                       UseCoreBusinessTemplate  \
                       CheckTools \
                       CheckBuiltBuildingState \
                       CheckInstalledInstallationState \
                       CheckSkinsLayers \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  # test of portal types
  def test_02_BusinessTemplateWithPortalTypes(self):
    """Test Business Template With Portal Types"""
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
                       CreateSecondBusinessTemplate \
                       UseSecondBusinessTemplate \
                       AddPortalTypeToBusinessTemplate \
                       FillPortalTypesFields \
                       ModifyPortalTypeInBusinessTemplate \
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
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckSkinsLayers \
                       CheckPortalTypeExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPortalTypeRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_021_BusinessTemplateWithPortalTypesAndWrongValues(self):
    """Test Business Template With Portal Types and Bad Values"""
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
    sequence_list.play(self)

  # test of skins
  def test_03_BusinessTemplateWithSkins(self):
    """Test Business Template With Skin Folder"""
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
    sequence_list.play(self)

  # test of workflow
  def test_04_BusinessTemplateWithWorkflow(self):
    """Test Business Template With Workflow"""
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
    sequence_list.play(self)

  def test_041_BusinessTemplateWithWorkflowRemoved(self):
    """Test Business Template With Remove Of Workflow"""
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
                       ModifyWorkflowChain \
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
                       CheckHasClearedCatalog \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckSkinsLayers \
                       CheckWorkflowExists \
                       CheckWorkflowChainRemoved \
                       SaveWorkflowChain \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_042_BusinessTemplateWithWorkflowRemoved(self):
    """Test Business Template With Remove Of Workflow"""
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
                       ModifyWorkflowChain \
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
                       Tic \
                       InstallWithRemoveCheckedBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckSkinsLayers \
                       CheckWorkflowRemoved \
                       CheckWorkflowChainRemoved \
                       SaveWorkflowChain \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_043_BusinessTemplateWithWorkflowChainRemoved(self):
    """Test Business Template With Remove Of Workflow Chain"""
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
                       AddWorkflowToBusinessTemplate \
                       AddRemovedWorkflowChainToBusinessTemplate \
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
                       Tic \
                       InstallWithRemoveCheckedBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckSkinsLayers \
                       CheckWorkflowExists \
                       CheckWorkflowChainRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  # test of module
  def test_05_BusinessTemplateWithModule(self):
    """Test Business Template With Module"""
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
                       RemoveModule \
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
                       CheckModulePermissions \
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
  def test_06_BusinessTemplateWithBaseCategory(self):
    """Test Business Template With Base Category"""
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
    sequence_list.play(self)

  def test_06_BusinessTemplateReInstallWithBaseCategory(self):
    """Test Business Template reinstall after removing Base Category"""
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
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       RemoveBaseCategory \
                       CheckPreinstallReturnSomething \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  # test of actions
  def test_07_BusinessTemplateWithOneAction(self):
    """Test Business Template With One Action"""
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
    sequence_list.play(self)

  def test_07_BusinessTemplateWithEmptyAction(self):
    """Test Business Template Upgrade With Empty Action"""
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
    sequence_list.play(self)

  def test_08_BusinessTemplateWithTwoActions(self):
    """Test Business Template With Two Actions"""
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
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckSecondActionNotExists \
                       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_09_BusinessTemplateWithPath(self):
    """Test Business Template With A Simple Path"""
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
    sequence_list.play(self)

  def test_091_BusinessTemplateDoNotUnindexObject(self):
    """Test Business Template Do Not Unindex Object At Build"""
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
    sequence_list.play(self)

  def test_10_BusinessTemplateWithPathAndJoker1(self):
    """Test Business Template With Path And Joker *"""
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
    sequence_list.play(self)

  def test_101_BusinessTemplateUninstallWithPathAndJoker1Removed(self):
    """Test Business Template Uninstall With Path And Joker * Removed"""
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
    sequence_list.play(self)

  def test_11_BusinessTemplateWithPathAndJoker2(self):
    """Test Business Template With Path And Joker **"""
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
    sequence_list.play(self)

  def test_111_BusinessTemplateWithContentTypeRegistry(self):
    """Test Business Template With Content Type Registry As Path

      Test if content_type_registry is propertly exported and installed within
      business template (as path).
      This test shows that there is a slight issue - when the bt that brought
      content_type_registry is uninstalled, the registry is removed altogether,
      not restored, which maybe is an issue and maybe not.
      The sequence string does not do CheckNoTrashBin after installing
      template because there is the old registry (I think) and it is ok.
    """
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
    sequence_list.play(self)

  def test_12_BusinessTemplateWithCatalogMethod(self):
    """Test Business Template With Catalog Method, Related Key, Result Key And Table"""
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
                       Tic \
                       CheckKeysAndTableRemoved \
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
    sequence_list.play(self)

  def test_121_BusinessTemplateWithUpdateOfCatalogMethod(self):
    """Test Business Template Update With Catalog Method, Related Key, Result Key And Table"""
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
                       RemoveCatalogMethod \
                       CreateUpdateCatalogMethod \
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
                       CreateCatalogMethod \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckPreinstallReturnSomething \
                       CheckCatalogPreinstallReturnCatalogMethod \
                       Tic \
                       InstallWithoutForceBusinessTemplate \
                       CheckHasClearedCatalog \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckSkinsLayers \
                       CheckUpdatedCatalogMethodExists \
                       CheckKeysAndTableExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckKeysAndTableRemoved \
                       CheckCatalogMethodRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_122_BusinessTemplateWithRemoveCatalogMethod(self):
    """Test Business Template remove a Catalog Method"""
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateCatalogMethod \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddCatalogMethodToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       SaveBusinessTemplate \
                       CheckNotInstalledInstallationState \
                       RemoveCatalogMethod \
                       RemoveBusinessTemplate \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallBusinessTemplate \
                       Tic \
                       CheckBuiltBuildingState \
                       CheckInstalledInstallationState \
                       CheckCatalogMethodExists \
                       \
                       CopyBusinessTemplate \
                       Tic \
                       RemoveCatalogMethodToBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       SaveBusinessTemplate \
                       ImportBusinessTemplate \
                       Tic \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallWithoutForceBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckInstalledInstallationState \
                       Tic \
                       CheckCatalogMethodRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_13_BusinessTemplateWithRole(self):
    """Test Business Template With Role"""
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
    sequence_list.play(self)

  def test_14_BusinessTemplateWithLocalRoles(self):
    """Test Business Template With Local Roles"""
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
                       Tic \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       Tic \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckModuleLocalRolesInCatalogBeforeUpdate \
                       InstallBusinessTemplate \
                       Tic \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckLocalRolesExists \
                       CheckModuleLocalRolesInCatalogAfterUpdate \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckLocalRolesRemoved \
                       RemoveModule \
                       RemovePortalType \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_15_BusinessTemplateWithPropertySheet(self):
    """Test Business Template With Property Sheet"""
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
    sequence_list.play(self)

  def test_151_BusinessTemplateWithPropertySheetMigration(self):
    """Test Business Template With Property Sheet Migration"""
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
                       CheckPropertySheetMigration \
                       CheckPropertySheetRemoved \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckMigratedPropertySheetRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_155_BusinessTemplateUpdateWithPropertySheet(self):
    """Test Business Template With Property Sheet"""
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
                       RemovePropertySheetFromZODB \
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
    sequence_list.play(self)

  def test_16_BusinessTemplateWithAllItems(self):
    """Test Business Template With All Items"""
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
                       RemoveModule \
                       RemovePortalType \
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
    sequence_list.play(self)

  def test_17_SubobjectsAfterUpgradeOfBusinessTemplate(self):
    """Test Upgrade Of Business Template Keeps Subobjects"""
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
    sequence_list.play(self)

  def test_18_upgradeBusinessTemplateWithAllItems(self):
    """Test Upgrade Business Template With All Items"""
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
                       RemoveModule \
                       RemovePortalType \
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
                       CheckWorkflowChainExists \
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
                       RemoveModule \
                       RemovePortalType \
                       RemoveSkinFolder \
                       RemoveBaseCategory \
                       RemoveWorkflow \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveRole \
                       RemovePropertySheetFromZODB \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  # test specific to erp5_core
  def test_19_checkUpdateBusinessTemplateWorkflow(self):
    """Test Check Update of Business Template Workflows is working"""
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
                       RemoveModule \
                       RemovePortalType \
                       RemoveSkinFolder \
                       RemoveBaseCategory \
                       RemoveWorkflow \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveRole \
                       RemovePropertySheetFromZODB \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_20_checkUpdateTool(self):
    """Test Check Update of Tool is working"""
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
                       RemoveModule \
                       RemovePortalType \
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
                       RemoveModule \
                       RemovePortalType \
                       RemoveSkinFolder \
                       RemoveBaseCategory \
                       RemoveWorkflow \
                       RemoveCatalogMethod \
                       RemoveKeysAndTable \
                       RemoveRole \
                       RemovePropertySheetFromZODB \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_21_CategoryIncludeSubobjects(self):
    """Test Category includes subobjects"""
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
    sequence_list.play(self)

  def test_23_CheckNoDependencies(self):
    """Test if a new Business Template has no dependencies"""
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
    sequence_list.play(self)

  def test_24_CheckMissingDependency(self):
    """Test if a exception is raised when a dependency is missing"""
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
    sequence_list.play(self)

  def test_25_CheckNoMissingDependency(self):
    """Test if the dependency problem is fixed when the dependency is installed"""
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
    sequence_list.play(self)

  # test of skins
  def test_26_ImportWithDoubleSlashes(self):
    """Test Importing Business Template With Double Slashes"""
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
    sequence_list.play(self)

  def test_27_CheckInstallWithBackup(self):
    """Test if backup works during installation of a bt with subfolder in skin folder"""
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
    sequence_list.play(self)

  def test_28_CheckBuildWithUnexistingPath(self):
    """Test if build fails when one of the paths does not exist"""
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
    sequence_list.play(self)

  def test_29_CheckUninstallRemovedSkinFolder(self):
    """Test if uninstall works even when the skin folder has already been removed from the site"""
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
    sequence_list.play(self)

  def test_30_CheckInstalledCatalogProperties(self):
    """
    Test if installing some new catalog properties do not overwrite existing ones

    Also check that it doesn't install two keys for the same column"""
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
                       ModifyRelatedKey \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       CheckCatalogConfigurationKept \
                       CheckRelatedKeyNonDuplicated \
                       DuplicateRelatedKeyColumn \
                       UninstallBusinessTemplate \
                       CheckOnlyDuplicateRelatedKeyRemains \
                       CheckCatalogConfigurationKept \
                       RemoveCatalogLocalConfiguration \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_31_BusinessTemplateWithCatalogMethod(self):
    """Test that we keep local changes if we specify a list of objects to update"""
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
    sequence_list.play(self)

  def test_32_BusinessTemplateWithDuplicatedPortalTypes(self):
    """Test Business Template With Duplicated Portal Types"""
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
    sequence_list.play(self)

  def test_33_BusinessTemplateWithNewSkinSelection(self):
    """Test Business Template With New Skin Selection"""
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       SetSkinFolderRegisteredSelections \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddRegisteredSelectionToBusinessTemplate \
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
    sequence_list.play(self)

  def test_34_UpgradeForm(self):
    """Test Upgrade Form"""
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
                       CheckHasClearedCatalog \
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
                       Tic \
                       InstallWithoutForceBusinessTemplate \
                       CheckHasClearedCatalog \
                       Tic \
                       \
                       CheckFormGroups \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_34_UpgradeFormAttribute(self):
    """Test Upgrade Form"""
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
    sequence_list.play(self)

  def test_34_RemoveForm(self):
    """Test Upgrade Form

    - Add a form into the skin folders of erp5_geek and erp5_nerd
    - Remove the form from erp5_geek
    - Check that the form is removed from erp5_geek
    - Check that the form is not removed from erp5_nerd
    - Check that the title field is not removed from erp5_nerd
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateAnotherSkinFolder \
                       CreateNewFormIntoErp5Nerd \
                       CreateNewForm \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddAnotherSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       RemoveAllTrashBins \
                       \
                       CheckFormGroups \
                       \
                       RemoveForm \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddAnotherSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       \
                       CreateNewForm \
                       \
                       CheckFieldTitleIsNotRemovedFromErp5Nerd \
                       \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckFormIsRemoved \
                       CheckFormIsNotRemovedFromErp5Nerd \
                       CheckFieldTitleIsNotRemovedFromErp5Nerd \
                       CheckTrashBin \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_checkDependencies(self):
    from Products.ERP5.Document.BusinessTemplate import \
          BusinessTemplateMissingDependency
    template_tool = self.getPortal().portal_templates
    erp5_core_version = template_tool.getInstalledBusinessTemplate(
                                    'erp5_core').getVersion()
    bt5 = self.getPortal().portal_templates.newContent(
          portal_type='Business Template',
          dependency_list=['erp5_core (>= %s)' % erp5_core_version])
    self.assertEqual(None, bt5.checkDependencies())

    bt5.setDependencyList(['erp5_core (> %s)' % erp5_core_version])
    self.assertRaises(BusinessTemplateMissingDependency, bt5.checkDependencies)

    bt5.setDependencyList(['not_exists (= 1.0)'])
    self.assertRaises(BusinessTemplateMissingDependency, bt5.checkDependencies)

  def test_34_RemovePartialWorkflowChain(self):
    """Test Remove Chain"""
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
    sequence_list.play(self)

  def test_35_UpdatePartialWorkflowChain(self):
    """Test Update Workflow Chain"""
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
    sequence_list.play(self)

  def test_35a_UpdatePartialWorkflowChainWithRemove(self):
    """Check that chains are correctly removed during update

    When previous business template defined that object is associated
    with workflows A, B and that new one says that only A association
    is required check that after installing only A will be on workflow
    chains."""
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
                       CopyBusinessTemplate \
                       Tic \
                       \
                       CreateCustomWorkflow \
                       CheckCustomWorkflowChain \
                       AppendWorkflowToBusinessTemplate \
                       AppendWorkflowChainToBusinessTemplate \
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
                       \
                       RemoveWorkflowFromBusinessTemplate \
                       RemoveWorkflowChainFromBusinessTemplate \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       SaveBusinessTemplate \
                       ImportBusinessTemplate \
                       Tic \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       CheckOriginalWorkflowChain \
                       CheckWorkflowChainExists \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_36_CheckPortalTypeRoles(self):
    """Test Portal Type Roles"""
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
    sequence_list.play(self)

  def test_37_UpdatePortalType(self):
    """Test Update Portal Type"""
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
    sequence_list.play(self)

  def test_38_CheckReinstallation(self):
    """Test Reinstallation"""
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
                       RemoveFirstAction \
                       CheckBeforeReinstall \
                       ReinstallBusinessTemplate Tic \
                       \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddCustomSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       InstallCurrentBusinessTemplate Tic \
                       CreateFakeZODBScript \
                       ReinstallBusinessTemplate \
                       Tic \
                       CheckFakeScriptIsDeleted \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_CheckInstallErasingExistingDocument(self):
    """ Installing a business template containing a path that already exist
    in the site should overwrite this path after storing it in portal_trash
    """
    sequence_list = SequenceList()

    sequence_string = '\
                       RemoveAllTrashBins \
                       CreateFakeZODBScript \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddCustomSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       ModifyFakeZODBScript \
                       SaveBusinessTemplate \
                       ImportBusinessTemplate \
                       InstallCurrentBusinessTemplate Tic \
                       CheckFakeZODBScriptIsUpdated \
                       CheckFakeZODBScriptIsBackedUp \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_CheckUpdateErasingExistingDocument(self):
    """ Updating a business template containing a path that already exist
    in the site should overwrite this path after storing it in portal_trash
    """
    sequence_list = SequenceList()

    sequence_string = '\
                       RemoveAllTrashBins \
                       CreateFakeZODBScript \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       ImportBusinessTemplate \
                       InstallCurrentBusinessTemplate Tic \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       AddCustomSkinFolderToBusinessTemplate \
                       BuildBusinessTemplate \
                       ModifyFakeZODBScript \
                       SaveBusinessTemplate \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallWithoutForceBusinessTemplate Tic \
                       CheckFakeZODBScriptIsUpdated \
                       CheckFakeZODBScriptIsBackedUp \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_39_CheckSiteProperties(self):
    """Test Site Properties"""
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
    sequence_list.play(self)

  # test of uid
  def test_40_BusinessTemplateUidOfCategoriesUnchanged(self):
    """Test that the uids of categories are unchanged during their reinstall

      Add sub categories with the title 'toto' and save their uid in a dict
      Create business template with the sub categories in path_template_list
      The sub categories title are changed in 'foo'
      Install business template
      Check the old sub categories with' toto' as title
      And check if the uid of sub categories is unchanged
    """
    sequence_list = SequenceList()
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
                       CheckSubCategoriesExists \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       ModifySubCategories \
                       Tic \
                       InstallBusinessTemplate \
                       Tic \
                       CheckSubCategoriesExists \
                       CheckUidSubCategories \
                       UninstallBusinessTemplate \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_158_BusinessTemplateSkinSelectionRemove(self):
    """Test Business Template Uninstall With Skin Selection"""
    sequence_list = SequenceList()
    sequence_string = 'CreateSkinFolder \
                       SetSkinFolderRegisteredSelections \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddRegisteredSelectionToBusinessTemplate \
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
    sequence_list.play(self)

  def test_158_BusinessTemplateSkinSelectionRemoveOnlyIfUnused(self):
    """Test Business Template Uninstall With an used Skin Selection"""
    sequence_list = SequenceList()
    sequence_string = 'CreateSkinFolder \
                       CreateStaticSkinFolder \
                       CreateSkinSelection \
                       SetSkinFolderRegisteredSelections \
                       SetStaticSkinFolderRegisteredSelections \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddRegisteredSelectionToBusinessTemplate \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveSkinFolder \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       InstallBusinessTemplate \
                       Tic \
                       CheckStaticSkinSelection \
                       UninstallBusinessTemplate \
                       CheckSkinSelectionNotRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_159_BusinessTemplateNotRegisterSkin(self):
    """Test Business Template will not register existing Skin"""
    sequence_list = SequenceList()
    sequence_string = 'CreateSkinFolder \
                       SetSkinFolderRegisteredSelections \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddSkinFolderToBusinessTemplate \
                       AddRegisteredSelectionToBusinessTemplate \
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
    sequence_list.play(self)

  def test_160_BusinessTemplateChangeOnlySelectedSkin(self):
    """Test Business Template will change only selected skins"""
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
    sequence_list.play(self)

  def test_161_BusinessTemplateCheckSkinPriorityOrderingEnabled(self):
    """Test Business Template will reorder skins path in Skin"""
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
    sequence_list.play(self)

  def test_162_BusinessTemplateCheckSkinPriorityOrderingDisabled(self):
    """Test Business Template will not reorder skins path in Skin"""
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
    sequence_list.play(self)

  def test_163_UpdateSkinFolderWithRegisteredSkinSelection(self):
    """Test Update Skin Folder"""
    sequence_list = SequenceList()
    sequence_list.addSequenceString("""
      CreateSkinFolder
      SetSkinFolderRegisteredSelections
      CreateNewBusinessTemplate
      UseExportBusinessTemplate
      AddSkinFolderToBusinessTemplate
      AddRegisteredSelectionToBusinessTemplate
      BuildBusinessTemplate
      SaveBusinessTemplate
      RemoveSkinFolder
      RemoveBusinessTemplate
      RemoveAllTrashBins

      ImportBusinessTemplate
      UseImportBusinessTemplate
      InstallBusinessTemplate
      Tic
      CheckSkinSelectionAdded

      ModifySkinFolder

      CopyBusinessTemplate
      Tic
      EditBusinessTemplate
      BuildBusinessTemplate
      CheckBuiltBuildingState
      SaveBusinessTemplate

      UnmodifySkinFolder

      ImportBusinessTemplate
      Tic
      UseImportBusinessTemplate
      InstallWithoutForceBusinessTemplate
      Tic

      CheckModifiedSkinFolderExists
      CheckSkinSelectionAdded

      SetSkinFolderRegisteredSelections2
      CopyBusinessTemplate
      EditRegisteredSelectionToBusinessTemplate
      BuildBusinessTemplate
      InstallCurrentBusinessTemplate
      Tic
    """)
    sequence_list.play(self)

  @expectedFailure
  def test_164_checkCopyBuild(self):
    """Test Check basic copy and build is working"""
    sequence_list = SequenceList()
    sequence_list.addSequenceString("""
      UseCoreBusinessTemplate
      CopyCoreBusinessTemplate
      BuildCopyCoreBusinessTemplate
      CheckOriginalAndCopyBusinessTemplate
      Tic
    """)
    sequence_list.play(self)

  def test_165_checkCopyBuildInstall(self):
    """Test Check basic copy, build and installation is working"""
    sequence_list = SequenceList()
    sequence_list.addSequenceString("""
      UseCoreBusinessTemplate
      CopyCoreBusinessTemplate
      BuildCopyCoreBusinessTemplate
      InstallCopyCoreBusinessTemplate
      Tic
    """)
    sequence_list.play(self)

  def test_167_InstanceAndRelatedClassDefinedInSameBT(self):
    # This test does too much since we don't modify objects anymore during
    # download. Objects are cleaned up during installation, which does not
    # require any specific action about garbage collection or pickle cache.
    from Products.ERP5.Document.BusinessTemplate import BaseTemplateItem
    portal = self.portal
    BaseTemplateItem_removeProperties = BaseTemplateItem.removeProperties
    object_id_list = 'old_file', 'some_file'
    marker_list = []
    def removeProperties(self, obj, export):
      # Check it works if the object is modified during install.
      if obj.id in object_id_list:
        obj.int_index = marker_list.pop()
      return obj
    SimpleItem_getCopy = SimpleItem._getCopy
    try:
      BaseTemplateItem.removeProperties = removeProperties
      SimpleItem._getCopy = lambda *args: self.fail()
      template_tool = portal.portal_templates
      bt_path = os.path.join(os.path.dirname(__file__), 'test_data',
                             'test_167_InstanceAndRelatedClassDefinedInSameBT')
      # create a previously existing instance of the overriden document type
      File = portal.portal_types.getPortalTypeClass('File')
      portal._setObject('another_file', File('another_file'))
      self.tic()
      # logged errors could keep a reference to a traceback having a reference
      # to 'another_file' object
      self.logged = []
      # check its class has not yet been overriden
      self.assertFalse(getattr(portal.another_file, 'isClassOverriden', False))
      for i in (0, 1):
        marker_list += [i] * len(object_id_list)
        gc.disable()
        bt = template_tool.download(bt_path)
        assert marker_list
        if i:
          self.tic()
        bt.install(force=1)
        assert not marker_list
        gc.enable()
        for id in object_id_list:
          self.assertEqual(getattr(portal, id).int_index, i)
        self.tic()
    finally:
      BaseTemplateItem.removeProperties = BaseTemplateItem_removeProperties
      SimpleItem._getCopy = SimpleItem_getCopy
      gc.enable()
    # check the previously existing instance now behaves as the overriden class
    self.assertTrue(getattr(portal.another_file, 'isClassOverriden', False))
    # test uninstall is effective
    self.uninstallBusinessTemplate('test_167_InstanceAndRelatedClassDefinedInSameBT')
    # check both File instances no longer behave like being overriden
    self.assertFalse(getattr(portal.another_file, 'isClassOverriden', False))

  def test_168_CheckPortalTypeAndPathInSameBusinessTemplate(self, change_broken_object=False):
    """
    Make sure we can define a portal type and instance of that portal type
    in same bt. It already happened that this failed with error :
    BrokenModified: Can't change broken objects

    It might sound similar to test_167, but we had cases not working even
    though test_167 was running fine (due to additional steps that were
    doing more reset of components)
    """
    # Make sure we have no portal type Foo generated from a previous test
    try:
      import erp5
      del erp5.portal_type.Foo
    except AttributeError:
      pass
    template_tool = self.portal.portal_templates
    bt_path = os.path.join(os.path.dirname(__file__), 'test_data',
                     'BusinessTemplate_test_168_CheckPortalTypeAndPathInSameBusinessTemplate')
    bt = template_tool.download(bt_path)
    foo_in_bt = bt._path_item._objects["foo"]
    if change_broken_object:
      foo_in_bt.__Broken_state__["title"] = "FooBar"
      foo_in_bt._p_changed = 1
    # Force evaluation of a method to force unghosting of the class
    getattr(foo_in_bt, "getTitle", None)
    self.assertTrue(isinstance(foo_in_bt, ERP5BaseBroken))
    self.commit()
    bt.install(force=1)
    self.commit()
    foo_in_portal = self.portal.foo
    self.assertFalse(isinstance(foo_in_portal, ERP5BaseBroken))
    self.assertEqual("Foo", foo_in_portal.getPortalType())
    if change_broken_object:
      self.assertEqual("FooBar", getattr(foo_in_portal, "title"))
    self.uninstallBusinessTemplate('test_168_CheckPortalTypeAndPathInSameBusinessTemplate')

  def test_169_CheckPortalTypeAndPathInSameBusinessTemplateAndBrokenObjectModification(self):
    """
    Make sure we have possibility to change broken
    objects, such possibility is needed when document are exported
    as separated file (one for metadata, one for the content, often
    use for anything containing text or code)
    """
    self.test_168_CheckPortalTypeAndPathInSameBusinessTemplate(change_broken_object=True)

  def test_type_provider(self):
    self.portal.newContent(id='dummy_type_provider', portal_type="Types Tool")
    type_provider = self.portal.dummy_type_provider
    types_tool = self.portal.portal_types

    registered_type_provider_list = types_tool.type_provider_list
    # register this type provider
    types_tool.type_provider_list = (
        'dummy_type_provider',) + registered_type_provider_list

    dummy_type = type_provider.newContent(
                             portal_type='Base Type',
                             id='Dummy Type',
                             type_class='Folder',
                             type_property_sheet_list=('Reference',),
                             type_base_category_list=('source',),
                             type_allowed_content_type_list=('Dummy Type',),
                             type_hidden_content_type_list=('Dummy Type',) )

    dummy_type.newContent(portal_type='Action Information',
                          reference='view',
                          title='View', )

    dummy_type.newContent(portal_type='Role Information',
                          title='Dummy Role Definition',
                          role_name_list=('Assignee', ))

    pw = self.getWorkflowTool()
    cbt = pw._chains_by_type.copy()
    props = {}
    for id, wf_ids in cbt.items():
      props['chain_%s' % id] = ','.join(wf_ids)
    props['chain_Dummy Type'] = 'edit_workflow'
    pw.manage_changeWorkflows('', props=props)
    self.assertEqual(('edit_workflow', ), pw.getChainFor('Dummy Type'))

    bt = self.portal.portal_templates.newContent(
                          portal_type='Business Template',
                          title='test_bt_%s' % self.id(),
                          template_tool_id_list=('dummy_type_provider', ),
                          template_portal_type_id_list=('Dummy Type',),
                          template_portal_type_role_list=('Dummy Type', ),
                          template_portal_type_workflow_chain_list=(
                             'Dummy Type | edit_workflow',),
                          template_portal_type_allowed_content_type_list=(
                             'Dummy Type | Dummy Type',),
                          template_portal_type_hidden_content_type_list=(
                             'Dummy Type | Dummy Type',),
                          template_portal_type_property_sheet_list=(
                             'Dummy Type | Reference',),
                          template_portal_type_base_category_list=(
                             'Dummy Type | source',),
                          template_action_path_list=(
                             'Dummy Type | view',),)
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      # portal type template item are exported in their physical location
      for template_item in ('PortalTypeTemplateItem',
                            'ActionTemplateItem',):
        self.assertEqual(['dummy_type_provider'],
            [os.path.basename(f) for f in
              glob.glob('%s/%s/*' % (export_dir, template_item))])
      new_bt = self.portal.portal_templates.download(
                        url='file:/%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)

    # uninstall the workflow chain
    pw._chains_by_type = cbt
    # unregister type provider
    types_tool.type_provider_list = registered_type_provider_list
    # uninstall the type provider (this will also uninstall the contained types)
    self.portal.manage_delObjects(['dummy_type_provider'])
    self.tic()

    new_bt.install()
    try:
      type_provider = self.portal._getOb('dummy_type_provider', None)
      self.assertNotEqual(None, type_provider)

      # This type provider, will be automatically registered on types tool during
      # business template installation, because it contains type information
      self.assertIn('dummy_type_provider', types_tool.type_provider_list)
      # The type is reinstalled
      self.assertIn('Dummy Type', type_provider.objectIds())
      # is available from types tool
      self.assertIn('Dummy Type', [ti.getId() for
                      ti in types_tool.listTypeInfo()])

      dummy_type = types_tool.getTypeInfo('Dummy Type')
      self.assertNotEquals(None, dummy_type)
      # all the configuration from the type is still here
      self.assertEqual(['Reference'], dummy_type.getTypePropertySheetList())
      self.assertEqual(['source'], dummy_type.getTypeBaseCategoryList())
      self.assertEqual(['Dummy Type'], dummy_type.getTypeAllowedContentTypeList())
      self.assertEqual(['Dummy Type'], dummy_type.getTypeHiddenContentTypeList())

      action_list = dummy_type.contentValues(portal_type='Action Information')
      self.assertEqual(['View'], [action.getTitle() for action in action_list])
      self.assertEqual(['view'], [action.getReference() for action in action_list])

      role_list = dummy_type.contentValues(portal_type='Role Information')
      self.assertEqual(['Dummy Role Definition'],
                        [role.getTitle() for role in role_list])

      self.assertEqual(('edit_workflow',), pw.getChainFor('Dummy Type'))

      # and our type can be used
      instance = self.portal.newContent(portal_type='Dummy Type',
                                        id='test_document')
      instance.setSourceReference('OK')
      self.assertEqual('OK', instance.getSourceReference())

    finally:
      new_bt.uninstall()
      self.assertNotEquals(None, types_tool.getTypeInfo('Base Category'))
      self.assertEqual(None, types_tool.getTypeInfo('Dummy Type'))
      self.assertNotIn('dummy_type_provider', types_tool.type_provider_list)

  def test_type_provider_2(self):
    self.portal.newContent(id='dummy_type_provider', portal_type="Types Tool")
    type_provider = self.portal.dummy_type_provider
    types_tool = self.portal.portal_types

    registered_type_provider_list = types_tool.type_provider_list
    # register this type provider
    types_tool.type_provider_list = (
        'dummy_type_provider',) + registered_type_provider_list

    bt = self.portal.portal_templates.newContent(
                          portal_type='Business Template',
                          title='test_bt_%s' % self.id(),
                          template_tool_id_list=('dummy_type_provider', ),)
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      new_bt = self.portal.portal_templates.download(
                        url='file:/%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)

    # unregister type provider
    types_tool.type_provider_list = registered_type_provider_list
    # uninstall the type provider (this will also uninstall the contained types)
    self.portal.manage_delObjects(['dummy_type_provider'])
    self.tic()

    new_bt.install()

    type_provider = self.portal._getOb('dummy_type_provider', None)
    self.assertNotEqual(None, type_provider)

    # This type provider, will be automatically registered on types tool during
    # business template installation, because it contains type information
    self.assertIn('dummy_type_provider', types_tool.type_provider_list)

    # Create a business template that has the same title but does not
    # contain type_provider.
    bt = self.portal.portal_templates.newContent(
                          portal_type='Business Template',
                          title='test_bt_%s' % self.id(),)
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      new_bt = self.portal.portal_templates.download(
                        url='file:/%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)

    new_bt.install(force=0, object_to_update={'dummy_type_provider':'remove'})
    self.assertNotEquals(None, types_tool.getTypeInfo('Base Category'))
    self.assertNotIn('dummy_type_provider', types_tool.type_provider_list)

  def test_global_action(self):
    # Tests that global actions are properly exported and reimported
    self.portal.portal_actions.addAction(
          id='test_global_action',
          name='Test Global Action',
          action='',
          condition='',
          permission='',
          category='object_view')
    action_idx = len(self.portal.portal_actions._actions)

    bt = self.portal.portal_templates.newContent(
                          portal_type='Business Template',
                          title='test_bt_%s' % self.id(),
                          template_action_path_list=(
                             'portal_actions | test_global_action',),)
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      # actions are exported in portal_types/ and then the id of the container
      # tool
      self.assertEqual(['portal_actions'],
            [os.path.basename(f) for f in
              glob.glob('%s/ActionTemplateItem/portal_types/*' % (export_dir, ))])
      new_bt = self.portal.portal_templates.download(
                        url='file:/%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)

    # manually uninstall the action
    self.portal.portal_actions.deleteActions(selections=[action_idx])
    self.tic()

    # install the business template and make sure the action is properly
    # installed
    new_bt.install()
    self.tic()
    self.assertNotEquals(None,
        self.portal.portal_actions.getActionInfo('object_view/test_global_action'))

  def test_indexation_of_updated_path_item(self):
    """Tests indexation on updated paths item.
    They should keep their uid and still be available to catalog
    This test is similar to test_40_BusinessTemplateUidOfCategoriesUnchanged,
    but it also checks the object is available to catalog.
    """
    self.portal.newContent(
            id='exported_path',
            title='Exported',
            portal_type='Folder')
    self.tic()

    uid = self.portal.exported_path.getUid()

    bt = self.portal.portal_templates.newContent(
                          portal_type='Business Template',
                          title='test_bt_%s' % self.id(),
                          template_path_list=(
                            'exported_path',))
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      new_bt = self.portal.portal_templates.download(
                        url='file:/%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)

    # modify the document
    self.portal.exported_path.setTitle('Modified')
    self.tic()

    # install the business template
    new_bt.install()

    # after installation, the exported document is replaced with the one from
    # the business template
    self.assertEqual('Exported', self.portal.exported_path.getTitle())
    # but its uid did not change
    self.assertEqual(uid, self.portal.exported_path.getUid())
    # and it is still in the catalog
    self.tic()
    self.assertEqual(self.portal.exported_path,
        self.portal.portal_catalog.getResultValue(uid=uid))

  @expectedFailure
  def test_build_and_export_bt5_into_same_transaction(self):
    """
      Copy, build and export a business template into the same transaction.

      Make sure all objects can be exported, when build() and export() are
      into the same transaction.

      NOTES:
       - it works for some business templates. (e.g. erp5_base)
       - the object which does not have ._p_jar property is always an
         ActionTemplateItem.
    """
    portal = self.getPortalObject()
    template_tool = portal.portal_templates
    # Try with erp5_base, which contais ActionTemplateItem and works.
    bt5obj = template_tool.getInstalledBusinessTemplate('erp5_base')
    template_copy = template_tool.manage_copyObjects(ids=(bt5obj.getId(),))
    new_id_list = template_tool.manage_pasteObjects(template_copy)

    new_bt5_id = new_id_list[0]['new_id']
    new_bt5_obj = getattr(template_tool, new_bt5_id, None)
    new_bt5_obj.edit()
    new_bt5_obj.build()
    template_tool.export(new_bt5_obj)

    # Use erp5_barcode because it contains ActionTemplateItem, which seems to
    # cause problems to be export. Maybe create a test bt5 with all items could
    # be more appropriated.
    bt5obj = template_tool.getInstalledBusinessTemplate('erp5_core')
    # it is required to copy and paste to be able to export it
    template_copy = template_tool.manage_copyObjects(ids=(bt5obj.getId(),))
    new_id_list = template_tool.manage_pasteObjects(template_copy)

    new_bt5_id = new_id_list[0]['new_id']
    new_bt5_obj = getattr(template_tool, new_bt5_id, None)
    new_bt5_obj.edit()
    new_bt5_obj.build()
    template_tool.export(new_bt5_obj)

  def test_local_roles_group_id(self):
    """Tests that roles definition defining local roles group ids are properly
    exported and installed.
    """
    # change security uid columns
    sql_catalog = self.portal.portal_catalog.getSQLCatalog()
    saved_sql_catalog_security_uid_columns = \
      sql_catalog.sql_catalog_security_uid_columns

    sql_catalog.sql_catalog_security_uid_columns = (
      ' | security_uid',
      'Alternate | alternate_security_uid',
      'Another | another_security_uid',
    )
    # add categories
    self.portal.portal_categories.local_role_group.newContent(
      portal_type='Category',
      reference='Alternate',
      id='Alternate')
    self.portal.portal_categories.local_role_group.newContent(
      portal_type='Category',
      reference='Another',
      id='Another')

    types_tool = self.portal.portal_types
    object_type = types_tool.newContent('Geek Object', 'Base Type',
                                type_class='Person')

    types_tool.newContent('Geek Module', 'Base Type',
      type_class='Folder',
      type_filter_content_type=1,
      type_allowed_content_type_list=('Geek Object',), )

    self.portal.newContent(portal_type='Geek Module', id='geek_module')
    new_object = self.portal.geek_module.newContent(
      portal_type='Geek Object', id='1')

    # simulate role assignment
    new_object.__ac_local_roles__ = dict(group=['Assignee', 'Assignor'],
                                         another_group=['Assignee'])
    initial___ac_local_roles_group_id_dict__ = dict(
      Alternate={('group', 'Assignee')},
      Another={('group', 'Assignor'),
               ('another_group', 'Assignee')})
    new_object.__ac_local_roles_group_id_dict__ = initial___ac_local_roles_group_id_dict__
    self.tic()

    # the role information defined here does not match the assigned roles that
    # we simulated above, but we just want to test that an exported role
    # information can be imported back
    object_type.newContent(portal_type='Role Information',
                           local_role_group_value=self.portal.portal_categories.local_role_group.Alternate,
                           role_name_list=('Assignee', ))

    bt = self.portal.portal_templates.newContent(
                          portal_type='Business Template',
                          title=self.id(),
                          template_local_role_list=('geek_module/1',),
                          template_path_list=('geek_module/1',),
                          template_portal_type_role_list=('Geek Object',),)

    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      new_bt = self.portal.portal_templates.download(
                        url='file://%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)

    # uninstall role information and paths
    object_type.manage_delObjects([x.id for x in object_type.getRoleInformationList()])
    self.portal.geek_module.manage_delObjects(['1'])
    self.tic()

    new_bt.install()
    try:
      role, = object_type.getRoleInformationList()
      self.assertEqual(self.portal.portal_categories.local_role_group.Alternate,
                        role.getLocalRoleGroupValue())
      path = self.portal.geek_module['1']
      self.assertEqual(sorted([
        ('another_group', ['Assignee']),
        ('group', ['Assignee', 'Assignor']),
        ]), sorted([item for item in
            path.__ac_local_roles__.items() if item[1] != ['Owner']]))
      self.assertEqual(initial___ac_local_roles_group_id_dict__,
        path.__ac_local_roles_group_id_dict__)
      # make sure we can reindexing the object works
      path.recursiveReindexObject()
      self.tic()
    finally:
      # restore state
      sql_catalog.sql_catalog_security_uid_columns = \
        saved_sql_catalog_security_uid_columns
      types_tool.manage_delObjects(['Geek Object', 'Geek Module'])
      self.portal.manage_delObjects(['geek_module'])
      self.tic()

  def test_update_business_template_with_template_keep_path_list(self):
    """Tests for `template_keep_path_list` feature
    """
    # Simulate the case where we have an installed business template providing
    # the path test_document
    new_object = self.portal.newContent(portal_type='File', id='test_document')

    bt = self.portal.portal_templates.newContent(
        portal_type='Business Template',
        title=self.id(),
        template_path_list=('test_document',),)
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      new_bt = self.portal.portal_templates.download(
         url='file://%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)
    new_bt.install()

    # In a new version of the business template, this path is no longer included
    # but we have configured this path as *keep_path_list*
    # build and reimport this business template
    bt = self.portal.portal_templates.newContent(
        portal_type='Business Template',
        title=self.id(),
        template_keep_path_list=('test_document',),)
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      new_bt = self.portal.portal_templates.download(
         url='file://%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)
    self.assertEqual(
       {'test_document': ('Removed but should be kept', 'Path')},
       new_bt.preinstall())

  def test_update_business_template_with_template_keep_path_list_catalog_method(self):
    """Tests for `template_keep_path_list` feature for the special case of catalog methods
    """
    # Simulate the case where we have an installed business template providing
    # the catalog method z_fake_method
    catalog = self.getCatalogTool().getSQLCatalog()
    catalog.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod(
        id='z_fake_method',
        title='',
        connection_id='erp5_sql_connection',
        arguments='',
        template='')

    bt = self.portal.portal_templates.newContent(
        portal_type='Business Template',
        title=self.id(),
        template_catalog_method_id_list=['erp5_mysql_innodb/z_fake_method'])
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      new_bt = self.portal.portal_templates.download(
         url='file://%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)
    new_bt.install()

    # In a new version of the business template, this catalog method is no
    # longer included, but we have configured this path as *keep_path_list*
    #  (note that the syntax is the actual path of the object, so it includes portal_catalog)

    # build and reimport this business template
    bt = self.portal.portal_templates.newContent(
        portal_type='Business Template',
        title=self.id(),
        template_keep_path_list=('portal_catalog/erp5_mysql_innodb/z_fake_method',),)
    self.tic()
    bt.build()
    self.tic()
    export_dir = tempfile.mkdtemp()
    try:
      bt.export(path=export_dir, local=True)
      self.tic()
      new_bt = self.portal.portal_templates.download(
         url='file://%s' % export_dir)
    finally:
      shutil.rmtree(export_dir)
    self.assertEqual(
       {'portal_catalog/erp5_mysql_innodb/z_fake_method':
         ('Removed but should be kept', 'CatalogMethod')},
       new_bt.preinstall())

  def test_BusinessTemplateWithTest(self):
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateTest \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddTestToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveTest \
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
                       CheckTestExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckTestRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepSetVersionPriorityRegisteredSelection(self, sequence=None, **kw):
    bt = sequence.get('current_bt')
    self.assertFalse(bt is None)

    version_priority_list = ('abc| 1.0',
                             'def |99.0',
                             'erp4')

    bt.edit(template_registered_version_priority_selection_list=version_priority_list)

    sequence.edit(expected_version_priority_list=('def | 99.0',
                                                  'abc | 1.0',
                                                  'erp5 | 0.0',
                                                  'erp4 | 0.0'),
                  current_bt_version_priority_list=tuple(sorted(version_priority_list)))

  def stepUpdateVersionPriorityRegisteredSelection(self, sequence=None, **kw):
    bt = sequence.get('current_bt')
    self.assertFalse(bt is None)

    version_priority_list = ('erp4',
                             'abc | 1.0',
                             'foo | 2.0',
                             'bar | 100.0')

    bt.edit(template_registered_version_priority_selection_list=version_priority_list)

    sequence.edit(expected_version_priority_list=('bar | 100.0',
                                                  'foo | 2.0',
                                                  'abc | 1.0',
                                                  'erp5 | 0.0',
                                                  'erp4 | 0.0'),
                  current_bt_version_priority_list=tuple(sorted(version_priority_list)))

  def stepCheckVersionPriorityRegisteredSelection(self, sequence=None, **kw):
    bt = sequence.get('current_bt')
    self.assertEqual(tuple(bt.getTemplateRegisteredVersionPrioritySelectionList()),
                     sequence['current_bt_version_priority_list'])

  def stepRemoveVersionPriorityRegisteredSelectionBeforeImport(self,
                                                               sequence=None,
                                                               **kw):
    bt = sequence.get('current_bt')
    bt.edit(template_registered_version_priority_selection_list=())

  def stepCheckVersionPrioritySetOnSite(self, sequence=None, **kw):
    bt = sequence.get('current_bt')
    self.assertEqual(self.getPortalObject().getVersionPriorityList(),
                     sequence['expected_version_priority_list'])

  def stepCheckVersionPriorityRemovedFromSite(self, sequence=None, **kw):
    bt = sequence.get('current_bt')
    self.assertEqual(self.getPortalObject().getVersionPriorityList(),
                     ('erp5 | 0.0',))

  def stepRemoveVersionPriorityRegisteredSelection(self, sequence=None, **kw):
    bt = sequence.get('current_bt')
    bt.edit(template_registered_version_priority_selection=())
    sequence.edit(expected_version_priority_list=('erp5 | 0.0'),
                  current_bt_version_priority_list=())

  def test_BusinessTemplateWithVersionPrioritySelection(self):
    sequence_list = SequenceList()
    sequence_string = 'CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       SetVersionPriorityRegisteredSelection \
                       BuildBusinessTemplate \
                       SaveBusinessTemplate \
                       RemoveVersionPriorityRegisteredSelectionBeforeImport \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckVersionPriorityRegisteredSelection \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       CheckVersionPrioritySetOnSite \
                       UninstallBusinessTemplate \
                       Tic \
                       CheckVersionPriorityRemovedFromSite \
                       \
                       UpdateVersionPriorityRegisteredSelection \
                       BuildBusinessTemplate \
                       CheckVersionPriorityRegisteredSelection \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       CheckVersionPrioritySetOnSite \
                       UninstallBusinessTemplate \
                       Tic \
                       CheckVersionPriorityRemovedFromSite \
                       '

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateTextFile(self, sequence=None, **kw):
    skin_tool = self.getSkinsTool()
    skin_folder = skin_tool._getOb(sequence.get('skin_folder_id'))

    file_id = 'fake_js_file'
    file_content = """
   var

        debug =  [42
 ];

    """

    from Products.ERP5Type.tests.utils import createZODBFile
    createZODBFile(skin_folder, file_id, 'text/javascript', file_content)

    sequence.edit(fake_file_id=file_id,
                  fake_file_content=file_content)

  def stepCheckTextFileContent(self, sequence=None, **kw):
    skin_folder = self.getSkinsTool()._getOb(sequence.get('skin_folder_id'))
    file_content = getattr(skin_folder, sequence.get('fake_file_id')).data
    expected_file_content = sequence.get('fake_file_content')

    self.assertEqual(file_content, expected_file_content)
    self.assertEqual(len(file_content), len(expected_file_content))

  def test_text_file_import_export(self):
    """
    When importing back ace.js containing a last line with whitespaces only,
    the last line was not imported, and thus the file could never been
    downloaded completely as its really size was less than the one on the File
    ZODB object
    """
    sequence_list = SequenceList()
    sequence_string = """
       CreateSkinFolder
       CreateTextFile
       CheckTextFileContent

       CreateNewBusinessTemplate
       UseExportBusinessTemplate
       AddSkinFolderToBusinessTemplate
       CheckModifiedBuildingState
       CheckNotInstalledInstallationState
       BuildBusinessTemplate
       CheckBuiltBuildingState
       CheckNotInstalledInstallationState
       CheckObjectPropertiesInBusinessTemplate
       SaveBusinessTemplate
       CheckBuiltBuildingState
       CheckNotInstalledInstallationState
       RemoveSkinFolder
       RemoveBusinessTemplate
       RemoveAllTrashBins

       ImportBusinessTemplate
       UseImportBusinessTemplate
       CheckBuiltBuildingState
       CheckNotInstalledInstallationState
       InstallWithoutForceBusinessTemplate
       Tic
       CheckInstalledInstallationState
       CheckBuiltBuildingState
       CheckNoTrashBin
       CheckSkinsLayers
       CheckSkinFolderExists
       CheckTextFileContent

       UninstallBusinessTemplate
       CheckBuiltBuildingState
       CheckNotInstalledInstallationState
       CheckSkinFolderRemoved
       """

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateOrganisation(self, sequence=None, **kw):
    """
    Organisation
    """
    organisation_module = self.portal.organisation_module
    id_list = []
    for i in range(self.organisation_amount):
      organisation = organisation_module.newContent(
                       portal_type = 'Organisation')
      self.assertTrue(organisation is not None)
      organisation.setTitle('organisation %d' % (i + 1))
      for j in range(self.email_amount):
        organisation.newContent(id='email%d' % (j+1),
                                title='my email%d' % (j+1),
                                portal_type='Email')
      id_list.append(organisation.getId())
    self.assertNotEquals(id_list, [])
    sequence.edit(organisation_id_list=id_list)

  def stepModifyOrganisation(self, sequence=None, **kw):
    """ Modify Organisation """
    organisation_id_list = sequence.get('organisation_id_list', [])
    self.assertNotEquals(organisation_id_list, [])
    for organisation_id in organisation_id_list:
      organisation_module = self.portal.organisation_module
      organisation = organisation_module[organisation_id]
      organisation.setTitle('[modified] ' + organisation.getTitle())
      for j in range(self.email_amount):
        email = organisation['email%d' % (j+1)]
        email.setTitle('[modified] ' + email.getTitle())

  def stepRewriteWithBrokenOrganisation(self, sequence=None, **kw):
    """
      Rewrite the organisation with a broken object.

      [Note]: In fact, it is a *mock* broken object. It behave like a broken
      object but it's not broken. To use *real* broken object is better.
      However it is rather difficult to create a real broken
      object in ZODB without restart Zope. Even if removing
      sys.modules['Products.ERP5.Document'].MockBrokenOrganisation, and
      retrieve it with a new connection, it does not become a broken object.
      Probablly there is remaing the object-cache somewhere in Zope.
    """
    setattr(sys.modules['Products.ERP5.Document'],
           'MockBrokenOrganisation', MockBrokenOrganisation)

    from Products.ERP5Type.Utils import registerDocumentClass
    registerDocumentClass('Products.ERP5.Document',
                          'MockBrokenOrganisation')
    self.commit()
    pt = self.getTypeTool()
    # create module object portal type
    pt.newContent('Mock Broken Organisation', 'Base Type',
                  type_class='MockBrokenOrganisation')
    pt['Organisation Module'].edit(
      type_allowed_content_type_list=('Organisation',
                                      'Mock Broken Organisation',))

    self.commit()
    self.portal.organisation_module.manage_delObjects(['1'])
    broken = self.portal.organisation_module.newContent(
                   portal_type='Mock Broken Organisation', id='1')
    self.commit()
    self.tic() # triger undex/index the document

    # set unindexable so that it will act as Broken object
    self.portal.organisation_module['1'].isIndexable = \
        ConstantGetter('isIndexable', value=False)
    self.commit()

    # to reproduce this problem we need to clear portal_caches
    self.portal.portal_caches.clearAllCache()

  def stepCheckOrganisationModified(self, sequence=None, **kw):
    organisation_id_list = sequence.get('organisation_id_list', [])
    self.assertNotEquals(organisation_id_list, [])
    for organisation_id in organisation_id_list:
      organisation_module = self.portal.organisation_module
      organisation = organisation_module[organisation_id]
      self.assertTrue(organisation.getTitle().startswith('[modified]'))
      for j in range(self.email_amount):
        email = organisation['email%d' % (j+1)]
        self.assertTrue(email.getTitle().startswith('[modified]'))

  def stepAddOrganisationToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    if bt.getTemplatePathList():
      path_list = bt.getTemplatePathList()[:]
      path_list = path_list + ('organisation_module/**',)
      bt.edit(template_path_list=path_list)
    else:
      bt.edit(template_path_list=['organisation_module/**'])

  def stepRevertOrganisation(self, sequence=None, **kw):
    organisation_id_list = sequence.get('organisation_id_list', [])
    self.assertNotEquals(organisation_id_list, [])
    for organisation_id in organisation_id_list:
      organisation_module = self.portal.organisation_module
      organisation = organisation_module[organisation_id]
      organisation.setTitle(organisation.getTitle().replace('[modified] ', ''))
      for j in range(self.email_amount):
        email = organisation['email%d' % (j+1)]
        email.setTitle(email.getTitle().replace('[modified] ', ''))

  def stepRemoveOrganisation(self, sequence=None, **kw):
    id_list = sequence.get('organisation_id_list', None)
    self.assertNotEquals(id_list, [])
    organisation_id_list = id_list[:]
    organisation_module = self.portal.organisation_module
    organisation_module.manage_delObjects(organisation_id_list)
    self.assertNotEquals(id_list, [])

  def stepCheckOrganisationRestored(self, sequence=None, **kw):
    organisation_id_list = sequence.get('organisation_id_list', [])
    self.assertNotEquals(organisation_id_list, [])
    for organisation_id in organisation_id_list:
      organisation_module = self.portal.organisation_module
      organisation = organisation_module[organisation_id]
      self.assertTrue(organisation.getTitle().startswith('organisation'))
      for j in range(self.email_amount):
        email = organisation['email%d' % (j+1)]
        self.assertTrue(email.getTitle().startswith('my email'))

  def test_UpgradeBrokenObject(self):
    """
      Test a case that there is an broken object and upgrade the path.

      [Test summary]
      1. create organisation_module/1
      2. set organisation_module/1 as a broken object (in fact it's a mock)
      3. upgrade organisation_module/1 by the PathTemplateItem
    """
    self.portal.portal_activities.manage_enableActivityTracking()
    self.organisation_amount = 2
    self.email_amount = 2
    sequence_list = SequenceList()
    sequence_string = """
                       CreateOrganisation
                       CreateNewBusinessTemplate
                       UseExportBusinessTemplate
                       AddOrganisationToBusinessTemplate
                       Tic
                       BuildBusinessTemplate
                       SaveBusinessTemplate
                       Tic
                       RemoveOrganisation
                       RemoveBusinessTemplate
                       RemoveAllTrashBins
                       Tic
                       ImportBusinessTemplate
                       UseImportBusinessTemplate
                       InstallBusinessTemplate
                       Tic
                       CheckOrganisationRestored
                       ModifyOrganisation
                       CreateNewBusinessTemplate
                       UseExportBusinessTemplate
                       AddOrganisationToBusinessTemplate
                       BuildBusinessTemplate
                       SaveBusinessTemplate
                       RevertOrganisation
                       Tic
                       CheckOrganisationRestored
                       RewriteWithBrokenOrganisation
                       Tic
                       ImportBusinessTemplate
                       UseImportBusinessTemplate
                       InstallBusinessTemplate
                       Tic
                       CheckOrganisationModified
                      """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def testKeepVariousObjectsAndProperties(self):
    sequence = Sequence()
    self.stepCreateNewBusinessTemplate(sequence=sequence)
    business_template = sequence.get("export_bt")
    for property_id, method_id in [('template_keep_path_list', 'isKeepObject'),
         ('template_keep_workflow_path_list', 'isKeepWorkflowObject'),
         ('template_keep_last_workflow_history_only_path_list', 'isKeepWorkflowObjectLastHistoryOnly')]:
      method = getattr(business_template, method_id)
      self.assertEqual(False, method("aa/bb"))
      business_template.setProperty(property_id, ["aa/bb"])
      self.assertEqual(True, method("aa/bb"))
      self.assertEqual(False, method("aa/bbcc"))
      business_template.setProperty(property_id, ["aa/*"])
      self.assertEqual(True, method("aa/bb"))
      self.assertEqual(False, method("aa/bb/cc"))
      business_template.setProperty(property_id, ["aa/b*"])
      self.assertEqual(True, method("aa/bb"))
      self.assertEqual(False, method("aa/bb/cc"))
      self.assertEqual(False, method("aa/ca"))
      business_template.setProperty(property_id, ["aa/**"])
      self.assertEqual(True, method("aa/bb"))
      self.assertEqual(True, method("aa/bb/cc"))

  def stepCreateDocumentComponentWhichTriggersAnOperationWhenSubDocumentIsAdded(
        self, sequence=None, **kw):
    from textwrap import dedent
    # The source code of the component
    document_data = dedent(
    """
    from Products.ERP5Type.Tool.BaseTool import BaseTool
    from Products.ERP5Type.Core.Folder import Folder

    class MyTool(BaseTool):
      ''' my tool '''
      id = 'portal_mytools'
      meta_type = 'ERP5 MyTool'
      portal_type = 'My Tool'

      def _setOb(self, id, object):
        '''
          override
        '''
        Folder._setOb(self, id, object)
    """)

    component_id_prefix = DocumentComponent.getIdPrefix()
    component_portal_type = DocumentComponent.portal_type
    tool_type = 'My Tool'
    tool_class = 'MyTool'
    document_id = component_id_prefix + '.erp5.' + tool_class
    component = self.portal.portal_components.newContent(
      id=document_id,
      version='erp5',
      reference=tool_class,
      text_content=document_data,
      portal_type=component_portal_type)
    component.validate()
    sequence.edit(document_title=tool_class,
                  document_id=document_id,
                  document_data=document_data,
                  tool_id='portal_mytools',
                  tool_type=tool_type,
                  tool_class=tool_class,
                  type_allowed_content_type_list =('Python Script', ),
                  template_property='template_document_id_list')
    self.portal.portal_components.reset(force=True)

  def stepCreateMyToolPortalType(self, sequence=None, **kw):
    pt = self.getTypeTool()
    kwdict = dict(type_class=sequence['tool_class'])
    allowed_type_list = sequence['type_allowed_content_type_list']
    if allowed_type_list:
      kwdict['type_allowed_content_type_list'] = allowed_type_list
    object_type = pt.newContent(sequence['tool_type'], 'Base Type', **kwdict)
    self.assertTrue(object_type is not None)
    sequence.edit(object_ptype_id=object_type.getId())

  def stepAddMyToolToERP5Site(self, sequence=None, **kw):
    from Products.ERP5 import ERP5Site
    tool_id = sequence['tool_id']
    ERP5Site.addERP5Tool(self.portal, tool_id, sequence['tool_type'])
    sequence.edit(parent_document=self.portal[tool_id])

  def stepSetSubdocumentAsMyScript(self, sequence=None, **kw):
    sequence.edit(subdocument_id='my_script',
                  subdocument_portal_type='Python Script')

  def stepCreateSubDocument(self, sequence=None, **kw):
    parent_document = sequence['parent_document']
    self.assertTrue(parent_document != None)
    subdocument_portal_type = sequence['subdocument_portal_type']
    sub_document = parent_document.newContent(sequence['subdocument_id'],
                                              portal_type=subdocument_portal_type,
                                              body='# zzz')
    sequence.edit(template_path_list=[sub_document.getRelativeUrl()])

  def stepRemoveDocumentComponent(self, sequence=None, **kw):
    document_id = sequence['document_id']
    self.portal.portal_components.manage_delObjects(document_id)
    self.assertEqual(getattr(self.portal.portal_components, document_id, None),
                     None)

  def stepRemoveSubDocument(self, sequence=None, **kw):
    subdocument_id = sequence['subdocument_id']
    parent_document = sequence['parent_document']
    parent_document.manage_delObjects([subdocument_id])
    self.assertEqual(getattr(parent_document, subdocument_id, None),
                     None)

  def stepAddDocumentComponentToBusinessTemplate(self, sequence=None, **kw):
    sequence['current_bt'].setProperty(sequence['template_property'],
                                       sequence['document_id'])

  def stepAddTestComponentToBusinessTemplate(self, sequence=None, **kw):
    sequence['current_bt'].setProperty('template_test_id_list',
                                      ['test.erp5.testActivityTool'])

  def stepAddMyToolPortalTypeToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    ptype_ids = []
    ptype_ids.append(sequence.get('object_ptype_id', ''))
    bt.edit(template_portal_type_id_list=ptype_ids)

  def stepAddSubDocumentPathToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence.get('current_bt', None)
    self.assertTrue(bt is not None)
    bt.edit(template_path_list=sequence['template_path_list'])

  def stepCheckDocumentComponentIsInstalled(self, sequence=None, **kw):
    my_tool = getattr(self.portal.portal_components, sequence['document_id'],
                      None)
    self.assertNotEqual(my_tool, None)
    self.assertEqual(my_tool.getPortalType(), 'Document Component')

  def stepCheckParentDocumentIsExist(self, sequence=None, **kw):
    parent_document = sequence['parent_document']
    self.assertNotEqual(parent_document, None)
    self.assertEqual(parent_document.getPortalType(), sequence['tool_type'])

  def stepCheckSubDocumentIsInstalled(self, sequence=None, **kw):
    parent_document = sequence['parent_document']
    subdocument_id = sequence['subdocument_id']
    subdocument = getattr(parent_document, subdocument_id, None)
    self.assertNotEqual(subdocument, None)

  def stepModifySubDocument(self, sequence=None, **kw):
    parent_document = sequence['parent_document']
    subdocument_id = sequence['subdocument_id']
    parent_document[subdocument_id].edit(body='# yyy')

  def stepRevertSubDocument(self, sequence=None, **kw):
    parent_document = sequence['parent_document']
    subdocument_id = sequence['subdocument_id']
    parent_document[subdocument_id].edit(body='# zzz')

  def stepCheckSubDocumentIsReverted(self, sequence=None, **kw):
    parent_document = sequence['parent_document']
    subdocument_id = sequence['subdocument_id']
    body = parent_document[subdocument_id].getBody().rstrip()
    self.assertEqual(body, '# zzz')

  def stepCheckSubDocumentIsModified(self, sequence=None, **kw):
    parent_document = sequence['parent_document']
    subdocument_id = sequence['subdocument_id']
    body = parent_document[subdocument_id].getBody().rstrip()
    self.assertEqual(body, '# yyy')

  def stepCreateDifferentBusinessTemplateForInstall(self, sequence=None, **kw):
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.assertTrue(template.getBuildingState() == 'draft')
    self.assertTrue(template.getInstallationState() == 'not_installed')
    template.edit(title='different template',
                  version='1.0',
                  description='bt for unit_test')
    # set current_bt and import_bt for install
    sequence.edit(current_bt=template)
    sequence.edit(import_bt=template)

  def stepSimulateToCreateNewRequest(self, sequence=None, **kw):
    """
     Clear the Request ZODB Component module caches to simulate a new REQUEST.

     Why we need this is because:
     - ZODB Components relies on this cache to prevend gc of the component,
     - Since Unit Test environment patches get_request() and publish(),
       and everything run in a single thread, the REQUEST is not recreated
       even if the request (transaction) is finished.
     This removal imitates the behavior in a real ZOPE environment
    """
    import erp5.component
    erp5.component.ref_manager.clear()

  def stepAddExtensionComponentToBusinessTemplate(self, sequence=None, **kw):
    sequence['current_bt'].setProperty('template_extension_id_list',
                                      ['extension.erp5.InventoryBrain'])


  def testUpdateDocumentWhichIsInsideZODBDocumentFolder(self):
    """
      Test a case when the subobject of a ZODBComponent is updated as a path,
      and at the same time, the component is triggered while the installation.
    """
    sequence_list = SequenceList()
    sequence_string = """
      CreateDocumentComponentWhichTriggersAnOperationWhenSubDocumentIsAdded
      CreateMyToolPortalType
      AddMyToolToERP5Site
      CreateNewBusinessTemplate
      UseExportBusinessTemplate
      AddDocumentComponentToBusinessTemplate
      AddMyToolPortalTypeToBusinessTemplate
      FillPortalTypesFields
      Tic
      BuildBusinessTemplate
      SaveBusinessTemplate
      Tic
      ImportBusinessTemplate
      UseImportBusinessTemplate
      InstallWithoutForceBusinessTemplate
      Tic
      SetSubdocumentAsMyScript
      CreateSubDocument
      Tic
      CreateDifferentBusinessTemplateForInstall
      AddSubDocumentPathToBusinessTemplate
      AddTestComponentToBusinessTemplate
      BuildBusinessTemplate
      SaveBusinessTemplate
      InstallWithoutForceBusinessTemplate
      Tic
      ModifySubDocument
      SimulateToCreateNewRequest
      Tic
      ImportBusinessTemplate
      UseImportBusinessTemplate
      BuildBusinessTemplate
      Tic
      InstallWithoutForceBusinessTemplate
      Tic
      RevertSubDocument
      SimulateToCreateNewRequest
      Tic
      ImportBusinessTemplate
      UseImportBusinessTemplate
      AddExtensionComponentToBusinessTemplate
      BuildBusinessTemplate
      InstallWithoutForceBusinessTemplate
      Tic
      """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

class _ZodbComponentTemplateItemMixin(BusinessTemplateMixin):
  """
  Test cases for all Test*TemplateItem test classes.
  """
  def stepCreateZodbDocument(self, sequence=None, **kw):
    document_id = self.component_id_prefix + '.erp5.' + self.document_title
    component = self.portal.portal_components.newContent(
      id=document_id,
      version='erp5',
      reference=self.document_title,
      text_content=self.document_data,
      portal_type=self.component_portal_type)

    component.validate()
    sequence.edit(document_title=self.document_title,
                  document_id=document_id,
                  document_data=self.document_data)

  def stepAddZodbDocumentToBusinessTemplate(self, sequence=None, **kw):
    sequence['current_bt'].setProperty(self.template_property,
                                       sequence['document_id'])

  def stepCheckZodbDocumentWorkflowHistoryUnchanged(self, sequence=None, **kw):
    component = getattr(self.getPortalObject().portal_components,
                        sequence['document_id'], None)

    self.assertNotEqual(component, None)

    all_wf_history_dict = component.workflow_history
    self.assertEqual(sorted(list(all_wf_history_dict)),
                     ['component_validation_workflow', 'edit_workflow'])

    wf_history_dict_list = all_wf_history_dict['component_validation_workflow']
    self.assertFalse(len(wf_history_dict_list) <= 1)
    for wf_history_dict in wf_history_dict_list:
      self.assertNotEqual(wf_history_dict.get('time'), None)
      self.assertNotEqual(wf_history_dict.get('actor'), None)
      self.assertNotEqual(wf_history_dict.get('comment'), None)

  def stepCheckZodbDocumentExistsAndValidated(self, sequence=None, **kw):
    component = getattr(self.getPortalObject().portal_components,
                        sequence['document_id'], None)

    self.assertNotEqual(component, None)
    self.assertEqual(component.getValidationState(), 'validated')

    # Only the last Workflow History should have been exported and without
    # 'time' as it is not needed and create conflicts with VCSs
    self.assertEqual(list(component.workflow_history),
                      ['component_validation_workflow'])

    validation_state_only_list = []
    for validation_dict in component.workflow_history['component_validation_workflow']:
      validation_state_only_list.append(validation_dict.get('validation_state'))
      self.assertEqual(validation_dict.get('time'), None)
      self.assertEqual(validation_dict.get('actor'), None)
      self.assertEqual(validation_dict.get('comment'), None)

    self.assertEqual(validation_state_only_list, ['validated'])

  def stepCheckZodbDocumentRemoved(self, sequence=None, **kw):
    component_tool = self.getPortalObject().portal_components
    self.assertNotIn(sequence['document_id'], component_tool.objectIds())

  def stepRemoveZodbDocument(self, sequence=None, **kw):
    self.portal.portal_components.manage_delObjects([sequence['document_id']])

  def stepCheckForkedMigrationExport(self, sequence=None, **kw):
    """
    After saving a Business Template, two files should have been created for
    each Component, one is the Python source code (ending with '.py') and the
    other one is the metadata (ending with '.xml')
    """
    component_bt_tool_path = os.path.join(sequence['template_path'],
                                          self.__class__.__name__[len('Test'):],
                                          'portal_components')

    self.assertTrue(os.path.exists(component_bt_tool_path))

    component_id = self.component_id_prefix + '.erp5.' + sequence['document_title']
    base_path = os.path.join(component_bt_tool_path, component_id)

    python_source_code_path = base_path + '.py'
    self.assertTrue(os.path.exists(python_source_code_path))

    source_code = sequence['document_data']
    with open(python_source_code_path) as f:
      self.assertEqual(f.read(), source_code)

    xml_path = base_path + '.xml'
    self.assertTrue(os.path.exists(xml_path))

    first_line = source_code.split('\n', 1)[0]
    with open(xml_path) as f:
      for line in f:
        self.assertNotIn(first_line, line)

  def test_BusinessTemplateWithZodbDocument(self):
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateZodbDocument \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddZodbDocumentToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckForkedMigrationExport \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckZodbDocumentWorkflowHistoryUnchanged \
                       RemoveZodbDocument \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckZodbDocumentExistsAndValidated \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckZodbDocumentRemoved \
                       SaveBusinessTemplate \
                       CheckForkedMigrationExport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_BusinessTemplateWithZodbDocumentNonExistingBefore(self):
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       \
                       CreateZodbDocument \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddZodbDocumentToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckForkedMigrationExport \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckZodbDocumentWorkflowHistoryUnchanged \
                       RemoveZodbDocument \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckZodbDocumentExistsAndValidated \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckZodbDocumentRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

class _ProductMigrationTemplateItemMixin:
  """
  Test Cases specific to migration of Products from filesystem
  (Products.XXX.{Document,mixin,interfaces}.YYY) to ZODB Components
  (erp5.component.{document,mixin,interface}.YYY).
  """
  def stepCreateProductDocumentAndPortalType(self, sequence=None, **_):
    # Delete the bt5 Document created by previous tests (same name)
    file_path = os.path.join(self.document_base_path, self.document_title + '.py')
    if os.path.exists(file_path):
      os.remove(file_path)

    # getMigratableSourceCodeFromFilesystemList()
    document_source_reference = 'Products.ERP5.Document.%s' % self.document_title
    import Products.ERP5.Document
    file_path = os.path.join(Products.ERP5.Document.__path__[0],
                             self.document_title + '.py')
    with open(file_path, 'w') as f:
      f.write(self.document_data)
    self.assertTrue(os.path.exists(file_path))
    from Products.ERP5Type.Utils import importLocalDocument
    # This is normally called at Zope startup to register Products Documents
    # into document_class_registry then used in generatePortalTypeClass().
    #
    # Another reason to do that is because bt5 Document may already be there
    # from a previous tests execution and thus would be used instead of this
    # one...
    importLocalDocument(
      self.document_title,
      class_path="%s.%s" % (document_source_reference, self.document_title))
    sequence.edit(document_title=self.document_title,
                  document_path=file_path,
                  document_data=self.document_data,
                  document_source_reference=document_source_reference)

    object_type = self.getTypeTool().newContent(self.document_portal_type,
                                                'Base Type',
                                                type_class=self.document_title)
    self.assertTrue(object_type is not None)
    sequence.edit(object_ptype_id=self.document_portal_type)

    import erp5.portal_type
    portal_type_class = getattr(erp5.portal_type, sequence['object_ptype_id'])
    # Accessing __mro__ would not load the class...
    portal_type_class.loadClass()
    from importlib import import_module
    filesystem_module = import_module(document_source_reference)
    filesystem_class = getattr(filesystem_module, self.document_title)
    self.assertTrue(filesystem_class in portal_type_class.__mro__)

  def stepCheckProductDocumentMigration(self, sequence=None, **kw):
    self.stepCheckDocumentMigration(sequence, **kw)

    from importlib import import_module

    module_name = sequence['document_title']
    import erp5.portal_type
    portal_type_class = getattr(erp5.portal_type, sequence['object_ptype_id'])
    # Accessing __mro__ would not load the class...
    portal_type_class.loadClass()

    filesystem_module = import_module('Products.ERP5.Document.%s' % module_name)
    filesystem_class = getattr(filesystem_module, module_name)
    self.assertFalse(filesystem_class in portal_type_class.__mro__)

    component_module_name = 'erp5.component.document.' + module_name
    try:
      component_module = import_module(component_module_name)
    except ImportError:
      raise AssertionError("%s should be importable" % component_module_name)
    else:
      component_class = getattr(component_module, module_name)
      self.assertTrue(component_class in portal_type_class.__mro__)

  def test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb(self):
    """
    Same as test_BusinessTemplateUpgradeDocumentFromFilesystemToZodb above,
    but for Product Document rather than bt5 Document. Also, Products Document
    are not going to be removed automatically (safer).
    """
    sequence_list = SequenceList()
    sequence_string = """
      CreateProductDocumentAndPortalType
      CreateNewBusinessTemplate
      UseExportBusinessTemplate
      AddPortalTypeToBusinessTemplate
      UseExportBusinessTemplate
      CheckModifiedBuildingState
      CheckNotInstalledInstallationState
      BuildBusinessTemplate
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      CheckObjectPropertiesInBusinessTemplate
      UseCurrentBusinessTemplateForInstall
      InstallWithoutForceBusinessTemplate
      Tic
      CheckInstalledInstallationState
      CheckBuiltBuildingState
      CheckSkinsLayers
      CheckDocumentExists

      CopyAndMigrateDocumentBusinessTemplate
      CheckProductDocumentMigration
      BuildBusinessTemplate
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      SaveBusinessTemplate
      RemoveBusinessTemplate
      CheckZodbDocumentWorkflowHistoryUnchanged
      RemoveZodbDocument
      CheckDocumentExists
      CheckZodbDocumentRemoved

      ImportBusinessTemplate
      UseImportBusinessTemplate
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      InstallWithoutForceBusinessTemplate
      Tic
      CheckInstalledInstallationState
      CheckBuiltBuildingState
      CheckSkinsLayers
      CheckDocumentExists
      CheckZodbDocumentExistsAndValidated

      UseExportBusinessTemplate
      CheckReplacedInstallationState
      UseImportBusinessTemplate

      UninstallBusinessTemplate
      RemoveAllTrashBins
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      CheckZodbDocumentRemoved
      """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

# bt5 (instancehome and ZODB Component)
class _LocalTemplateItemMixin:
  """
  Test Cases for (legacy) local documents (eg instancehome/{Document,Test,
  Constraint,Extensions}) and their migration to ZODB Components.
  """
  def stepCreateDocument(self, sequence=None, **kw):
    file_path = os.path.join(self.document_base_path, self.document_title+'.py')
    if os.path.exists(file_path):
      os.remove(file_path)
    f = file(file_path, 'w')
    f.write(self.document_data)
    f.close()
    self.assertTrue(os.path.exists(file_path))
    sequence.edit(document_title=self.document_title,
                  document_path=file_path,
                  document_data=self.document_data)

  def stepCreateUpdatedDocument(self, sequence=None, **kw):
    file_path = os.path.join(self.document_base_path, self.document_title+'.py')
    if os.path.exists(file_path):
      os.remove(file_path)
    f = file(file_path, 'w')
    f.write(self.document_data_updated)
    f.close()
    self.assertTrue(os.path.exists(file_path))
    sequence.edit(document_title=self.document_title, document_path=file_path,
        document_data_updated=self.document_data_updated)

  def stepAddDocumentToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence['current_bt']
    document_title = sequence['document_title']
    bt.edit(**{self.template_property: [document_title]})
    # getMigratableSourceCodeFromFilesystemList()
    sequence.edit(document_source_reference='%s:%s' % (bt.getTitle(),
                                                       document_title))

  def stepRemoveDocument(self, sequence=None, **kw):
    document_path = sequence['document_path']
    os.remove(document_path)
    self.assertFalse(os.path.exists(document_path))

  def stepCheckDocumentExists(self, sequence=None, **kw):
    self.assertFalse(not os.path.exists(sequence['document_path']))
    self.assertEqual(file(sequence['document_path']).read(),
        sequence['document_data'])

  def stepCheckUpdatedDocumentExists(self, sequence=None, **kw):
    self.assertFalse(not os.path.exists(sequence['document_path']))
    self.assertEqual(file(sequence['document_path']).read(),
        sequence['document_data_updated'])

  def stepCheckDocumentRemoved(self, sequence=None, **kw):
    self.assertFalse(os.path.exists(sequence['document_path']))

  def test_BusinessTemplateWithDocument(self):
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateDocument \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddDocumentToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveDocument \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckDocumentExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckDocumentRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_BusinessTemplateUpdateWithDocument(self):
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateDocument \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddDocumentToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveDocument \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckDocumentExists \
                       RemoveDocument \
                       CreateUpdatedDocument \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddDocumentToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CreateDocument \
                       RemoveBusinessTemplate \
                       RemoveAllTrashBins \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       CheckUpdatedDocumentExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckDocumentRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_BusinessTemplateWithDocumentNonExistingBefore(self):
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       \
                       CreateDocument \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddDocumentToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveDocument \
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
                       CheckNoTrashBin \
                       CheckSkinsLayers \
                       CheckDocumentExists \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckDocumentRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_BusinessTemplateWithDocumentPropertySheetMigrated(self):
    """Checks that if Business Template defines Document and PropertySheet
    Document is not removed after Property Sheet was migrated and Business Template
    was updated"""
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateDocument \
                       CreatePropertySheet \
                       CheckDocumentPropertySheetSameName \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddDocumentToBusinessTemplate \
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
                       RemoveDocument \
                       RemovePropertySheet \
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
                       CheckNoTrashBin \
                       CheckDocumentExists \
                       CheckPropertySheetExists \
                       \
                       SimulateAndCopyPrePropertySheetMigrationBusinessTemplate \
                       Tic \
                       \
                       CreateAllPropertySheetsFromFilesystem \
                       Tic \
                       CheckPropertySheetRemoved \
                       CheckPropertySheetMigration \
                       \
                       CheckDraftBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveBusinessTemplate \
                       Tic \
                       CreatePropertySheet \
                       RemovePropertySheetZodbOnly \
                       Tic \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckPropertySheetMigration \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckDocumentExists \
                       CheckPropertySheetRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCopyAndMigrateDocumentBusinessTemplate(self, sequence=None, **kw):
    """
    Simulate migration from filesystem to ZODB

    XXX-arnau: implement importer at BusinessTemplate level
    """
    portal = self.getPortalObject()
    template_tool = portal.portal_templates
    current_bt = sequence['current_bt']
    cb_data = template_tool.manage_copyObjects([current_bt.getId()])
    copied, = template_tool.manage_pasteObjects(cb_data)
    copied_bt = template_tool._getOb(copied['new_id'])

    copied_bt.migrateSourceCodeFromFilesystem(version='erp5')

    sequence.edit(current_bt=copied_bt)

  def stepCheckDocumentMigration(self, sequence=None, **kw):
    """
    Check bt5 migration of Document from the Filesystem to ZODB
    """
    bt = sequence.get('current_bt')
    component_id = '%s.erp5.%s' % (self.component_id_prefix,
                                   sequence.get('document_title'))

    self.assertEqual(bt.getProperty(self.template_property),
                      [component_id])

    component_tool = self.getPortalObject().portal_components
    self.assertIn(component_id, component_tool.objectIds())

    component = getattr(component_tool, component_id)
    self.assertEqual(component.getReference(), sequence['document_title'])
    self.assertEqual(component.getTextContent(), sequence['document_data'])
    self.assertEqual(component.getPortalType(), self.component_portal_type)
    self.assertEqual(component.getSourceReference(), sequence['document_source_reference'])
    if self.component_portal_type in ('Extension Component', 'Test Component'):
      self.assertEqual(component.getValidationState(), 'validated')
    else:
      # Not validated automatically
      self.assertEqual(component.getValidationState(), 'draft')
      component.validate()
      self.tic()
      self.assertEqual(component.getValidationState(), 'validated')
    sequence.edit(document_id=component_id)

  def test_BusinessTemplateWithZodbDocumentMigrated(self):
    """
    Checks that if Business Template defines filesystem Document, they are
    properly migrated to ZODB, can be imported again and the ZODB Document is
    properly removed upon uninstall
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateDocument \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddDocumentToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveDocument \
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
                       CheckNoTrashBin \
                       CheckDocumentExists \
                       \
                       CopyAndMigrateDocumentBusinessTemplate \
                       CheckDocumentMigration \
                       Tic \
                       \
                       CheckDraftBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckForkedMigrationExport \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveBusinessTemplate \
                       CheckZodbDocumentWorkflowHistoryUnchanged \
                       RemoveZodbDocument \
                       Tic \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckZodbDocumentExistsAndValidated \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       \
                       UninstallBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckZodbDocumentRemoved \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepUseCurrentBusinessTemplateForInstall(self, sequence=None, **kw):
    sequence.edit(import_bt=sequence.get('current_bt'))

  def test_BusinessTemplateUpgradeDocumentFromFilesystemToZodb(self):
    sequence_list = SequenceList()
    sequence_string = """
      CreateDocument
      CreateNewBusinessTemplate
      UseExportBusinessTemplate
      AddDocumentToBusinessTemplate
      CheckModifiedBuildingState
      CheckNotInstalledInstallationState
      BuildBusinessTemplate
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      CheckObjectPropertiesInBusinessTemplate
      UseCurrentBusinessTemplateForInstall
      InstallWithoutForceBusinessTemplate
      Tic
      CheckInstalledInstallationState
      CheckBuiltBuildingState
      CheckSkinsLayers
      CheckDocumentExists

      CopyAndMigrateDocumentBusinessTemplate
      CheckDocumentMigration
      BuildBusinessTemplate
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      SaveBusinessTemplate
      RemoveBusinessTemplate
      CheckZodbDocumentWorkflowHistoryUnchanged
      RemoveZodbDocument
      CheckDocumentExists
      CheckZodbDocumentRemoved

      ImportBusinessTemplate
      UseImportBusinessTemplate
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      InstallWithoutForceBusinessTemplate
      Tic
      CheckInstalledInstallationState
      CheckBuiltBuildingState
      CheckSkinsLayers
      CheckDocumentRemoved
      CheckZodbDocumentExistsAndValidated

      UseExportBusinessTemplate
      CheckReplacedInstallationState
      UseImportBusinessTemplate

      UninstallBusinessTemplate
      RemoveAllTrashBins
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      CheckZodbDocumentRemoved
      """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckDocumentMigrationFailWithConsistencyError(self, sequence=None, **kw):
    current_bt = sequence['current_bt']
    self.assertRaises(RuntimeError,
                      current_bt.migrateSourceCodeFromFilesystem,
                      # version must not start with '_'
                      version='_invalid_version')

  def test_BusinessTemplateUpgradeDocumentFromFilesystemToZodbWithConsistencyError(self):
    """
    Check that component.checkConsistency() (called before "validating" a ZODB
    Component) is done when migrating Document from filesystem to ZODB
    """
    sequence_list = SequenceList()
    sequence_string = """
      CreateDocument
      CreateNewBusinessTemplate
      UseExportBusinessTemplate
      AddDocumentToBusinessTemplate
      CheckModifiedBuildingState
      CheckNotInstalledInstallationState
      BuildBusinessTemplate
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      CheckObjectPropertiesInBusinessTemplate
      UseCurrentBusinessTemplateForInstall
      InstallWithoutForceBusinessTemplate
      Tic
      CheckInstalledInstallationState
      CheckBuiltBuildingState
      CheckSkinsLayers
      CheckDocumentExists

      CopyBusinessTemplate
      CheckDocumentMigrationFailWithConsistencyError
      """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckDocumentMigrationFailWithSourceCodeError(self, sequence=None, **kw):
    current_bt = sequence['current_bt']

    from Products.ERP5Type.mixin.component import ComponentMixin
    orig_checkSourceCode = ComponentMixin.checkSourceCode
    try:
      ComponentMixin.checkSourceCode = lambda *args, **kwargs: [
        {'type': 'E', 'row': 1, 'column': 1,
         'text': 'Source Code Error for Unit Test'}]
      self.assertRaises(RuntimeError, current_bt.migrateSourceCodeFromFilesystem,
                        version='erp5')

      ComponentMixin.checkSourceCode = lambda *args, **kwargs: [
        {'type': 'F', 'row': 1, 'column': 1,
         'text': 'Source Code Error for Unit Test'}]
      self.assertRaises(RuntimeError, current_bt.migrateSourceCodeFromFilesystem,
                        version='erp5')
    finally:
      ComponentMixin.checkSourceCode = orig_checkSourceCode

  def test_BusinessTemplateUpgradeDocumentFromFilesystemToZodbWithSyntaxError(self):
    """
    Check that component.checkSourceCode() (called before "validating" a ZODB
    Component) is done when migrating Document from filesystem to ZODB
    """
    sequence_list = SequenceList()
    sequence_string = """
      CreateDocument
      CreateNewBusinessTemplate
      UseExportBusinessTemplate
      AddDocumentToBusinessTemplate
      CheckModifiedBuildingState
      CheckNotInstalledInstallationState
      BuildBusinessTemplate
      CheckBuiltBuildingState
      CheckNotInstalledInstallationState
      CheckObjectPropertiesInBusinessTemplate
      UseCurrentBusinessTemplateForInstall
      InstallWithoutForceBusinessTemplate
      Tic
      CheckInstalledInstallationState
      CheckBuiltBuildingState
      CheckSkinsLayers
      CheckDocumentExists

      CopyBusinessTemplate
      CheckDocumentMigrationFailWithSourceCodeError
      """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

from Products.ERP5Type.Core.DocumentComponent import DocumentComponent
# bt5 (instancehome and ZODB Component) and Products
class TestDocumentTemplateItem(_LocalTemplateItemMixin,
                               _ZodbComponentTemplateItemMixin,
                               _ProductMigrationTemplateItemMixin):
  document_title = 'UnitTest'
  document_portal_type = 'Unit Test'
  document_data = """from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class UnitTest(XMLObject):
  meta_type = 'ERP5 Unit Test'
  portal_type = 'Unit Test'
  security = ClassSecurityInfo()

InitializeClass(UnitTest)
"""
  document_data_updated = """from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class UnitTest(XMLObject):
  meta_type = 'ERP5 Unit Test'
  portal_type = 'Unit Test'
  security = ClassSecurityInfo()

  def updated(self):
    pass

InitializeClass(UnitTest)
"""
  document_base_path = os.path.join(getConfiguration().instancehome, 'Document')
  template_property = 'template_document_id_list'
  component_id_prefix = DocumentComponent.getIdPrefix()
  component_portal_type = DocumentComponent.portal_type

from Products.ERP5Type.Core.InterfaceComponent import InterfaceComponent
# bt5 (ZODB Component only) and Products
class TestInterfaceTemplateItem(_ZodbComponentTemplateItemMixin,
                                _ProductMigrationTemplateItemMixin):
  document_title = 'IUnitTest'
  document_data = '''from zope.interface import Interface

class IUnitTest(Interface):
  def foo():
    """
    Anything
    """
'''
  template_property = 'template_interface_id_list'
  component_id_prefix = InterfaceComponent.getIdPrefix()
  component_portal_type = InterfaceComponent.portal_type

from Products.ERP5Type.Core.MixinComponent import MixinComponent
# bt5 (ZODB Component only) and Products
class TestMixinTemplateItem(_ZodbComponentTemplateItemMixin,
                            _ProductMigrationTemplateItemMixin):
  document_title = 'UnitTestMixin'
  document_data = '''class UnitTestMixin:
  def foo(self):
    """
    Anything
    """
    return '42'
'''
  template_property = 'template_mixin_id_list'
  component_id_prefix = MixinComponent.getIdPrefix()
  component_portal_type = MixinComponent.portal_type

# bt5 (instancehome (legacy) and ZODB Component) and Products
class TestConstraintTemplateItem(_LocalTemplateItemMixin,
                                 _ZodbComponentTemplateItemMixin,
                                 _ProductMigrationTemplateItemMixin):
  document_title = 'UnitTest'
  document_data = ' \nclass UnitTest: \n  """ \n  Fake constraint for unit test \n \
    """ \n  _properties = ( \n  ) \n  _categories = ( \n  ) \n\n'
  document_data_updated = ' \nclass UnitTest2: \n  """ \n  Second Fake constraint for unit test \n \
    """ \n  _properties = ( \n  ) \n  _categories = ( \n  ) \n\n'
  document_base_path = os.path.join(getConfiguration().instancehome, 'Constraint')
  template_property = 'template_constraint_id_list'

from Products.ERP5Type.Core.ExtensionComponent import ExtensionComponent
# bt5 (instancehome (legacy) and ZODB Component)
class TestExtensionTemplateItem(_LocalTemplateItemMixin,
                                _ZodbComponentTemplateItemMixin):
  document_title = 'UnitTest'
  document_data = """class UnitTest:
  meta_type = 'ERP5 Unit Test'
  portal_type = 'Unit Test'"""
  document_data_updated = """class UnitTest:
  meta_type = 'ERP5 Unit Test'
  portal_type = 'Unit Test'
  def updated(self):
    pass"""
  document_base_path = os.path.join(getConfiguration().instancehome, 'Extensions')
  template_property = 'template_extension_id_list'

  # Specific to ZODB Extension Component
  component_id_prefix = ExtensionComponent.getIdPrefix()
  component_portal_type = ExtensionComponent.portal_type

from Products.ERP5Type.Core.TestComponent import TestComponent
# bt5 (instancehome (legacy) and ZODB Component) and Products
class TestTestTemplateItem(_LocalTemplateItemMixin,
                           _ZodbComponentTemplateItemMixin,
                           _ProductMigrationTemplateItemMixin):
  document_title = 'UnitTest'
  document_data = """class UnitTest:
  meta_type = 'ERP5 Unit Test'
  portal_type = 'Unit Test'"""
  document_data_updated = """class UnitTest:
  meta_type = 'ERP5 Unit Test'
  portal_type = 'Unit Test'
  def updated(self):
    pass"""
  document_base_path = os.path.join(getConfiguration().instancehome, 'tests')
  template_property = 'template_test_id_list'

  # Specific to ZODB Extension Component
  component_id_prefix = TestComponent.getIdPrefix()
  component_portal_type = TestComponent.portal_type

  def stepAddTestToBusinessTemplate(self, sequence=None, **kw):
    bt = sequence['current_bt']
    bt.edit(template_test_id_list=[sequence['test_title']])

  def stepCheckDocumentTestSameName(self, sequence=None, **kw):
    self.assertEqual(sequence['test_title'], sequence['document_title'])
    self.assertEqual(os.path.basename(sequence['document_path']),
        os.path.basename(sequence['test_path']))

  def stepRemoveTestFromBusinessTemplate(self, sequence=None, **kw):
    """
    Add Property Sheet to Business Template
    """
    sequence['current_bt'].edit(template_test_id_list=[])

  def test_BusinessTemplateWithDocumentTestRemoved(self):
    """Checks that if Business Template defines Document and Test
    Document is not removed"""
    self.document_base_path = os.path.join(getConfiguration().instancehome, 'Document')
    self.template_property = 'template_document_id_list'
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateDocument \
                       CreateTest \
                       CheckDocumentTestSameName \
                       CreateNewBusinessTemplate \
                       UseExportBusinessTemplate \
                       AddDocumentToBusinessTemplate \
                       AddTestToBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       RemoveDocument \
                       RemoveTest \
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
                       CheckNoTrashBin \
                       CheckDocumentExists \
                       CheckTestExists \
                       \
                       CopyBusinessTemplate \
                       Tic \
                       \
                       RemoveTestFromBusinessTemplate \
                       CheckModifiedBuildingState \
                       CheckNotInstalledInstallationState \
                       BuildBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       CheckObjectPropertiesInBusinessTemplate \
                       SaveBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       ImportBusinessTemplate \
                       UseImportBusinessTemplate \
                       CheckBuiltBuildingState \
                       CheckNotInstalledInstallationState \
                       InstallWithoutForceBusinessTemplate \
                       Tic \
                       \
                       CheckInstalledInstallationState \
                       CheckBuiltBuildingState \
                       CheckTestRemoved \
                       CheckDocumentExists \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

# XXX-arnau: Skip until ZODB Constraints have been implemented (not
# expectedFailure because following tests would fail after the ZODB Component
# has been created)
TestConstraintTemplateItem.test_BusinessTemplateWithZodbDocument = skip(
  'Not implemented yet')(TestConstraintTemplateItem.test_BusinessTemplateWithZodbDocument)

TestConstraintTemplateItem.test_BusinessTemplateWithZodbDocumentNonExistingBefore = \
    skip('Not implemented yet')(TestConstraintTemplateItem.test_BusinessTemplateWithZodbDocumentNonExistingBefore)

TestConstraintTemplateItem.test_BusinessTemplateWithZodbDocumentMigrated = \
    skip('Not implemented yet')(TestConstraintTemplateItem.test_BusinessTemplateWithZodbDocumentMigrated)

TestConstraintTemplateItem.test_BusinessTemplateUpgradeDocumentFromFilesystemToZodb = \
    skip('Not implemented yet')(TestConstraintTemplateItem.test_BusinessTemplateUpgradeDocumentFromFilesystemToZodb)

TestConstraintTemplateItem.test_BusinessTemplateUpgradeDocumentFromFilesystemToZodbWithConsistencyError = \
    skip('Not implemented yet')(TestConstraintTemplateItem.test_BusinessTemplateUpgradeDocumentFromFilesystemToZodbWithConsistencyError)

TestConstraintTemplateItem.test_BusinessTemplateUpgradeDocumentFromFilesystemToZodbWithSyntaxError = \
    skip('Not implemented yet')(TestConstraintTemplateItem.test_BusinessTemplateUpgradeDocumentFromFilesystemToZodbWithSyntaxError)

TestConstraintTemplateItem.test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb = \
    skip('Not implemented yet')(TestConstraintTemplateItem.test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb)

# TODO-arnau
TestInterfaceTemplateItem.test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb = \
    skip('Not implemented yet')(TestInterfaceTemplateItem.test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb)

TestTestTemplateItem.test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb = \
    skip('Not implemented yet')(TestTestTemplateItem.test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb)

TestMixinTemplateItem.test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb = \
    skip('Not implemented yet')(TestMixinTemplateItem.test_BusinessTemplateUpgradeProductDocumentFromFilesystemToZodb)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBusinessTemplate))
  suite.addTest(unittest.makeSuite(TestConstraintTemplateItem))
  suite.addTest(unittest.makeSuite(TestDocumentTemplateItem))
  suite.addTest(unittest.makeSuite(TestInterfaceTemplateItem))
  suite.addTest(unittest.makeSuite(TestMixinTemplateItem))
  suite.addTest(unittest.makeSuite(TestExtensionTemplateItem))
  suite.addTest(unittest.makeSuite(TestTestTemplateItem))
  return suite
