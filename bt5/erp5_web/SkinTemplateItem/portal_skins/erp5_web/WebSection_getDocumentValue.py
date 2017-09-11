"""
 - the portal parameter was introduced to
   fix acquisition issues within the _aq_dynamic
   lookup from WebSection class.
"""
if portal is None:
  portal = context.getPortalObject()
document_list = portal.portal_catalog.getDocumentValueList(
  reference=name,
  language=language,
  strict_language=strict_language,
  now=now,
  **kw
)
if document_list:
  return document_list[0].getObject()
