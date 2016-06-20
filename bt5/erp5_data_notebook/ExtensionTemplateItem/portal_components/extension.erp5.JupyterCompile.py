# -*- coding: utf-8 -*-

from cStringIO import StringIO
from erp5.portal_type import Image
from types import ModuleType

import sys
import traceback
import ast
import base64
import copy

import transaction
import astor

from matplotlib.figure import Figure
from IPython.core.display import DisplayObject
from IPython.lib.display import IFrame


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
  mime_type = 'text/plain'
  status = u'ok'
  ename, evalue, tb_list = None, None, None
  
  # Other way would be to use all the globals variables instead of just an empty
  # dictionary, but that might hamper the speed of exec or eval.
  # Something like -- user_context = globals(); user_context['context'] = self;
  user_context = {}

  # Saving the initial globals dict so as to compare it after code execution
  globals_dict = globals()
  result_string = ''

  # XXX: The focus is on 'ok' status only, we're letting errors to be raised on
  # erp5 for now, so as not to hinder the transactions while catching them.
  # TODO: This can be refactored by using client side error handling instead of
  # catching errors on server/erp5.
  #
  local_variable_dict = copy.deepcopy(old_local_variable_dict)

  # Execute only if jupyter_code is not empty
  #
  if jupyter_code:
    # Create ast parse tree
    #
    try:
      ast_node = ImportFixer().visit(ast.parse(jupyter_code))
      environment_collector = EnvironmentParser()
      ast_node = environment_collector.visit(ast_node)
    except Exception as e:
      # It's not necessary to abort the current transaction here 'cause the 
      # user's code wasn't executed at all yet.
      #
      return getErrorMessageForException(self, e, local_variable_dict)
    
    # Get the node list from the parsed tree
    #
    nodelist = ast_node.body

    # Handle case for empty nodelist(in case of comments as jupyter_code)
    #
    if nodelist:
      # If the last node is instance of ast.Expr, set its interactivity as 'last'
      # This would be the case if the last node is expression
      #
      if isinstance(nodelist[-1], ast.Expr):
        interactivity = "last"
      else:
        interactivity = "none"

      # Here, we define which nodes to execute with 'single' and which to execute
      # with 'exec' mode.
      #
      if interactivity == 'none':
        to_run_exec, to_run_interactive = nodelist, []
      elif interactivity == 'last':
        to_run_exec, to_run_interactive = nodelist[:-1], nodelist[-1:]

      # TODO: fix this global handling by replacing the print statement with
      # a custom print function. Tip: create an ast.NodeTransformer, like the
      # one used to fix imports.
      #
      old_stdout = sys.stdout
      result = StringIO()
      sys.stdout = result
      
      # Variables used at the display hook to get the proper form to display
      # the last returning variable of any code cell.
      #
      display_data = {'result': '', 'mime_type': None}
      
      # This is where one part of the  display magic happens. We create an 
      # instance of ProcessorList and add each of the built-in processors.
      # The classes which each of them are responsiblefor rendering are defined
      # in the classes themselves.
      #
      # The customized display hook will automatically use the processor
      # of the matching class to decide how the object should be displayed.
      #        
      processor_list = ProcessorList()
      processor_list.addProcessor(IPythonDisplayObjectProcessor)
      processor_list.addProcessor(MatplotlibFigureProcessor)
      processor_list.addProcessor(ERP5ImageProcessor)
      processor_list.addProcessor(IPythonDisplayObjectProcessor)
      
      # Putting necessary variables in the `exec` calls context and storing
      #
      inject_variable_dict = {
        'context': self,
        'environment': Environment(),
        '_display_data': display_data,
        '_processor_list': processor_list,
        '_volatile_variable_list': []
      }
      user_context.update(inject_variable_dict)
      user_context.update(local_variable_dict['variables'])
      
      # Getting the environment setup defined in the current code cell
      #
      current_setup_dict = environment_collector.getEnvironmentSetupDict()
      current_var_dict = environment_collector.getEnvironmentVarDict()

      # Removing old setup from the setup functions
      #
      removed_setup_message_list = []
      for func_alias in environment_collector.getEnvironmentRemoveList():
        found = False
        for key, data in local_variable_dict['setup'].items():
          if key == func_alias:
            found = True
            func_name = data['func_name']
            del local_variable_dict['setup'][func_alias]
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
          raise Exception("Trying to remove non existing function/variable from environment: '%s'\nEnvironment: %s" % (func_alias, str(local_variable_dict['setup'])))
      
      # Removing all the setup functions if user call environment.clearAll()
      #
      if environment_collector.clearAll():
        keys = local_variable_dict['setup'].keys()
        for key in keys:
          del local_variable_dict['setup'][key]
      
      # Running all the setup functions that we got
      #
      for key, value in local_variable_dict['setup'].iteritems():
        try:
          code = compile(value['code'], '<string>', 'exec')
          exec(code, user_context, user_context)
        except:
          etype, exc_value, tb = sys.exc_info()
          if value['func_name'] in user_context:
            del user_context[value['func_name']]
          result_string += (
            "An error happened when trying to run the setup function %s (%s). "
            "This setup function was ignored. The error was: %s.\n"
          ) % (value['func_name'], key, str(exc_value))
      
      # Iterating over envinronment.define calls captured by the environment collector
      # that are functions and saving them as setup functions.
      #
      for func_name, data in current_setup_dict.iteritems():
        setup_string = (
          "%s\n"
          "_result = %s()\n"
          "if _result and isinstance(_result, dict):\n"
          "    globals().update(_result)\n"
          "_volatile_variable_list += _result.keys()\n"
          "del %s, _result\n"
        ) % (data['code'], func_name, func_name)
        local_variable_dict['setup'][data['alias']] = {
          "func_name": func_name,
          "code": setup_string
        }

      # Iterating over envinronment.define calls captured by the environment collector
      # that are simple variables and saving them in the setup.
      #
      for variable, value, in current_var_dict.iteritems():
        setup_string = "%s = %s\n" % (variable, repr(value))
        local_variable_dict['setup'][variable] = {
          'func_name': variable,
          'code': setup_string
        }
        user_context['_volatile_variable_list'] += variable
        
      if environment_collector.showEnvironmentSetup():
        result_string += "%s\n" % str(local_variable_dict['setup'])
        # environment_list = []
        # for func_alias, data in local_variable_dict['setup'].iteritems():
        #   environment_list.append([data['func_name'], func_alias])
        # result_string += "%s\n" % environment_list

      # Execute the nodes with 'exec' mode
      #
      for node in to_run_exec:
        mod = ast.Module([node])
        code = compile(mod, '<string>', "exec")
        try:
          exec(code, user_context, user_context)
        except Exception as e:
          # Abort the current transaction. As a consequence, the notebook lines
          # are not added if an exception occurs.
          #
          # TODO: store which notebook line generated which exception.
          #
          transaction.abort()
          # Clear the portal cache from previous transaction
          self.getPortalObject().portal_caches.clearAllCache()
          return getErrorMessageForException(self, e, local_variable_dict)

      # Execute the interactive nodes with 'single' mode
      #
      for node in to_run_interactive:
        mod = ast.Interactive([node])
        try:
          code = compile(mod, '<string>', 'single')
          exec(code, user_context, user_context)
        except Exception as e:
          # Abort the current transaction. As a consequence, the notebook lines
          # are not added if an exception occurs.
          #
          # TODO: store which notebook line generated which exception.
          #
          transaction.abort()
          # Clear the portal cache from previous transaction
          self.getPortalObject().portal_caches.clearAllCache()
          return getErrorMessageForException(self, e, local_variable_dict)

      sys.stdout = old_stdout
      mime_type = display_data['mime_type'] or mime_type
      result_string += "\n".join(removed_setup_message_list) + result.getvalue() + display_data['result']
    
    # Checking in the user context what variables are pickleable and we can store
    # safely. Everything that is not pickleable shall not be stored and the user
    # needs to be warned about it.
    #
    volatile_variable_list = current_setup_dict.keys() + inject_variable_dict.keys() + user_context['_volatile_variable_list']
    del user_context['_volatile_variable_list']
    for key, val in user_context.items():
      if not key in globals_dict.keys() and not isinstance(val, ModuleType) and not key in volatile_variable_list:
        try:
          import pickle
          pickle.dumps(val)
          local_variable_dict['variables'][key] = val
        except:
          del user_context[key]
          result_string += ("Cannot pickle the variable named %s whose value is %s, "
                            "thus it will not be stored in the context. "
                            "You should move it's definition to a function and " 
                            "use the environment object to load it.\n") % (key, val)
    
    # Deleting from the variable storage the keys that are not in the user 
    # context anymore (i.e., variables that are deleted by the user)
    #
    for key in local_variable_dict['variables'].keys():
      if not key in user_context:
        del local_variable_dict['variables'][key]

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
              message = (
                'Not enough arguments for environment definition. Function '
                'name and alias are required.'
              )
              raise Exception(message)
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
              #
              node_value_dict = {
                ast.Num: lambda node: str(node.n),
                ast.Str: lambda node: node.s,
                ast.Name: lambda node: node.id
              }
              arg_value = node_value_dict[type(arg_value_node)](arg_value_node)
              self.environment_var_dict[arg_name] = arg_value
          elif name == 'environment' and function.attr == 'undefine':
            func_alias = value.args[0].s
            self.environment_remove_list.append(func_alias)
          elif name == 'environment' and function.attr == 'clearAll':
            self.environment_clear_all = True
          elif name == 'environment'and function.attr == 'showSetup':
            self.show_environment_setup = True
    return node
    
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
          self.import_func_dict[alias.name] = node.name  
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
    module_name = node.names[0].name
    if getattr(node.names[0], 'asname'):
      module_name = node.names[0].asname
    if not self.import_func_dict.get(module_name):
      empty_function = self.newEmptyFunction("%s_setup" % module_name)
      return_dict = self.newReturnDict(module_name)
      empty_function.body = [node, return_dict]
      environment_set = self.newEnvironmentSetCall("%s_setup" % module_name)
      warning = self.newImportWarningCall(module_name)
      return [empty_function, environment_set, warning]
    else:
      return node

  def newEmptyFunction(self, func_name):
    """
      Return a AST.Function object representing a function with name `func_name`
      and an empty body.
    """
    func_body = "def %s(): pass" % func_name
    return ast.parse(func_body).body[0]

  def newReturnDict(self, module_name):
    """
      Return an AST.Expr representing a returned dict with one single key named
      `'module_name'` (as string) which returns the variable `module_name` (as 
      exoression).
    """
    return_dict = "return {'%s': %s}" % (module_name, module_name)
    return ast.parse(return_dict).body[0]

  def newEnvironmentSetCall(self, func_name):
    """
      Return an AST.Expr representaion an `environment.define` call receiving
      `func_name` (as an expression) and `'func_name'` (as string).
    """
    code_string = "environment.define(%s, '%s')" % (func_name, func_name)
    tree = ast.parse(code_string)
    return tree.body[0]

  def newImportWarningCall(self, module_name):
    """
      Return an AST.Expr representanting a print statement with a warning to an
      user about the import of a module named `module_name` and instructs him
      on how to fix it.
    """
    warning = ("print '"
               "WARNING: Your imported the module %s without using "
               "the environment object, which is not recomended. "
               "Your import was automatically converted to use such method."
               "The setup function registered was named %s_setup.\\n" 
               "'") % (module_name, module_name)
    tree = ast.parse(warning)
    return tree.body[0]

  
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
  #   4. Base_compileJupyterCode frame (where we want to change variable)
  #   3. exec call to run the user's code
  #   2. ExternalMethod Patch call through `context.Base_renderAsHtml` in the notebook
  #   1. renderAsHtml frame (where the function is)
  # 
  # So sys._getframe(3) is enough to get us up into the frame we want.
  #
  compile_jupyter_frame = sys._getframe(3)
  compile_jupyter_locals = compile_jupyter_frame.f_locals
  processor = compile_jupyter_locals['processor_list'].getProcessorFor(renderable_object)
  result, mime_type = processor(renderable_object).process()
  compile_jupyter_locals['result'].write(result)
  compile_jupyter_locals['display_data']['mime_type'] = 'text/html'

def getErrorMessageForException(self, exception, local_variable_dict):
  '''
    getErrorMessageForException receives an Expcetion object and a context for
    code execution (local_variable_dict) and will return a dict as Jupyter
    requires for error rendering.
  '''
  etype, value, tb = sys.exc_info()
  traceback_text = traceback.format_exc().split('\n')[:-1]
  return {
    'status': 'error',
    'result_string': None,
    'local_variable_dict': local_variable_dict,
    'mime_type': 'text/plain',
    'evalue': str(value),
    'ename': exception.__class__.__name__,
    'traceback': traceback_text
  }

def AddNewLocalVariableDict(self):
  """
  Function to add a new Local Variable for a Data Notebook
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

