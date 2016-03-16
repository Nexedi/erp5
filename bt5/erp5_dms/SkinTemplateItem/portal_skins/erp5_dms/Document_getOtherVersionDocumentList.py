"""
  Get other versions of this document.
"""
request = context.REQUEST
portal = context.getPortalObject()

# we can use current_web_document in case it's "embedded" into a Web Section
document = request.get('current_web_document', context)

kw['reference'] = document.getReference()
if kw['reference'] is None:
  # we can not find other "verions" of this document as it doesn't have a reference
  return []
kw['uid'] = '!=%s' %document.getUid()
if 'portal_type' not in kw:
  kw['portal_type'] = context.getPortalDocumentTypeList()
return portal.portal_catalog(**kw)
