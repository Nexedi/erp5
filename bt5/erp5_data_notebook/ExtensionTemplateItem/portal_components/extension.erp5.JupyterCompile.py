# -*- coding: utf-8 -*-

from cStringIO import StringIO
from Products.ERP5Type.Globals import  PersistentMapping
from erp5.portal_type import Image


import sys
import traceback
import ast
import types
import base64

from matplotlib.figure import Figure
from IPython.core.display import DisplayObject
from IPython.lib.display import IFrame


mime_type = 'text/plain'
# IPython expects 2 status message - 'ok', 'error'
status = u'ok'
ename, evalue, tb_list = None, None, None

def Base_executeJupyter(self, python_expression=None, reference=None, title=None, request_reference=False, **kw):
  context = self
  portal = context.getPortalObject()
  # Check permissions for current user and display message to non-authorized user 
  if not portal.Base_checkPermission('portal_components', 'Manage Portal'):
    return "You are not authorized to access the script"
  
  import json
  
  # Convert the request_reference argument string to their respeced boolean values
  request_reference = {'True': True, 'False': False}.get(request_reference, False)
  
  # Return python dictionary with title and reference of all notebooks
  # for request_reference=True
  if request_reference:
    data_notebook_list = portal.portal_catalog(portal_type='Data Notebook')
    notebook_detail_list = [{'reference': obj.getReference(), 'title': obj.getTitle()} for obj in data_notebook_list]
    return notebook_detail_list
  
  if not reference:
    message = "Please set or use reference for the notebook you want to use"
    return message
  
  # Take python_expression as '' for empty code from jupyter frontend
  if not python_expression:
    python_expression = ''
  
  # Get Data Notebook with the specific reference
  data_notebook = portal.portal_catalog.getResultValue(portal_type='Data Notebook',
                        reference=reference)
  
  # Create new Data Notebook if reference doesn't match with any from existing ones
  if not data_notebook:
    notebook_module = portal.getDefaultModule(portal_type='Data Notebook')
    data_notebook = notebook_module.DataNotebookModule_addDataNotebook(
      title=title,
      reference=reference,
      batch_mode=True
    )
  
  # Add new Data Notebook Line to the Data Notebook
  data_notebook_line = data_notebook.DataNotebook_addDataNotebookLine(
    notebook_code=python_expression,
    batch_mode=True
  )
  
  # Get active_process associated with data_notebook object
  process_id = data_notebook.getProcess()
  active_process = portal.portal_activities[process_id]
  # Add a result object to Active Process object
  result_list = active_process.getResultList()
  
  # Get local variables saves in Active Result, local varibales are saved as
  # persistent mapping object
  old_local_variable_dict = result_list[0].summary
  if not old_local_variable_dict:
    old_local_variable_dict = context.Base_addLocalVariableDict()
  
  # Pass all to code Base_runJupyter external function which would execute the code
  # and returns a dict of result
  final_result = Base_compileJupyterCode(self, python_expression, old_local_variable_dict)
  code_result = final_result['result_string']
  new_local_variable_dict = final_result['local_variable_dict']
  ename = final_result['ename']
  evalue = final_result['evalue']
  traceback = final_result['traceback']
  status = final_result['status']
  mime_type = final_result['mime_type']
  
  # Call to function to update persistent mapping object with new local variables
  # and save the variables in the Active Result pertaining to the current Data Notebook
  new_dict = context.Base_updateLocalVariableDict(new_local_variable_dict)
  result_list[0].edit(summary=new_dict)
  
  result = {
    u'code_result': code_result,
    u'ename': ename,
    u'evalue': evalue,
    u'traceback': traceback,
    u'status': status,
    u'mime_type': mime_type
  }
  
  # Catch exception while seriaizing the result to be passed to jupyter frontend
  # and in case of error put code_result as None and status as 'error' which would
  # be shown by Jupyter frontend
  try:
    serialized_result = json.dumps(result)
  except UnicodeDecodeError:
    result = {
      u'code_result': None,
      u'ename': u'UnicodeDecodeError',
      u'evalue': None,
      u'traceback': None,
      u'status': u'error',
      u'mime_type': mime_type
    }
    serialized_result = json.dumps(result)
  
  data_notebook_line.edit(notebook_code_result=code_result, mime_type=mime_type)
  
  return serialized_result

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
  # Updating global variable mime_type to its original value
  # Required when call to Base_displayImage is made which is changing
  # the value of gloabl mime_type
  # Same for status, ename, evalue, tb_list
  global mime_type, status, ename, evalue, tb_list
  mime_type = 'text/plain'
  status = u'ok'
  ename, evalue, tb_list = None, None, None
  
  # Other way would be to use all the globals variables instead of just an empty
  # dictionary, but that might hamper the speed of exec or eval.
  # Something like -- g = globals(); g['context'] = self;
  g = {}

  # Saving the initial globals dict so as to compare it after code execution
  globals_dict = globals()
  g['context'] = self
  result_string = ''
  # Update globals dict and use it while running exec command
  g.update(old_local_variable_dict['variables'])

  # XXX: The focus is on 'ok' status only, we're letting errors to be raised on
  # erp5 for now, so as not to hinder the transactions while catching them.
  # TODO: This can be refactored by using client side error handling instead of
  # catching errors on server/erp5.
  local_variable_dict = old_local_variable_dict

  # Execute only if jupyter_code is not empty
  if jupyter_code:
  
    # Create ast parse tree
    try:
      ast_node = ast.parse(jupyter_code)
    except Exception as e:
      return getErrorMessageForException(self, e, local_variable_dict)
    # Get the node list from the parsed tree
    nodelist = ast_node.body

    # Handle case for empty nodelist(in case of comments as jupyter_code)
    if nodelist:
      # Import all the modules from local_variable_dict['imports']
      # While any execution, in locals() dict, a module is saved as:
      # code : 'from os import path'
      # {'path': <module 'posixpath'>}
      # So, here we would try to get the name 'posixpath' and import it as 'path'
      for k, v in old_local_variable_dict['imports'].iteritems():
        import_statement_code = 'import %s as %s'%(v, k)
        exec(import_statement_code, g, g)
      
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
      
      # Putting necessary variables in the `exec` calls context.
      # 
      # - result: is required to store the order of manual calls to the rendering
      #   function;
      #
      # - display_data: is required to support mime type changes;
      #
      # - processor_list: is required for the proper rendering of the objects
      #
      g['_display_data'] = display_data
      g['_processor_list'] = processor_list
      
      # Here's where the last part of the display magic happens. This is a 
      # custom display hook to capture last returning variables and render 
      # them in a different form.
      #
      def my_displayhook(value):
        processor = processor_list.getProcessorFor(value)
        result, mime_type = processor(value).process()
        display_data['result'] += result
        display_data['mime_type'] = mime_type
      old_displayhook = sys.displayhook
      sys.displayhook = my_displayhook

      # Execute the nodes with 'exec' mode
      for node in to_run_exec:
        mod = ast.Module([node])
        code = compile(mod, '<string>', "exec")
        try:
          exec(code, g, g)
        except Exception as e:
          return getErrorMessageForException(self, e, local_variable_dict)
      
      # Execute the interactive nodes with 'single' mode
      for node in to_run_interactive:
        mod = ast.Interactive([node])
        code = compile(mod, '<string>', "single")
        try:
          exec(code, g, g)
        except Exception as e:
          return getErrorMessageForException(self, e, local_variable_dict)
      # Letting the code fail in case of error while executing the python script/code
      # XXX: Need to be refactored so to acclimitize transactions failure as well as
      # normal python code failure and show it to user on jupyter frontend.
      # Decided to let this fail silently in backend without letting the frontend
      # user know the error so as to let tranasction or its error be handled by ZODB
      # in uniform way instead of just using half transactions.
      sys.displayhook = old_displayhook
      sys.stdout = old_stdout
      mime_type = display_data['mime_type'] or mime_type
      result_string = result.getvalue() + display_data['result']

    # Difference between the globals variable before and after exec/eval so that
    # we don't have to save unnecessary variables in database which might or might
    # not be picklabale
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
  
