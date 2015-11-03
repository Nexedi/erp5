# -*- coding: utf-8 -*-

from StringIO import StringIO
from Products.ERP5Type.Globals import  PersistentMapping

import sys
import ast
import types

mime_type = 'text/plain'

def Base_compileJupyterCode(self, jupyter_code, old_local_variable_dict):
  """
    Function to execute jupyter code and update the local_varibale dictionary.
    Code execution depends on 'interactivity', a.k.a , if the ast.node object has
    ast.Expr instance(valid for expressions) or not.
    
    old_local_variable_dict should contain both variables dict and modules imports.
    Here, imports dict is key, value pair of modules and their name in sys.path,
    executed separately everytime before execution of jupyter_code to populate
    sys modules beforehand.

    For example :
    old_local_variable_dict = {
                                'imports': {'numpy': 'np', 'sys': 'sys'},
                                'variables': {'np.split': <function split at 0x7f4e6eb48b90>}
                                }

    The behaviour would be similar to that of jupyter notebook:-
    ( https://github.com/ipython/ipython/blob/master/IPython/core/interactiveshell.py#L2954 )
    Example:

      code1 = '''
      23
      print 23 #Last node not an expression, interactivity = 'last'
      '''
      out1 = '23'

      code2 = '''
      123
      12 #Last node an expression, interactivity = 'none'
      '''
      out2 = '12'

  """
  # Other way would be to use all the globals variables instead of just an empty
  # dictionary, but that might hamper the speed of exec or eval.
  # Something like -- g = globals(); g['context'] = self;
  g = {}

  # Saving the initial globals dict so as to compare it after code execution
  globals_dict = globals()
  g['context'] = self
  result_string = None
  ename, evalue, tb_list = None, None, None
  # Update globals dict and use it while running exec command
  g.update(old_local_variable_dict['variables'])

  # IPython expects 2 status message - 'ok', 'error'
  # XXX: The focus is on 'ok' status only, we're letting errors to be raised on
  # erp5 for now, so as not to hinder the transactions while catching them.
  # TODO: This can be refactored by using client side error handling instead of
  # catching errors on server/erp5.
  status = u'ok'

  # Execute only if jupyter_code is not empty
  if jupyter_code:
    # Import all the modules from local_variable_dict['imports']
    # While any execution, in locals() dict, a module is saved as:
    # code : 'from os import path'
    # {'path': <module 'posixpath'>}
    # So, here we would try to get the name 'posixpath' and import it as 'path'
    for k, v in old_local_variable_dict['imports'].iteritems():
      import_statement_code = 'import %s as %s'%(v, k)
      exec(import_statement_code, g, g)
  
    # Create ast parse tree
    ast_node = ast.parse(jupyter_code)
    # Get the node list from the parsed tree
    nodelist = ast_node.body

    # If the last node is instance of ast.Expr, set its interactivity as 'last'
    # This would be the case if the last node is expression
    if isinstance(nodelist[-1], ast.Expr):
      interactivity = "last"
    else:
      interactivity = "none"

    # Here, we define which nodes to execute with 'single' and which to execute
    # with 'exec' mode.
    if interactivity == 'none':
      to_run_exec, to_run_interactive = nodelist, []
    elif interactivity == 'last':
      to_run_exec, to_run_interactive = nodelist[:-1], nodelist[-1:]

    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result

    # Execute the nodes with 'exec' mode
    for node in to_run_exec:
      mod = ast.Module([node])
      code = compile(mod, '<string>', "exec")
      exec(code, g, g)

    # Execute the interactive nodes with 'single' mode
    for node in to_run_interactive:
      mod = ast.Interactive([node])
      code = compile(mod, '<string>', "single")
      exec(code, g, g)

    # Letting the code fail in case of error while executing the python script/code
    # XXX: Need to be refactored so to acclimitize transactions failure as well as
    # normal python code failure and show it to user on jupyter frontend.
    # Decided to let this fail silently in backend without letting the frontend
    # user know the error so as to let tranasction or its error be handled by ZODB
    # in uniform way instead of just using half transactions.

    sys.stdout = old_stdout
    result_string = result.getvalue()
  else:
    result_string = jupyter_code

  # Difference between the globals variable before and after exec/eval so that
  # we don't have to save unnecessary variables in database which might or might
  # not be picklabale
  local_variable_dict = old_local_variable_dict
  local_variable_dict_new = {key: val for key, val in g.items() if key not in globals_dict.keys()}
  local_variable_dict['variables'].update(local_variable_dict_new)

  # Differentiate 'module' objects from local_variable_dict and save them as
  # string in the dict as {'imports': {'numpy': 'np', 'matplotlib': 'mp']}
  if 'variables' and 'imports' in local_variable_dict:
    for key, val in local_variable_dict['variables'].items():
      # Check if the val in the dict is ModuleType and remove it in case it is
      if isinstance(val, types.ModuleType):
        # Update local_variable_dict['imports'] dictionary with key, value pairs
        # with key corresponding to module name as its imported and value as the
        # module name being stored in sys.path
        # For example : 'np': <numpy module at ...> -- {'np': numpy}
        local_variable_dict['imports'][key] = val.__name__

        # XXX: The next line is mutating the dict, beware in case any reference
        # is made later on to local_variable_dict['variables'] dictionary
        local_variable_dict['variables'].pop(key)

  result = {
    'result_string': result_string,
    'local_variable_dict': local_variable_dict,
    'status': status,
    'mime_type': mime_type,
    'evalue': evalue,
    'ename': ename,
    'traceback': tb_list,
  }

  return result

def AddNewLocalVariableDict(self):
  """
  Function to add a new Local Variable for a Data Notebook
  """
  new_dict = PersistentMapping()
  variable_dict = PersistentMapping()
  module_dict = PersistentMapping()
  new_dict['variables'] = variable_dict
  new_dict['imports'] = module_dict
  return new_dict

def UpdateLocalVariableDict(self, existing_dict):
  """
  Function to update local_varibale_dict for a Data Notebook
  """
  new_dict = self.Base_addLocalVariableDict()
  for key, val in existing_dict['variables'].iteritems():
    new_dict['variables'][key] = val
  for key, val in existing_dict['imports'].iteritems():
    new_dict['imports'][key] = val
  return new_dict

def Base_displayMatplotlibImage(self, plot_object=None):
  """
  External function to display Matplotlib Plot objects to jupyter function.
  
  Parameters
  ----------
  
  plot_object : Any matplotlib object from which we can create a plot.
                Can be <matplotlib.lines.Line2D>, <matplotlib.text.Text>, etc.
  
  Output
  -----
  
  Returns base64 encoded string of the plot on which it has been called.

  """
  if plot_object:
    from io import BytesIO
    import base64

    # Create a ByteFile on the server which would be used to save the plot
    figfile = BytesIO()
    # Save plot as 'png' format in the ByteFile
    plot_object.savefig(figfile, format='png')
    figfile.seek(0)
    # Encode the value in figfile to base64 string so as to serve it jupyter frontend
    figdata_png = base64.b64encode(figfile.getvalue())
    # Chanage global variable 'mime_type' to 'image/png'
    global mime_type
    mime_type = 'image/png'

    return figdata_png
  