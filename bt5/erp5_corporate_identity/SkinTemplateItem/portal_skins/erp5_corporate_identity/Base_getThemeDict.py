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
pref = context.getPortalObject().portal_preferences

# theme content might not be visible on the default View
lookup_skin = blank
if skin:
  lookup_skin = "?portal_skin=" + skin

theme_logo_dict = {}
theme = (
  context.Base_getTemplateProxyParameter(parameter="theme", source_data=None) or
  pref.getPreferredCorporateIdentityTemplateDefaultTheme()
)
if not theme_reference and theme is not None:
  theme = theme.lower()
  theme_logo_prefix = pref.getPreferredCorporateIdentityTemplateDefaultLogoPrefix()
  if theme_logo_prefix:
    theme_reference = theme_logo_prefix + theme.capitalize()

if theme_reference:
  theme_logo_list = context.Base_getTemplateProxyParameter(parameter="logo", source_data=theme_reference) or []
  if len(theme_logo_list) > 0:
    theme_logo_dict = theme_logo_list[0]


theme_dict = {
  "theme":theme,
  "theme_logo_description":theme_logo_dict.get("description", blank)
}

fallback_logo_url = pref.getPreferredCorporateIdentityTemplateFallbackLogoRelativeUrl() + "?format=png"
# if a theme logo is available, use it instead and add format=png (note, image
# conversion doesn't seem to work with files loaded from skins folders)
if theme_logo_dict.get("relative_url", None):
  theme_dict["theme_logo_url"] = theme_logo_dict.get("relative_url") + "?format=png"
else:
  theme_dict["theme_logo_url"] = fallback_logo_url

theme_dict["template_css_url"] = css_path + pdf
theme_dict["fallback_img_url"] = fallback_logo_url or blank
theme_dict["theme_css_font_list"] = [x + pdf for x in pref.getPreferredCorporateIdentityTemplateDefaultThemeFontList() or []]
theme_css_url = pref.getPreferredCorporateIdentityTemplateThemeCssRelativeUrl()
if theme_css_url:
  theme_dict["theme_css_url"] = theme_css_url + lookup_skin
else:
  theme_dict["theme_css_url"] = blank
return theme_dict
