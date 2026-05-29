"""
Override of WebSection_getDocumentValue for the RedirectAssist skin selection.

When the sub-path matches a Discussion Thread reference, issue a 301 redirect to the project app thread URL
"""
if not name:
  return None

if portal is None:
  portal = context.getPortalObject()

thread_brain_list = portal.portal_catalog(
  portal_type='Discussion Thread',
  reference=name,
  limit=1,
)
if thread_brain_list:
  thread = thread_brain_list[0].getObject()
  forum_list = list(portal.portal_domains.searchPredicateList(
    thread,
    portal_type='Discussion Forum',
    validation_state=('published', 'published_alive', 'released',
                      'released_alive', 'shared', 'shared_alive'),
  ))
  if forum_list:
    forum = forum_list[0]
    redirect_domain = context.getLayoutProperty('redirect_domain', '')
    base_url = redirect_domain.split('/#/')[0]
    redirect_url = (
      '%s/#!push_history_stored_state'
      '?p.jio_key=%s&p.page=form&p.view=view'
      '&n.jio_key=%s&n.page=form&n.view=view'
    ) % (base_url, forum.getRelativeUrl(), thread.getRelativeUrl())
    context.REQUEST.RESPONSE.redirect(redirect_url, status=301, lock=1)
    return None

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
