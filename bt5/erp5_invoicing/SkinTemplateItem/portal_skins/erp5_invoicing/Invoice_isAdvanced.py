"""
If the business template 'erp5_advanced_invoicing' is installed, returns True.
If it is not, returns False.
"""
return context.getPortalObject().portal_templates.getInstalledBusinessTemplate(
    'erp5_advanced_invoicing', strict=True) is not None
