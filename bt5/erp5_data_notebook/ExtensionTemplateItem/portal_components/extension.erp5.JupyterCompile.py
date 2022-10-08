# -*- coding: utf-8 -*-
from matplotlib.figure import Figure
from IPython.core.display import DisplayObject
from IPython.lib.display import IFrame
from six.moves import cStringIO as StringIO
from erp5.portal_type import Image
from types import ModuleType
from ZODB.serialize import ObjectWriter
import six.moves.cPickle
import sys
import traceback
import ast
import base64
import json
import transaction
import Acquisition
import astor
import importlib
from erp5.component.module.Log import log
from Products.ERP5Type.Utils import ensure_list

# Display matplotlib figure automatically like
# the original python kernel
import matplotlib
import matplotlib.pyplot as plt
from IPython.core.pylabtools import print_figure
from IPython.core.display import _pngxy
from ipykernel.jsonutil import json_clean, encode_images
import threading
display_data_wrapper_lock = threading.Lock()

# Well known unserializable types
from Record import Record
well_known_unserializable_type_tuple = (ModuleType, Record)
# ZBigArray may not be available
try:
  from wendelin.bigarray.array_zodb import ZBigArray
  # FIXME ZBigArrays are regular ZODB objects and must be serializable
  # FIXME the bug is probably in CanSerialize()
  # FIXME -> see https://lab.nexedi.com/nexedi/erp5/commit/5fb16acd#note_33582 for details
  well_known_unserializable_type_tuple = tuple(list(well_known_unserializable_type_tuple) + [ZBigArray])
except ImportError:
  pass

def Base_executeJupyter(self, python_expression=None, reference=None, \
                        title=None, request_reference=False, **kw):
  # Check if implementation is enabled
  if not self.getPortalObject().ERP5Site_isDataNotebookEnabled():
    return "The synchronous and unrestricted implementation is not enabled on the server"
  # Check permissions for current user and display message to non-authorized user
  if not self.Base_checkPermission('portal_components', 'Manage Portal'):
    return "You are not authorized to access the script"

  # Convert the request_reference argument string to their respeced boolean values
  request_reference = {'True': True, \
                       'False': False}.get(request_reference, False)

  # Return python dictionary with title and reference of all notebooks
  # for request_reference=True
  if request_reference:
    data_notebook_list = self.portal_catalog(portal_type='Data Notebook')
    notebook_detail_list = [{'reference': obj.getReference(), \
                             'title': obj.getTitle()} for obj in data_notebook_list]
    return notebook_detail_list

  if not reference:
    message = "Please set or use reference for the notebook you want to use"
    return message

  # Take python_expression as '' for empty code from jupyter frontend
  if not python_expression:
    python_expression = ''

  # Get Data Notebook with the specific reference
  data_notebook = self.portal_catalog.getResultValue(
                         portal_type='Data Notebook',
                         reference=reference)

  # Create new Data Notebook if reference doesn't match with any from existing ones
  if not data_notebook:
    notebook_module = self.getDefaultModule(portal_type='Data Notebook')
    data_notebook = notebook_module.DataNotebookModule_addDataNotebook(
                                      title=title,
                                      reference=reference,
                                      batch_mode=True)

  # By default, store_history is True
  store_history = kw.get('store_history', True)
  data_notebook_line = None
  if store_history:
    # Add new Data Notebook Line to the Data Notebook
    data_notebook_line = data_notebook.DataNotebook_addDataNotebookLine(
                                       notebook_code=python_expression,
                                       batch_mode=True)

  # Gets the context associated to the data notebook being used
  old_notebook_context = data_notebook.getNotebookContext()
  if not old_notebook_context:
    old_notebook_context = self.Base_createNotebookContext()

  # Pass all to code Base_runJupyter external function which would execute the code
  # and returns a dict of result
  final_result = displayDataWrapper(lambda:Base_runJupyterCode(self, python_expression, old_notebook_context))

  new_notebook_context = final_result['notebook_context']

  result = {
    u'code_result': final_result['result_string'],
    u'print_result': final_result['print_result'],
    u'displayhook_result': final_result['displayhook_result'],
    u'ename': final_result['ename'],
    u'evalue': final_result['evalue'],
    u'traceback': final_result['traceback'],
    u'status': final_result['status'],
    u'mime_type': final_result['mime_type'],
    u'extra_data_list': final_result['extra_data_list'],
  }

  # Updates the context in the notebook with the resulting context of code
  # execution.
  data_notebook.setNotebookContext(new_notebook_context)

  # We try to commit, but the notebook context property may have variables that
  # cannot be serialized into the ZODB and couldn't be captured by our code yet.
  # In this case we abort the transaction and warn the user about it. Unforunately,
  # the exeception raised when this happens doesn't help to know exactly which
  # object caused the problem, so we cannot tell the user what to fix.
  try:
    transaction.commit()
  except transaction.interfaces.TransactionError as e:
    transaction.abort()
    exception_dict = getErrorMessageForException(self, e, new_notebook_context)
    result.update(exception_dict)
    return json.dumps(result)

  # Catch exception while seriaizing the result to be passed to jupyter frontend
  # and in case of error put code_result as None and status as 'error' which would
  # be shown by Jupyter frontend
  try:
    serialized_result = json.dumps(result)
  except UnicodeDecodeError:
    result = {
      u'code_result': None,
      u'print_result': None,
      u'displayhook_result': None,
      u'ename': u'UnicodeDecodeError',
      u'evalue': None,
      u'traceback': None,
      u'status': u'error',
      u'mime_type': result['mime_type']}
    serialized_result = json.dumps(result)

  if data_notebook_line is not None:
    data_notebook_line.edit(
      notebook_code_result = result['code_result'],
      mime_type = result['mime_type'])

  return serialized_result


