"""Hook called when a person object is closed.

We want to reset reference, which is the user login in ERP5Security.
One exception is when a person object is installed from business template.
"""
context.setUserId(None)
context.Person_initUserId()
if not context.REQUEST.get('is_business_template_installation', 0):
  context.setReference(None)
