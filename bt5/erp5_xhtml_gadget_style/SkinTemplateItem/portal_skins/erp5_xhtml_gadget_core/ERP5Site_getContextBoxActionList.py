"""
  Return action and modules links for ERP5's navigation
  box.
"""
from json import dumps

portal= context.getPortalObject()
actions = context.Base_filterDuplicateActions(portal.portal_actions.listFilteredActionsFor(context))
preferred_html_style_developper_mode = portal.portal_preferences.getPreferredHtmlStyleDevelopperMode()


# XXX: use client side translation!
translate = context.Base_translateString

def unLazyActionList(action_list):
  # convert to plain dict as list items are lazy calculated ActionInfo instances
  fixed_action_list = []
  for action in action_list:
    d = {}
    for k,v in action.items():
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
result['type_info_list'] = []
result['workflow_list'] = []
result['document_template_list'] = []
result['object_workflow_action_list'] = []
result['object_action_list'] = []
result['object_view_list'] = []
result['folder_action_list'] = []
result['object_jump_list'] = unLazyActionList(actions['object_jump'])

# add links to edit current portal type
if preferred_html_style_developper_mode:
  type_info_list = []
  type_info = portal.portal_types.getTypeInfo(context)
  if type_info is not None:
    type_info_list = [{"title": "-- %s --" %translate("Developer Mode"),
                       "url": ""},
                      {"title": "Edit Portal Type %s" %type_info.getPortalTypeName(),
                       "url": type_info.absolute_url()}]
  result['type_info_list'] = type_info_list

# add links for workflows
if portal.portal_workflow.Base_getSourceVisibility():
  workflow_list = portal.portal_workflow.getWorkflowValueListFor(context)
  if workflow_list:
    result['workflow_list'] = [{"title": "-- %s --" %translate("Workflows"),
                                "url": ""}]
    result['workflow_list'].extend([{"title": x.title,
                                    "url": "%s/manage_main" %x.absolute_url()} for x in workflow_list])
# allowed types to add
visible_allowed_content_type_list = context.getVisibleAllowedContentTypeList()
result['visible_allowed_content_type_list'] = [{"title": "Add %s" %x,
                                                "url": "add %s" %x} for x in visible_allowed_content_type_list]

document_template_list = context.getDocumentTemplateList()
if document_template_list:
  result['document_template_list'] = [{"title": "-- %s --" %translate("Templates"),
                                       "url": ""}]
  result['document_template_list'].extend([{"title": "Add %s" %x,
                                            "url": "template %s" %x} for x in document_template_list])

# workflow actions
object_workflow_action_list = unLazyActionList(actions["workflow"])
if object_workflow_action_list:
  result['object_workflow_action_list'] = [{"title": "-- %s --" %translate("Workflows"),
                                            "url": ""}]
  result['object_workflow_action_list'].extend([{"title": "%s" %x['title'],
                                                 "url": "workflow %s" %x['url']} for x in object_workflow_action_list])

# object actions
object_action_list = unLazyActionList(actions["object_action"])
if object_action_list:
  result['object_action_list'] = [{"title": "-- %s --" %translate("Object"),
                                   "url": ""}]
  result['object_action_list'].extend([{"title": "%s" %x['title'],
                                        "url": "object %s" %x['url']} for x in object_action_list])

# object_view
object_view_list = [i for i in actions["object_view"] if i['id']=='module_view']
object_view_list = unLazyActionList(object_view_list)
if object_view_list:
  result['object_view_list'].extend([{"title": "%s" %x['title'],
                                      "url": "object %s" %x['url']} for x in object_view_list])

# folder ones
folder_action_list = unLazyActionList(actions["folder"])
if folder_action_list:
  result['folder_action_list'] = [{"title": "-- %s --" %translate("Folder"),
                                   "url": ""}]
  result['folder_action_list'].extend([{"title": "%s" %x['title'],
                                        "url": "folder %s" %x['url']} for x in object_action_list])
# XXX: buttons

return dumps(result)
