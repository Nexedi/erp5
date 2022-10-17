theme_used = context.Base_getThemeDict(css_path="template_css/book")

if theme:
  return theme_used.get('theme', '')

document_description = context.REQUEST.get('override_document_description', '')
document_short_title = context.REQUEST.get('override_document_short_title', '')
document_title = context.REQUEST.get('override_document_title', '')
document_version = context.REQUEST.get('override_document_version', '')
document_reference = context.REQUEST.get('override_document_reference', '')

if title:
  return document_title if document_title else context.getTitle()

if short_title:
  return document_short_title if document_short_title else context.getShortTitle()

if reference:
  book_reference = document_reference if document_reference else context.getReference()
  if not book_reference:
    book_title = document_title if document_title else context.getTitle()
    book_prefix = context.portal_preferences.getPreferredCorporateIdentityTemplateBookDocumentPrefix() or "Book."
    book_reference = book_prefix + book_title.replace(" ", ".")
  return book_reference

if description:
  return document_description if document_description else context.getDescription()

if version:
  return document_version if document_version else context.getVersion()

source = context.Base_getSourceDict(
  source = context.getSource(),
  override_source_person_title = context.REQUEST.get('override_source_person_title', None),
  override_source_organisation_title = context.REQUEST.get('override_source_organisation_title', None),
  override_logo_reference=context.REQUEST.get('override_logo_reference', None),
  theme_logo_url=theme_used.get("theme_logo_url", None)
)

if source_organisation:
  return source.get("organisation_title", "")

if source_person:
  return source.get("name", "")

if logo:
  url = source.get('enhanced_logo_url', '')
  return url.split('?')[0]


return ''