def mergeTracebackListIntoResultDict(result_dict, error_result_dict_list):
  if error_result_dict_list:
    if result_dict['traceback'] is None:
      result_dict['traceback'] = []
    for error_result_dict in error_result_dict_list:
      result_dict['traceback'].append(error_result_dict['traceback'])
      result_dict['status'] = error_result_dict['status']
  return result_dict


def matplotlib_pre_run():
  matplotlib.interactive(False)
  rc = {'figure.figsize': (6.0,4.0),
        'figure.facecolor': (1,1,1,0),
        'figure.edgecolor': (1,1,1,0),
        'font.size': 10,
        'figure.dpi': 72,
        'figure.subplot.bottom' : .125
        }
  for key, value in rc.items():
    matplotlib.rcParams[key] = value
  plt.gcf().clear()

def matplotlib_post_run(data_list):
  png_data = None
  figure = plt.gcf()
  # Always try to get the current figure.
  # This is not efficient, but we can support any libraries
  # that use matplotlib.
  png_data = print_figure(figure, fmt='png')
  figure.clear()
  if png_data is not None:
    width, height = _pngxy(png_data)
    data = encode_images({'image/png':png_data})
    metadata = {'image/png':dict(width=width, height=height)}
    data_list.append(json_clean(dict(data=data, metadata=metadata)))

class Displayhook(object):
  def hook(self, value):
    if value is not None:
      if getattr(value, '_repr_html_', None) is not None:
        self.result = {'data':{'text/html':value._repr_html_()}, 'metadata':{}}
      else:
        self.result = repr(value)
  def pre_run(self):
    self.old_hook = sys.displayhook
    sys.displayhook = self.hook
    self.result = None
  def post_run(self):
    sys.displayhook = self.old_hook
displayhook = Displayhook()

def displayDataWrapper(function):
  with display_data_wrapper_lock:
    # pre run
    displayhook.pre_run()
    matplotlib_pre_run()
    extra_data_list = []
    try:
      result = function()
      extra_data_list = result.get('extra_data_list', [])
    finally:
      # post run
      displayhook.post_run()
      matplotlib_post_run(extra_data_list)
  result['extra_data_list'] = extra_data_list
  return result

