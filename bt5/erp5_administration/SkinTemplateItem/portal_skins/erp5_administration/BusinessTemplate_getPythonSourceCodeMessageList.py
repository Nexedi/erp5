"""Return python source code in business template
"""
import json

class Message:
  """A python code linter message, with a link to edit the source code.

  Supports both being displayed in a listbox and being printed.
  """
  def __init__(self, location, message, edit_url):
    self.location = location
    self.message = message
    self.edit_url = edit_url

  def getListItemUrl(self, *args, **kw):
    return self.edit_url

  def getListItemUrlDict(self, *args, **kw):
    return {
      'command': 'raw',
      'options': {
        'url': self.edit_url
      }
    }

  def __repr__(self):
    return "{}:{}".format(self.location, self.message)


portal = context.getPortalObject()
line_list = []

def checkPythonScript(script_instance, script_path):
  """Check a python script, adding messages to global `line_list`
  """
  # printed is from  RestrictedPython.RestrictionMutator the rest comes from
  # RestrictedPython.Utilities.utility_builtins
  extra_builtins = ['printed', 'same_type', 'string', 'sequence', 'random',
    'DateTime', 'whrandom', 'reorder', 'sets', 'test', 'math']
  for annotation in json.loads(portal.ERP5Site_checkPythonSourceCodeAsJSON(
      {'bound_names': extra_builtins +
         script_instance.getBindingAssignments().getAssignedNamesInOrder(),
       'params': script_instance.params(),
       'code': unicode(script_instance.body(), 'utf8')
      }))['annotations']:
    annotation["script_path"] = script_path
    line_list.append(
      Message(
        location="{script_path}:{row}:{column}".format(**annotation),
        message=annotation['text'],
        edit_url="{script_path}/manage_main?line={row}".format(**annotation),))

def checkComponent(component_instance):
  """Check a component, adding messages to global `line_list`
  """
  for annotation in json.loads(portal.ERP5Site_checkPythonSourceCodeAsJSON(
        {'code': unicode(component_instance.getTextContent(), 'utf8')}))['annotations']:
    annotation['component_path'] = component_instance.getRelativeUrl()
    line_list.append(
      Message(
        location="{component_path}:{row}:{column}".format(**annotation),
        message=annotation["text"],
        edit_url="{component_path}?line={row}".format(**annotation),))

# Check scripts
script_container_list = []
for skin_id in context.getTemplateSkinIdList():
  script_container_list.append(portal.portal_skins[skin_id])
for workflow_id in context.getTemplateWorkflowIdList():
  script_container_list.append(portal.portal_workflow[workflow_id])

for script_container in script_container_list:
  for script_path, script_instance in portal.ZopeFind(
      script_container,
      obj_metatypes=['Script (Python)'],
      search_sub=1):
    checkPythonScript(script_instance, "%s/%s" % (
      portal.portal_url.getRelativeUrl(script_container), script_path))

# Check components
for component_id in (
    context.getTemplateExtensionIdList()
    + context.getTemplateDocumentIdList()
    + context.getTemplateMixinIdList()
    + context.getTemplateTestIdList()
    + context.getTemplateModuleComponentIdList()
    + context.getTemplateToolComponentIdList()
  ):
  checkComponent(portal.portal_components[component_id])

return line_list
