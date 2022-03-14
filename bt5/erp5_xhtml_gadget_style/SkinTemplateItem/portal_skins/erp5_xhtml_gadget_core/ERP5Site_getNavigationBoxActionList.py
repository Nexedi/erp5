"""
  Return action and modules links for ERP5's navigation
  box.
"""
from builtins import str
from json import dumps

portal= context.getPortalObject()

def unLazyActionList(action_list):
  # convert to plain dict as list items are lazy calculated ActionInfo instances
  fixed_action_list = []
  for action in action_list:
    d = {}
    for k,v in list(action.items()):
      if k in ['url', 'title']:
        if k == 'url':
          # escape '&' as not possible use it in a JSON string
          if type(v)!=type('s'):
            # this is a tales expression so we need to calculate it
            v = str(context.execExpression(v))
        d[k] = v
    fixed_action_list.append(d)
  return fixed_action_list

result = {}
module_list = portal.ERP5Site_getModuleItemList()
search_portal_type_list = portal.getPortalDocumentTypeList() + ('Person', 'Organisation',)
language_list = portal.Localizer.get_languages_map()
actions = portal.portal_actions.listFilteredActionsFor(context)
ordered_global_actions = context.getOrderedGlobalActionList(actions['global']);
user_actions = actions['user']

ordered_global_action_list = unLazyActionList(ordered_global_actions)
user_action_list = unLazyActionList(user_actions)

result['favourite_dict'] = {"ordered_global_action_list": ordered_global_action_list,
                            "user_action_list": user_action_list
                            }
result['module_list'] = module_list
result['language_list'] = language_list
result['search_portal_type_list'] = [ [x,x] for x  in search_portal_type_list]

return dumps(result)
