"""Hook called when a person object is closed.

We want to reset the reference, which is the user login in ERP5Security.
One exception is when a person object is installed from business template.
"""
is_business_template_installation = context.REQUEST.get('is_business_template_installation', 0)
if not is_business_template_installation:
  context.setReference(None)
