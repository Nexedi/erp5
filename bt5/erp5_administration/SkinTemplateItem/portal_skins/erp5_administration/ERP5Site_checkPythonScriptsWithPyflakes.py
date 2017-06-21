"""Runs pylint/pyflakes on all python scripts.

TODO / BUGS:
* script containing only a comment cannot be parsed
* wouldn't it be better to use this on a business template to check scripts
from the business template ?
"""
import json

def checkPythonSourceCode(script_instance):
  # printed is from  RestrictedPython.RestrictionMutator the rest comes from
  # RestrictedPython.Utilities.utility_builtins
  extra_builtins = ['printed', 'same_type', 'string', 'sequence', 'random',
    'DateTime', 'whrandom', 'reorder', 'sets', 'test', 'math']
  return json.loads(context.ERP5Site_checkPythonSourceCodeAsJSON(
      {'bound_names': extra_builtins + script_instance.getBindingAssignments().getAssignedNamesInOrder(),
       'params': script_instance.params(),
       'code': unicode(script_instance.read(), 'utf8')
      }))['annotations']

for script_container in (context.portal_skins, context.portal_workflow):
  for script_path, script_instance in context.ZopeFind(script_container, obj_metatypes=['Script (Python)'], search_sub=1):
    for annotation in checkPythonSourceCode(script_instance):
      annotation["script_path"] = "%s/%s" % (script_container.getId(), script_path)
      print "{script_path}:{row}:{column}:{text}".format(**annotation)


return printed
