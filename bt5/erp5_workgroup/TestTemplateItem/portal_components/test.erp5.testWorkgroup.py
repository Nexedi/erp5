# -*- coding: utf8 -*-
##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################


from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl import getSecurityManager
from Products.ERP5Type.tests.utils import TemporaryPythonScript


WORKGROUP_SCRIPT = """
rule_dict = {
  tuple(context.getPortalObject().getPortalAssignmentBaseCategoryList()): ((), )
}
category_list = context.ERP5User_getSecurityCategoryValueFromAssignment(
                                                           rule_dict=rule_dict)

# Extend default behaviour with workgroup support, this is not performance
# optimal.
from DateTime import DateTime
now = DateTime()
for assignment in context.objectValues(portal_type='Assignment'):
  workgroup = assignment.getDestinationValue(portal_type="Workgroup")
  if assignment.getValidationState() == 'open' and workgroup is not None and \
    (
      not assignment.hasStartDate() or assignment.getStartDate() <= now
    ) and (
      not assignment.hasStopDate() or assignment.getStopDate() >= now
    ):
    category_list.extend(
      workgroup.ERP5User_getSecurityCategoryValueFromAssignment(
        rule_dict=rule_dict))
return category_list
"""

class TestWorkgroup(ERP5TypeTestCase):
  """
  Test for erp5_workgroup business template.
  """
  def getTitle(self):
    return "TestWorkgroup"

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_workgroup',)

  def afterSetUp(self):
    self.person = self.portal.person_module.newContent(
        portal_type='Person',
        first_name='Test Workgroup First',
        last_name='Test Workgroup Last'
    )
    login = self.person.newContent(portal_type='ERP5 Login',
            reference="testworkgroup%s" % self.person.getId(),
            password="q98219281&odiajsdis$%s" % self.person.getUid())
    login.validate()
    self.person.validate()
    assignment = self.person.newContent(portal_type = 'Assignment')
    assignment.open()
    self.tic()

  def test(self):
    with TemporaryPythonScript(self.portal,
        "ERP5User_getUserSecurityCategoryValueList", "", WORKGROUP_SCRIPT):

      self.login(self.person.getUserId())
      user = getSecurityManager().getUser()
      self.assertIn('Authenticated', user.getRoles())
      self.assertSameSet([], user.getGroups())

      # add to group category
      self.login()
      # Ensure fake group exist
      category_tool = self.portal.portal_categories
      group_category = getattr(
        category_tool.group, "test_workgroup_company", None)
      if group_category is None:
        group_category = category_tool.group.newContent(portal_type="Category",
                                       id="test_workgroup_company")
      group_category.edit(codification="G-TESTWGCOMPANY")

      # Add assignment and check if the Codification is added as Roles
      self.person.newContent(portal_type='Assignment',
                        group='test_workgroup_company').open()
      self.tic()
      self.portal.portal_caches.clearAllCache()
      self.login(self.person.getUserId())
      user = getSecurityManager().getUser()
      self.assertIn('Authenticated', user.getRoles())
      self.assertSameSet([group_category.getCodification()], user.getGroups())

      # add workgroup
      self.login()
      workgroup = self.portal.workgroup_module.newContent(
        portal_type='Workgroup',
        title='workgroup-%s' % self.person.getUid()
      )
      workgroup.validate()

      self.person.newContent(portal_type='Assignment',
        destination_value=workgroup).open()
      self.tic()

      self.portal.portal_caches.clearAllCache()
      self.login(self.person.getUserId())
      user = getSecurityManager().getUser()
      self.assertIn('Authenticated', user.getRoles())
      self.assertSameSet([group_category.getCodification()], user.getGroups())

      self.login()

      # Ensure fake role exist
      category_tool = self.portal.portal_categories
      function_category = getattr(
        category_tool.function, "test_workgroup_function", None)
      if function_category is None:
        function_category = category_tool.function.newContent(
            portal_type="Category", id="test_workgroup_function")
      function_category.edit(codification="F-TESTWGFUNC")

      # Add assignment to the workgroup and check if the Codification is
      # added as user Roles
      workgroup.newContent(portal_type='Assignment',
                        function='test_workgroup_function').open()
      self.tic()

      self.portal.portal_caches.clearAllCache()
      self.login(self.person.getUserId())
      user = getSecurityManager().getUser()
      self.assertIn('Authenticated', user.getRoles())
      self.assertSameSet([function_category.getCodification(),
        group_category.getCodification()],
        user.getGroups())
