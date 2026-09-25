"""
  Rows for the project app recent changes feed: one entry per recently changed
  Bug, Task or Task Report, newest first.
  Context: the project app Web Site.
"""
from Products.PythonScripts.standard import Object

# both can arrive as strings when passed through the listbox from the URL
limit = int(kw.get("limit", 50))
size = int(kw.pop("size", limit))
limit = min(size, limit)

portal = context.getPortalObject()
app_url = context.absolute_url()

# mirrors VALID_STATE_LIST in gadget_erp5_page_project_front_page.js, plus the
# states a change is still worth reporting in: draft and delivered
simulation_state_list = ('draft', 'planned', 'auto_planned', 'ordered',
                         'confirmed', 'ready', 'started', 'stopped',
                         'delivered', 'submitted', 'validated')

data_list = []
for brain in portal.portal_catalog(
    portal_type=('Bug', 'Task', 'Task Report'),
    simulation_state=simulation_state_list,
    sort_on=(('modification_date', 'DESC'),),
    limit=limit):
  document = brain.getObject()
  project_title = document.getSourceProjectTitle()
  description_list = [document.getSimulationStateTitle()]
  if project_title:
    description_list.insert(0, project_title)
  data_list.append(Object(**{
    'title': '[%s] %s' % (document.getTranslatedPortalType(),
                          document.getTitle('')),
    'description': ', '.join(description_list),
    'link': '%s/#/%s' % (app_url, document.getRelativeUrl()),
    'guid': document.getRelativeUrl(),
    'pubDate': document.getModificationDate(),
  }))

return data_list
