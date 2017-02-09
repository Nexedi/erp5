import unittest
from erp5.component.test.testWorkflowMixin import testWorkflowMixin

class TestWorklist(testWorkflowMixin):

  run_all_test = 1
  quiet = 1

  user_dict = {
    'foo': [None, None],
    'bar': [None, None],
  }

  test_worklist_dict = {
    'assignor_worklist':
      {'action_name': 'assignor_todo', 'role': 'Assignor', 'expr': None, 'state': 'draft', 'int_variable': None},
    'owner_worklist':
      {'action_name': 'owner_todo', 'role': 'Owner', 'expr': None, 'state': 'draft', 'int_variable': None},
    'owner_worklist_desactivated':
      {'action_name':'owner_todo_desactivated', 'role': 'Owner', 'expr': 'python: 0', 'state': 'draft', 'int_variable': None},
    'owner_worklist_wrong_state':
      {'action_name':'owner_todo_wrong_state', 'role': 'Owner', 'expr': None, 'state': 'not_draft', 'int_variable': None},
    'assignor_owner_worklist':
      {'action_name':'assignor_owner_todo', 'role': 'Assignor ; Owner','expr':  None, 'state': 'draft', 'int_variable': None},
    'int_value_worklist':
      {'action_name':'int_value_todo', 'role': None, 'expr': None, 'state': None, 'int_variable': str(1)}
  }


  def getTitle(self):
    return "Worklist"

  def cleanUp(self):
    # delete all objects of some modules
    for module in [self.portal.organisation_module, self.portal.portal_categories.region,
                   self.portal.portal_categories.role]:
      module.manage_delObjects(list(module.objectIds()))

    # delete "person" objects created by this test suite
    person_module = self.portal.person_module
    test_user_id_list = self.user_dict.keys()
    to_remove_list = [person.getId() for person in person_module.objectValues()
                      if person.getReference() in test_user_id_list]
    if to_remove_list:
      person_module.manage_delObjects(to_remove_list)
    self.tic()

  def afterSetUp(self):
    self.cleanUp()
    self.logMessage("Create users")
    self.createERP5Users()
    self.clearCache()
    self.tic()
    worklist_to_remove_list = [ key for key in self.test_worklist_dict.keys()
        if getattr(self.getPortalObject().portal_workflow.validation_workflow,
                   key,
                   False)
    ]
    self.removeWorklist('validation_workflow', worklist_to_remove_list)
    self.tic()

  def beforeTearDown(self):
    self.cleanUp()

  def createManagerAndLogin(self):
    """
    Create a simple user in user_folder with manager rights.
    This user will be used to initialize data in the method afterSetup
    """

    acl_user_folder = getattr(self.getPortal(), 'acl_users', None)
    acl_user_folder._doAddUser('manager', '', ['Manager'], [])
    self.loginByUserName('manager')

  def createERP5Users(self):
    """
    Create all ERP5 users needed for the test.
    ERP5 user = Person object + Assignment object in erp5 person_module.
    """

    module = self.portal.getDefaultModule("Person")
    # Create the Person.
    for user_login, user_data in self.user_dict.items():
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
      )
      assignment.open()
      person.newContent(portal_type='ERP5 Login', reference=user_login).validate()
    # Reindexing is required for the security to work
    self.tic()

  def createDocument(self, **kw):
    module = self.getPortal().getDefaultModule('Organisation')
    result = module.newContent(portal_type='Organisation', **kw)
    result.setProperty('int_index', 1)
    assert result.getValidationState() == 'draft'
    return result

  def associatePropertySheet(self):
    self._addPropertySheet('Organisation', 'SortIndex')

  def addWorkflowCataloguedVariable(self, workflow_id, variable_id):
    # Add new workflow compatibility
    # Will otherwise add dynamic variable in worklist.
    workflow_value = self.getWorkflowTool()[workflow_id]
    if workflow_value.getPortalType() != 'Workflow':
      variables = workflow_value.variables
      if not getattr(variables, variable_id, None):
        variables.addVariable(variable_id)
      variable_value = variables[variable_id]
      assert variable_value.for_catalog == 1

  def createWorklist(self, workflow_id, *args, **kw):
    workflow_value = self.getWorkflowTool()[workflow_id]
    if workflow_value.getPortalType() == 'Workflow':
      self.createERP5Worklist(workflow_value,*args, **kw)
    else:
      self.createDCWorklist(workflow_value, *args, **kw)

  def createERP5Worklist(self, workflow_value, worklist_id, action_name,
                     action=None, portal_type=None, validation_state=None,
                     guard_roles='', guard_expr=None, **kw):
    action_name='%s (%%(count)s)' % action_name
    if workflow_value.getPortalType() == 'Workflow':
      if getattr(workflow_value, worklist_id, None):
        workflow_value.manage_delObjects([worklist_id])
      worklist_value = getattr(workflow_value, 'worklist_%s' % worklist_id, None)
      if worklist_value is None:
        worklist_value = workflow_value.newContent(portal_type='Worklist')
      guard_roles = [] if not guard_roles else [role.strip() for role in guard_roles.split(';')]
      validation_state = None if not validation_state else 'state_' + validation_state

      worklist_value.edit(
        reference=worklist_id,
        action_name=action_name,
        action=action,
        action_type='global',
        matched_validation_state=validation_state,
        matched_portal_type_list=portal_type,
        guard_role_list=guard_roles,
        guard_expression=guard_expr
      )

      for worklist_variable_key, worklist_variable_value in kw.iteritems():
        worklist_variable = worklist_value.newContent(portal_type='Worklist Variable',
                                                      variable_value=worklist_variable_value,
                                                      reference=worklist_variable_key)
        if isinstance(worklist_variable_value, str) and worklist_variable_value.startswith('python'):
          worklist_variable.setVariableExpression(worklist_variable_value)

  def createDCWorklist(self, workflow_value, worklist_id, action_name,
                       action=None, **kw):
    action_name='%s (%%(count)s)' % action_name

    worklists = workflow_value.worklists
    if worklists._getOb(worklist_id, None):
      worklists.deleteWorklists([worklist_id])
    worklists.addWorklist(worklist_id)
    worklist_value = worklists._getOb(worklist_id)
    worklist_value.setProperties('', actbox_name=action_name, actbox_url=action,
                                 props={k if k.startswith('guard_')
                                          else 'var_match_' + k: v
                                        for k, v in kw.iteritems()})

  def removeWorklist(self, workflow_id, worklist_id_list):
    # add new workflow compatibility
    workflow_value = self.getWorkflowTool()[workflow_id]
    if workflow_value.getPortalType() == 'Workflow':
      for worklist_id in worklist_id_list:
        try:
          workflow_value._delObject('worklist_'+worklist_id)
        except KeyError:
          pass
    else:
      worklists = self.getWorkflowTool()[workflow_id].worklists
      worklists.deleteWorklists(worklist_id_list)

  def createCategories(self):
    category_tool = self.getCategoryTool()
    for base_category, category_list in (
        ('region', ('somewhere', 'elsewhere')),
        ('role',   ('client',    'supplier'))):
      newContent = category_tool[base_category].newContent
      for category in category_list:
        if not getattr(category_tool[base_category], category, None):
          newContent(portal_type='Category', id=category)

  def test_01_permission(self, quiet=0, run=run_all_test):
    """
    Test the permission of the building module.
    """
    if not run:
      return

    workflow_tool = self.portal.portal_workflow

    self.createManagerAndLogin()

    self.logMessage("Create worklists")
    self.associatePropertySheet()
    self.addWorkflowCataloguedVariable('validation_workflow',
                                       'int_index')
    for worklist_id in self.test_worklist_dict.keys():
      worklist = self.test_worklist_dict[worklist_id]
      self.createWorklist('validation_workflow',
                          worklist_id,
                          worklist['action_name'],
                          guard_roles=worklist['role'],
                          guard_expr=worklist['expr'],
                          portal_type='Organisation',
                          validation_state=worklist['state'],
                          int_index=worklist['int_variable'])
    self.tic()
    try:
      self.logMessage("Create document as Manager")
      document = self.createDocument()
      self.tic()
      self.clearCache()

      # Users can not see worklist as they are not Assignor
      for user_id in ('manager', ):
        self.loginByUserName(user_id)
        result = workflow_tool.listActions(object=document)

        self.logMessage("Check Assignor worklist as %s" % user_id)
        self.checkWorklist(result, 'assignor_todo', 0)
        self.logMessage("Check Owner worklist as %s" % user_id)
        self.checkWorklist(result, 'owner_todo', 1)
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
          self.logMessage("  Check Assignor worklist as %s" % user_id)
          self.checkWorklist(result, 'assignor_todo', assignor)
          self.logMessage("  Check Owner worklist as %s" % user_id)
          self.checkWorklist(result, 'owner_todo', owner)
          self.logMessage("  Check Owner and Assignor worklist as %s" % user_id)
          self.checkWorklist(result, 'assignor_owner_todo', both)

      # Check if int variable are managed by the worklist
      user_id = 'manager'
      self.loginByUserName(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist with int value as %s" % \
                                     (user_id, 1))
      self.checkWorklist(result, 'int_value_todo', 1)

      # Change int value on document
      document.setProperty('int_index', 2)
      self.tic()
      self.clearCache()

      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist with int value as %s" % \
                                     (user_id, 2))

      self.checkWorklist(result, 'int_value_todo', 0)

      #
      # Check monovalued security role
      #
      self.loginByUserName('manager')
      module = self.getPortal().getDefaultModule('Organisation')
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
          self.checkWorklist(result, 'owner_todo', count)

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
      self.commit()

  def test_02_related_key(self, quiet=0, run=run_all_test):
    """
    Test related keys
    """
    if not run:
      return

    workflow_tool = self.getWorkflowTool()
    self.createManagerAndLogin()

    self.logMessage("Create categories")
    self.createCategories()

    self.logMessage("Create worklists using 'base_category_id' related key")

    self.addWorkflowCataloguedVariable('validation_workflow',
                                       'base_category_id')
    self.createWorklist('validation_workflow', 'region_worklist', 'has_region',
                        portal_type='Organisation',
                        base_category_id='region')
    self.createWorklist('validation_workflow', 'role_worklist', 'has_role',
                        portal_type='Organisation',
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
      self.removeWorklist('validation_workflow',
                          ['region_worklist', 'role_worklist'])
      self.commit()


  def test_03_worklist_guard(self, quiet=0, run=run_all_test):
    """
    Test worklist guard
    """
    if not run:
      return

    workflow_tool = self.getWorkflowTool()
    self.createManagerAndLogin()

    self.logMessage("Create worklists with guard expression")
    self.createWorklist('validation_workflow', 'guard_expression_worklist',
                        'valid_guard_expression',
                        portal_type='Organisation',
                        validation_state='validated',
                        guard_roles='Associate',
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
      self.removeWorklist('validation_workflow',
                          ['guard_expression_worklist'])
      self.commit()


  def test_04_dynamic_variables(self):
    """
    Test related keys and TALES Expression
    """

    workflow_tool = self.getWorkflowTool()
    self.createManagerAndLogin()

    self.logMessage("Create categories")
    self.createCategories()

    self.logMessage("Create worklists using 'region_uid' related key"\
                    " and TALES Expression")
    self.addWorkflowCataloguedVariable('validation_workflow',
                                       'region_uid')
    self.createWorklist('validation_workflow', 'region_worklist',
                        'has_semewhere_region',
                        portal_type='Organisation',
                        action='organisation_module?'\
                        'region_uid:list=%(region_uid)s&'\
                        'portal_type:list=%(portal_type)s&reset:int=1',
                        region_uid='python:[str(object.getPortalObject().'\
                        'portal_categories.region.somewhere.getUid())]')

    try:
      document = self.createDocument()
      self.tic()
      self.clearCache()
      self.logMessage("  Check no document has region categories defined")
      action_list = workflow_tool.listActions(object=document)
      self.checkWorklist(action_list, 'has_semewhere_region', 0)

      self.logMessage("  Creates documents with region categories defined")

      self.createDocument(region='somewhere')
      self.createDocument(region='somewhere')
      self.createDocument(region='elsewhere')

      self.tic()
      self.clearCache()
      self.logMessage("  Check there are documents with region categories defined")
      action_list = workflow_tool.listActions(object=document)
      url_parameter_dict = {'region_uid': [str(self.portal.portal_categories.\
                                          region.somewhere.getUid())],
                            'portal_type': ['Organisation']}
      self.checkWorklist(action_list, 'has_semewhere_region', 2,
                         url_parameter_dict=url_parameter_dict, selection_name='organisation_module_selection')

    finally:
      self.removeWorklist('validation_workflow', ['region_worklist'])
      self.commit()

  def test_05_guard_expression_setters(self):
    worklist_id = 'guarded_worklist'
    workflow_id = 'validation_workflow'
    workflow_value = self.getWorkflowTool()[workflow_id]
    self.logMessage("  Check ERP5 Workflow 'guard expression' setter")
    if workflow_value.getPortalType() == 'Workflow':
      self.createWorklist(workflow_id, worklist_id,
                          action_name='guarded_test')
      worklist_value = getattr(workflow_value, 'worklist_%s' % worklist_id)

      # expression
      worklist_value.setGuardExpression('python: "Hello, world"')
      self.assertEqual(worklist_value.guard_expression.text, 'python: "Hello, world"')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestWorklist))
  return suite
