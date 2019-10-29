##############################################################################
#
# Copyright (c) 2002-2019 Nexedi SA and Contributors. All Rights Reserved.
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

import re
import typing
from typing import List # pylint: disable=unused-import
import enum
import textwrap

from collections import namedtuple
# TODO: just import !

# https://microsoft.github.io/monaco-editor/api/classes/monaco.position.html
# lineNumber and column start at 1
Position = namedtuple('Position', 'lineNumber column')
Completion = namedtuple('Completion', 'text description')  # TODO
# with ReferenceCompletion, we can use regexs
ReferenceCompletion = namedtuple('ReferenceCompletion', 'text description')

# /TODO

if typing.TYPE_CHECKING:
  xScriptType = typing.Union[typing.Literal['Python (Script)']]
  import erp5.portal_type  # pylint: disable=import-error,unused-import


class ScriptType(enum.Enum):
  Component = 0
  SkinFolderPythonScript = 1
  WorkflowPythonScript = 1


# XXX workaround missing completions from unittest.TestCase
import unittest


class XERP5TypeTestCase(ERP5TypeTestCase, unittest.TestCase):
  pass


class PythonSupportTestCase(XERP5TypeTestCase):
  """TestCase for python support 
  """
  def assertCompletionIn(self, completion, completion_list):
    # type: (ReferenceCompletion, List[Completion]) -> None
    """check that `completion` is in `completion_list`
    """
    self.fail('TODO')

  def assertCompletionNotIn(self, completion, completion_list):
    # type: (ReferenceCompletion, List[Completion]) -> None
    """check that `completion` is not in `completion_list`
    """
    self.fail('TODO')


class TestCompleteFromScript(PythonSupportTestCase):
  """Test completions from within a python scripts
  
  Check that magic of python scripts with context and params
  is properly emulated.
  """
  script_name = 'Base_example'
  script_params = ''

  def getCompletionList(self, code, position=None):
    # type: (str, Position) -> List[Completion]
    return self.portal.portal_python_support.getCompletionList(code, position)

  def test_portal_tools(self):
    completion_list = self.getCompletionList(
        textwrap.dedent('''
          context.getPortalObject().'''))
    self.assertCompletionIn(Completion(text="person_module"), completion_list)
    self.assertCompletionIn(Completion(text="portal_types"), completion_list)

  def test_base_method(self):
    completion_list = self.getCompletionList(
        textwrap.dedent('''
          context.getP'''))
    self.assertCompletionIn(Completion(text="getPortalType"), completion_list)
    self.assertCompletionIn(Completion(text="getParentValue"), completion_list)

  def test_context_name(self):
    self.script_name = 'Person_example'
    completion_list = self.getCompletionList(
        textwrap.dedent('''
          context.getFir'''))
    self.assertCompletionIn(Completion(text="getFirstName"), completion_list)

  def test_params_type_comment(self):
    self.script_params = 'person'
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            # type: (erp5.portal_type.Person) -> str
            person.getFir'''))
    self.assertCompletionIn(Completion(text="getFirstName"), completion_list)


class TestCompleteWithScript(PythonSupportTestCase):
  """Check that python scripts are offered as completions items like methods on objects.
  """
  def afterSetUp(self):
    super(TestCompleteWithScript, self).afterSetUp()
    # sanity check that the scripts we are asserting with really exist
    self.assertTrue(hasattr(self.portal, 'Account_getFormattedTitle'))
    self.assertTrue(hasattr(self.portal, 'Person_getAge'))
    self.assertTrue(hasattr(self.portal, 'Base_edit'))
    self.assertTrue(hasattr(self.portal, 'ERP5Site_getSearchResultList'))

  def test_context(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.'''))
    self.assertCompletionIn(Completion(text="Person_getAge"), completion_list)
    self.assertCompletionIn(
        Completion(text="ERP5Site_getSearchResultList"), completion_list)
    self.assertCompletionIn(Completion(text="Base_edit"), completion_list)
    self.assertCompletionNotIn(
        Completion(text="Account_getFormattedTitle"), completion_list)

  def test_docstring(self):
    # create python script with docstring
    # check docstring from completion contain this docstring + a link to /manage_main on the script
    self.fail('TODO')

  def test_docstring_plus_type_comment(self):
    # create python script with docstring and type comment for parameters
    # check docstring from completion contain this docstring + a link to /manage_main on the script
    self.fail('TODO')

  def test_no_docstring(self):
    # create python script with no docstring
    # check docstring from completion contain a link to /manage_main on the script
    self.fail('TODO')

  def test_typevar_in_type_comment(self):
    # create a Base_x python script with a type comment returning content same portal_type,
    # like Base_createCloneDocument
    # type: (X,) -> X
    self.fail('TODO')


