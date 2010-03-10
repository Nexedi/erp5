# -*- coding: utf-8 -*-
"""
  This simply sucks, hate doing it this way (Ivan)
"""
import sys
from ZODB.POSException import ConflictError
from Products.Formulator.MethodField import Method
from Products.PythonScripts.PythonScript import PythonScript

def getMethodObject(self, method_id):
  return Method(method_id)
  
def editForm(self, form, update_dicts):
  for key, value in update_dicts.items():
    setattr(form, key, value)
    
def Base_runPythonCode(self, code):
  """
    Run python code
  """
  code_lines = code.split('\r\n')
  python_wrapper_code = """class CodeWrapper:
  def runMethod(code_wrapper_self, self):
    context=self
    if 1:
      %s
"""%'\n      '.join(code_lines)
  exec(compile(python_wrapper_code,"-","exec"))
  wrapper = CodeWrapper()
  return wrapper.runMethod(self)
  

def Base_runPythonScript(self, code):
  script = PythonScript('Python Shell Script').__of__(self)
  code_line_list = code.split('\r\n')
  code = '\n'.join(code_line_list)
  script.write(code)
  if script._code is None:
    raise ValueError, repr(script.errors)

  return script()

def getPythonCodeExecutionError(self):
  result = None
  try:
    self.Base_executePython()
  except ConflictError:
    raise
  except :
    result = sys.exc_info()
  
  return result[1]


import lxml

def updateCodeWithMainContent(self, html_code, div_class):
   main_content = """
       <div class="%s">
        <tal:block metal:define-slot="main"/>
      </div>      
   """ % (div_class)
   document = lxml.html.fromstring(html_code)
   element = document.find_class(div_class)[0]
   element.getparent().replace(element, lxml.html.fromstring(main_content))
   return lxml.html.tostring(document, pretty_print=True)
