"""
If the business template 'erp5_advanced_invoicing' is installed, returns True.
If it is not, returns False.
"""
business_template_list = context.portal_templates.getInstalledBusinessTemplateList()
return filter(lambda x: x.getTitle() == "erp5_advanced_invoicing", business_template_list, False)
