Base_translateString = context.getPortalObject().Base_translateString
allowed_type_list = context.getVisibleAllowedContentTypeList()

if not allowed_type_list:
  return context.ERP5Site_redirect(context.absolute_url(), keep_items={'portal_status_message': Base_translateString("You are not allowed to add new content in this context.")})

# newContent will add the first allowed type when we do not specify portal_type=
new_object = context.newContent(portal_type=allowed_type_list[0])

return context.ERP5Site_redirect(new_object.absolute_url(),
                                 keep_items={'portal_status_message': Base_translateString("Object created."),
                                             'editable_mode': 1})
