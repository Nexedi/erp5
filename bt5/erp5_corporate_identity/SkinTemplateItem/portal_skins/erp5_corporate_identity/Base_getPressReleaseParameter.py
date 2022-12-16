theme_used = context.Base_getThemeDict(css_path="template_css/release")

if theme:
  return theme_used.get('theme', '')


source = context.Base_getSourceDict(
  override_source_person_title = context.REQUEST.get('override_source_person_title', None),
  override_source_organisation_title = context.REQUEST.get('override_source_organisation_title', None),
  theme_logo_url=theme_used.get("theme_logo_url", None)
)

if sender_company:
  return source.get("organisation_title", "")

if sender:
  return source.get("name", "")
