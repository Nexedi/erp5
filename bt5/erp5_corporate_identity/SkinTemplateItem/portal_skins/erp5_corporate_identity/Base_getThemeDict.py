"""
================================================================================
Create a theme dict for filling templates
=====================================r===========================================
"""
# parameters:
# ------------------------------------------------------------------------------
# format                              Output format for building css paths
# css_path                            Path for template css

blank = ''

# -------------------------------  Set Theme -----------------------------------
# XXX images in portal_skins folders don't convert with ?params. Only format 
# is kept in Base_convertHtmlToSingleFile
img = context.Base_getCustomTemplateParameter("fallback_image") or blank
pdf = ".pdf" if format == "pdf" else blank
css = "default_theme_css_url"
font = "default_theme_font_css_url_list"
param = "?format=png"
theme_logo_alt = "Default Logo"

theme_logo_list = []
theme_logo_dict = {}
theme_reference = None
theme = (
  context.Base_getCustomTemplateProxyParameter("theme") or
  context.Base_getCustomTemplateParameter("theme") or
  context.Base_getCustomTemplateParameter("default_company_title")
)
if theme is not None:
  theme = theme.lower()
  theme_logo_prefix = context.Base_getCustomTemplateParameter("default_logo_prefix")
  if theme_logo_prefix:
    theme_reference = theme_logo_prefix + theme.capitalize()
    theme_logo_list = context.Base_getCustomTemplateProxyParameter("logo", theme_reference)
    if len(theme_logo_list) > 0:
      theme_logo_dict = theme_logo_list[0]
if theme is None:
  theme = "default"

theme_dict = {}
theme_dict["theme"] = theme
theme_dict["theme_logo_description"] = theme_logo_dict.get("description", blank)
theme_dict["theme_logo_url"] = context.Base_getCustomTemplateParameter("fallback_image")
if theme_logo_dict.get("relative_url", None) is not None:
  theme_dict["theme_logo_url"] = theme_logo_dict.get("relative_url") + param
theme_dict["template_css_url"] = css_path + pdf + ".css"
theme_dict["fallback_img_url"] = context.Base_getCustomTemplateParameter("fallback_image") or blank
theme_dict["theme_css_font_list"] = context.Base_getCustomTemplateParameter(font) or []
theme_dict["theme_css_url"] = context.Base_getCustomTemplateParameter(css) or context.Base_getCustomTemplateParameter(css) or blank
return theme_dict
