"""Add an object of the same type as self in the container, unless
this type cannot be added in the container.
"""
Base_translateString = context.Base_translateString
parent = context.getParentValue()
allowed_type_list = parent.getVisibleAllowedContentTypeList()

if not allowed_type_list:
  return context.ERP5Site_redirect('%s/%s' % (context.absolute_url(), form_id),
        keep_items={'portal_status_message':Base_translateString("You are not allowed to add new content in this context.")})

if context.getPortalType() not in allowed_type_list:
  return context.ERP5Site_redirect('%s/%s' % (context.absolute_url(), form_id),
        keep_items={'portal_status_message':Base_translateString("You are not allowed to add ${portal_type} in this context.",
              mapping=dict(portal_type=context.getTranslatedPortalType()))})
  
new_content = parent.newContent(portal_type=context.getPortalType())
return context.ERP5Site_redirect('%s/%s' % (new_content.absolute_url(), form_id),
              keep_items={'portal_status_message':Base_translateString("Object created.")})
