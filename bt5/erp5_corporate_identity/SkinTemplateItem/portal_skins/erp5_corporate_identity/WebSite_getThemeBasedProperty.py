"""
================================================================================
(Backcompat) Retrieve theme parameter for Website css
================================================================================
"""
# XXX Keep until a new website template is available, the old erp5_ci_web needs
# to keep working. This method fetches the parameters required. Remove once no
# longer needed.

# parameters   (* default)
# ------------------------------------------------------------------------------
# parameter:                   parameter to retriev
# proxy:                       proxy role is required to access parameter
# source_uid:                  uid to use when requiring parameter value

page = context

if parameter is not None:
  page_theme = page.Base_getThemeDict(doc_format="html", css_path="template_css/web")
  page_source = page.Base_getSourceDict(theme_logo_url=page_theme.get('theme_logo_url'))
  if parameter == "Theme":
    return page_theme.get("theme")
  if parameter == "default_themes_css_url":
    return page_theme.get("theme_css_url")
  if parameter == "site_publisher":
    return page_source.get('organisation_title') or ''

return "XXX could not retrieve %s" % (parameter or " undefined parameter")
