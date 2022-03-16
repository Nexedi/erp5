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
import glob
import os
import tarfile

from Acquisition import aq_base
from Testing import ZopeTestCase

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import findContentChain


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

  def test_rebuild_business_template(self):
    """Try to rebuild business template to catch packaging errors.
    """
    template_tool = self.portal.portal_templates
    for bt_title in self.getTestedBusinessTemplateList():
      bt = template_tool.getInstalledBusinessTemplate(bt_title, strict=True)
      # make sure we can rebuild
      bt.build()

      # check we don't add or remove members.
      # first, build a set of files that were on the original business template repository
      base_path, local_path = self.portal.portal_templates.getLastestBTOnRepos(bt_title)
      existing_files = set([os.path.relpath(y, base_path)
        for x in os.walk(os.path.join(base_path, local_path))
            for y in glob.glob(os.path.join(x[0], '*')) if os.path.isfile(y)])

      # then compare this with the files in the newly exported business template.
      bt_file = bt.export()
      bt_file.seek(0) # XXX this StringIO was already read...
      new_files = set(tarfile.open(fileobj=bt_file, mode='r:gz').getnames())

      self.maxDiff = None
      self.assertEqual(existing_files, new_files)

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

        for action_category, action_list in self.portal.portal_actions.listFilteredActionsFor(
            document).iteritems():
          # We ignore duplicate actions in action categories used by OfficeJS
          # because OfficeJS only display actions referenced in the router
          # gadget configuration.
          if action_category in ('object_jio_view', 'object_jio_js_script'):
            continue
          for action_name, action_count in collections.Counter(
              [action['name'] for action in action_list]).iteritems():
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
