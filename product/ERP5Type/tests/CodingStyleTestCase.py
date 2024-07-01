# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Jean-Paul Smets <jp@nexedi.com>
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

import collections
import difflib
import filecmp
import fnmatch
import glob
import os
import shutil
import tempfile
import warnings

from Acquisition import aq_base
from Testing import ZopeTestCase

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import findContentChain
import six


class CodingStyleTestCase(ERP5TypeTestCase):
  """Test case to test coding style in business templates.

  Subclasses must override:
    * getBusinessTemplateList to list business template to install.
    * getTestedBusinessTemplateList to list business templates to test.
  """
  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    Override this method in implementation class.
    """
    raise NotImplementedError

  def getTestedBusinessTemplateList(self):
    """
    Return the list of business templates to be
    checked for consistency. By default, return
    the last business template of the
    list of installed business templates.
    """
    return self.getBusinessTemplateList()[-1:]

  def afterSetUp(self):
    self.login()

  def _getTestedBusinessTemplateValueList(self):
    for business_template in self.portal.portal_templates.contentValues():
      if business_template.getTitle() in self.getTestedBusinessTemplateList():
        yield business_template

  def test_SkinCodingStyle(self):
    """
    Find all skin items of business templates to be checked
    and gather all consistency messages.
    """
    # Find the list if skins to test - we only test the last business template
    skin_id_set = set()
    for business_template in self._getTestedBusinessTemplateValueList():
      skin_id_set.update(business_template.getTemplateSkinIdList())

    # Init message list
    message_list = []

    # Test skins
    portal_skins = self.portal.portal_skins
    for skin_id in skin_id_set:
      skin = portal_skins[skin_id]
      for _, document in skin.ZopeFind(
          skin,
          obj_metatypes=(),
          search_sub=True):
        if getattr(aq_base(document), 'checkConsistency', None) is not None:
          message_list.extend(document.checkConsistency())
    self.maxDiff = None
    self.assertEqual(message_list, [])

  def test_PythonSourceCode(self):
    """test python script from the tested business templates.

    reuses BusinessTemplate_getPythonSourceCodeMessageList
    """
    self.maxDiff = None
    for business_template in self._getTestedBusinessTemplateValueList():
      self.assertEqual(business_template.BusinessTemplate_getPythonSourceCodeMessageList(), [])


  # Paths for which we ignore differences when re-exporting business templates
  rebuild_business_template_ignored_path = """
  # portal_transforms seem to be always different
  erp5_core/ToolTemplateItem/portal_transforms.xml

  # Empty messages are exported in message catalog, so they can be different because of
  # empty messages. Reindexing during creation for example insert entries for all workflow
  # states, so this change often.
  */MessageTranslationTemplateItem/*/*/translation.po

  # This seem to be a copy of
  # bt5/erp5_configurator_standard/PathTemplateItem/business_configuration_module/default_standard_configuration.xml
  # that was modified. When re-exporting it is different, but since this is test data we ignore it for now.
  erp5_scalability_test/PathTemplateItem/business_configuration_module/default_standard_configuration.xml
  erp5_scalability_test/PathTemplateItem/business_configuration_module/default_standard_configuration/*

  # This is different for some unknown reason, because it's test data we ignore for now
  erp5_payroll_l10n_fr_test/PathTemplateItem/accounting_module/trainee_january.xml
  erp5_payroll_l10n_fr_test/PathTemplateItem/accounting_module/trainee_january/*
  """
  def test_rebuild_business_template(self):
    """Try to rebuild business template to catch packaging errors and make sur output is stable.
    """
    self.maxDiff = None
    template_tool = self.portal.portal_templates
    diff_line_list = []
    diff_files = []
    for bt_title in self.getTestedBusinessTemplateList():
      bt = template_tool.getInstalledBusinessTemplate(bt_title, strict=True)
      # run migrations on the business template, except for the BT used to
      # test workflow migration.
      if bt_title != 'erp5_workflow_test':
        bt.BusinessTemplate_convertAllDCWorkflowToERP5Workflow()
      # make sure we can rebuild
      bt.build()

      # Compute the differences between the reference business template
      # from the working copy and the newly exported business template.
      bt_base_path, bt_local_path = self.portal.portal_templates.getLastestBTOnRepos(bt_title)
      bt_dir = os.path.join(bt_base_path, bt_local_path)
      export_base_path = tempfile.mkdtemp()
      self.addCleanup(shutil.rmtree, export_base_path)
      export_dir = os.path.join(export_base_path, bt_local_path)
      bt.export(export_dir, local=True)

      ignored_paths = {
          p.strip() for p in self.rebuild_business_template_ignored_path.splitlines()
          if p and not p.strip().startswith("#")}

      def get_difference(path, has_old=True, has_new=True):
        old = (
          os.path.join(bt_base_path, path)
          if has_old else
          os.devnull
        )
        new = (
          os.path.join(export_base_path, path)
          if has_new else
          os.devnull
        )
        old_is_dir = os.path.isdir(old)
        new_is_dir = os.path.isdir(new)
        # Raise if we are going from a directory to a file or vice-versa.
        assert not has_old or not has_new or old_is_dir == new_is_dir, (path, old_is_dir, new_is_dir)
        if old_is_dir or new_is_dir:
          return
        with open(old) as ff, open(new) as tf:
          diff_line_list.extend(
            difflib.unified_diff(
              ff.readlines(),
              tf.readlines(),
              (
                os.path.join('git', path)
                if has_old else
                os.devnull
              ),
              (
                os.path.join('bt5', path)
                if has_new else
                os.devnull
              ),
            ),
          )

      def get_differences(dcmp, base):
        for name in dcmp.left_only:
          path = os.path.join(base, name)
          yield 'removed: ' + path
          get_difference(path, has_new=False)
        for name in dcmp.right_only:
          path = os.path.join(base, name)
          yield 'added: ' + path
          get_difference(path, has_old=False)
        for name in dcmp.funny_files:
          yield 'funny: ' + os.path.join(base, name)
        for name in dcmp.diff_files:
          path = os.path.join(base, name)
          get_difference(path)
          if not any(fnmatch.fnmatch(path, ignored_path) for ignored_path in ignored_paths):
            yield 'modified: ' + path
        for sub_path, sub_dcmp in six.iteritems(dcmp.subdirs):
          for diff in get_differences(sub_dcmp, os.path.join(base, sub_path)):
            yield diff

      diff_files.extend(list(get_differences(filecmp.dircmp(bt_dir, export_dir), bt_local_path)))

    # dump a diff in log directory, to help debugging
    from Products.ERP5Type.tests.runUnitTest import log_directory
    if log_directory and diff_line_list:
      with open(os.path.join(log_directory, '%s.diff' % self.id()), 'w') as f:
        f.writelines(diff_line_list)
    if diff_files and six.PY3:  # TODO zope4py3
      warnings.warn(
        "Ignoring test_rebuild_business_template until we re-export "
        "business templates with protocol 3.")
      return
    self.assertEqual(diff_files, [])


  def test_run_upgrader(self):
    # Check that pre and post upgrade do not raise problems.
    # We dont check upgrade step, because upgrader by default want to
    # uninstall business templates.
    self.portal.portal_alarms.upgrader_check_pre_upgrade.activeSense(fixit=True)
    self.tic()
    self.portal.portal_alarms.upgrader_check_pre_upgrade.activeSense()
    self.tic()
    self.assertFalse(
        self.portal.portal_alarms.upgrader_check_pre_upgrade.sense(),
        [
            '\n'.join(x.detail) for x in self.portal.portal_alarms
            .upgrader_check_post_upgrade.Alarm_getReportResultList()
        ],
    )

    self.portal.portal_alarms.upgrader_check_post_upgrade.activeSense(
        fixit=True)
    self.tic()
    self.portal.portal_alarms.upgrader_check_post_upgrade.activeSense()
    self.tic()
    self.assertFalse(
        self.portal.portal_alarms.upgrader_check_post_upgrade.sense(),
        [
            '\n'.join(x.detail) for x in self.portal.portal_alarms
            .upgrader_check_post_upgrade.Alarm_getReportResultList()
        ],
    )

  def test_DuplicateActions(self):
    """test actions from the tested business templates are not duplicated.
    """
    self.maxDiff = None
    duplicate_action_list = []
    for business_template in self._getTestedBusinessTemplateValueList():
      # consider all portal types for which this business template defines actions
      portal_type_list = set([
          action_definition.split(' | ')[0] for action_definition in
          business_template.getTemplateActionPathList()
      ])
      for portal_type in portal_type_list:
        # ignore other actions providers, such as the ones for global actions.
        if self.portal.portal_types.get(portal_type) is None:
          continue

        document, content_portal_type_list = findContentChain(
            self.portal, portal_type)
        for content_portal_type in content_portal_type_list:
          document = document.newContent(portal_type=content_portal_type)

        for action_category, action_list in six.iteritems(self.portal.portal_actions.listFilteredActionsFor(
            document)):
          # We ignore duplicate actions in action categories used by OfficeJS
          # because OfficeJS only display actions referenced in the router
          # gadget configuration.
          if action_category in ('object_jio_view', 'object_jio_js_script'):
            continue
          for action_name, action_count in six.iteritems(collections.Counter(
              [action['name'] for action in action_list])):
            if action_count > 1:
              duplicate_action_list.append({
                  'portal_type': portal_type,
                  'category': action_category,
                  'action_name': action_name,
              })
    self.assertEqual(duplicate_action_list, [])

  def test_workflow_consistency(self):
    self.maxDiff = None
    workflow_id_set = set()
    for business_template in self._getTestedBusinessTemplateValueList():
      workflow_id_set.update(business_template.getTemplateWorkflowIdList())

    message_list = []
    for workflow_id in workflow_id_set:
      message_list.extend(
          self.portal.portal_workflow[workflow_id].checkConsistency())

    self.assertEqual(message_list, [])
