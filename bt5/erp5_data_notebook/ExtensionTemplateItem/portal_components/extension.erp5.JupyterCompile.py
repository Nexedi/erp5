# -*- coding: utf-8 -*-

from cStringIO import StringIO
from Products.ERP5Type.Globals import  PersistentMapping
from OFS.Image import Image as OFSImage

import sys
import ast
import types
import inspect

mime_type = 'text/plain'
# IPython expects 2 status message - 'ok', 'error'
status = u'ok'
ename, evalue, tb_list = None, None, None


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
    ast_node = ast.parse(jupyter_code)
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

      # Execute the nodes with 'exec' mode
      for node in to_run_exec:
        mod = ast.Module([node])
        code = compile(mod, '<string>', "exec")
        exec(code, g, g)

      # Execute the interactive nodes with 'single' mode
      for node in to_run_interactive:
        mod = ast.Interactive([node])
        code = compile(mod, '<string>', "single")
        context = self
        exec(code, g, g)

      # Letting the code fail in case of error while executing the python script/code
      # XXX: Need to be refactored so to acclimitize transactions failure as well as
      # normal python code failure and show it to user on jupyter frontend.
      # Decided to let this fail silently in backend without letting the frontend
      # user know the error so as to let tranasction or its error be handled by ZODB
      # in uniform way instead of just using half transactions.

      sys.stdout = old_stdout
      result_string = result.getvalue()

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
  
def Base_displayHTML(self, node):
  """
  External function to identify Jupyter display classes and render them as
  HTML. There are many classes from IPython.core.display or IPython.lib.display 
  that we can use to display media, like audios, videos, images and generic
  HTML/CSS/Javascript. All of them hold their HTML representation in the
  `_repr_html_` method.
  """
  if getattr(node, '_repr_html_'):
    global mime_type
    mime_type = 'text/html'
    html = node._repr_html_()
    print html
    return
    

def Base_displayImage(self, image_object=None):
  """
  External function to display Image objects to jupyter frontend.

  XXX:  This function is intented to be called from Base_executeJupyter 
        or Jupyter frontend.That's why printing string and returning None.
        Also, it clears the plot for Matplotlib object after every call, so
        in case of saving the plot, its essential to call Base_saveImage before
        calling Base_displayImage.

  Parameters
  ----------
  
  image_object :Any image object from ERP5 
                Any matplotlib object from which we can create a plot.
                Can be <matplotlib.lines.Line2D>, <matplotlib.text.Text>, etc.
  
  Output
  -----
  
  Prints base64 encoded string of the plot on which it has been called.

  """
  if image_object:

    import base64
    # Chanage global variable 'mime_type' to 'image/png'
    global mime_type

    # Image object in ERP5 is instance of OFS.Image object
    if isinstance(image_object, OFSImage):
      figdata = base64.b64encode(image_object.getData())
      mime_type = image_object.getContentType()

    # Ensure that the object we are taking as `image_object` is basically a
    # Matplotlib.pyplot module object from which we are seekign the data of the
    # plot .
    elif inspect.ismodule(image_object) and image_object.__name__=="matplotlib.pyplot":

      # Create a ByteFile on the server which would be used to save the plot
      figfile = StringIO()
      # Save plot as 'png' format in the ByteFile
      image_object.savefig(figfile, format='png')
      figfile.seek(0)
      # Encode the value in figfile to base64 string so as to serve it jupyter frontend
      figdata = base64.b64encode(figfile.getvalue())
      mime_type = 'image/png'
      # Clear the plot figures after every execution
      image_object.close()

    # XXX: We are not returning anything because we want this function to be called
    # by Base_executeJupyter , inside exec(), and its better to get the printed string
    # instead of returned string from this function as after exec, we are getting
    # value from stdout and using return we would get that value as string inside
    # an string which is unfavourable.
    print figdata
    return None

def Base_saveImage(self, plot=None, reference=None, **kw):
  """
  Saves generated plots from matplotlib in ERP5 Image module

  XXX:  Use only if bt5 'erp5_wendelin' installed
        This function is intented to be called from Base_executeJupyter 
        or Jupyter frontend.

  Parameters
  ----------
  plot : Matplotlib plot object
  
  reference: Reference of Image object which would be generated
             Id and reference should be always unique
  
  Output
  ------
  Returns None, but saves the plot object as ERP5 image in Image Module with
  reference same as that of data_array_object.
  
  """

  # As already specified in docstring, this function should be called from
  # Base_executeJupyter or Jupyter Frontend which means that it would pass
  # through exec and hence the printed result would be caught in a string and
  # that's why we are using print and returning None.
  if not reference:
    print 'No reference specified for Image object'
    return None
  if not plot:
    print 'No matplotlib plot object specified'
    return None

  filename = '%s.png'%reference
  # Save plot data in buffer
  buff = StringIO()
  plot.savefig(buff, format='png')
  buff.seek(0)
  data = buff.getvalue()

  import time
  image_id = reference+str(time.time())
  # Add new Image object in erp5 with id and reference
  image_module = self.getDefaultModule(portal_type='Image')
  image_module.newContent(
    portal_type='Image',
    id=image_id,
    reference=reference,
    data=data,
    filename=filename)

  return None

def getError(self, previous=1):
  """
  Show error to the frontend and change status of code as 'error' from 'ok'
  
  Parameters
  ----------
  previous: Type - int. The number of the error you want to see.
  Ex: 1 for last error
      2 for 2nd last error and so on..

  """
  error_log_list = self.error_log._getLog()
  if error_log_list:
    if isinstance(previous, int):
      # We need to get the object for last index of list
      error = error_log_list[-previous]
  global status, ename, evalue, tb_list
  status = u'error'
  ename = unicode(error['type'])
  evalue = unicode(error['value'])
  tb_list = [l+'\n' for l in error['tb_text'].split('\n')]

  return None
  
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
  iframe = IFrame(src=url, width='100%', height='500')
  return Base_displayHTML(self, iframe)
