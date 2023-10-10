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

import os
import unittest
from glob import glob

from Products.ERP5.tests import testXHTML
from Products.ERP5.Document.BusinessTemplate import BusinessTemplateMissingDependency
from Products.ERP5Type.tests.utils import addUserToDeveloperRole
from Products.ERP5Type.tests.CodingStyleTestCase import CodingStyleTestCase


class CodingStyleTest(CodingStyleTestCase, testXHTML.TestXHTMLMixin):
  """Run a coding style test for business template defined by
  TESTED_BUSINESS_TEMPLATE environment variable, that is set by
  ERP5BusinessTemplateCodingStyleTestSuite in test/__init__.py
  """

  def getBusinessTemplateList(self):
    # note: more business templates will be installed by
    # _installBusinessTemplateList
    return (self.tested_business_template, )

  def _installBusinessTemplateList(self,
                                   bt_list,
                                   update_repository_bt_list=True,
                                   *args,
                                   **kwargs):
    """Install dependencies automatically and also install erp5_upgrader,
    which is needed for CodingStyleTestCase.test_run_upgrader

    the resolution approach is taken from runUnitTest._ZodbTestComponentBootstrapOnly.
    """
    template_tool = self.portal.portal_templates

    from Products.ERP5.ERP5Site import getBootstrapDirectory
    bt5_path_list = [os.environ.get('erp5_tests_bootstrap_path') or
                     getBootstrapDirectory()]
    for path in os.environ['erp5_tests_bt5_path'].split(','):
      if os.path.exists(os.path.join(path, "bt5list")):
        bt5_path_list.append(path)
      for path in glob(os.path.join(path, "*", "bt5list")):
        bt5_path_list.append(os.path.dirname(path))

    template_tool.updateRepositoryBusinessTemplateList(bt5_path_list)

    bt_to_install_title_set = set(x[1] for x in bt_list)
    bt_to_install_title_set.add('erp5_core')
    # Install the tested business template.
    try:
      url_bt_tuple_list = [
        ('%s/%s' % (repository, bt_title), bt_title) for repository, bt_title in
        template_tool.resolveBusinessTemplateListDependency(
          bt_to_install_title_set,
          with_test_dependency_list=True)]
    except BusinessTemplateMissingDependency as e:
      # it may have a virtual dependency on erp5_full_text_catalog, if that's
      # the case, we choose erp5_full_text_mroonga_catalog
      if str(e).startswith('Unable to resolve dependencies for erp5_full_text_catalog,'):
        url_bt_tuple_list = [
          ('%s/%s' % (repository, bt_title), bt_title) for repository, bt_title in
          template_tool.resolveBusinessTemplateListDependency(
            bt_to_install_title_set | set(('erp5_full_text_mroonga_catalog',)),
            with_test_dependency_list=True)]

    if 'erp5_upgrader' not in bt_to_install_title_set:
      upgrader_url_bt_tuple_list = [
        ('%s/%s' % (repository, bt_title), bt_title) for repository, bt_title in
        template_tool.resolveBusinessTemplateListDependency(
          ['erp5_upgrader'],
          # We don't actually run erp5_upgrader test, so we don't want to install
          # erp5_upgrader test dependencies
          with_test_dependency_list=False)]
      for url, bt in upgrader_url_bt_tuple_list:
        if bt not in bt_to_install_title_set:
          url_bt_tuple_list.append((url, bt))

    return super(CodingStyleTest,
                 self)._installBusinessTemplateList(url_bt_tuple_list,
                                                    *args, **kwargs)


def test_suite():
  suite = unittest.TestSuite()
  tested_business_template = os.environ['TESTED_BUSINESS_TEMPLATE']

  if tested_business_template == 'erp5_invoicing':
    from Testing import ZopeTestCase
    ZopeTestCase._print(
      '\nDo nothing: Invoice Line container is defined in '
      'erp5_{simplified,advanced}_invoicing so you should run those instead\n')
    return suite
  tested_business_template_list = [tested_business_template]
  if tested_business_template in ('erp5_simplified_invoicing',
                                    'erp5_advanced_invoicing'):
    tested_business_template_list.append('erp5_invoicing')

  testclass = type(
      'CodingStyleTest %s' % tested_business_template,
      (CodingStyleTest,),
      {
          'tested_business_template': tested_business_template,
      },
  )

  testXHTML.addTestMethodDynamically(
      testclass,
      testXHTML.validator,
      tested_business_template_list,
      expected_failure_list=testXHTML.expected_failure_list,
  )

  # required to create content in portal_components
  addUserToDeveloperRole('ERP5TypeTestCase')

  suite.addTest(unittest.makeSuite(testclass))
  return suite
