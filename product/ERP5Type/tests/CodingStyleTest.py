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

from Products.ERP5Type.tests.CodingStyleTestCase import CodingStyleTestCase

class CodingStyleTest(CodingStyleTestCase):
  """Run a coding style test for business template defined by
  TESTED_BUSINESS_TEMPLATE environment variable, that is set by
  ERP5BusinessTemplateCodingStyleTestSuite in test/__init__.py
  """

  def getBusinessTemplateList(self):
    # install erp5_administration to check with tools from erp5_administration
    return ('erp5_administration', self.tested_business_template)

  def _installBusinessTemplateList(self,
                                   bt_list,
                                   update_repository_bt_list=True,
                                   *args,
                                   **kwargs):
    """Install depencencies automatically
    
    taken from runUnitTest._ZodbTestComponentBootstrapOnly.
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
    
    
    url_bt_tuple_list = [
      ('%s/%s' % (repository, bt_title), bt_title) for repository, bt_title in
      template_tool.resolveBusinessTemplateListDependency(
        [x[1] for x in bt_list],
        with_test_dependency_list=True)]

    return super(CodingStyleTest,
                 self)._installBusinessTemplateList(url_bt_tuple_list,
                                                    *args, **kwargs)

def test_suite():
  suite = unittest.TestSuite()
  tested_business_template = os.environ['TESTED_BUSINESS_TEMPLATE']

  testclass = type(
      'CodingStyleTest %s' % tested_business_template,
      (CodingStyleTest, ),
      {'tested_business_template': tested_business_template})

  suite.addTest(unittest.makeSuite(testclass))
  return suite

