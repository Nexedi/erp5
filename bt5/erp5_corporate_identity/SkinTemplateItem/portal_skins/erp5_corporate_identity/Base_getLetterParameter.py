theme_used = context.Base_getThemeDict(css_path="template_css/letter")

if theme:
  return theme_used.get('theme', '')


letter_source = context.Base_getSourceDict(
  source = context.getSource(),
  override_source_person_title = context.REQUEST.get('override_source_person_title', None),
  override_source_organisation_title = context.REQUEST.get('override_source_organisation_title', None),
  override_logo_reference=None,
  theme_logo_url=theme_used.get("theme_logo_url", None),
  letter_context=True
)

if sender_company:
  return letter_source.get("organisation_title", "")

if sender:
  return letter_source.get("name", "")

letter_destination = context.Base_getDestinationDict(
  destination=context.getDestination(),
  override_destination_person_title=context.REQUEST.get('override_destination_person_title', None),
  override_destination_organisation_title= context.REQUEST.get('override_destination_organisation_title', None)
)

if recipient_company:
  return letter_destination.get("organisation_title", "")
if recipient:
  return letter_destination.get("name", "")

return ''
