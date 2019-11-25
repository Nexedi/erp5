portal = context.getPortalObject()

if context.cb_dataValid:
  object_list = context.cb_dataItems()
  try:
    portal_type_set = set(x.getPortalType() for x in object_list)
  except AttributeError:
    error_message = 'Sorry, you can not paste these items here.'
  else:
    if portal_type_set.issubset(context.getVisibleAllowedContentTypeList()):
      try:
        context.manage_pasteObjects(portal.REQUEST['__cp'])
      except KeyError:
        error_message = 'Nothing to paste.'
      else:
        #new_id_list = [i['new_id'] for i in new_item_list]
        error_message = 'Items paste in progress.'
    else:
      error_message = 'Sorry, you can not paste these items here.'
else:
  error_message = 'Copy or cut one or more items to paste first.'
return context.Base_redirect(form_id, keep_items=dict(
  portal_status_message=portal.Base_translateString(error_message)))
