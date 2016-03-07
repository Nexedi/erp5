"""
  Script used by UNG Docs. searchFolder() is used instead of portal_catalog 
  because is needed ignore ERP5 Templates added in UNG Preference.
"""
return context.web_page_module.searchFolder(**kw)
