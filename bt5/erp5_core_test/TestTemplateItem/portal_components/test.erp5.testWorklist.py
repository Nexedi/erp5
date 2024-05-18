##############################################################################
#
# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
##############################################################################

from erp5.component.mixin.TestWorkflowMixin import TestWorkflowMixin
from Products.ERP5Type.tests.utils import todo_erp5
import six

class TestWorklist(TestWorkflowMixin):

  run_all_test = 1
  quiet = 1

  checked_portal_type = 'Organisation'
  module_selection_name = 'organisation_module_selection'
  checked_validation_state = 'draft'
  not_checked_validation_state = 'not_draft'
  checked_workflow = 'validation_workflow'
  worklist_assignor_id = 'assignor_worklist'
  actbox_assignor_name = 'assignor_todo'
  worklist_owner_id = 'owner_worklist'
  actbox_owner_name = 'owner_todo'
  worklist_assignor_owner_id = 'assignor_owner_worklist'
  actbox_assignor_owner_name = 'assignor_owner_todo'
  worklist_desactivated_id = '%s_desactivated' % worklist_owner_id
  actbox_desactivated_by_expression = '%s_desactivated' % actbox_owner_name
  worklist_wrong_state_id = '%s_wrong_state' % worklist_owner_id
  actbox_wrong_state = '%s_wrong_state' % actbox_owner_name

  worklist_int_variable_id = 'int_value_worklist'
  actbox_int_variable_name = 'int_value_todo'
  int_catalogued_variable_id = 'int_index'
  int_value = 1

  def getTitle(self):
    return "Worklist"

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.person_module)
    self.clearModule(self.portal.organisation_module)
    self.clearModule(self.portal.portal_categories.region)
    self.clearModule(self.portal.portal_categories.role)

  def getBusinessTemplateList(self):
    """
    Return list of bt5 to install
    """
    return ('erp5_base',)

  def getUserFolder(self):
    """
    Return the user folder
    """
    return getattr(self.getPortal(), 'acl_users', None)

  def createManagerAndLogin(self):
    """
    Create a simple user in user_folder with manager rights.
    This user will be used to initialize data in the method afterSetup
    """
    self.getUserFolder()._doAddUser('manager', self.newPassword(),
                                    ['Manager'], [])
    self.loginByUserName('manager')

  def createERP5Users(self, user_dict):
    """
    Create all ERP5 users needed for the test.
    ERP5 user = Person object + Assignment object in erp5 person_module.
    """
    portal = self.getPortal()
    module = portal.getDefaultModule("Person")
    # Create the Person.
    for user_login, user_data in user_dict.items():
      # Create the Person.
      self.logMessage("Create user: %s" % user_login)
      person = module.newContent(
        portal_type='Person',
        user_id=user_login,
        password='hackme',
      )
      # Create the Assignment.
      assignment = person.newContent(
        portal_type = 'Assignment',
        group = "%s" % user_data[0],
        function = "%s" % user_data[1],
        start_date = '01/01/1900',
        stop_date = '01/01/2900',
      )
      assignment.open()
      person.newContent(portal_type='ERP5 Login', reference=user_login).validate()
    # Reindexing is required for the security to work
    self.tic()

  def createUsers(self):
    """
    Create all users needed for the test
    """
    self.createERP5Users(self.getUserDict())

  def getUserDict(self):
    """
    Return dict of users needed for the test
    """
    user_dict = {
      'foo': [None, None],
      'bar': [None, None],
    }
    return user_dict

  def createDocument(self, **kw):
    module = self.getPortal().getDefaultModule(self.checked_portal_type)
    result = module.newContent(portal_type=self.checked_portal_type, **kw)
    result.setProperty(self.int_catalogued_variable_id, self.int_value)
    assert result.getValidationState() == self.checked_validation_state
    return result

  def associatePropertySheet(self):
    self._addPropertySheet(self.checked_portal_type, 'SortIndex')

  def addWorkflowCataloguedVariable(self, workflow_id, variable_id):
    # add new workflow compatibility
    workflow_value = self.getWorkflowTool()[workflow_id]
    if workflow_value.__class__.__name__ == 'Workflow':
      # Will add dynamic variable in worklist.
      pass
    else:
      variables = workflow_value.variables
      variables.addVariable(variable_id)
      variable_value = variables[variable_id]
      assert variable_value.for_catalog == 1

  def createWorklist(self, workflow_id, worklist_id, actbox_name,
                     actbox_url=None, **kw):
    # add new workflow compatibility
    workflow_value = self.getWorkflowTool()[workflow_id]
    if workflow_value.__class__.__name__ == 'Workflow':
      worklist_value = workflow_value.newContent(portal_type='Worklist')
      worklist_value.setReference(worklist_id)
      # Configure new workflow:
      actbox_name='%s (%%(count)s)' % actbox_name
      worklist_value.setActionName(str(actbox_name))
      worklist_value.setAction(str(actbox_url))
      worklist_value.setActionType('global')

      # Update guard configuration for view and guard value.
      from Products.ERP5Type.Tool.WorkflowTool import SECURITY_PARAMETER_ID
      v = kw.pop('guard_expr', None)
      if v:
        worklist_value.setGuardExpression(v)
      v = kw.pop('guard_roles', None)
      if v:
        worklist_value.setCriterion(SECURITY_PARAMETER_ID,
                                    [var.strip() for var in v.split(';')])
      for k, v in six.iteritems(kw):
        if k not in (SECURITY_PARAMETER_ID, workflow_value.getStateVariable()):
          variable_value = workflow_value.getVariableValueByReference(k)
          if variable_value is None:
            workflow_value.newContent(portal_type='Workflow Variable', reference=k)

        worklist_value.setCriterion(k, (v,))

    else:
      worklists = workflow_value.worklists
      worklists.addWorklist(worklist_id)
      worklist_value = worklists._getOb(worklist_id)
      worklist_value.setProperties('',
        actbox_name='%s (%%(count)s)' % actbox_name, actbox_url=actbox_url,
        props={k if k.startswith('guard_') else 'var_match_' + k: v
               for k, v in six.iteritems(kw)})


  def removeWorklist(self, workflow_id, worklist_id_list):
    # add new workflow compatibility
    workflow_value = self.getWorkflowTool()[workflow_id]
    if workflow_value.__class__.__name__ == 'Workflow':
      for worklist_id in worklist_id_list:
        workflow_value._delObject('worklist_'+worklist_id)
    else:
      worklists = self.getWorkflowTool()[workflow_id].worklists
      worklists.deleteWorklists(worklist_id_list)

  def createWorklists(self):
    self.createWorklist(self.checked_workflow,
                        self.worklist_assignor_id,
                        self.actbox_assignor_name,
                        portal_type=self.checked_portal_type,
                        guard_roles='Assignor',
                        validation_state=self.checked_validation_state)
    self.createWorklist(self.checked_workflow,
                        self.worklist_owner_id,
                        self.actbox_owner_name,
                        portal_type=self.checked_portal_type,
                        guard_roles='Owner',
                        validation_state=self.checked_validation_state)
    self.createWorklist(self.checked_workflow,
                        self.worklist_desactivated_id,
                        self.actbox_desactivated_by_expression,
                        portal_type=self.checked_portal_type,
                        guard_roles='Owner',
                        guard_expr='python: 0',
                        validation_state=self.checked_validation_state)
    self.createWorklist(self.checked_workflow,
                        self.worklist_wrong_state_id,
                        self.actbox_wrong_state,
                        portal_type=self.checked_portal_type,
                        guard_roles='Owner',
                        validation_state=self.not_checked_validation_state)
    self.createWorklist(self.checked_workflow,
                        self.worklist_assignor_owner_id,
                        self.actbox_assignor_owner_name,
                        portal_type=self.checked_portal_type,
                        guard_roles='Assignor; Owner',
                        validation_state=self.checked_validation_state)
    self.createWorklist(self.checked_workflow,
                        self.worklist_int_variable_id,
                        self.actbox_int_variable_name,
                        portal_type=self.checked_portal_type,
                        **{self.int_catalogued_variable_id: str(self.int_value)})

  def removeWorklists(self):
    self.removeWorklist(self.checked_workflow, [
          self.worklist_assignor_id,
          self.worklist_owner_id,
          self.worklist_desactivated_id,
          self.worklist_wrong_state_id,
          self.worklist_assignor_owner_id,
          self.worklist_int_variable_id,
    ])

  def test_edit_worklist_view(self):
    """Checks we can view and edit worklist.
    """
    def check_visible(worklist):
      self.clearCache()
      worklist.view()
    workflow_value = self.getWorkflowTool()[self.checked_workflow]

    # edit reference first
    worklist_value = workflow_value.newContent(portal_type='Worklist')
    check_visible(worklist_value)
    worklist_value.setReference(self.worklist_assignor_id)
    check_visible(worklist_value)
    worklist_value.setActionName('Test (%(count)s)')
    worklist_value.setAction('/')
    worklist_value.setActionType('global')
    check_visible(worklist_value)

    # edit reference last
    worklist_value = workflow_value.newContent(portal_type='Worklist')
    check_visible(worklist_value)
    worklist_value.setActionName('Test (%(count)s)')
    worklist_value.setAction('/')
    worklist_value.setActionType('global')
    check_visible(worklist_value)
    worklist_value.setReference(self.worklist_owner_id)
    check_visible(worklist_value)

  def test_01_permission(self, quiet=0, run=run_all_test):
    """
    Test the permission of the building module.
    """
    if not run:
      return

    workflow_tool = self.portal.portal_workflow

    self.logMessage("Create users")
    self.createManagerAndLogin()
    self.createUsers()
    self.logMessage("Create worklists")
    self.associatePropertySheet()
    self.addWorkflowCataloguedVariable(self.checked_workflow,
                                       self.int_catalogued_variable_id)
    self.createWorklists()
    try:
      self.logMessage("Create document as Manager")
      document = self.createDocument()

      self.tic()
      self.clearCache()

      result = workflow_tool.listActions(object=document)

      # Users can not see worklist as they are not Assignor
      for user_id in ('manager', ):
        self.loginByUserName(user_id)
        result = workflow_tool.listActions(object=document)
        self.logMessage("Check %s worklist as Assignor" % user_id)
        self.checkWorklist(result, self.actbox_assignor_name, 0)
        self.logMessage("Check %s worklist as Owner" % user_id)
        self.checkWorklist(result, self.actbox_owner_name, 1)
      for user_id in ('foo', 'bar'):
        self.logMessage("Check %s worklist" % user_id)
        self.loginByUserName(user_id)
        result = workflow_tool.listActions(object=document)
        self.assertEqual(result, [])

      for role, user_id_list in (('Assignor', ('foo', 'manager')),
                                 ('Assignee', ('foo', 'bar'))):
        self.loginByUserName('manager')
        for user_id in user_id_list:
          self.logMessage("Give %s %s role" % (user_id, role))
          document.manage_addLocalRoles(user_id, [role])
        document.reindexObject()
        self.tic()
        self.clearCache()

        for user_id, assignor, owner, both in (('manager', 1, 1, 1),
                                               ('bar'    , 0, 0, 0),
                                               ('foo'    , 1, 0, 1)):
          self.loginByUserName(user_id)
          result = workflow_tool.listActions(object=document)
          self.logMessage("  Check %s worklist as Assignor" % user_id)
          self.checkWorklist(result, self.actbox_assignor_name, assignor)
          self.logMessage("  Check %s worklist as Owner" % user_id)
          self.checkWorklist(result, self.actbox_owner_name, owner)
          self.logMessage("  Check %s worklist as Owner and Assignor" % user_id)
          self.checkWorklist(result, self.actbox_assignor_owner_name, both)

      # Check if int variable are managed by the worklist
      user_id = 'manager'
      self.loginByUserName(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist with int value as %s" % \
                                     (user_id, self.int_value))
      self.checkWorklist(result, self.actbox_int_variable_name, 1)

      # Change int value on document
      new_value = self.int_value + 1
      document.setProperty(self.int_catalogued_variable_id, new_value)
      self.tic()
      self.clearCache()

      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist with int value as %s" % \
                                     (user_id, new_value))
      self.checkWorklist(result, self.actbox_int_variable_name, 0)

      #
      # Check monovalued security role
      #
      self.loginByUserName('manager')
      module = self.getPortal().getDefaultModule(self.checked_portal_type)
      module.manage_setLocalRoles('bar', ['Author'])

      self.loginByUserName('bar')

      bar_document = self.createDocument()
      bar_document.manage_permission('View', ['Owner', 'Assignee'], 0)

      bar_assignee_document = self.createDocument()
      bar_assignee_document.manage_setLocalRoles('manager', ['Assignee'])
      bar_assignee_document.manage_permission('View', ['Owner', 'Assignee'], 0)

      user_id = 'manager'
      self.loginByUserName(user_id)

      module.manage_delLocalRoles('bar')

      def test(*count_list):
        local_role_list = 'Assignee', 'Owner'
        document.manage_setLocalRoles('manager', local_role_list)

        for i, count in enumerate(count_list):
          document.manage_permission('View', local_role_list[:i], 0)
          document.reindexObject()
          self.tic()
          self.clearCache()

          result = workflow_tool.listActions(object=document)
          self.logMessage("Check %s worklist as Owner (%s)" % (user_id, count))
          self.checkWorklist(result, self.actbox_owner_name, count)

      test(0, 0, 1)

      # Define a local role key
      sql_catalog = self.portal.portal_catalog.getSQLCatalog()
      current_sql_catalog_local_role_keys = \
            sql_catalog.sql_catalog_local_role_keys
      sql_catalog.sql_catalog_local_role_keys = ('Owner | owner', )
      self.commit()
      self.portal.portal_caches.clearAllCache()

      try:
        test(0, 1, 1)
      finally:
        sql_catalog.sql_catalog_local_role_keys = \
            current_sql_catalog_local_role_keys
        self.commit()
    finally:
      self.removeWorklists()

  def test_02_related_key(self, quiet=0, run=run_all_test):
    """
    Test related keys
    """
    if not run:
      return

    workflow_tool = self.getWorkflowTool()
    self.createManagerAndLogin()

    self.logMessage("Create categories")
    for base_category, category_list in (
        ('region', ('somewhere', 'elsewhere')),
        ('role',   ('client',    'supplier'))):
      newContent = self.getCategoryTool()[base_category].newContent
      for category in category_list:
        newContent(portal_type='Category', id=category)

    self.logMessage("Create worklists using 'base_category_id' related key")
    self.addWorkflowCataloguedVariable(self.checked_workflow,
                                       'base_category_id')
    self.createWorklist(self.checked_workflow, 'region_worklist', 'has_region',
                        portal_type=self.checked_portal_type,
                        base_category_id='region')
    self.createWorklist(self.checked_workflow, 'role_worklist', 'has_role',
                        portal_type=self.checked_portal_type,
                        base_category_id='role')

    try:
      document = self.createDocument()
      self.tic()
      self.clearCache()
      self.logMessage("  Check no document has region/role categories defined")
      result = workflow_tool.listActions(object=document)
      self.checkWorklist(result, 'has_region', 0)
      self.checkWorklist(result, 'has_role', 0)

      self.logMessage("  Creates documents with region/role categories defined")
      self.createDocument(role='client')
      self.createDocument(region='somewhere')
      self.createDocument(region='elsewhere')

      self.tic()
      self.clearCache()
      self.logMessage(
               "  Check there are documents with region/role categories defined")
      result = workflow_tool.listActions(object=document)
      self.checkWorklist(result, 'has_region', 2)
      self.checkWorklist(result, 'has_role', 1)
    finally:
      self.removeWorklist(self.checked_workflow,
                          ['region_worklist', 'role_worklist'])

  def test_03_worklist_guard(self, quiet=0, run=run_all_test):
    """
    Test worklist guard
    """
    if not run:
      return

    workflow_tool = self.getWorkflowTool()
    self.createManagerAndLogin()
    self.createUsers()

    self.logMessage("Create worklists with guard expression")
    self.createWorklist(self.checked_workflow, 'guard_expression_worklist',
                        'valid_guard_expression',
                        portal_type=self.checked_portal_type,
                        validation_state='validated',
                        guard_roles="Associate",
                        guard_expr='python: user.getId() == "bar"')

    try:
      document = self.createDocument()
      document.manage_addLocalRoles("bar", ["Associate"])
      document.manage_addLocalRoles("foo", ["Associate"])
      document.validate()
      document.reindexObject()
      self.tic()
      self.clearCache()

      self.logMessage("  Check that manager can not access worklist")
      result = workflow_tool.listActions(object=document)
      self.checkWorklist(result, 'valid_guard_expression', 0)

      self.logMessage("  Check that user bar can access worklist")
      self.loginByUserName('bar')
      result = workflow_tool.listActions(object=document)
      self.checkWorklist(result, 'valid_guard_expression', 1)

      self.logMessage("  Check that user foo can not access worklist")
      self.loginByUserName('foo')
      result = workflow_tool.listActions(object=document)
      self.checkWorklist(result, 'valid_guard_expression', 0)
    finally:
      self.removeWorklist(self.checked_workflow,
                          ['guard_expression_worklist'])

  @todo_erp5
  def test_04_dynamic_variables(self):
    """
    Test related keys and TALES Expression
    """
    workflow_tool = self.getWorkflowTool()
    self.createManagerAndLogin()

    self.logMessage("Create categories")
    for base_category, category_list in (
        ('region', ('somewhere', 'elsewhere')),
        ('role',   ('client',    'supplier'))):
      newContent = self.getCategoryTool()[base_category].newContent
      for category in category_list:
        newContent(portal_type='Category', id=category)

    self.logMessage("Create worklists using 'region_uid' related key"\
                    " and TALES Expression")
    self.addWorkflowCataloguedVariable(self.checked_workflow,
                                       'region_uid')
    self.createWorklist(self.checked_workflow, 'region_worklist',
                        'has_semewhere_region',
                        portal_type=self.checked_portal_type,
                        actbox_url='organisation_module?'\
                        'region_uid:list=%(region_uid)s&'\
                        'portal_type:list=%(portal_type)s&reset:int=1',
                        region_uid='python:object.getPortalObject().'\
                        'portal_categories.getCategoryUid("somewhere",'\
                        ' base_category="region")')

    try:
      document = self.createDocument()
      self.tic()
      self.clearCache()
      self.logMessage("  Check no document has region categories defined")
      result = workflow_tool.listActions(object=document)
      self.checkWorklist(result, 'has_semewhere_region', 0)

      self.logMessage("  Creates documents with region categories defined")

      self.createDocument(region='somewhere')
      self.createDocument(region='somewhere')
      self.createDocument(region='elsewhere')

      self.tic()
      self.clearCache()
      self.logMessage(
               "  Check there are documents with region categories defined")
      result = workflow_tool.listActions(object=document)
      url_parameter_dict = {'region_uid': [str(self.portal.portal_categories.\
                                          getCategoryUid("region/somewhere"))],
                            'portal_type': [self.checked_portal_type]}
      self.checkWorklist(result, 'has_semewhere_region', 2,
                         url_parameter_dict=url_parameter_dict)

    finally:
      self.removeWorklist(self.checked_workflow, ['region_worklist'])