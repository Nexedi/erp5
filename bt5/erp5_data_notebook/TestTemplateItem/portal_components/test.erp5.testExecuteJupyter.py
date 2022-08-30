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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import addUserToDeveloperRole
from Products.ERP5Type.tests.utils import createZODBPythonScript, removeZODBPythonScript

import time
import json
import jupyter_client
import base64
import random
import string


class TestExecuteJupyter(ERP5TypeTestCase):
  
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
    # Create script to mock execution
    createZODBPythonScript(self.getPortal().portal_skins.custom, "ERP5Site_isDataNotebookEnabled", '', "return True")

    self.tic()

  def beforeTearDown(self):
    removeZODBPythonScript(self.getPortal().portal_skins.custom, "ERP5Site_isDataNotebookEnabled")
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
    Test if JupyterCompile portal_component correctly catches exceptions as 
    expected by the Jupyter frontend as also automatically abort the current
    transaction.
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
    # a call to the newly created ZODB python_script and assert if the call 
    # processes correctly the NameError as we are sending an invalid 
    # python_code to it.
    # 
    result = portal.Base_runJupyter(
      jupyter_code=jupyter_code, 
      old_notebook_context=portal.Base_createNotebookContext()
    )
    
    self.assertEquals(result['ename'], 'NameError')
    self.assertEquals(result['result_string'], None)
    
    # There's no need to abort the current transaction. The error handling code
    # should be responsible for this, so we check the script's title
    script_title = script_container.JupyterCompile_errorResult.getTitle()
    self.assertNotEqual(script_title, new_test_title)
    
    removeZODBPythonScript(script_container, script_id)

    # Test that calling Base_runJupyter shouldn't change the context Title
    self.assertNotEqual(portal.getTitle(), new_test_title)
    
  def testBase_executeJupyterRespectPreference(self):
    self.login('dev_user')
    removeZODBPythonScript(self.getPortal().portal_skins.custom, "ERP5Site_isDataNotebookEnabled")
    createZODBPythonScript(self.getPortal().portal_skins.custom, "ERP5Site_isDataNotebookEnabled", '', "return False")
    self.tic()

    jupyter_code = "a = 1\na"
    reference = 'Test.Notebook.PreferenceHandle'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.assertEqual(result, 'The synchronous and unrestricted implementation is not enabled on the server')

  def testJupyterCompileInvalidPythonSyntax(self):
    """
    Test how the JupyterCompile extension behaves when it receives Python
    code to be executed that has invalid syntax. 
    """
    self.login('dev_user')
    jupyter_code = "a = 1\na++"
    
    reference = 'Test.Notebook.ErrorHandling.SyntaxError'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    result_json = json.loads(result)
    
    self.assertEquals(result_json['ename'], 'SyntaxError')

  def testUserCannotAccessBaseExecuteJupyter(self):
    """
    Test if non developer user can't access Base_executeJupyter
    """
    portal = self.portal

    self.login('member_user')
    result = portal.Base_executeJupyter(title='Any title', reference='Any reference')

    self.assertEquals(result, 'You are not authorized to access the script')

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

    result = json.loads(portal.Base_executeJupyter(
      title=title, 
      reference=reference, 
      python_expression=python_expression
    ))
    
    self.assertEquals(result['ename'], 'NameError')
    self.assertEquals(result['code_result'], None)

  def testBaseExecuteJupyterSaveNotebookContext(self):
    """
    Test if user context is being saved in the notebook_context property and the 
    user can access access and execute python code on it.
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
    notebook_context = notebook.getNotebookContext()['variables']
    result = {'a':2, 'b':3}
    self.assertDictContainsSubset(result, notebook_context)

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

  def testSavingModuleObjectLocalVariables(self):
    """
    Test to check the saving of module objects in notebook_context
    and if they work as expected.
    """
    portal = self.portal
    self.login('dev_user')
    jupyter_code = """
import imghdr as imh
import sys
"""
    reference = 'Test.Notebook.ModuleObject %s' %time.time()
    portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
      )
    self.tic()

    jupyter_code =  "print imh.__name__"
    result = portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code)

    self.assertEquals(json.loads(result)['code_result'].rstrip(), 'imghdr')
    self.assertEquals(json.loads(result)['mime_type'].rstrip(), 'text/plain')

  def testERP5ImageProcessor(self):
    """
    Test the fucntioning of the ERP5ImageProcessor and the custom system 
    display hook too. 
    """
    self.image_module = self.portal.getDefaultModule('Image')
    self.assertTrue(self.image_module is not None)
    # Create a new ERP5 image object
    reference = 'testBase_displayImageReference5'
    data_template = '<img src="data:application/unknown;base64,%s" /><br />'
    data = 'qwertyuiopasdfghjklzxcvbnm<somerandomcharacterstosaveasimagedata>'
    if getattr(self.image_module, 'testBase_displayImageID5', None) is not None:
      self.image_module.manage_delObjects(ids=['testBase_displayImageID5'])
    self.image_module.newContent(
      portal_type='Image',
      id='testBase_displayImageID5',
      reference=reference,
      data=data,
      filename='test.png'
      )
    self.tic()

    # Call Base_displayImage from inside of Base_runJupyter
    jupyter_code = """
