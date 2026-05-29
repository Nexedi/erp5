"""Forward unresolved sub-paths to the project app, which resolves the thread."""
if not name:
  return None

redirect_domain = context.getLayoutProperty('redirect_domain', '')
if redirect_domain:
  redirect_url = '%s?old_thread=%s' % (redirect_domain, name)
  context.REQUEST.RESPONSE.redirect(redirect_url, status=301, lock=1)
  return None

# Not migrated: fall back to the default document lookup.
if portal is None:
  portal = context.getPortalObject()
kw['limit'] = 1
document_list = portal.portal_catalog.getDocumentValueList(
  reference={'query': name, 'key': 'ExactMatch'},
  language=language,
  strict_language=strict_language,
  now=now,
  **kw
)
if document_list:
  return document_list[0].getObject()
