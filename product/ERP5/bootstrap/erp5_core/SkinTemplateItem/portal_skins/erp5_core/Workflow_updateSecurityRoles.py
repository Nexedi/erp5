"""
Changes permissions of all objects related to this workflow
"""
from builtins import range
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
ACTIVITY_GROUPING_COUNT = 100
portal_type_id_list = context.getPortalTypeListForWorkflow()
object_list = []
if portal_type_id_list:
  object_list = portal.portal_catalog(portal_type=portal_type_id_list, limit=None)
  portal_activities_activate = portal.portal_activities.activate
  object_path_list = [x.path for x in object_list]
  for i in range(0, len(object_list), ACTIVITY_GROUPING_COUNT):
    current_path_list = object_path_list[i:i+ACTIVITY_GROUPING_COUNT]
    portal_activities_activate(
        activity='SQLQueue',
        priority=3,
    ).callMethodOnObjectList(
        current_path_list,
        'updateRoleMappingsFor',
        wf_id=context.getId(),
    )
message = translateString('No document updated.')
if object_list:
  message = translateString(
      '${document_count} documents updated.',
      mapping={'document_count': len(object_list)},
  )
return context.Base_redirect(form_id, keep_items={'portal_status_message': message})
