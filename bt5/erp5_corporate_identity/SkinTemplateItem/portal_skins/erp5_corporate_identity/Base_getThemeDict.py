"""
================================================================================
Create a theme dict for filling templates
================================================================================
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

theme_logo = None
theme_logo_url = None
theme_logo_description = blank

theme = (
  context.Base_getCustomTemplateProxyParameter("theme") or
  context.Base_getCustomTemplateParameter("theme") or
  context.Base_getCustomTemplateParameter("default_company_title")
)

if theme is not None:
  logo_prefix = context.Base_getCustomTemplateParameter("default_logo_prefix")
  theme = theme.lower()
  if logo_prefix:
    theme_logo_url = logo_prefix + theme.capitalize()
    try:
      theme_logo = context.restrictedTraverse(theme_logo_url)
    except LookupError:
      #__traceback_info__ = "theme_logo_url: %r" % (theme_logo_url,)
      #raise Exception("%s and context: %r" % (theme_logo_url, context.restrictedTraverse(theme_logo_url),))
      theme_logo = None
      
  if theme_logo:
    theme_logo_description = theme_logo.getDescription()
if theme is None:
  theme = "default"

theme_dict = {}
theme_dict["theme"] = theme
theme_dict["theme_logo_description"] = theme_logo_description
theme_dict["theme_logo_url"] = (theme_logo_url + param) if theme_logo_url is not None else context.Base_getCustomTemplateParameter("fallback_image")
theme_dict["template_css_url"] = css_path + pdf + ".css"
theme_dict["fallback_img_url"] = context.Base_getCustomTemplateParameter("fallback_image") or blank
theme_dict["theme_css_font_list"] = context.Base_getCustomTemplateParameter(font) or []
theme_dict["theme_css_url"] = context.Base_getCustomTemplateParameter(css) or context.Base_getCustomTemplateParameter(css) or blank
return theme_dict
