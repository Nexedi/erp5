theme_used = context.Base_getThemeDict(css_path="template_css/slide")

if theme:
  return theme_used.get('theme', '')

source_dict = context.Base_getSourceDict(
  override_source_organisation_title=context.REQUEST.get('override_source_organisation_title', None),
  override_logo_reference=context.REQUEST.get('override_logo_reference', None),
  theme_logo_url=theme_used.get("theme_logo_url", None))

if logo:
  url = source_dict.get('enhanced_logo_url', '')
  return url.split('?')[0]

if organisation:
  return source_dict.get('organisation_title', '')

return ''
