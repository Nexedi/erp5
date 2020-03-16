"""
If the business template 'erp5_advanced_invoicing' is installed, returns True.
If it is not, returns False.
"""
for bt in context.portal_templates.getInstalledBusinessTemplateList():
  if bt.getTitle() == "erp5_advanced_invoicing":
    return True
return False
