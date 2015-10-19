# -*- coding: utf-8 -*-

from StringIO import StringIO
from Products.ERP5Type.Globals import  PersistentMapping

import sys
import ast

def Base_compileJupyterCode(self, jupyter_code, old_local_variable_dict):
  """
    Function to execute jupyter code and update the local_varibale dictionary.
    Code execution depends on 'interactivity', a.k.a , if the ast.node object has
    ast.Expr instance(valid for expressions) or not.

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
  g.update(old_local_variable_dict)

  # IPython expects 2 status message - 'ok', 'error'
  # XXX: The focus is on 'ok' status only, we're letting errors to be raised on
  # erp5 for now, so as not to hinder the transactions while catching them.
  # TODO: This can be refactored by using client side error handling instead of
  # catching errors on server/erp5.
  status = u'ok'

  # Execute only if jupyter_code is not empty
  if jupyter_code:
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
  local_variable_dict.update(local_variable_dict_new)

  result = {
    'result_string': result_string,
    'local_variable_dict': local_variable_dict,
    'status': status,
    'evalue': evalue,
    'ename': ename,
    'traceback': tb_list,
  }
  return result

def AddPersistentMapping(self):
  """
  Function to add PersistentMapping object which can be used as a dictionary
  """
  new_dict = PersistentMapping()
  return new_dict

def UpdatePersistentMapping(self, existing_dict):
  """
  Function to update PersistentMapping object
  """
  new_dict = PersistentMapping()
  for key, value in existing_dict.iteritems():
    new_dict[key]=value
  return new_dict
