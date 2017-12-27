kw = {}

if context.getProperty('incremental_check'):
  last_active_process = context.getLastActiveProcess()
  if last_active_process is not None:
    kw['indexation_timestamp'] = '>= %s' % last_active_process.getStartDate().ISO()

active_process = context.newActiveProcess().getRelativeUrl()
query_string = context.getProperty('catalog_query_string', '')
# the query sould be something like "validation_state:!=deleted validation_state:!=draft portal_type:Organisation" etc
portal = context.getPortalObject()

if query_string is not None:
  kw.update(SearchableText=query_string)

parent_uid =[portal.restrictedTraverse(module).getUid()
             for module in context.getProperty('module_list') or []]
if parent_uid:
  kw.update(parent_uid=parent_uid)


portal.portal_catalog.searchAndActivate(
    method_id='Base_checkAlarmConsistency',
    method_kw={'fixit': fixit, 'active_process': active_process},
    activate_kw={'tag':tag, 'priority': 8},
    **kw)

context.activate(after_tag=tag).getId()
