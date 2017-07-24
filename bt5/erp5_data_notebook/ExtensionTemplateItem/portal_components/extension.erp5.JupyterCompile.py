# -*- coding: utf-8 -*-
from matplotlib.figure import Figure
from IPython.core.display import DisplayObject
from IPython.lib.display import IFrame
from cStringIO import StringIO
from erp5.portal_type import Image
from types import ModuleType
from ZODB.serialize import ObjectWriter
import cPickle
import sys
import traceback
import ast
import base64
import json
import transaction
import Acquisition
import astor
from Products.ERP5Type.Log import log
import time
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

  data_notebook_line = data_notebook.DataNotebook_addDataNotebookLine(
                                     notebook_code=python_expression,
                                     batch_mode=True)
  
  # Gets the context associated to the data notebook being used
  old_notebook_context = data_notebook.getNotebookContext()
  if not old_notebook_context:
    old_notebook_context = self.Base_createNotebookContext()
  
  # Pass all to code Base_runJupyter external function which would execute the code
  # and returns a dict of result
  final_result = displayDataWrapper(lambda:Base_runJupyterCode(self, data_notebook_line, old_notebook_context))
    
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
  except TypeError:
    result = {
      u'code_result': None,
      u'print_result': None,
      u'displayhook_result': None,
      u'ename': u'TypeError',
      u'evalue': None,
      u'traceback': None,
      u'status': u'error',
      u'mime_type': result['mime_type']}
    serialized_result = json.dumps(result)

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

def Base_runJupyterCode(self, data_notebook_line, old_notebook_context):
  mime_type = 'text/plain'
  status = u'ok'
  activity_tool = self.getPortalObject().portal_activities
  active_process = activity_tool.newActiveProcess()
  log('active_process = %r' %(active_process,))
  data_notebook_line.activate(
    active_process=active_process
  ).DataNotebookLine_execute(
    active_process=active_process.getRelativeUrl())
  transaction.commit()  # XXX stupid? --> otherwise hasActivity returns False
  activity_error = False
  try_num = 1
  while True:
    # XXX: Of course, instead of looping here, we gonna immediately return some URL,
    #      which will be queried by Jupyter Notebook Server (the guy calling us),
    #      inside of ERP5 kernel and it will poll.
    log('[%s] Try %s' % (active_process.getRelativeUrl(), try_num,))
    try_num += 1
  # XXX: Support activity_error!!
#    if active_process.hasErrorActivity():
#      activity_error = True
#      break
    if not active_process.hasActivity():
      break
    time.sleep(0.5)
    transaction.commit()  # XXX stupid? --> otherwise hasActivity state does not change
  result_list = [q.detail for q in active_process.getResultList()]
  log(repr(result_list))
  output = '\n'.join(result_list)
  notebook_context = {}
  displayhook_result = None
  evalue = None
  ename = None
  tb_list = None
  result = {
    'result_string': output,
    'print_result': {"data":{"text/plain":output}, "metadata":{}},
    'displayhook_result': displayhook_result,
    'notebook_context': notebook_context,
    'status': status,
    'mime_type': mime_type,
    'evalue': evalue,
    'ename': ename,
    'traceback': tb_list
  }
  return mergeTracebackListIntoResultDict(result, [])


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
      cPickle.loads(cPickle.dumps(obj))
    # By unknowing reasons, trying to catch cPickle.PicklingError in the "normal"
    # way isn't working. This issue might be related to some weirdness in 
    # pickle/cPickle that is reported in this issue: http://bugs.python.org/issue1457119.
    #
    # So, as a temporary fix, we're investigating the exception's class name as
    # string to be able to identify them.
    # 
    # Even though the issue seems complicated, this quickfix should be 
    # properly rewritten in a better way as soon as possible.
    except (cPickle.PicklingError, TypeError, NameError, AttributeError):
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
