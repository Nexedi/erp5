"""Hook called when a person object is closed.

We want to reset reference, which is the user login in the old ERP5Security.
We don't want neither to clone the Logins of the user.
One exception is when a person object is installed from business template.
"""
context.setUserId(None)
context.manage_delObjects(ids=[
  document.getId() for document in context.objectValues(
    portal_type=context.getPortalObject().getPortalLoginTypeList()
  )
])

context.initUserId()
if not context.REQUEST.get('is_business_template_installation', 0):
  context.setReference(None)
