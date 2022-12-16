theme_used = context.Base_getThemeDict(css_path="template_css/leaflet", theme_reference=context.REQUEST.get('override_logo_reference', None))

if theme:
  return theme_used.get('theme', '')


source = context.Base_getSourceDict(
  source = context.getSource(),
  override_source_person_title = context.REQUEST.get('override_source_person_title', None),
  override_source_organisation_title = context.REQUEST.get('override_source_organisation_title', None),
  override_logo_reference=context.REQUEST.get('override_logo_reference', None),
  theme_logo_url=theme_used.get("theme_logo_url", None)
)

if sender_company:
  return source.get("organisation_title", "")

if sender:
  return source.get("name", "")

if logo:
  url = source.get('enhanced_logo_url', '')
  return url.split('?')[0]

if leaflet_header:
  override_leaflet_header_title = context.REQUEST.get('override_leaflet_header_title', '')
  return override_leaflet_header_title if override_leaflet_header_title else theme_used.get("theme_logo_description", "")
return ''
