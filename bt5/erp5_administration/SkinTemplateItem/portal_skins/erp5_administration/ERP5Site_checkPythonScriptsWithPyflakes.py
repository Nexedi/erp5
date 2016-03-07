"""Runs pyflakes on all python scripts.

TODO / BUGS:
* there is an offset in the line numbers in the reports
* script containing only a comment cannot be parsed
* integrate this directly in python script ZMI
* wouldn't it be better to use this on a business template to check scripts
from the business template ?
"""

pyflakes = context.ERP5Site_runPyflakes

def indent(text):
  return ''.join(("  " + line) for line in text.splitlines(True))

def make_body(script):
  """rewrite a python script as if it was a python function with all
  bound names in the signature.
  """
  bound_names = script.getBindingAssignments().getAssignedNamesInOrder()
  # printed is from  RestrictedPython.RestrictionMutator the rest comes from
  # RestrictedPython.Utilities.utility_builtins
  extra_builtins= ['printed', 'same_type', 'string', 'sequence', 'random',
    'DateTime', 'whrandom', 'reorder', 'sets', 'test', 'math']
  
  params = script.params()
  
  signature_parts = bound_names + extra_builtins
  if params:
    signature_parts += [params]
  signature = ", ".join(signature_parts)
  
  function_name = script.getId().replace(".", "__dot__").replace(" ", "__space__")
  
  body = "def %s(%s):\n%s" % (function_name, signature, indent(script.body()) or "  pass")
  return body


for script_container in (context.portal_skins, context.portal_workflow):
  for script_path, script in context.ZopeFind(script_container, obj_metatypes=['Script (Python)'], search_sub=1):
    err = pyflakes(make_body(script), '%s/%s' % (script_container.getId(), script_path))
    if err:
      print err,

return printed
