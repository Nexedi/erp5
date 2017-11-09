Base_translateString = context.getPortalObject().Base_translateString

if not type_name:
  allowed_type_list = context.getVisibleAllowedContentTypeList()
  if not allowed_type_list:
    return context.Base_redirect(keep_items={'portal_status_message':
      Base_translateString("You are not allowed to add new content in this context.")})
  # newContent will add the first allowed type when we do not specify portal_type=
  type_name = allowed_type_list[0]

if keep_items is None:
  keep_items =  {}
new_content = context.newContent(portal_type=type_name)
keep_items['portal_status_message'] = Base_translateString("Object created.")
keep_items['editable_mode'] = 1
kw = new_content.getRedirectParameterDictAfterAdd(context, **kw)
redirect_url = kw.pop('redirect_url', None)
return new_content.Base_redirect(redirect_url, keep_items=keep_items, **kw)
