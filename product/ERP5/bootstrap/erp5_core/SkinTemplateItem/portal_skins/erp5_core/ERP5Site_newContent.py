"""
This script creates a new content from any part of a Web Site.
Content will be created in the appropriate module. It is
intended to be called from the user interface only.
"""
translateString = context.Base_translateString

# Create the new content in appropriate module
portal_object = context.getPortalObject()
module = portal_object.getDefaultModule(portal_type)
new_object = module.newContent(portal_type=portal_type)

# Redirect to new content with translated message
portal_status_message = translateString("New ${portal_type} created.", mapping = dict(portal_type = portal_type))
return new_object.Base_redirect('view', keep_items = dict(portal_status_message=portal_status_message,
                                                          editable_mode=1))