image = context.portal_catalog.getResultValue(portal_type='Image',reference='%s')
context.Base_renderAsHtml(image)
"""%reference

    notebook_context = {'setup' : {}, 'variables' : {}}
    result = self.portal.Base_runJupyter(
      jupyter_code=jupyter_code,
      old_notebook_context=notebook_context
      )

    self.assertTrue((data_template % base64.b64encode(data)) in result['result_string'])
    # Mime_type shouldn't be  image/png just because of filename, instead it is
    # dependent on file and file data
    self.assertNotEqual(result['mime_type'], 'image/png')

  def testImportSameModuleDifferentNamespace(self):
    """
    Test if the imports of python modules with same module name but different
    namespace work correctly as expected
    """
    portal = self.portal
    self.login('dev_user')

    # First we execute a jupyter_code which imports sys module as 'ss' namespace
    jupyter_code = "import sys as ss"
    reference = 'Test.Notebook.MutlipleImports %s' %time.time()
    portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
      )
    self.tic()

    # Call Base_executeJupyter again with jupyter_code which imports sys module
    # as 'ss1' namespace
    jupyter_code1 = "import sys as ss1"
    portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code1
      )
    self.tic()

    # Call Base_executeJupyter to check for the name of module and match it with
    # namespace 'ss1'
    jupyter_code2 = "print ss1.__name__"
    result = portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code2
      )
    self.assertEquals(json.loads(result)['code_result'].rstrip(), 'sys')
    
  def testEnvironmentObjectWithFunctionAndClass(self):
    self.login('dev_user')
    environment_define_code = '''
def create_sum_machines():
  def sum_function(x, y):
    return x + y
    
  class Calculator(object):
  
    def sum(self, x, y):
      return x + y
    
  return {'sum_function': sum_function, 'Calculator': Calculator}

environment.clearAll()
environment.define(create_sum_machines, 'creates sum function and class')
'''
    reference = 'Test.Notebook.EnvironmentObject.Function'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=environment_define_code
    )
    
    self.tic()
    self.assertEquals(json.loads(result)['status'], 'ok')
    
    jupyter_code = '''
print sum_function(1, 1)
print Calculator().sum(2, 2)
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    
    self.tic()
    result = json.loads(result)
    output = result['code_result']
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(output.strip(), '2\n4')
    
  def testEnvironmentObjectSimpleVariable(self):
    self.login('dev_user')
    environment_define_code = '''
environment.clearAll()
environment.define(x='couscous')
'''
    reference = 'Test.Notebook.EnvironmentObject.Variable'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=environment_define_code
    )
    
    self.tic()
    self.assertEquals(json.loads(result)['status'], 'ok')
    
    jupyter_code = 'print x'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    
    self.tic()
    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), 'couscous')
    
  def testEnvironmentUndefineFunctionClass(self):
    self.login('dev_user')
    environment_define_code = '''
def create_sum_machines():
  def sum_function(x, y):
    return x + y
    
  class Calculator(object):
  
    def sum(self, x, y):
      return x + y
    
  return {'sum_function': sum_function, 'Calculator': Calculator}

environment.clearAll()
environment.define(create_sum_machines, 'creates sum function and class')
'''
    reference = 'Test.Notebook.EnvironmentObject.Function.Undefine'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=environment_define_code
    )
    
    self.tic()
    self.assertEquals(json.loads(result)['status'], 'ok')
    
    undefine_code = '''
environment.undefine('creates sum function and class')
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=undefine_code
    )
    
    self.tic()
    self.assertEquals(json.loads(result)['status'], 'ok')
    
    jupyter_code = '''
print 'sum_function' in locals()
print 'Calculator' in locals()
'''

    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    result = json.loads(result)
    output = result['code_result']
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(output.strip(), 'False\nFalse')
    
  def testEnvironmentUndefineVariable(self):
    self.login('dev_user')
    environment_define_code = '''
environment.clearAll()
environment.define(x='couscous')
'''
    reference = 'Test.Notebook.EnvironmentObject.Variable.Undefine'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=environment_define_code
    )
    
    self.tic()
    self.assertEquals(json.loads(result)['status'], 'ok')
    
    undefine_code = 'environment.undefine("x")'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=undefine_code
    )
    
    self.tic()
    self.assertEquals(json.loads(result)['status'], 'ok')
    
    jupyter_code = "print 'x' in locals()"
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    
    self.tic()
    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), 'False')
    
  def testImportFixer(self):
    self.login('dev_user')
    import_code = '''
import random
'''

    reference = 'Test.Notebook.EnvironmentObject.ImportFixer'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=import_code
    )
    
    self.tic()
    self.assertEquals(json.loads(result)['status'], 'ok')
    
    jupyter_code = '''
print random.randint(1,1)
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    
    self.tic()
    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), '1')
    
  def testEnvorinmentUndefineErrors(self):
    """
      Tests if environment.undefine wrong usage errors are correctly captured 
      and rendered in Jupyter.
    """
    self.login('dev_user')
    undefine_not_found = 'environment.undefine("foobar")' 
    
    reference = 'Test.Notebook.EnvironmentObject.Errors.Undefine'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=undefine_not_found
    )
    self.tic()
    
    error_substring = 'EnvironmentUndefineError: Trying to remove non existing'
    self.assertTrue(error_substring in result)
    
    not_string_code = 'def foobar(): pass\nenvironment.undefine(foobar)'
    
    reference = 'Test.Notebook.EnvironmentObject.Errors.Undefine'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=not_string_code
    )
    self.tic()
    
    error_substring = 'EnvironmentUndefineError: Type mismatch.'
    self.assertTrue(error_substring in result)
    
  def testEnvironmentDefineErrrors(self):
    """
      Tests if environment.define wrong usage errors are correctly captured 
      and rendered in Jupyter.
    """
    self.login('dev_user')
    
    first_arg_type_code = "environment.define('foobar', 'foobar')" 
    
    reference = 'Test.Notebook.EnvironmentObject.Errors.Define'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=first_arg_type_code
    )
    self.tic()
    
    error_substring = 'EnvironmentDefinitionError: Type mismatch'
    self.assertTrue(error_substring in result)
    self.assertTrue('first argument' in result)
    
    second_arg_type_code = 'def couscous(): pass\nenvironment.define(couscous, 123)'
    
    reference = 'Test.Notebook.EnvironmentObject.Errors.Define'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=second_arg_type_code
    )
    self.tic()
    
    error_substring = 'EnvironmentDefinitionError: Type mismatch'
    self.assertTrue(error_substring in result)
    self.assertTrue('second argument' in result)
    
  def testImportFixerWithAlias(self):
    self.login('dev_user')
    import_code = '''
import random as rand
'''

    reference = 'Test.Notebook.EnvironmentObject.ImportFixer'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=import_code
    )
    
    self.tic()
    self.assertEquals(json.loads(result)['status'], 'ok')
    
    jupyter_code = '''
print rand.randint(1,1)
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    
    self.tic()
    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), '1')  

  def testPivotTableJsIntegration(self):
    '''
      This test ensures the PivotTableJs user interface is correctly integrated
      into our Jupyter kernel.
    '''
    portal = self.portal
    self.login('dev_user')
    jupyter_code = '''
class DataFrameMock(object):
    def to_csv(self):
        return "column1, column2; 1, 2;" 

my_df = DataFrameMock()
iframe = context.Base_erp5PivotTableUI(my_df)
context.Base_renderAsHtml(iframe)
'''
    reference = 'Test.Notebook.PivotTableJsIntegration %s' % time.time()
    notebook = self._newNotebook(reference=reference)
    result = portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    json_result = json.loads(result)
    
    # The big hash in this string was previous calculated using the expect hash
    # of the pivot table page's html.
    pivottable_frame_display_path = 'Base_displayPivotTableFrame?key=853524757258b19805d13beb8c6bd284a7af4a974a96a3e5a4847885df069a74d3c8c1843f2bcc4d4bb3c7089194b57c90c14fe8dd0c776d84ce0868e19ac411'
    
    self.assertTrue(pivottable_frame_display_path in json_result['code_result'])

  def testConsecutiveImports(self):
    '''
      This test guarantees that importing a module's variables consecutively in
      Jupyter works.
    '''
    self.login('dev_user')
    import_code = '''
from string import ascii_lowercase, ascii_uppercase, digits
'''
    reference = 'Test.Notebook.EnvironmentObject.Errors.Import'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=import_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')

    jupyter_code = '''
print ascii_lowercase
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), 'abcdefghijklmnopqrstuvwxyz')

    jupyter_code = '''
print ascii_uppercase
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    jupyter_code = '''
print digits
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), '0123456789')

  def testStarImport(self):
    '''
      This test guarantees that "from x import *" works in Jupyter.
    '''
    self.login('dev_user')
    import_code = '''
from string import *
'''
    reference = 'Test.Notebook.EnvironmentObject.Errors.Import'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=import_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')

    jupyter_code = '''
print ascii_lowercase
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), 'abcdefghijklmnopqrstuvwxyz')

  def testAsImport(self):
    '''
      This test guarantees that "from x import a as b" works in Jupyter.
    '''
    self.login('dev_user')
    import_code = '''
from string import digits as dig
'''
    reference = 'Test.Notebook.EnvironmentObject.Errors.Import'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=import_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')

    jupyter_code = '''
print dig
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), '0123456789')
    
  def testReferenceWarning(self):
    '''
      Tests Base_checkExistingReference in JupyterCompile.
    '''
    self.login('dev_user')
    
    notebook_reference = u''.join(random.choice(string.ascii_lowercase) for _ in range(30))
    notebook_title = u''.join(random.choice(string.ascii_lowercase) for _ in range(30))
    
    notebook_module = self.portal.getDefaultModule(portal_type='Data Notebook')
    data_notebook = notebook_module.DataNotebookModule_addDataNotebook(
                                      title=notebook_title,
                                      reference=notebook_reference,
                                      batch_mode=True)
    self.tic()
        
    result = self.portal.Base_checkExistingReference(
      reference=notebook_reference,
    )
    self.tic()

    self.assertEquals(result, True)

  def testNPArrayPrint(self):
    self.login('dev_user')
    import_code = '''
import numpy as np
'''
    reference = 'Test.Notebook.EnvironmentObject.Errors.NPArrayTest'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=import_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    jupyter_code = '''
print np.random.rand(256, 256, 256)
'''

    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')

    jupyter_code = '''
print np.random.randint(low = 2 ** 63 - 1, size = (256, 256, 256), dtype = 'int64')
'''

    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')

  def testImportWarning(self):
    '''
      This test checks the warning output for imports in Jupyter.
    '''
    self.login('dev_user')
    import_code = '''
import numpy as np
import matplotlib.pyplot as plt
import datetime
'''
    reference = 'Test.Notebook.EnvironmentObject.Errors.Import'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=import_code
    )
    self.tic()
    
    expected_result = (u'WARNING: You imported from the modules numpy'
                       u', matplotlib.pyplot, datetime without using the environment'
                       u' object, which is not recomended. Your import was'
                       u' automatically converted to use such method. The setup'
                       u' functions were named as *module*_setup.')

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), expected_result)

    jupyter_code = '''
print np.array([1, 2, 3])
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()
    
    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')
    self.assertEquals(result['code_result'].strip(), u'[1 2 3]')
    
  def testDotImport(self):
    '''
      This test guarantees that "import modulea.moduleb" works in Jupyter.
    '''
    self.login('dev_user')
    import_code = '''
import os.path
'''
    reference = 'Test.Notebook.EnvironmentObject.Errors.DotImport'
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=import_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')

    jupyter_code = '''
print os.path
'''
    result = self.portal.Base_executeJupyter(
      reference=reference,
      python_expression=jupyter_code
    )
    self.tic()

    result = json.loads(result)
    self.assertEquals(result['status'], 'ok')

  def checkEgg(self, egg):
    '''
      Returns whether an egg is available.
    '''

    reference = 'Test.Notebook.EnvironmentObject.Errors.EggImport'

    try:
      result = self.portal.Base_executeJupyter(
        reference=reference,
        python_expression='import %s as _' % egg
      )
    except Exception:
      result = json.dumps(dict(status='error'))
    self.tic()

    result = json.loads(result)

    return result['status'] == 'ok'

  def testEggs(self):
    '''
      Test whether essential modules are available.
    '''
    self.login('dev_user')

    egg_list = [
      'datetime',
      'h5py',
      'math',
      'matplotlib',
      'openpyxl',
      'pandas',
      'pylab',
      'scipy',
      'sklearn',
      'statsmodels',
      'sympy',
    ]
    imported_egg_list = [egg for egg in egg_list if self.checkEgg(egg)]
    self.assertEqual(set(egg_list), set(imported_egg_list))

  def testERP5hasAccessToERP5Kernel(self):
    '''
      Test whether the erp5 specific jupyter kernel is accessible from within erp5.
    '''
    try:
      jupyter_client.kernelspec.KernelSpecManager().get_kernel_spec('erp5')
    except jupyter_client.kernelspec.NoSuchKernel:
      has_access_to_erp5_kernel = False
    else:
      has_access_to_erp5_kernel = True
    self.assertTrue(has_access_to_erp5_kernel)