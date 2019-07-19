"""
  This script creates a new event with given metadata and
  attaches it to the current bug.
"""
Base_translateString = context.Base_translateString
portal_type = 'Bug'
module = context.getDefaultModule(portal_type)

if portal_type not in module.getVisibleAllowedContentTypeList():
  return context.Base_redirect(form_id,
                               keep_items=dict(
    portal_status_message=Base_translateString("You do not have permission to add new bug.")))

# Create a new event
bug = module.newContent(portal_type=portal_type,
                        description=description,
                        title=title,
                        follow_up=context.getRelativeUrl())

# Redirect to even
portal_status_message = Base_translateString(
  "Created and associated a new ${portal_type} to the ticket.",
  mapping = dict(portal_type=Base_translateString(portal_type)))
kw['keep_items'] = dict(portal_status_message=portal_status_message)
return bug.Base_redirect('view', **kw)
