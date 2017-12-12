"""
================================================================================
Create a theme dict for filling templates
================================================================================
"""
blank = ''

# --------------------------  External parameters ------------------------------

# eg "Nexedi" specific parameters
customHandler = getattr(context, "WebPage_getCustomParameter", None)

# parameters common to all templates
commonHandler = getattr(context, "WebPage_getCommonParameter", None)
commonProxyHandler = getattr(context, "WebPage_getCommonProxyParameter", None)

def getCustomParameter(my_parameter, my_override_data):
  if customHandler is not None:
    source_data = my_override_data or context.getUid()
    return customHandler(parameter=my_parameter, source_data=source_data)

def getCommonParameter(my_parameter, my_override_data):
  if commonHandler is not None:
    source_data = my_override_data or context.getUid()
    return commonHandler(parameter=my_parameter, source_data=source_data)

def getCommonProxyParameter(my_parameter, my_override_data):
  if commonProxyHandler is not None:
    source_data = my_override_data or context.getUid()
    return commonProxyHandler(parameter=my_parameter, source_data=source_data)

# -------------------------------  Set Theme -----------------------------------
# XXX images in portal_skins folders don't convert with ?params. Only format 
# is kept in Base_convertHtmlToSingleFile
img = getCommonParameter("fallback_image", blank)
pdf = ".pdf" if format == "pdf" else blank
css = "default_theme_css_url"
font = "default_theme_font_css_url_list"
param = "?format=png"
theme_logo_alt = "Default Logo"
default_company_title = getCustomParameter("default_company_title", None)

theme_logo = None
theme_logo_url = None
theme_logo_description = blank

theme = (
  getCommonProxyParameter("theme", None) or
  custom_theme or
  default_company_title
)
if theme and override_batch_mode:
  theme = "default"
if theme is not None:
  logo_prefix = getCustomParameter("default_logo_prefix", None)
  theme = theme.lower()
  if logo_prefix:
    theme_logo_url = logo_prefix + theme.capitalize()
    try:
      theme_logo = context.restrictedTraverse(theme_logo_url)
    except LookupError:
      theme_logo = None
  if theme_logo:
    theme_logo_description = theme_logo.getDescription()
if theme is None:
  theme = "default"

theme_dict = {}
theme_dict["theme"] = theme
theme_dict["theme_logo_description"] = theme_logo_description
theme_dict["theme_logo_url"] = (theme_logo_url + param) if theme_logo_url is not None else getCommonParameter("fallback_image", None)
theme_dict["template_css_url"] = ''.join([url, css_path, pdf, ".css"])
theme_dict["fallback_img_url"] = ''.join([url, '/', img])
theme_dict["theme_css_font_list"] = getCustomParameter(font, None) or []
theme_dict["theme_css_url"] = getCustomParameter(css, None) or getCommonParameter(css, None) or blank
return theme_dict
