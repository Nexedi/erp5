"""
  Return the Discussion Forum (via predicate) that owns this Discussion Thread,
  or None if no matching forum is found.
"""
from Products.CMFCore.utils import getToolByName

portal = context.getPortalObject()
domain_tool = getToolByName(portal, 'portal_domains')

forum_list = list(domain_tool.searchPredicateList(
  context,
  portal_type='Discussion Forum',
  validation_state=('published', 'published_alive', 'released',
                    'released_alive', 'shared', 'shared_alive'),
))
if forum_list:
  return forum_list[0]
return None