class TestCompletePortalType(PythonSupportTestCase):

  def test_getattr(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person_module = None # type: erp5.portal_type.PersonModule
            person_module.person.getFi'''))
    self.assertCompletionIn(Completion(text="getFirstName"), completion_list)

  def test_getitem(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person_module = None # type: erp5.portal_type.PersonModule
            person_module[person].getFi'''))
    self.assertCompletionIn(Completion(text="getFirstName"), completion_list)

  def test_newContent_return_value(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person_module = None # type: erp5.portal_type.PersonModule
            person_module.newContent().getFi'''))
    self.assertCompletionIn(Completion(text="getFirstName"), completion_list)

  def test_newContent_portal_type_return_value(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.newContent(portal_type="Bank Account").get'''))
    self.assertCompletionIn(
        Completion(text="getBankAccountHolderName"), completion_list)

    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.newContent(portal_type="Address").get'''))
    self.assertCompletionNotIn(
        Completion(text="getBankAccountHolderName"), completion_list)

  def test_searchFolder_return_value(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person_module = None # type: erp5.portal_type.PersonModule
            person_module.searchFolder()[0].'''))
    self.assertCompletionIn(Completion(text="getObject"), completion_list)
    self.assertCompletionNotIn(Completion(text="getFirstName"), completion_list)

    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person_module = None # type: erp5.portal_type.PersonModule
            person_module.searchFolder()[0].getObject().'''))
    self.assertCompletionIn(Completion(text="getFirstName"), completion_list)

  def test_searchFolder_portal_type_return_value(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.searchFolder(portal_type="Bank Account")[0].get'''))
    self.assertCompletionIn(Completion(text="getObject"), completion_list)
    self.assertCompletionNotIn(
        Completion(text="getBankAccountHolderName"), completion_list)

    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.searchFolder(portal_type="Bank Account")[0].getObject().get'''
        ))
    self.assertCompletionIn(
        Completion(text="getBankAccountHolderName"), completion_list)

    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.searchFolder(portal_type="Address")[0].getObject().get'''))
    self.assertCompletionNotIn(
        Completion(text="getBankAccountHolderName"), completion_list)

  def test_getPortalType_docstring(self):
    # getPortalType docstring has a full description of the portal type and a link
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.getPortalType'''))
    self.assertCompletionIn(
        Completion(
            description=re.compile(
                ".*Persons capture the contact information.*")),
        completion_list)
    self.assertCompletionIn(
        Completion(description=re.compile(".*portal_types/Person.*")),
        completion_list)

  def test_getPortalType_literal(self):
    # jedi knows what literal getPortalType returns
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            this = "a"
            if person.getPortalType() = "Person":
              this = []
            this.'''))
    # jedi understood that `this` is list in this case
    self.assertCompletionIn(Completion(text="append"), completion_list)
    self.assertCompletionNotIn(Completion(text="capitalize"), completion_list)

  def test_getParentValue(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.getParentValue().getPortalType'''))
    self.assertCompletionIn(
        Completion(description=re.compile(".*Person Module.*")),
        completion_list)

  def test_workflow_state_getter(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.get'''))
    self.assertCompletionIn(
        Completion(text="getValidationState"), completion_list)
    self.assertCompletionIn(
        Completion(text="getTranslatedValidationStateTitle"), completion_list)
    self.assertCompletionNotIn(
        Completion(text="getSimulationState"), completion_list)

  def test_workflow_method(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.validat'''))
    self.assertCompletionIn(Completion(text="validate"), completion_list)

  def test_edit_argument(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.edit(fir'''))
    self.assertCompletionIn(Completion(text="first_name"), completion_list)

  def test_new_content_argument(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person_module = None # type: erp5.portal_type.PersonModule
            person_module.newContent(fir'''))
    self.assertCompletionIn(Completion(text="first_name"), completion_list)


class TestCompletePropertySheet(PythonSupportTestCase):
  def test_content_property(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.getDefaultAddre'''))
    self.assertCompletionIn(
        Completion(text="getDefaultAddressStreetAddress"), completion_list)
    self.assertCompletionIn(
        Completion(text="getDefaultAddressCity"), completion_list)
    self.assertCompletionIn(
        Completion(text="getDefaultAddressText"), completion_list)
    self.assertCompletionIn(
        Completion(text="getDefaultAddressRegionTitle"), completion_list)

    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.setDefaultAddre'''))
    self.assertCompletionIn(
        Completion(text="setDefaultAddressStreetAddress"), completion_list)
    self.assertCompletionIn(
        Completion(text="setDefaultAddressCity"), completion_list)
    self.assertCompletionIn(
        Completion(text="setDefaultAddressText"), completion_list)
    self.assertCompletionIn(
        Completion(text="setDefaultAddressRegionValue"), completion_list)
    self.assertCompletionNotIn(
        Completion(text="setDefaultAddressRegionTitle"), completion_list)

  def test_category(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.get'''))
    self.assertCompletionIn(Completion(text="getRegion"), completion_list)
    self.assertCompletionIn(Completion(text="getRegionTitle"), completion_list)
    self.assertCompletionIn(Completion(text="getRegionValue"), completion_list)
    self.assertCompletionIn(
        Completion(text="getDefaultRegionTitle"), completion_list)

    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.set'''))
    self.assertCompletionIn(
        Completion(text="setRegion"),
        completion_list)  # XXX include this accessor ?
    self.assertCompletionNotIn(
        Completion(text="getRegionTitle"), completion_list)
    self.assertCompletionIn(Completion(text="setRegionValue"), completion_list)
    self.assertCompletionNotIn(
        Completion(text="setDefaultRegionTitle"), completion_list)

  def test_category_value_getter_portal_type(self):
    # filtered for a portal type
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.getRegionValue(portal_type="Bank Account").'''))
    self.assertCompletionIn(
        Completion(text="getBankAccountHolderName"), completion_list)
    # a list of portal types
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.getRegionValue(portal_type=("Bank Account", "Address")).'''))
    self.assertCompletionIn(
        Completion(text="getBankAccountHolderName"), completion_list)
    # not filter assume any portal type
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            person = None # type: erp5.portal_type.Person
            person.getRegionValue().'''))
    self.assertCompletionIn(
        Completion(text="getBankAccountHolderName"), completion_list)


