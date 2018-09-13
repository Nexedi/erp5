"""
================================================================================
Create a theme dict for filling templates
=================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# doc_format                          Output format for building css paths
# css_path                            Path for template css

blank = ''

# -------------------------------  Set Theme -----------------------------------
# XXX images in portal_skins folders don't convert with ?params. Only format
# is kept in Base_convertHtmlToSingleFile
pdf = ".pdf.css" if doc_format == "pdf" else ".css"
css = "default_theme_css_url"
font = "default_theme_font_css_url_list"
param = "?format=png"

# theme content might not be visible on the default View
lookup_skin = blank
if skin:
  lookup_skin = "?portal_skin=" + skin

theme_logo_list = []
theme_logo_dict = {}
theme_reference = None
theme = (
  context.Base_getTemplateProxyParameter(parameter="theme", source_data=None) or
  context.Base_getTemplateParameter("theme") or
  context.Base_getTemplateParameter("default_company_title")
)
if theme is not None:
  theme = theme.lower()
  theme_logo_prefix = context.Base_getTemplateParameter("default_logo_prefix")
  if theme_logo_prefix:
    theme_reference = theme_logo_prefix + theme.capitalize()
    theme_logo_list = context.Base_getTemplateProxyParameter(parameter="logo", source_data=theme_reference) or []
    if len(theme_logo_list) > 0:
      theme_logo_dict = theme_logo_list[0]
if theme is None:
  theme = "default"

theme_dict = {}
theme_dict["theme"] = theme
theme_dict["theme_logo_description"] = theme_logo_dict.get("description", blank)
theme_dict["theme_logo_url"] = context.Base_getTemplateParameter("fallback_image")
if theme_logo_dict.get("relative_url", None) is not None:
  theme_dict["theme_logo_url"] = theme_logo_dict.get("relative_url") + param
theme_dict["template_css_url"] = css_path + pdf
theme_dict["fallback_img_url"] = context.Base_getTemplateParameter("fallback_image") or blank
theme_dict["theme_css_font_list"] = []
theme_font_list = context.Base_getTemplateParameter(font) or []
for font in theme_font_list:
  theme_dict["theme_css_font_list"].append(font + pdf)
theme_css_url = context.Base_getTemplateParameter(css)
if theme_css_url:
  theme_dict["theme_css_url"] = context.Base_getTemplateParameter(css) + lookup_skin
else:
  theme_dict["theme_css_url"] = blank
return theme_dict
