# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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

import os
import glob
import unittest

from Products.ERP5Type.tests.utils import addUserToDeveloperRole
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class ReExportBusinessTemplateTest(ERP5TypeTestCase):
  """Reuse test infrastructure to rebuild and export business template.

  The business template to export is defined by RE_EXPORT_BUSINESS_TEMPLATE
  ReExportERP5BusinessTemplateTestSuite in test/__init__.py can be used
  to rebuild all business templates.
  """
  def getBusinessTemplateList(self):
    # include erp5_forge for VCS integration
    return (
      'erp5_forge',
      self.re_export_business_template,
    )

  def _getBusinessTemplatePathList(self):
    from Products.ERP5.ERP5Site import getBootstrapDirectory
    bt5_path_list = [
      os.environ.get('erp5_tests_bootstrap_path') or getBootstrapDirectory()
    ]
    for path in os.environ['erp5_tests_bt5_path'].split(','):
      if os.path.exists(os.path.join(path, "bt5list")):
        bt5_path_list.append(path)
      for path in glob.glob(os.path.join(path, "*", "bt5list")):
        bt5_path_list.append(os.path.dirname(path))
    return bt5_path_list

  def _installBusinessTemplateList(
      self, bt_list, update_repository_bt_list=True, *args, **kwargs):
    """Install dependencies automatically

    taken from runUnitTest._ZodbTestComponentBootstrapOnly.
    """
    template_tool = self.portal.portal_templates

    bt5_path_list = self._getBusinessTemplatePathList()
    template_tool.updateRepositoryBusinessTemplateList(bt5_path_list)
    url_bt_tuple_list = [
      ('%s/%s' % (repository, bt_title), bt_title) for repository, bt_title in
      template_tool.resolveBusinessTemplateListDependency(
        [x[1] for x in bt_list], with_test_dependency_list=True)
    ]

    return super(ReExportBusinessTemplateTest,
                 self)._installBusinessTemplateList(
                   url_bt_tuple_list, *args, **kwargs)

  def test_re_export_business_template(self):
    template_tool = self.portal.portal_templates
    pref = self.portal.portal_preferences.newContent(
      portal_type='System Preference')
    pref.setPreferredWorkingCopyList(self._getBusinessTemplatePathList())
    pref.enable()
    self.tic()

    bt = template_tool.getInstalledBusinessTemplate(
      self.re_export_business_template, strict=True)
    bt.build()

    getattr(bt, 'tree.xml')()
    # TODO: do the actual commit from here ? for now we leave the changes in the
    # working copy and developer will review and commit the changes.


def test_suite():
  suite = unittest.TestSuite()
  re_export_business_template = os.environ['RE_EXPORT_BUSINESS_TEMPLATE']

  testclass = type(
    'ReExportBusinessTemplate %s' % re_export_business_template,
    (ReExportBusinessTemplateTest, ),
    {
      're_export_business_template': re_export_business_template,
    },
  )

  # required to create content in portal_components
  addUserToDeveloperRole('ERP5TypeTestCase')

  suite.addTest(unittest.makeSuite(testclass))
  return suite