class TestCompleteERP5Site(PythonSupportTestCase):
  def test_base_method(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.res'''))
    self.assertCompletionIn(Completion(text="restrictedTraverse"), completion_list)

  def test_content(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.acl'''))
    self.assertCompletionIn(Completion(text="acl_users"), completion_list)
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.acl_users.getUs'''))
    self.assertCompletionIn(Completion(text="getUserById"), completion_list)

  def test_portal_itself(self):
    # non regression for bug, when completing on portal. this cause:
    # AttributeError: 'CompiledObject' object has no attribute 'py__get__'
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.'''))
    self.assertCompletionIn(Completion(text="getTitle"), completion_list)


class TestCompleteCatalogTool(PythonSupportTestCase):
  def test_brain(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_catalog.searchResults().'''))
    self.assertCompletionIn(Completion(text="getObject"), completion_list)
    self.assertCompletionIn(Completion(text="title"), completion_list)
    self.assertCompletionIn(Completion(text="path"), completion_list)
    self.assertCompletionNotIn(Completion(text="getTitle"), completion_list)

  def test_portal_type(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_catalog.searchResults(
                portal_type='Bank Account').getObject().getBank'''))
    self.assertCompletionIn(
        Completion(text="getBankAccountHolderName"), completion_list)

  def test_arguments(self):
    # catalog columns
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_catalog(titl'''))
    self.assertCompletionIn(
        Completion(text="title"), completion_list)
    # related keys
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_catalog(tra'''))
    self.assertCompletionIn(
        Completion(text="translated_simulation_state_title"), completion_list)
    # category dynamic related keys
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_catalog(grou'''))
    self.assertCompletionIn(
        Completion(text="group_uid"), completion_list)
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_catalog(default_grou'''))
    self.assertCompletionIn(
        Completion(text="default_group_uid"), completion_list)
    # scriptable keys
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_catalog(full'''))
    self.assertCompletionIn(
        Completion(text="full_text"), completion_list)


class TestCompleteSimulationTool(PythonSupportTestCase):
  def test_inventory_list_brain(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_simulation.getInventoryList()[0].'''))
    self.assertCompletionIn(Completion(text="getObject"), completion_list)
    self.assertCompletionIn(Completion(text="section_title"), completion_list)
    self.assertCompletionIn(Completion(text="section_uid"), completion_list)
    self.assertCompletionIn(Completion(text="quantity"), completion_list)
    self.assertCompletionIn(Completion(text="total_price"), completion_list)
    self.assertCompletionNotIn(Completion(text="getQuantity"), completion_list)

  def test_movement_history_list_brain(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_simulation.getMovementHistoryList()[0].'''))
    self.assertCompletionIn(Completion(text="getObject"), completion_list)
    self.assertCompletionIn(Completion(text="section_title"), completion_list)
    self.assertCompletionIn(Completion(text="section_uid"), completion_list)
    self.assertCompletionIn(Completion(text="quantity"), completion_list)
    self.assertCompletionIn(Completion(text="total_price"), completion_list)
    self.assertCompletionNotIn(Completion(text="getQuantity"), completion_list)

  def test_brain_date_is_date_time(self):
    for method in (
        'getInventoryList',
        'getMovementHistoryList',):
      completion_list = self.getCompletionList(
          textwrap.dedent(
              '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_simulation.{}()[0].date.''').format(method))
      self.assertCompletionIn(Completion(text="year"), completion_list)

  def test_brain_node_value_is_node(self):
    for method in (
        'getInventoryList',
        'getMovementHistoryList',):
      completion_list = self.getCompletionList(
          textwrap.dedent(
              '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_simulation.{}()[0].node_value.''').format(method))
      self.assertCompletionIn(Completion(text="getTitle"), completion_list)

  def test_portal_type(self):
    for method in (
        'getInventoryList',
        'getMovementHistoryList',):
      completion_list = self.getCompletionList(
          textwrap.dedent(
              '''
              portal = None # type: erp5.portal_type.ERP5Site
              portal.portal_simulation.{}(
                  portal_type='Sale Order Line'
              )[0].getObject().getPortalType''').format(method))
    self.assertCompletionIn(
        Completion(description=re.compile("Sale Order Line")), completion_list)


class TestCompletePreferenceTool(PythonSupportTestCase):
  def test_preference_tool_preference_getter(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_preferrences.get'''))
    self.assertCompletionIn(Completion(text="getPreferredClientRoleList"), completion_list)

  def test_preference_tool_preference_setter(self):
    completion_list = self.getCompletionList(
        textwrap.dedent(
            '''
            portal = None # type: erp5.portal_type.ERP5Site
            portal.portal_preferrences.set'''))
    self.assertCompletionNotIn(Completion(text="setPreferredClientRoleList"), completion_list)