def renderAsHtml(self, something):
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
  #   3. Base_compileJupyterCode frame (where we want to change variable)
  #   2. ExternalMethod call through `context.Base_renderAsHtml` in the notebook
  #   1. renderAsHtml frame (where the function is)
  # 
  # So sys._getframe(2) is enough to get us up into the frame we want.
  #
  upper_frame = sys._getframe(2)
  g = upper_frame.f_globals
  processor = g['_processor_list'].getProcessorFor(something)
  result, mime_type = processor(something).process()
  g['result'].write(result)
  g['_display_data']['mime_type'] = 'text/html'

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
    'mime_type': mime_type,
    'evalue': str(value),
    'ename': exception.__class__.__name__,
    'traceback': traceback_text
  }


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

class ObjectProcessor(object):
  '''
    Basic object processor that stores the first parameters of the constructor
    in the `subject` attribute and store the target classes for that processor.
  '''
  TARGET_CLASSES=None
  
  @classmethod
  def getTargetClasses(cls):
    return cls.TARGET_CLASSES
    
  def __init__(self, something):
    self.subject = something

class MatplotlibFigureProcessor(ObjectProcessor):
  '''
    MatplotlibFigureProcessor handles the rich display of 
    matplotlib.figure.Figure objects. It displays them using an img tag with
    the inline png image encoded as base64.
  '''
  TARGET_CLASSES=[Figure,]

  def process(self):
    image_io = StringIO()
    self.subject.savefig(image_io, format='png')
    image_io.seek(0)
    return self._getImageHtml(image_io), 'text/html'
  
  def _getImageHtml(self, image_io):
    return '<img src="data:image/png;base64,%s" />' % base64.b64encode(image_io.getvalue())
    
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
    return '<img src="data:%s;base64,%s" />' % (mime_type, figure_data), 'text/html'

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
    return html_repr, 'text/html' 

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
    for klass in classes:
      self.processors[klass] = processor
      for subclass in klass.__subclasses__():
        self.processors[subclass] = processor
      
  def getProcessorFor(self, something):
    return self.processors.get(something.__class__, self.default_processor)

def storeIFrame(self, html, key):
  memcached_tool = self.getPortalObject().portal_memcached
  memcached_dict = memcached_tool.getMemcachedDict(key_prefix='pivottablejs', plugin_path='portal_memcached/default_memcached_plugin')
  memcached_dict[key] = html
  return True

def erp5PivotTableUI(self, df, erp5_url):
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
  url = "%s/Base_displayPivotTableFrame?key=%s" % (erp5_url, key)
  return IFrame(src=url, width='100%', height='500')
