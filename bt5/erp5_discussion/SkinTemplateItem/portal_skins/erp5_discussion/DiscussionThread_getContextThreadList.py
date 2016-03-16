"""This script returns the Discussion Thread list that is associated to this context.
Need a proxy to work correctly with anonymous user"""

if not kw.has_key('portal_type'):
  kw["portal_type"] = "Discussion Thread"
kw["follow_up_uid"] = context.getUid()
 
return [x.getObject() for x in context.portal_catalog(**kw)]