def Base_runJupyterCode(self, jupyter_code, old_notebook_context):
  """
    Function to execute jupyter code and update the context dictionary.
    Code execution depends on 'interactivity', a.k.a , if the ast.node object has
    ast.Expr instance (valid for expressions) or not.

    old_notebook_context should contain both variables dict and setup functions.
    Here, setup dict is {key: value} pair of setup function names and another dict,
    which contains the function's alias and code, as string. These functions
    should be executed before `jupyter_code` to properly create the required
    environment.

    For example:
    old_notebook_context =  {
      'setup': {
        'numpy setup': {
          'func_name': 'numpy_setup_function',
          'code': ...
        }
      },
      'variables': {
        'my_variable': 1
      }
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
  mime_type = 'text/plain'
  status = u'ok'
  ename, evalue, tb_list = None, None, None

  # Other way would be to use all the globals variables instead of just an empty
  # dictionary, but that might hamper the speed of exec or eval.
  # Something like -- user_context = globals(); user_context['context'] = self;
  user_context = {}
  output = ''

  # Saving the initial globals dict so as to compare it after code execution
  globals_dict = globals()
  notebook_context = old_notebook_context

  inject_variable_dict = {}
  current_var_dict = {}
  current_setup_dict = {}
  setup_error_return_dict_list = []

  # Execute only if jupyter_code is not empty
  if jupyter_code:
    # Create ast parse tree
    try:
      ast_node = ast.parse(jupyter_code)
    except Exception as e:
      # It's not necessary to abort the current transaction here 'cause the
      # user's code wasn't executed at all yet.
      return getErrorMessageForException(self, e, notebook_context)

    # Fixing "normal" imports and detecting environment object usage
    import_fixer = ImportFixer()
    print_fixer = PrintFixer()
    environment_collector = EnvironmentParser()
    ast_node = import_fixer.visit(ast_node)

    # Whenever we have new imports we need to warn the user about the
    # environment
    if (import_fixer.warning_module_names != []):
      warning = ("print ('"
                 "WARNING: You imported from the modules %s without "
                 "using the environment object, which is not recomended. "
                 "Your import was automatically converted to use such method. "
                 "The setup functions were named as *module*_setup. "
                 "')") % (', '.join(import_fixer.warning_module_names))
      tree = ast.parse(warning)
      tree.body[0].lineno = ast_node.body[-1].lineno+5
      ast_node.body.append(tree.body[0])

    ast_node = print_fixer.visit(ast_node)
    ast.fix_missing_locations(ast_node)

    # The collector also raises errors when environment.define and undefine
    # calls are made incorrectly, so we need to capture them to propagate
    # to Jupyter for rendering.
    try:
      ast_node = environment_collector.visit(ast_node)
    except (EnvironmentDefinitionError, EnvironmentUndefineError) as e:
      transaction.abort()
      return getErrorMessageForException(self, e, notebook_context)

    # Get the node list from the parsed tree
    nodelist = ast_node.body

    # Handle case for empty nodelist(in case of comments as jupyter_code)
    if nodelist:
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

      # Variables used at the display hook to get the proper form to display
      # the last returning variable of any code cell.
      display_data = {'result': '',
                      'mime_type': None}

      # This is where one part of the  display magic happens. We create an
      # instance of ProcessorList and add each of the built-in processors.
      # The classes which each of them are responsiblefor rendering are defined
      # in the classes themselves.
      # The customized display hook will automatically use the processor
      # of the matching class to decide how the object should be displayed.
      processor_list = ProcessorList()
      processor_list.addProcessor(IPythonDisplayObjectProcessor)
      processor_list.addProcessor(MatplotlibFigureProcessor)
      processor_list.addProcessor(ERP5ImageProcessor)
      processor_list.addProcessor(IPythonDisplayObjectProcessor)

      # Putting necessary variables in the `exec` calls context and storing
      inject_variable_dict = {
        'context': self,
        'environment': Environment(),
        '_display_data': display_data,
        '_processor_list': processor_list,
        '_volatile_variable_list': [],
        '_print': CustomPrint()}
      user_context.update(inject_variable_dict)
      user_context.update(notebook_context['variables'])

      # Getting the environment setup defined in the current code cell
      current_setup_dict = environment_collector.getEnvironmentSetupDict()
      current_var_dict = environment_collector.getEnvironmentVarDict()

      # Removing old setup from the setup functions
      removed_setup_message_list = []
      for func_alias in environment_collector.getEnvironmentRemoveList():
        found = False
        for key, data in notebook_context['setup'].items():
          if key == func_alias:
            found = True
            func_name = data['func_name']
            del notebook_context['setup'][func_alias]
            try:
              del user_context[func_alias]
            except KeyError:
              pass
            removed_setup_message = (
              "%s (%s) was removed from the setup list. "
              "Variables it may have added to the context and are not pickleable "
              "were automatically removed.\n"
            ) % (func_name, func_alias)
            removed_setup_message_list.append(removed_setup_message)
            break
        if not found:
          transaction.abort()
          result = {
            'result_string': "EnvironmentUndefineError: Trying to remove non existing function/variable from environment: '%s'\n" % func_alias,
            'print_result': {"data":{"text/plain":"EnvironmentUndefineError: Trying to remove non existing function/variable from environment: '%s'\n" % func_alias}, "metadata":{}},
            'displayhook_result': None,
            'notebook_context': notebook_context,
            'status': 'ok',
            'mime_type': 'text/plain',
            'evalue': None,
            'ename': None,
            'traceback': None}
          return result

      # Removing all the setup functions if user call environment.clearAll()
      if environment_collector.clearAll():
        keys = notebook_context ['setup'].keys()
        for key in keys:
          del notebook_context['setup'][key]

      # Running all the setup functions that we got
      failed_setup_key_list = []
      for key, value in notebook_context['setup'].iteritems():
        try:
          code = compile(value['code'], '<string>', 'exec')
          exec(code, user_context, user_context)
        # An error happened, so we show the user the stacktrace along with a
        # note that the exception happened in a setup function's code.
        except Exception as e:
          failed_setup_key_list.append(key)
          if value['func_name'] in user_context:
            del user_context[value['func_name']]
          error_return_dict = getErrorMessageForException(self, e, notebook_context)
          additional_information = "An error happened when trying to run the one of your setup functions:"
          error_return_dict['traceback'].insert(0, additional_information)
          setup_error_return_dict_list.append(error_return_dict)
      for failed_setup_key in failed_setup_key_list:
        del notebook_context['setup'][failed_setup_key]

      # Iterating over envinronment.define calls captured by the environment collector
      # that are functions and saving them as setup functions.
      for func_name, data in current_setup_dict.iteritems():
        setup_string = (
          "%s\n"
          "_result = %s()\n"
          "if _result and isinstance(_result, dict):\n"
          "    globals().update(_result)\n"
          "_volatile_variable_list += _result.keys()\n"
          "del %s, _result\n"
        ) % (data['code'], func_name, func_name)
        notebook_context['setup'][data['alias']] = {
          "func_name": func_name,
          "code": setup_string}

      # Iterating over envinronment.define calls captured by the environment collector
      # that are simple variables and saving them in the setup.
      for variable, value, in current_var_dict.iteritems():
        setup_string = "%s = %s\n" % (variable, repr(value))
        notebook_context['setup'][variable] = {
          'func_name': variable,
          'code': setup_string}
        user_context['_volatile_variable_list'] += variable

      if environment_collector.showEnvironmentSetup():
        inject_variable_dict['_print'].write("%s\n" % str(notebook_context['setup']))

      # Execute the nodes with 'exec' mode
      for node in to_run_exec:
        mod = ast.Module([node])
        code = compile(mod, '<string>', "exec")
        try:
          exec(code, user_context, user_context)
        except Exception as e:
          # Abort the current transaction. As a consequence, the notebook lines
          # are not added if an exception occurs.
          transaction.abort()
          return mergeTracebackListIntoResultDict(getErrorMessageForException(self, e, notebook_context),
                                                  setup_error_return_dict_list)

      # Execute the interactive nodes with 'single' mode
      for node in to_run_interactive:
        mod = ast.Interactive([node])
        try:
          code = compile(mod, '<string>', 'single')
          exec(code, user_context, user_context)
        except Exception as e:
          # Abort the current transaction. As a consequence, the notebook lines
          # are not added if an exception occurs.
          transaction.abort()
          return mergeTracebackListIntoResultDict(getErrorMessageForException(self, e, notebook_context),
                                                  setup_error_return_dict_list)

      mime_type = display_data['mime_type'] or mime_type
      inject_variable_dict['_print'].write("\n".join(removed_setup_message_list) + display_data['result'])

    # Saves a list of all the variables we injected into the user context and
    # shall be deleted before saving the context.
    volatile_variable_list = ensure_list(current_setup_dict.keys()) + ensure_list(inject_variable_dict.keys()) + user_context.get('_volatile_variable_list', [])
    volatile_variable_list.append('__builtins__')

    for key, val in user_context.items():
      if not key in globals_dict.keys() and not isinstance(val, well_known_unserializable_type_tuple) and not key in volatile_variable_list:
        if canSerialize(val):
          notebook_context['variables'][key] = val
        else:
          del user_context[key]
          message = (
            "Cannot serialize the variable named %s whose value is %s, "
            "thus it will not be stored in the context. "
            "You should move it's definition to a function and "
            "use the environment object to load it.\n"
          ) % (key, val)
          inject_variable_dict['_print'].write(message)

    # Deleting from the variable storage the keys that are not in the user
    # context anymore (i.e., variables that are deleted by the user).
    for key in notebook_context['variables'].keys():
      if not key in user_context:
        del notebook_context['variables'][key]

    if inject_variable_dict.get('_print') is not None:
      output = inject_variable_dict['_print'].getCapturedOutputString()

  displayhook_result = {"data":{}, "metadata":{}}
  if displayhook.result is not None:
    if isinstance(displayhook.result, str):
      displayhook_result["data"]["text/plain"] = displayhook.result
    elif isinstance(displayhook.result, dict):
      displayhook_result = displayhook.result
  result = {
    'result_string': output,
    'print_result': {"data":{"text/plain":output}, "metadata":{}},
    'displayhook_result': displayhook_result,
    'notebook_context': notebook_context,
    'status': status,
    'mime_type': mime_type,
    'evalue': evalue,
    'ename': ename,
    'traceback': tb_list}
  return mergeTracebackListIntoResultDict(result, setup_error_return_dict_list)


class EnvironmentUndefineError(TypeError):
  pass


class EnvironmentDefinitionError(TypeError):
  pass


def canSerialize(obj):

  container_type_tuple = (list, tuple, dict, set, frozenset)

  # if object is a container, we need to check its elements for presence of
  # objects that cannot be put inside the zodb
  if isinstance(obj, container_type_tuple):
    if isinstance(obj, dict):
      result_list = []
      for key, value in obj.iteritems():
        result_list.append(canSerialize(key))
        result_list.append(canSerialize(value))
    else:
      result_list = [canSerialize(element) for element in obj]
    return all(result_list)
  # if obj is an object and implements __getstate__, ZODB.serialize can check
  # if we can store it
  elif isinstance(obj, object) and hasattr(obj, '__getstate__') and hasattr(obj, '_p_jar'):
    # Need to unwrap the variable, otherwise we get a TypeError, because
    # objects cannot be pickled while inside an acquisition wrapper.
    unwrapped_obj = Acquisition.aq_base(obj)
    try:
      writer = ObjectWriter(unwrapped_obj)
    except:
      # Ignore any exceptions, otherwise Jupyter becomes permanent unusble state.
      return False
    for obj in writer:
      try:
        writer.serialize(obj)
      # Because writer.serialize(obj) relies on the implementation of __getstate__
      # of obj, all errors can happen, so the "except all" is necessary here.
      except:
        return False
    return True
  else:
    # If cannot serialize object with ZODB.serialize, try with cPickle
    # Only a dump of the object is not enough. Dumping and trying to
    # load it will properly raise errors in all possible situations,
    # for example: if the user defines a dict with an object of a class
    # that he created the dump will stil work, but the load will fail.
    try:
      six.moves.cPickle.loads(six.moves.cPickle.dumps(obj))
    # By unknowing reasons, trying to catch cPickle.PicklingError in the "normal"
    # way isn't working. This issue might be related to some weirdness in
    # pickle/cPickle that is reported in this issue: http://bugs.python.org/issue1457119.
    #
    # So, as a temporary fix, we're investigating the exception's class name as
    # string to be able to identify them.
    #
    # Even though the issue seems complicated, this quickfix should be
    # properly rewritten in a better way as soon as possible.
    except (six.moves.cPickle.PicklingError, TypeError, NameError, AttributeError):
      return False
    else:
      return True


class CustomPrint(object):

  def __init__(self):
    self.captured_output_list = []

  def write(self, *args):
    self.captured_output_list += args

  def getCapturedOutputString(self):
    return ''.join(self.captured_output_list)


class PrintFixer(ast.NodeTransformer):

  def visit_Print(self, node):
    _print_name_node = ast.Name(id="_print", ctx=ast.Load())
    node.dest = _print_name_node
    return node


class EnvironmentParser(ast.NodeTransformer):
  """
    EnvironmentParser class is an AST transformer that walks in the abstract
    code syntax tree to find calls to `define` and `undefine`  on a variable
    named `environment`.

    The `define` call should receive a function, which will have it's code
    stored as string in `self.environment_setup_dict`. If only kw args are
    provided, the variables definition will be stored in self.environment_var_dict.

    The `undefine` call will removed keys in self.environment_setup_dict.
  """

  def __init__(self):
    self.environment_setup_dict = {}
    self.environment_var_dict = {}
    self.environment_remove_list = []
    self.function_dict = {}
    self.environment_clear_all = False
    self.show_environment_setup = False

  def visit_FunctionDef(self, node):
    """
      Stores all the function nodes in a dictionary to be accesed later when
      we detect they are used as parameters for an `environment.define` call.
    """
    self.function_dict[node.name] = node
    return node

  def visit_Expr(self, node):
    """
      Visits expressions and check if they are in the form of either
      `environment.define` or `environment.undefine` properly stores the
      arguments definition as string.
    """
    value = node.value
    if isinstance(value, ast.Call):
      function = value.func
      if isinstance(function, ast.Attribute):
        attribute = function.value
        if isinstance(attribute, ast.Name):
          name = attribute.id
          if name == 'environment' and function.attr == 'define' and not value.keywords:
            if not len(value.args) == 2:
              raise EnvironmentDefinitionError('environment.define calls receive 2 arguments')

            self._ensureType(
              obj=value.args[0],
              klass=ast.Name,
              error_message='Type mismatch. environment.define receives a function as first argument.'
            )

            self._ensureType(
              obj=value.args[1],
              klass=ast.Str,
              error_message='Type mismatch. environment.define receives a string as second argument.'
            )

            func_name = value.args[0].id
            func_alias = value.args[1].s
            function_node = self.function_dict[func_name]
            function_string = astor.to_source(function_node)
            self.environment_setup_dict[func_name] = {
              "code": function_string,
              "alias": func_alias
            }
          elif name == 'environment' and function.attr == 'define' and value.keywords:
            for keyword in value.keywords:
              arg_name = keyword.arg
              arg_value_node = keyword.value

              # The value can be a number, string or name. We need to handle
              # them separatedly. This dict trick was used to avoid the very
              # ugly if.
              node_value_dict = {
                ast.Num: lambda node: str(node.n),
                ast.Str: lambda node: node.s,
                ast.Name: lambda node: node.id
              }
              arg_value = node_value_dict[type(arg_value_node)](arg_value_node)
              self.environment_var_dict[arg_name] = arg_value
          elif name == 'environment' and function.attr == 'undefine':
            self._ensureType(
              obj=value.args[0],
              klass=ast.Str,
              call_type='undefine',
              error_message='Type mismatch. environment.undefine receives only a string as argument.'
            )

            func_alias = value.args[0].s
            self.environment_remove_list.append(func_alias)
          elif name == 'environment' and function.attr == 'clearAll':
            self.environment_clear_all = True
          elif name == 'environment'and function.attr == 'showSetup':
            self.show_environment_setup = True
    return node

  def _ensureType(self, obj=None, klass=None, error_message=None, call_type='define'):
    if not isinstance(obj, klass):
      if call_type == 'define':
        error_class = EnvironmentDefinitionError
      elif call_type == 'undefine':
        error_class = EnvironmentUndefineError
      raise error_class(error_message)

  def clearAll(self):
    return self.environment_clear_all

  def showEnvironmentSetup(self):
    return self.show_environment_setup

  def getEnvironmentSetupDict(self):
    return self.environment_setup_dict

  def getEnvironmentVarDict(self):
    return self.environment_var_dict

  def getEnvironmentRemoveList(self):
    return self.environment_remove_list


class Environment(object):
  """
   Dumb object used to receive call on an object named `environment` inside
   user context. These calls will be tracked by the EnvironmentParser calls.
  """

  def define(self, *args, **kwargs):
    pass

  def undefine(self, name):
    pass

  def clearAll(self):
    pass

  def showSetup(self):
    pass


class ImportFixer(ast.NodeTransformer):
  """
   The ImportFixer class is responsivle for fixing "normal" imports that users
   might try to execute.

   It will automatically replace them with the proper usage of the environment
   object using AST manipulation.
  """

  def __init__(self):
    self.import_func_dict = {}
    self.warning_module_names = []

  def visit_FunctionDef(self, node):
    """
      Processes funcion definition nodes. We want to store a list of all the
      import that are inside functions, because they do not affect the outter
      user context, thus do not imply in any un-pickleable variable being added
      there.
    """
    for child in node.body:
      if isinstance(child, ast.Import):
        for alias in child.names:
          if getattr(alias, 'asname'):
            import_name = alias.asname
          else:
            import_name = alias.name
          self.import_func_dict[import_name] = node.name
    return self.generic_visit(node)

  def visit_ImportFrom(self, node):
    """
     Fixes `import x from y` statements in the same way `import y` is fixed.
    """
    return self.visit_Import(node)

  def visit_Import(self, node):
    """
    This function replaces `normal` imports by creating AST nodes to define
    and environment function which setups the module and return it to be merged
    with the user context.
    """

    test_import_string = None
    result_name = ""
    root_module_name = ""

    module_names = []

    if getattr(node, "module", None) is not None:
      # case when 'from <module_name> import <something>'
      root_module_name = node.module

      if (node.names[0].name == '*'):
        # case when "from <module_name> import *"
        mod = importlib.import_module(node.module)
        tmp_dict = mod.__dict__

        for name in tmp_dict.keys():
          if (name[0] != '_'):
            module_names.append(name)

        test_import_string = "from %s import *" %(node.module)
        result_name = "%s_ALL" %(node.module)
      else:
        # case when "from <module_name> import a as b, c as d, ..."
        original_names = []
        as_names = []

        for name in node.names:
          original_names.append(name.name)
          if getattr(name, "asname", None) is None:
            as_names.append(None)
          else:
            as_names.append(name.asname)

        test_import_string = "from %s import " %(node.module)
        for i in range(0, len(original_names)):
          test_import_string = test_import_string + original_names[i]
          if as_names[i]!=None:
            test_import_string = test_import_string + ' as %s' %(as_names[i])
          test_import_string = test_import_string + ', '
        test_import_string = test_import_string[:-2]

        module_names = []
        for i in range(0, len(original_names)):
          if as_names[i]!=None:
            module_names.append(as_names[i])
          else:
            module_names.append(original_names[i])

        for i in range(0, len(original_names)):
          if as_names[i]!=None:
            result_name = result_name + '%s_' %(as_names[i])
          else:
            result_name = result_name + '%s_' %(original_names[i])
        result_name = result_name[:-1]



    elif getattr(node.names[0], 'asname'):
      # case when "import <module_name> as <name>""
      module_names = [(node.names[0].asname), ]
      test_import_string = "import %s as %s" %(node.names[0].name,
                                               module_names[0])
      result_name = node.names[0].asname
      root_module_name = node.names[0].name

    else:
      # case when "import <module_name>"
      module_names = [(node.names[0].name), ]
      test_import_string = "import %s" %node.names[0].name
      result_name = node.names[0].name
      root_module_name = node.names[0].name

    final_module_names = []
    for name in module_names:
      if not self.import_func_dict.get(name):
        final_module_names.append(name)

    if final_module_names:
      # try to import module before it is added to environment
      # this way if user tries to import non existent module Exception
      # is immediately raised and doesn't block next Jupyter cell execution
      exec(test_import_string)

      dotless_result_name = ""
      for character in result_name:
        if character == '.':
          dotless_result_name = dotless_result_name + '_dot_'
        else:
          dotless_result_name = dotless_result_name + character

      empty_function = self.newEmptyFunction("%s_setup" %dotless_result_name)
      return_dict = self.newReturnDict(final_module_names)

      empty_function.body = [node, return_dict]
      environment_set = self.newEnvironmentSetCall("%s_setup" %dotless_result_name)
      self.newImportWarningCall(root_module_name, dotless_result_name)
      return [empty_function, environment_set]
    else:
      return node

  def newEmptyFunction(self, func_name):
    """
      Return a AST.Function object representing a function with name `func_name`
      and an empty body.
    """
    func_body = "def %s(): pass" % func_name
    return ast.parse(func_body).body[0]

  def newReturnDict(self, module_names):
    """
      Return an AST.Expr representing a returned dict with one single key named
      `'module_name'` (as string) which returns the variable `module_name` (as
      expression).
    """
    return_dict = "return {"
    for name in module_names:
      if name.find('.') != -1:
        base_name = name[:name.find('.')]
      else:
        base_name = name
      return_dict = return_dict + "'%s': %s, " % (base_name, base_name)
    return_dict = return_dict + '}'
    return ast.parse(return_dict).body[0]

  def newEnvironmentSetCall(self, func_name):
    """
      Return an AST.Expr representaion an `environment.define` call receiving
      `func_name` (as an expression) and `'func_name'` (as string).
    """
    code_string = "environment.define(%s, '%s')" % (func_name, func_name)
    tree = ast.parse(code_string)
    return tree.body[0]

  def newImportWarningCall(self, module_name, function_name):
    """
      Adds a new module to the warning to the user about the importing of new
      modules.
    """
    self.warning_module_names.append(module_name)


def renderAsHtml(self, renderable_object):
  '''
    renderAsHtml will render its parameter as HTML by using the matching
    display processor for that class. Some processors can be found in this
    file.
  '''
  # Ugly frame hack to access the processor list defined in the body of the
  # kernel's code, where `exec` is called.
  #
  # At this point the stack should be, from top to the bottom:
  #
  #   5. ExternalMethod Patch call
  #   4. Base_runJupyterCode frame (where we want to change variable)
  #   3. exec call to run the user's code
  #   2. ExternalMethod Patch call through `context.Base_renderAsHtml` in the notebook
  #   1. renderAsHtml frame (where the function is)
  #
  # So sys._getframe(3) is enough to get us up into the frame we want.
  #
  compile_jupyter_frame = sys._getframe(3)
  compile_jupyter_locals = compile_jupyter_frame.f_locals
  processor = compile_jupyter_locals['processor_list'].getProcessorFor(renderable_object)
  result, _ = processor(renderable_object).process()
  compile_jupyter_locals['inject_variable_dict']['_print'].write(result)
  compile_jupyter_locals['display_data']['mime_type'] = 'text/html'

def getErrorMessageForException(self, exception, notebook_context):
  '''
    getErrorMessageForException receives an Expcetion object and a context for
    code execution (notebook_context) and will return a dict as Jupyter
    requires for error rendering.
  '''
  _, value, _ = sys.exc_info()
  traceback_text = traceback.format_exc().split('\n')[:-1]
  return {
    'status': 'error',
    'result_string': None,
    'print_result': None,
    'displayhook_result': None,
    'notebook_context': notebook_context,
    'mime_type': 'text/plain',
    'evalue': str(value),
    'ename': exception.__class__.__name__,
    'traceback': traceback_text
  }

def createNotebookContext(self):
  """
  Function to create an empty notebook context.
  """
  return {'variables': {}, 'setup': {}}

class ObjectProcessor(object):
  '''
    Basic object processor that stores the first parameters of the constructor
    in the `subject` attribute and store the target classes for that processor.
  '''
  TARGET_CLASSES=None
  TARGET_MODULES=None

  @classmethod
  def getTargetClasses(cls):
    return cls.TARGET_CLASSES

  @classmethod
  def getTargetModules(cls):
    return cls.TARGET_MODULES

  def __init__(self, something):
    self.subject = something

class MatplotlibFigureProcessor(ObjectProcessor):
  '''
    MatplotlibFigureProcessor handles the rich display of
    matplotlib.figure.Figure objects. It displays them using an img tag with
    the inline png image encoded as base64.
  '''
  TARGET_CLASSES=[Figure,]
  TARGET_MODULES=['matplotlib.pyplot',]

  def process(self):
    image_io = StringIO()
    self.subject.savefig(image_io, format='png')
    image_io.seek(0)
    return self._getImageHtml(image_io), 'text/html'

  def _getImageHtml(self, image_io):
    return '<img src="data:image/png;base64,%s" /><br />' % base64.b64encode(image_io.getvalue())

class ERP5ImageProcessor(ObjectProcessor):
  '''
   ERP5ImageProcessor handles the rich display of ERP5's image_module object.
   It gets the image data and content type and use them to create a proper img
   tag.
  '''
  TARGET_CLASSES=[Image,]

  def process(self):
    from base64 import b64encode
    figure_data = b64encode(self.subject.getData())
    mime_type = self.subject.getContentType()
    return '<img src="data:%s;base64,%s" /><br />' % (mime_type, figure_data), 'text/html'

class IPythonDisplayObjectProcessor(ObjectProcessor):
  '''
    IPythonDisplayObjectProcessor handles the display of all objects from the
    IPython.display module, including: Audio, IFrame, YouTubeVideo, VimeoVideo,
    ScribdDocument, FileLink, and FileLinks.

    All these objects have the `_repr_html_` method, which is used by the class
    to render them.
  '''
  TARGET_CLASSES=[DisplayObject, IFrame]

  def process(self):
    html_repr = self.subject._repr_html_()
    return html_repr + '<br />', 'text/html'

class GenericProcessor(ObjectProcessor):
  '''
    Generic processor to render objects as string.
  '''

  def process(self):
    return str(self.subject), 'text/plain'

class ProcessorList(object):
  '''
    ProcessorList is responsible to store all the processors in a dict using
    the classes they handle as the key. Subclasses of these classes will have
    the same processor of the eigen class. This means that the order of adding
    processors is important, as some classes' processors may be overwritten in
    some situations.

    The `getProcessorFor` method uses `something.__class__' and not
    `type(something)` because using the later onobjects returned by portal
    catalog queries will return an AcquisitionWrapper type instead of the
    object's real class.
  '''

  def __init__(self, default=GenericProcessor):
    self.processors = {}
    self.default_processor = GenericProcessor

  def addProcessor(self, processor):
    classes = processor.getTargetClasses()
    modules = processor.getTargetModules()

    if classes and not len(classes) == 0:
      for klass in classes:
        self.processors[klass] = processor
        for subclass in klass.__subclasses__():
          self.processors[subclass] = processor

    if modules and not len(modules) == 0:
      for module in modules:
        self.processors[module] = processor

  def getProcessorFor(self, something):
    if not isinstance(something, ModuleType):
      return self.processors.get(something.__class__, self.default_processor)
    else:
      return self.processors.get(something.__name__, self.default_processor)


def storeIFrame(self, html, key):
  self.portal_caches.erp5_pivottable_frame_cache.set(key, html)
  return True


# WARNING!
#
# This is a highly experimental PivotTableJs integration which does not follow
# ERP5 Javascrpt standards and it will be refactored to use JIO and RenderJS.
#
def erp5PivotTableUI(self, df):
  from IPython.display import IFrame
  template = """
  <!DOCTYPE html>
  <html>
    <head>
      <title>PivotTable.js</title>

      <!-- external libs from cdnjs -->
      <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.css">
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script>
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery-csv/0.71/jquery.csv-0.71.min.js"></script>
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.10/c3.min.js"></script>

      <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.0.2/pivot.min.css">
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.0.2/pivot.min.js"></script>
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.0.2/d3_renderers.min.js"></script>
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.0.2/c3_renderers.min.js"></script>
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.0.2/export_renderers.min.js"></script>

      <style>
        body {font-family: Verdana;}
        .node {
         border: solid 1px white;
         font: 10px sans-serif;
         line-height: 12px;
         overflow: hidden;
         position: absolute;
         text-indent: 2px;
        }
        .c3-line, .c3-focused {stroke-width: 3px !important;}
        .c3-bar {stroke: white !important; stroke-width: 1;}
        .c3 text { font-size: 12px; color: grey;}
        .tick line {stroke: white;}
        .c3-axis path {stroke: grey;}
        .c3-circle { opacity: 1 !important; }
      </style>
    </head>
    <body>
      <script type="text/javascript">
        $(function(){
          if(window.location != window.parent.location)
            $("<a>", {target:"_blank", href:""})
              .text("[pop out]").prependTo($("body"));

          $("#output").pivotUI(
            $.csv.toArrays($("#output").text()),
            {
              renderers: $.extend(
                $.pivotUtilities.renderers,
                $.pivotUtilities.c3_renderers,
                $.pivotUtilities.d3_renderers,
                $.pivotUtilities.export_renderers
                ),
              hiddenAttributes: [""]
            }
          ).show();
         });
      </script>
      <div id="output" style="display: none;">%s</div>
    </body>
  </html>
  """
  html_string = template % df.to_csv()
  from hashlib import sha512
  key = sha512(html_string).hexdigest()
  storeIFrame(self, html_string, key)
  iframe_host = self.REQUEST['HTTP_X_FORWARDED_HOST'].split(',')[0]
  url = "https://%s/erp5/Base_displayPivotTableFrame?key=%s" % (iframe_host, key)
  return IFrame(src=url, width='100%', height='500')

def Base_checkExistingReference(self, reference):
  existing_notebook = self.portal_catalog.getResultValue(
                         owner=self.portal_membership.getAuthenticatedMember().getUserName(),
                         portal_type='Data Notebook',
                         reference=reference)
  if not existing_notebook is None:
    return True
  return False
