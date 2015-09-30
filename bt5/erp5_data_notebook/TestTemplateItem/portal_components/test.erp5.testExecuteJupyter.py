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

import time
import json

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

  def _newNotebookMessage(self, notebook_module=None, notebook_code=None):
    """
    Function to create new notebook messgae
    """
    return notebook_module.DataNotebook_addDataNotebookMessage(
      notebook_code=notebook_code,
      batch_mode=True
      )

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
    Test if user can create Data Notebook Message object or not
    """
    portal = self.portal

    notebook = self._newNotebook(reference='new_notebook_with_code')
    self.tic()

    notebook_code='some_random_invalid_notebook_code %s' % time.time()
    self._newNotebookMessage(
                            notebook_module=notebook,
                            notebook_code=notebook_code
                            )
    self.tic()

    notebook_message_search_result = portal.portal_catalog(
                                                  portal_type='Data Notebook',
                                                  notebook_code=notebook_code
                                                  )

    result = [obj.getId() for obj in notebook_message_search_result]

    if result:
      self.assertIn(notebook.getId(), result)

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

  def testBaseExecuteJupyterAddNotebookMessage(self):
    """
    Test if the notebook adds code history to the Data Notebook Message
    portal type
    """
    portal = self.portal
    self.login('dev_user')
    python_expression = "print 52"
    reference = 'Test.Notebook.AddNewNotebookMessage %s' % time.time()
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

    notebook_list = portal.portal_catalog(
                                          portal_type='Data Notebook',
                                          reference=reference
                                          )

    notebook_message_search_result = portal.portal_catalog(
                                              portal_type='Data Notebook',
                                              notebook_code=python_expression
                                              )

    result = [obj.getId() for obj in notebook_message_search_result]

    self.assertIn(notebook_list[0].getId(), result)

  def testBaseExecuteJupyterErrorHandling(self):
    """
    Test if the error message are saved by the Data Notebook Message portal
    type. We don't want to ignore the error message or show the error message
    as erp5 html. Best way would be to catch te exception and display it on
    notebook frontend.
    """
    portal = self.portal
    self.login('dev_user')
    python_expression = 'some_random_invalid_python_code'
    reference = 'Test.Notebook.ExecuteJupyterErrorHandling %s' % time.time()
    title = 'Test NB Title %s' % time.time()

    result = portal.Base_executeJupyter(
                              title=title,
                              reference=reference,
                              python_expression=python_expression
                              )
    self.tic()

    expected_status = 'error'
    self.assertEquals(json.loads(result)['status'].rstrip(), expected_status)

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
