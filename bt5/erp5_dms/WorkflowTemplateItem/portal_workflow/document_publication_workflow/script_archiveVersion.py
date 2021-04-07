"""
This script is invoked each time a new document is published.
The previous version is archived automatically if document has a past
(None being infinitely in the past) publication date.

This will only apply to documents with enough coordinates
(ex. reference, language, version).
"""
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery
document = state_change['object']
reference = document.getReference()
if now is None:
  now = DateTime()
if not reference or document.getEffectiveDate() > now:
  # If this object has no reference, we can not do anything
  return

portal = document.getPortalObject()
portal_catalog = portal.portal_catalog
language = document.getLanguage()
search_kw = {
  'reference': reference,
  'validation_state': validation_state,
  # exclude current workflow changed document
  'uid': SimpleQuery(uid=document.getUid(), comparison_operator='!='),
  'effective_date': ComplexQuery(
    SimpleQuery(effective_date=None),
    SimpleQuery(effective_date=now, comparison_operator='<='),
    logical_operator='or',
  ),
}
if not language:
  # If language is None, we have to check is this document
  # is language independent. In this case, archival is possible
  # But if a document exists with same reference and defined
  # language, we can not do anything
  for old_document in portal_catalog(**search_kw):
    old_document = old_document.getObject()
    if old_document.getValidationState() in validation_state and not old_document.getLanguage():
      old_document.archive()
  return

# We can now archive all documents with same reference and language in published state
search_kw['language'] = language
for old_document in portal_catalog(**search_kw):
  old_document = old_document.getObject()
  if old_document.getValidationState() in validation_state:
    old_document.archive()
