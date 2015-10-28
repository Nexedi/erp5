##############################################################################
#
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from Products.ERP5Type.tests.utils import addUserToDeveloperRole
from Products.ERP5Type.tests.utils import createZODBPythonScript, removeZODBPythonScript

import time
import json
import transaction

class TestExecuteJupyter(SecurityTestCase):
  
  def afterSetUp(self):
    """
    Ran to set the environment
    """
    self.notebook_module = self.portal.getDefaultModule(portal_type='Data Notebook')
    self.assertTrue(self.notebook_module is not None)

    # Create user to be used in tests
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser('dev_user', '', ['Manager',], [])
    user_folder._doAddUser('member_user', '', ['Member','Authenticated',], [])
    # Assign developer role to user
    addUserToDeveloperRole('dev_user')
    self.tic()

  def _newNotebook(self, reference=None):
    """
    Function to create new notebook
    """
    return self.notebook_module.DataNotebookModule_addDataNotebook(
      title='Some Notebook Title',
      reference=reference,
      form_id='DataNotebookModule_viewAddNotebookDialog',
      batch_mode=True
      )

  def _newNotebookLine(self, notebook_module=None, notebook_code=None):
    """
    Function to create new notebook line
    """
    return notebook_module.DataNotebook_addDataNotebookLine(
      notebook_code=notebook_code,
      batch_mode=True
      )

  def testJupyterCompileErrorRaise(self):
    """
    Test if JupyterCompile portal_component raises error on the server side.
    Take the case in which one line in a statement is valid and another is not.
    """
    portal = self.getPortalObject()
    script_id = "JupyterCompile_errorResult"
    script_container = portal.portal_skins.custom

    new_test_title = "Wendelin Test 1"
    # Check if the existing title is different from new_test_title or not
    if portal.getTitle()==new_test_title:
      new_test_title = "Wendelin"

    python_script = """
portal = context.getPortalObject()
portal.setTitle('%s')
print an_undefined_variable
"""%new_test_title

    # Create python_script object with the above given code and containers
    createZODBPythonScript(script_container, script_id, '', python_script)
    self.tic()

    # Call the above created script in jupyter_code
    jupyter_code = """
portal = context.getPortalObject()
portal.%s()
"""%script_id

    # Make call to Base_runJupyter to run the jupyter code which is making
    # a call to the newly created ZODB python_script and assert if the call raises
    # NameError as we are sending an invalid python_code to it
    self.assertRaises(
                      NameError,
                      portal.Base_runJupyter,
                      jupyter_code=jupyter_code,
                      old_local_variable_dict={}
                      )
    # Abort the current transaction of test so that we can proceed to new one
    transaction.abort()
    # Clear the portal cache from previous transaction
    self.portal.portal_caches.clearAllCache()
    # Remove the ZODB python script created above
    removeZODBPythonScript(script_container, script_id)

    # Test that calling Base_runJupyter shouldn't change the context Title
    self.assertNotEqual(portal.getTitle(), new_test_title)

  def testUserCannotAccessBaseExecuteJupyter(self):
    """
    Test if non developer user can't access Base_executeJupyter
    """
    portal = self.portal

    self.login('member_user')
    result = portal.Base_executeJupyter.Base_checkPermission('portal_components', 'Manage Portal')

    self.assertFalse(result)

  def testUserCanCreateNotebookWithoutCode(self):
    """
    Test the creation of Data Notebook object
    """
    portal = self.portal

    notebook = self._newNotebook(reference='new_notebook_without any_code')
    self.tic()

    notebook_search_result = portal.portal_catalog(
                                      portal_type='Data Notebook',
                                      title='Some Notebook Title'
                                      )

    result_title = [obj.getTitle() for obj in notebook_search_result]
    if result_title:
      self.assertEquals(notebook.getTitle(), result_title[0])

  def testUserCanCreateNotebookWithCode(self):
    """
    Test if user can create Data Notebook Line object or not
    """
    portal = self.portal

    notebook = self._newNotebook(reference='new_notebook_with_code %s' %time.time())
    self.tic()

    notebook_code='some_random_invalid_notebook_code %s' % time.time()
    notebook_line = self._newNotebookLine(
                            notebook_module=notebook,
                            notebook_code=notebook_code
                            )
    self.tic()

    notebook_line_search_result = portal.portal_catalog(portal_type='Data Notebook Line')

    result_reference_list = [obj.getReference() for obj in notebook_line_search_result]
    result_id_list = [obj.getId() for obj in notebook_line_search_result]

    if result_reference_list:
      self.assertIn(notebook.getReference(), result_reference_list)
      self.assertEquals(notebook_line.getReference(), notebook.getReference())
      self.assertIn(notebook_line.getId(), result_id_list)

  def testBaseExecuteJupyterAddNewNotebook(self):
    """
    Test the functionality of Base_executeJupyter python script.
    This test will cover folowing cases - 
    1. Call to Base_executeJupyter without python_expression
    2. Creating new notebook using the script
    """
    portal = self.portal
    self.login('dev_user')
    reference = 'Test.Notebook.AddNewNotebook %s' % time.time()
    title = 'Test new NB Title %s' % time.time()

    portal.Base_executeJupyter(title=title, reference=reference)
    self.tic()

    notebook_list = portal.portal_catalog(
                                    portal_type='Data Notebook',
                                    reference=reference
                                    )

    self.assertEquals(len([obj.getTitle() for obj in notebook_list]), 1)

  def testBaseExecuteJupyterAddNotebookLine(self):
    """
    Test if the notebook adds code history to the Data Notebook Line
    portal type while multiple calls are made to Base_executeJupyter with
    notebooks having same reference
    """
    portal = self.portal
    self.login('dev_user')
    python_expression = "print 52"
    reference = 'Test.Notebook.AddNewNotebookLine %s' % time.time()
    title = 'Test NB Title %s' % time.time()

    # Calling the function twice, first to create a new notebook and then
    # sending python_expression to check if it adds to the same notebook
    portal.Base_executeJupyter(title=title, reference=reference)
    self.tic()

    portal.Base_executeJupyter(
                              reference=reference,
                              python_expression=python_expression
                              )
    self.tic()

    notebook = portal.portal_catalog.getResultValue(
                                          portal_type='Data Notebook',
                                          reference=reference
                                          )

    notebook_line_search_result = portal.portal_catalog.getResultValue(
                                              portal_type='Data Notebook Line',
                                              reference=reference
                                              )
    # As we use timestamp in the reference and the notebook is created in this
    # function itself so, if anyhow a new Data Notebook Line has been created,
    # then it means that the code has been added to Input and Output of Data
    # Notebook Line portal_type
    if notebook_line_search_result:
      self.assertEquals(notebook.getReference(), notebook_line_search_result.getReference())

  def testBaseExecuteJupyterErrorHandling(self):
    """
    Test if the Base_executeJupyter with invalid python code raises error on
    server side. We are not catching the exception here. Expected result is
    raise of exception.
    """
    portal = self.portal
    self.login('dev_user')
    python_expression = 'some_random_invalid_python_code'
    reference = 'Test.Notebook.ExecuteJupyterErrorHandling %s' % time.time()
    title = 'Test NB Title %s' % time.time()

    self.assertRaises(
                      NameError, 
                      portal.Base_executeJupyter,
                      title=title,
                      reference=reference,
                      python_expression=python_expression
                      )

  def testBaseExecuteJupyterSaveActiveResult(self):
    """
    Test if the result is being saved inside active_process and the user can
    access the loacl variable and execute python expression on them
    """
    portal = self.portal
    self.login('dev_user')
    python_expression = 'a=2; b=3; print a+b'
    reference = 'Test.Notebook.ExecutePythonExpressionWithVariables %s' % time.time()
    title = 'Test NB Title %s' % time.time()

    portal.Base_executeJupyter(
                              title=title,
                              reference=reference,
                              python_expression=python_expression
                              )
    self.tic()

    notebook_list = portal.portal_catalog(
                                          portal_type='Data Notebook',
                                          reference=reference
                                          )
    notebook = notebook_list[0]
    process_id = notebook.getProcess()
    active_process = portal.portal_activities[process_id]
    result_list = active_process.getResultList()
    result = {'a':2, 'b':3}
    self.assertDictContainsSubset(result, result_list[0].summary)

  def testBaseExecuteJupyterRerunWithPreviousLocalVariables(self):
    """
    Test if the Base_compileJupyter function in extension is able to recognize
    the local_variables from the previous run and execute the python code
    """
    portal = self.portal
    self.login('dev_user')
    python_expression = 'a=2; b=3; print a+b'
    reference = 'Test.Notebook.ExecutePythonExpressionWithVariables %s' % time.time()
    title = 'Test NB Title %s' % time.time()

    portal.Base_executeJupyter(
                              title=title,
                              reference=reference,
                              python_expression=python_expression
                              )
    self.tic()

    python_expression = 'x=5; b=4; print a+b+x'
    result = portal.Base_executeJupyter(
                                        reference=reference,
                                        python_expression=python_expression
                                        )
    self.tic()

    expected_result = '11'
    self.assertEquals(json.loads(result)['code_result'].rstrip(), expected_result)

  def testBaseExecuteJupyterWithContextObjectsAsLocalVariables(self):
    """
    Test Base_executeJupyter with context objects as local variables
    """
    portal = self.portal
    self.login('dev_user')
    python_expression = 'a=context.getPortalObject(); print a.getTitle()'
    reference = 'Test.Notebook.ExecutePythonExpressionWithVariables %s' % time.time()
    title = 'Test NB Title %s' % time.time()

    result = portal.Base_executeJupyter(
                                        title=title,
                                        reference=reference,
                                        python_expression=python_expression
                                        )
    self.tic()

    expected_result = portal.getTitle()
    self.assertEquals(json.loads(result)['code_result'].rstrip(), expected_result)
