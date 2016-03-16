MARKER = ('', None,)
portal = context.getPortalObject()
portal_categories = portal.portal_categories

kw.update({'validation_state' :['validated']})

box_relative_url = context.REQUEST.get('box_relative_url')
box = context.restrictedTraverse(box_relative_url)
preferences = box.KnowledgeBox_getDefaultPreferencesDict()

for key in ('role', 'function', 'site'):
  value = preferences.get('preferred_%s' %key)
  context.log('%s=%s' %(key, value))
  if value not in MARKER:
    kw['%s_uid' %key] = portal_categories.restrictedTraverse('%s/%s' %(key, value)).getUid()

return portal.portal_catalog(**kw)
