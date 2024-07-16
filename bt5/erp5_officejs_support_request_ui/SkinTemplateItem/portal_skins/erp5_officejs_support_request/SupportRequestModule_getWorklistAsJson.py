# return worklists from ticket workflow in JSON format
from Products.ERP5Type.Message import translateString
import json
import six
portal = context.getPortalObject()

worklist_query_dict = portal.ERP5Site_getTicketWorkflowWorklistInfoDict(
    portal_type='Support Request'
)

# Query portal actions to get the worklist count and
# extend this information with the query from our helper script.
worklist_action_list = [
  {
    'action_name': six.text_type(translateString(action['name'].rsplit(' (', 1)[0])), # Action name include the count, but we display it separatly.
    'action_count': action['count'],
    'query': worklist_query_dict[action['worklist_id']],
  }
  for action in portal.portal_actions.listFilteredActionsFor(context)['global']
  if action['category'] == 'global'
    and action.get('workflow_id') == 'ticket_workflow'
    and action.get('worklist_id') in worklist_query_dict
]

return json.dumps(worklist_action_list)
