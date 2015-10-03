# -*- coding: utf-8 -*-

from StringIO import StringIO
from IPython.utils import py3compat
from IPython.utils.py3compat import unicode_type
from Products.ERP5Type.Globals import  PersistentMapping

import sys
import traceback

def Base_compileJupyterCode(self, jupyter_code, old_local_variable_dict):
  """
    Function to execute jupyter code and update the local_varibale dictionary.
    It also handles the exception raised, catch them and return them as a python
    dictionary. Use of eval for expressions and exec for statements
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
  # Error would be updated only after the exec throws the error here, in all
  # other cases, status would be 'ok'
  status = u'ok'

  # eval used before exec because exec can handle the error raised by both eval
  # and exec. Example to explain execution :-
  # code        eval_result      eval_error     exec_result       exec_error
  # =======================================================================
  # print 42    None            Syntax Error     42                None
  # 42          42              None             None              None
  # abc         None            Name Error       None              Name Error
  # a=42;print ab None          Syntax Error     None              Name Error
  # From above, it infers that the invalid syntax is being handled by exec only
  try:
    jupyter_compiled = compile(jupyter_code, '<string>', 'eval')
    eval_result = eval(jupyter_compiled, g, g)
    result_string = str(eval_result)
  # Trying to catch everything which results in error from eval
  # It can be just an invalid syntax, invalid expression or some error

  except Exception:
    # Returning the printed statement from exec using sys.stdout
    # Catching the executed output and saving it in a variable
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    try:
      jupyter_compiled = compile(jupyter_code, '<string>', 'exec')
      exec(jupyter_compiled, g, g)
      sys.stdout = old_stdout
      result_string = result.getvalue()

    except Exception:
      etype, evalue, tb = sys.exc_info()
      tb_list = traceback.format_exception(etype, evalue, tb)
      status = u'error'
      ename = unicode_type(etype.__name__)
      evalue = py3compat.safe_unicode(evalue)

      sys.stdout.flush()
      sys.stderr.flush()

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