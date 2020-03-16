"""
  The purpose of the script is to tell if configuration of a site was finished or not.
  It is used from Deployment Tests.
"""
return context.portal_templates.getInstalledBusinessTemplate("erp5_trade", strict=True) is not None
